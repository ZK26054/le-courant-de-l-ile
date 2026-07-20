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


def make_paginated_get(payload: dict):
    """
    Fabrique un faux `requests.get` qui sert `payload` (fixture, 100 lignes max)
    à offset=0, puis une page vide à tout offset suivant — ce qui STOPPE la
    pagination de `_fetch_records` sans boucle infinie, exactement comme le
    ferait l'API réelle une fois le jeu de données épuisé.
    """
    def fake_get(url, params=None, timeout=None):
        params = params or {}
        offset = params.get("offset", 0)
        if offset == 0:
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
        offset = params.get("offset", 0)
        if offset == 0:
            return FakeResponse(200, json_data=payload)
        return FakeResponse(200, json_data={"total_count": payload.get("total_count", 0), "results": []})
    return fake_get


def make_synthetic_two_page_get(page1_size: int = 100, page2_size: int = 30):
    """
    Fabrique un faux `requests.get` synthétique (données factices minimales,
    PAS la fixture réelle) qui sert deux pages distinctes selon `offset`,
    dédiées à prouver le MÉCANISME de pagination de `_fetch_records`
    (respect du plafond API_MAX_LIMIT=100, avance de l'offset, assemblage
    des pages) indépendamment du contenu réel capturé le 2026-07-20.
    """
    def make_row(i):
        return {
            "date": f"2026-01-01T00:{i:02d}:00+00:00",
            "jour": "2026-01-01",
            "statut": "Validé",
            "total": float(i),
            "photovoltaique": 0.0, "eolien": 0.0, "hydraulique": 0.0,
            "bioenergies": 0.0, "charbon": 0.0, "diesel": 0.0,
            "turbines_combustion": 0.0, "stockage": 0.0,
        }

    page1 = [make_row(i) for i in range(page1_size)]
    page2 = [make_row(i) for i in range(page1_size, page1_size + page2_size)]

    def fake_get(url, params=None, timeout=None):
        params = params or {}
        offset = params.get("offset", 0)
        if offset == 0:
            return FakeResponse(200, json_data={"total_count": page1_size + page2_size, "results": page1})
        elif offset == page1_size:
            return FakeResponse(200, json_data={"total_count": page1_size + page2_size, "results": page2})
        return FakeResponse(200, json_data={"total_count": page1_size + page2_size, "results": []})
    return fake_get
