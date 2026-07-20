"""
fixture_utils.py — utilitaires PARTAGÉS pour les tests, zéro réseau.

Charge la fixture JSON figée (tests/fixtures/payload_edf.json, capturée le
2026-07-20 sur l'endpoint explore v2.1 réel — voir tests/README.md) et fournit
de petits doubles de test (`FakeResponse`, fabriques de `requests.get` factices)
pour que TOUS les tests du projet s'exécutent sans accès réseau, y compris
ceux qui reconstituent les 2 bugs d'origine.

Ce fichier n'est PAS un test (pas de préfixe `test_`) : pytest ne le collecte
pas, il est seulement importé par les modules de test.
"""
import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

FIXTURE_PATH = Path(__file__).parent / "tests" / "fixtures" / "payload_edf.json"


def load_edf_payload() -> dict:
    """Charge le payload EDF figé : {"total_count": N, "results": [...]}."""
    with open(FIXTURE_PATH, encoding="utf-8") as f:
        return json.load(f)


class FakeResponse:
    """Double minimal de requests.Response, suffisant pour fetch_data/_fetch_records."""

    def __init__(self, status_code=200, json_data=None, text_data=""):
        self.status_code = status_code
        self._json = json_data
        # Corps texte brut : utile pour simuler les erreurs 400 de l'API
        # explore v2.1, qui répondent en text/plain (pas en JSON).
        self.text = text_data

    def raise_for_status(self):
        if self.status_code >= 400:
            import requests
            err = requests.exceptions.HTTPError(f"{self.status_code} Error")
            err.response = self
            raise err

    def json(self):
        if self._json is None:
            # Reproduit le comportement réel : un corps text/plain fait
            # planter un .json() naïf avec une ValueError (JSONDecodeError).
            raise ValueError("No JSON object could be decoded (réponse text/plain)")
        return self._json


def _extract_cursor(params: dict):
    """Extrait la date-curseur d'un paramètre `where="date < '...'"` (pagination
    par curseur, voir dashboard_reunion._fetch_records). None si absent."""
    where = params.get("where")
    if not where:
        return None
    m = re.search(r"date < '([^']+)'", where)
    return m.group(1) if m else None


def make_paginated_get(payload: dict):
    """
    Fabrique un faux `requests.get` qui sert `payload` (fixture, 100 lignes max)
    au 1er appel (sans `where`, page ancrée sur rien = première page), puis une
    page vide à tout appel suivant (avec `where`, curseur posé) — ce qui STOPPE
    la pagination de `_fetch_records` sans boucle infinie, exactement comme le
    ferait l'API réelle une fois le jeu de données épuisé (fixture = 100 lignes,
    aucune page suivante disponible).
    """
    def fake_get(url, params=None, timeout=None):
        params = params or {}
        if _extract_cursor(params) is None:
            return FakeResponse(200, json_data=payload)
        return FakeResponse(200, json_data={"total_count": payload.get("total_count", 0), "results": []})
    return fake_get


def make_order_by_sensitive_get(payload: dict):
    """
    Fabrique un faux `requests.get` qui reproduit fidèlement le comportement
    de l'API explore v2.1 vis-à-vis du paramètre `order_by` :
      - `order_by="date desc"` (minuscule, correct) -> sert la fixture, paginée.
      - toute autre valeur (ex. "Date DESC") -> HTTP 400, corps text/plain,
        exactement comme observé lors du re-probe du 2026-07-17.
    """
    def fake_get(url, params=None, timeout=None):
        params = params or {}
        if params.get("order_by") != "date desc":
            return FakeResponse(
                400,
                text_data="Impossible de trier sur le champ Date, il n'existe pas",
            )
        if _extract_cursor(params) is None:
            return FakeResponse(200, json_data=payload)
        return FakeResponse(200, json_data={"total_count": payload.get("total_count", 0), "results": []})
    return fake_get


def make_synthetic_two_page_get(page1_size: int = 100, page2_size: int = 30):
    """
    Fabrique un faux `requests.get` synthétique (données factices minimales,
    PAS la fixture réelle) qui sert deux pages distinctes selon le CURSEUR
    (`where=date < '...'`), dédiées à prouver le MÉCANISME de pagination de
    `_fetch_records` (respect du plafond API_MAX_LIMIT=100, avance du curseur,
    assemblage des pages) indépendamment du contenu réel capturé le 2026-07-20.

    Dates construites en ordre DÉCROISSANT avec `i` (i=0 = la plus récente),
    comme le fait l'API réelle avec `order_by=date desc` : ainsi
    `where=date < '<curseur>'` retrouve exactement la suite logique.
    """
    def make_row(i):
        return {
            "date": f"2026-01-01T00:00:{99999 - i:05d}+00:00",  # decroit avec i
            "jour": "2026-01-01",
            "statut": "Validé",
            "total": float(i),
            "photovoltaique": 0.0, "eolien": 0.0, "hydraulique": 0.0,
            "bioenergies": 0.0, "charbon": 0.0, "diesel": 0.0,
            "turbines_combustion": 0.0, "stockage": 0.0,
        }

    all_rows = [make_row(i) for i in range(page1_size + page2_size)]

    def fake_get(url, params=None, timeout=None):
        params = params or {}
        limit = params.get("limit", 100)
        cursor = _extract_cursor(params)
        pool = all_rows if cursor is None else [r for r in all_rows if r["date"] < cursor]
        page = pool[:limit]
        return FakeResponse(200, json_data={"total_count": len(all_rows), "results": page})
    return fake_get


def make_sliding_window_rows(n_before: int = 130):
    """
    Construit deux instantanés d'une fenêtre glissante synthétique (dates
    ISO 8601 construites pour être triables lexicographiquement comme
    chronologiquement, à l'image de l'API réelle), afin de reproduire le
    glissement documenté dans CLAUDE.md entre deux appels de pagination :
    une nouvelle ligne apparaît en tête pendant qu'on pagine.

    - `before_rows` : instantané au 1er appel — n_before lignes, i=0 la plus
      récente .. i=n_before-1 la plus ancienne.
    - `after_rows`  : instantané au(x) appel(s) suivant(s) — une ligne
      supplémentaire, plus récente que tout `before_rows`, est apparue en
      tête ; toutes les lignes de `before_rows` sont encore présentes
      (glissement par insertion, sans éviction, pour isoler proprement
      l'effet de dérive sur un `offset` fixe).

    Retourne (before_rows, after_rows).
    """
    base = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

    def row(i):
        d = base - timedelta(minutes=5 * i)
        return {
            "date": d.isoformat(),
            "jour": "2026-01-01",
            "statut": "Validé",
            "total": float(100 - i),
            "photovoltaique": 0.0, "eolien": 0.0, "hydraulique": 0.0,
            "bioenergies": 0.0, "charbon": 0.0, "diesel": 0.0,
            "turbines_combustion": 0.0, "stockage": 0.0,
        }

    before_rows = [row(i) for i in range(n_before)]
    new_row = row(-1)  # date plus recente que toutes les before_rows
    after_rows = [new_row] + before_rows
    return before_rows, after_rows


def make_sliding_window_get(before_rows: list, after_rows: list):
    """
    Fabrique un faux `requests.get` qui sert `before_rows` au 1er appel, puis
    `after_rows` à TOUS les appels suivants — simule le temps qui passe
    pendant la pagination (nouvelle(s) ligne(s) arrivée(s) en tête).
    Comprend À LA FOIS le style `offset` (ancienne logique, pour reconstituer
    le bug) et le style curseur `where=date < '...'` (nouvelle logique de
    production), afin qu'un seul mock serve les deux tests AVANT/APRÈS.
    """
    call_count = [0]

    def fake_get(url, params=None, timeout=None):
        params = params or {}
        limit = params.get("limit", 100)
        window = before_rows if call_count[0] == 0 else after_rows
        call_count[0] += 1

        cursor = _extract_cursor(params)
        if cursor is not None:
            pool = [r for r in window if r["date"] < cursor]
            page = pool[:limit]
        else:
            offset = params.get("offset", 0)
            page = window[offset: offset + limit]

        return FakeResponse(200, json_data={"total_count": len(window), "results": page})
    return fake_get
