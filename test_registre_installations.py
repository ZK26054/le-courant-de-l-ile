"""
test_registre_installations.py — Carte des installations (registre EDF, maille
communale, ADR-003). ZÉRO RÉSEAU : `requests.get` est systématiquement patché,
sur le modèle de test_fetch_data.py (voir tests/README.md).

Couvre T1 (centroïdes), T3 (fetch + conversion kW->MW + sum(nbinstallations)
!= count(*) + code INSEE vide), T4 (jointure), T5 (carte à bulles, pur),
T6 (onglet Streamlit via AppTest — dégradation locale + nominal).

Suit le même style « test_AVANT_ / test_APRES_ » que test_fetch_data.py pour
les régressions à casse volontaire (leçon Phase 4, invariant n°4 CLAUDE.md) :
un test_AVANT_ reconstitue le bug hypothétique et prouve qu'il produirait
bien le symptôme observable ; le test_APRES_ correspondant exerce le VRAI
code de production (`registre_installations.fetch_registre_par_commune_filiere`,
jamais une copie recollée) et prouve que ce symptôme n'apparaît pas.
"""
import json
import re
from pathlib import Path

import pandas as pd
import pytest
import requests

import dashboard_reunion as dash
import registre_installations as reg
from fixture_utils import FakeResponse, load_edf_payload, make_paginated_get

REGISTRE_FIXTURE_PATH = Path(__file__).parent / "tests" / "fixtures" / "payload_registre.json"


def load_registre_payload() -> dict:
    """Charge le payload registre figé (capturé le 2026-07-28, voir tests/README.md)."""
    with open(REGISTRE_FIXTURE_PATH, encoding="utf-8") as f:
        return json.load(f)


REGISTRE_PAYLOAD = load_registre_payload()


def make_registre_get(payload: dict):
    """
    Faux `requests.get` pour le registre : sert `payload` à la 1re page
    (offset=0), une page vide ensuite — stoppe la pagination par OFFSET
    (pas de curseur `date` ici : ce registre n'est pas une fenêtre glissante
    temporelle, voir en-tête de registre_installations.py).
    """
    def fake_get(url, params=None, timeout=None):
        params = params or {}
        offset = params.get("offset", 0)
        if offset == 0:
            return FakeResponse(200, json_data=payload)
        return FakeResponse(200, json_data={"total_count": payload.get("total_count", 0), "results": []})
    return fake_get


@pytest.fixture(autouse=True)
def _clear_st_cache_data():
    """Les fonctions décorées @st.cache_data partagent un cache mémoire
    GLOBAL au process : sans purge, un test peut silencieusement lire le
    résultat mis en cache par le test précédent au lieu d'appeler le faux
    requests.get patché ici. Purge avant ET après chaque test."""
    dash.fetch_data.clear()
    reg.fetch_registre_par_commune_filiere.clear()
    reg.load_centroides.clear()
    yield
    dash.fetch_data.clear()
    reg.fetch_registre_par_commune_filiere.clear()
    reg.load_centroides.clear()


# ═══════════════════════════════════════════════════════════════════
#  T1 — Table des centroïdes communaux (geo/communes_974_centroides.json)
# ═══════════════════════════════════════════════════════════════════

def test_centroides_exactement_24_lignes():
    df = reg.load_centroides.__wrapped__()
    assert len(df) == 24, f"attendu 24 communes, obtenu {len(df)}"


def test_centroides_codes_format_insee_et_aucun_doublon():
    df = reg.load_centroides.__wrapped__()
    assert df["codeinseecommune"].is_unique, "code INSEE en double dans les centroïdes"
    for code in df["codeinseecommune"]:
        assert re.match(r"^974\d{2}$", code), f"code INSEE hors format attendu (974xx) : {code}"


def test_centroides_lat_lon_dans_bbox_reunion():
    df = reg.load_centroides.__wrapped__()
    assert df["lat"].between(-21.5, -20.7).all(), f"latitude hors bbox Réunion : {df['lat'].tolist()}"
    assert df["lon"].between(55.1, 55.9).all(), f"longitude hors bbox Réunion : {df['lon'].tolist()}"


def test_load_centroides_preserve_zeros_initiaux(tmp_path):
    """Jointure en STRING STRICT (voir T4) : un code INSEE à zéro initial ne
    doit jamais être interprété comme un entier (qui perdrait ce zéro)."""
    p = tmp_path / "custom_centroides.json"
    p.write_text(
        json.dumps([{"code": "00101", "nom": "Commune Test", "lat": -21.0, "lon": 55.5}]),
        encoding="utf-8",
    )
    df = reg.load_centroides.__wrapped__(path=p)
    assert df.iloc[0]["codeinseecommune"] == "00101", "le zéro initial du code INSEE a été perdu"


# ═══════════════════════════════════════════════════════════════════
#  T3 — fetch_registre_par_commune_filiere : conversion kW->MW,
#  sum(nbinstallations) != count(*), exclusion code INSEE vide
# ═══════════════════════════════════════════════════════════════════

# ── (a) sum(nbinstallations) != count(*) ────────────────────────────
def _fetch_registre_ORIGINE_COUNT_STAR(results: list) -> pd.DataFrame:
    """
    Reconstitution d'un bug HYPOTHÉTIQUE : compter les LIGNES groupées
    (count(*), un "n_inst" de 1 par ligne) au lieu de sommer le champ réel
    `nbinstallations` de l'API. Sous-compte massivement le parc réel, car
    l'API agrège déjà plusieurs installations par ligne (voir CLAUDE.md/ADR-003).
    """
    records = []
    for r in results:
        code = r.get("codeinseecommune")
        if not code:
            continue
        records.append({
            "codeinseecommune": str(code), "commune": r["commune"], "filiere": r["filiere"],
            "mw": (r.get("p_kw") or 0) / 1000.0,
            "n_inst": 1,  # <-- le bug : "une ligne = une installation"
        })
    return pd.DataFrame(records)


def test_AVANT_count_star_sous_compte_massivement_les_installations():
    df_bug = _fetch_registre_ORIGINE_COUNT_STAR(REGISTRE_PAYLOAD["results"])
    total_bug = df_bug["n_inst"].sum()
    assert total_bug == len(df_bug), "reconstitution count(*) : exactement 1 'n_inst' par ligne"
    assert total_bug < 9800, (
        f"count(*) devrait sous-compter largement (obtenu {total_bug}, "
        f"attendu ~9878 avec sum(nbinstallations))"
    )


def test_APRES_total_installations_via_sum_nbinstallations(monkeypatch):
    """Exerce le VRAI code de production : dash.reg.fetch_registre_par_commune_filiere."""
    monkeypatch.setattr(reg.requests, "get", make_registre_get(REGISTRE_PAYLOAD))
    df, _ = reg.fetch_registre_par_commune_filiere.__wrapped__()
    total = int(df["n_inst"].sum())
    assert total == 9878, f"total installations attendu 9878 (sum nbinstallations), obtenu {total}"
    assert total != len(df), (
        "le total ne doit JAMAIS coïncider avec le nombre de lignes groupées (count(*)) : "
        f"{total} vs {len(df)} lignes"
    )


# ── (b) sortie en MW, pas en kW ──────────────────────────────────────
def _fetch_registre_ORIGINE_SANS_CONVERSION_KW(results: list) -> pd.DataFrame:
    """Reconstitution d'un bug HYPOTHÉTIQUE : oublie la conversion kW->MW."""
    records = []
    for r in results:
        code = r.get("codeinseecommune")
        if not code:
            continue
        records.append({
            "codeinseecommune": str(code), "commune": r["commune"],
            "mw": r.get("p_kw") or 0,  # <-- le bug : pas de /1000
        })
    return pd.DataFrame(records)


def test_AVANT_sans_conversion_kw_valeurs_restent_en_milliers():
    df_bug = _fetch_registre_ORIGINE_SANS_CONVERSION_KW(REGISTRE_PAYLOAD["results"])
    le_port = df_bug[df_bug["commune"] == "Le Port"]["mw"].sum()
    assert le_port > 1000, (
        f"sans conversion, Le Port devrait rester en ordre de grandeur kW (obtenu {le_port})"
    )


def test_APRES_conversion_kw_vers_mw_le_port_ordre_de_grandeur_plausible(monkeypatch):
    """Exerce le VRAI code de production. Le Port ≈ 256 MW total (Bioénergies
    211 + Solaire 45, voir tests/fixtures/payload_registre.json), PAS 256000."""
    monkeypatch.setattr(reg.requests, "get", make_registre_get(REGISTRE_PAYLOAD))
    df, _ = reg.fetch_registre_par_commune_filiere.__wrapped__()
    le_port = df[df["commune"] == "Le Port"]["mw"].sum()
    assert 200 < le_port < 300, f"Le Port hors plage MW plausible : {le_port}"
    assert le_port < 1000, "la valeur ne doit plus être en ordre de grandeur kW après conversion"


def test_fetch_preserve_zeros_initiaux_du_code_insee(monkeypatch):
    payload = {
        "total_count": 1,
        "results": [{"codeinseecommune": "00101", "commune": "Test", "filiere": "Solaire",
                     "p_kw": 1000, "n_inst": 1}],
    }
    monkeypatch.setattr(reg.requests, "get", make_registre_get(payload))
    df, _ = reg.fetch_registre_par_commune_filiere.__wrapped__()
    assert df.iloc[0]["codeinseecommune"] == "00101", "le zéro initial du code INSEE a été perdu"


# ── (c) ligne(s) à code INSEE vide/null exclue(s) sans exception, comptées ──
def test_ligne_insee_vide_ou_null_exclue_sans_exception_et_comptee(monkeypatch):
    payload = {
        "total_count": 3,
        "results": [
            {"codeinseecommune": "97407", "commune": "Le Port", "filiere": "Bioénergies",
             "p_kw": 211000, "n_inst": 1},
            {"codeinseecommune": "", "commune": "Inconnu", "filiere": "Solaire",
             "p_kw": 500, "n_inst": 2},
            {"codeinseecommune": None, "commune": "Inconnu2", "filiere": "Eolien",
             "p_kw": 300, "n_inst": 1},
        ],
    }
    monkeypatch.setattr(reg.requests, "get", make_registre_get(payload))
    # Ne doit PAS lever d'exception (dégradation propre, invariant n°3).
    df, n_exclus = reg.fetch_registre_par_commune_filiere.__wrapped__()
    assert n_exclus == 2, f"2 lignes à code INSEE vide/null attendues exclues, obtenu {n_exclus}"
    assert len(df) == 1
    assert df.iloc[0]["codeinseecommune"] == "97407"


def test_fetch_erreur_http_400_leve_httperror_type(monkeypatch):
    """Statut d'erreur (comme le plafond limit>100 du flux temps réel, corps
    text/plain) -> HTTPError typée, pas une exception brute imprévue."""
    def fake_get(url, params=None, timeout=None):
        return FakeResponse(400, text_data="limit should be less than 100")
    monkeypatch.setattr(reg.requests, "get", fake_get)
    with pytest.raises(requests.exceptions.HTTPError):
        reg.fetch_registre_par_commune_filiere.__wrapped__()


def test_fetch_corps_200_non_json_leve_valueerror_geree(monkeypatch):
    """Statut 200 mais corps illisible (non-JSON) : `.json()` naïf lèverait une
    JSONDecodeError brute ; _fetch_registre_page la reconvertit en ValueError
    explicite, que render_carte_tab sait attraper (voir son bloc except)."""
    def fake_get(url, params=None, timeout=None):
        return FakeResponse(200, json_data=None, text_data="pas du json")
    monkeypatch.setattr(reg.requests, "get", fake_get)
    with pytest.raises(ValueError, match="réponse illisible"):
        reg.fetch_registre_par_commune_filiere.__wrapped__()


def test_toutes_les_filieres_observees_ont_une_couleur_dediee():
    """Aucune filière réelle ne doit retomber silencieusement sur la couleur
    par défaut : preuve que la palette locale FILIERE_COLORS est à jour."""
    filieres_observees = {r["filiere"] for r in REGISTRE_PAYLOAD["results"]}
    for f in filieres_observees:
        assert f in reg.FILIERE_COLORS, (
            f"filière '{f}' non couverte par FILIERE_COLORS -> couleur par défaut silencieuse"
        )


# ═══════════════════════════════════════════════════════════════════
#  T4 — joindre_centroides
# ═══════════════════════════════════════════════════════════════════

def test_jointure_nominale_24_communes_sans_orphelin(monkeypatch):
    monkeypatch.setattr(reg.requests, "get", make_registre_get(REGISTRE_PAYLOAD))
    df_registre, n_exclus = reg.fetch_registre_par_commune_filiere.__wrapped__()
    centroides = reg.load_centroides.__wrapped__()

    df_joint, orphelines, communes_sans_donnee = reg.joindre_centroides(df_registre, centroides)

    assert n_exclus == 0
    assert len(df_joint) == 24, f"attendu 24 communes jointes, obtenu {len(df_joint)}"
    assert orphelines == [], f"aucun orphelin attendu sur la fixture réelle, obtenu {orphelines}"
    assert communes_sans_donnee == [], f"toutes les communes ont des données, obtenu {communes_sans_donnee}"
    assert abs(df_joint["mw_total"].sum() - 1200.693) < 0.01


def test_commune_registre_sans_centroide_devient_orpheline():
    df_registre = pd.DataFrame([
        {"codeinseecommune": "97407", "commune": "Le Port", "filiere": "Bioénergies", "mw": 211.0, "n_inst": 1},
        {"codeinseecommune": "99999", "commune": "Commune Fantôme", "filiere": "Solaire", "mw": 5.0, "n_inst": 1},
    ])
    centroides = pd.DataFrame([{"codeinseecommune": "97407", "nom": "Le Port", "lat": -20.9459, "lon": 55.3038}])

    df_joint, orphelines, communes_sans_donnee = reg.joindre_centroides(df_registre, centroides)

    assert "99999" in orphelines, "la commune sans centroïde doit être signalée explicitement"
    assert "99999" not in df_joint["codeinseecommune"].tolist(), "ne doit pas apparaître (NaN silencieux) dans df_joint"
    assert len(df_joint) == 1
    assert communes_sans_donnee == []


def test_commune_centroide_sans_donnee_registre_symetrique():
    df_registre = pd.DataFrame([
        {"codeinseecommune": "97407", "commune": "Le Port", "filiere": "Bioénergies", "mw": 211.0, "n_inst": 1},
    ])
    centroides = pd.DataFrame([
        {"codeinseecommune": "97407", "nom": "Le Port", "lat": -20.9459, "lon": 55.3038},
        {"codeinseecommune": "97424", "nom": "Cilaos", "lat": -21.1403, "lon": 55.4555},
    ])

    df_joint, orphelines, communes_sans_donnee = reg.joindre_centroides(df_registre, centroides)

    assert "97424" in communes_sans_donnee, "Cilaos sans donnée registre doit être signalée"
    assert "97424" not in df_joint["codeinseecommune"].tolist()
    assert len(df_joint) == 1
    assert orphelines == []


# ═══════════════════════════════════════════════════════════════════
#  T5 — make_bubble_map (fonction PURE, sans Streamlit)
# ═══════════════════════════════════════════════════════════════════

def test_bulles_tailles_croissantes_avec_mw_et_dans_la_bbox():
    df_joint = pd.DataFrame([
        {"codeinseecommune": "97401", "commune": "Petit", "lat": -21.20, "lon": 55.36,
         "mw_total": 5.0, "n_inst_total": 2, "filiere_dominante": "Solaire", "mix": "Solaire: 5.0 MW"},
        {"codeinseecommune": "97407", "commune": "Moyen", "lat": -20.95, "lon": 55.30,
         "mw_total": 80.0, "n_inst_total": 10, "filiere_dominante": "Hydraulique", "mix": "Hydraulique: 80.0 MW"},
        {"codeinseecommune": "97419", "commune": "Gros", "lat": -21.18, "lon": 55.74,
         "mw_total": 256.0, "n_inst_total": 8, "filiere_dominante": "Bioénergies", "mix": "Bioénergies: 256.0 MW"},
    ])

    fig = reg.make_bubble_map(df_joint)  # 0 exception attendue

    sizes = list(fig.data[0].marker.size)
    assert sizes[0] < sizes[1] < sizes[2], f"les tailles devraient croître avec la puissance : {sizes}"

    lats, lons = list(fig.data[0].lat), list(fig.data[0].lon)
    assert all(-21.5 <= lat <= -20.7 for lat in lats), f"latitude hors bbox Réunion : {lats}"
    assert all(55.1 <= lon <= 55.9 for lon in lons), f"longitude hors bbox Réunion : {lons}"


def test_bulles_zero_exception_sur_df_joint_vide():
    df_vide = pd.DataFrame(columns=[
        "codeinseecommune", "commune", "lat", "lon", "mw_total", "n_inst_total", "filiere_dominante", "mix",
    ])
    fig = reg.make_bubble_map(df_vide)  # 0 exception attendue, même sur df vide
    assert fig is not None


# ═══════════════════════════════════════════════════════════════════
#  T6 — render_carte_tab, via l'app complète (AppTest)
# ═══════════════════════════════════════════════════════════════════

def _make_dispatch_get(registre_get):
    """
    Faux `requests.get` UNIQUE routé par URL : les deux modules
    (dashboard_reunion et registre_installations) importent le MÊME objet
    module `requests` — patcher `dash.requests.get` patche donc aussi
    `reg.requests.get` (même objet). Ce dispatcher sert le flux temps réel
    normalement (fixture payload_edf.json) et délègue le flux registre au
    comportement `registre_get` fourni par chaque test.
    """
    edf_get = make_paginated_get(load_edf_payload())

    def fake_get(url, params=None, timeout=None):
        if reg.REGISTRE_URL in url:
            return registre_get(url, params, timeout)
        return edf_get(url, params=params, timeout=timeout)
    return fake_get


def test_apptest_carte_ko_degradation_locale_autres_onglets_intacts(monkeypatch):
    """(a) Registre injoignable -> 0 exception non gérée, message LOCAL à
    l'onglet Carte, les 3 autres onglets restent fonctionnels (PAS de st.stop()
    global — invariant n°3)."""
    def registre_ko(url, params, timeout):
        raise requests.exceptions.ConnectionError("simulated: registre injoignable")

    monkeypatch.setattr(dash.requests, "get", _make_dispatch_get(registre_ko))

    at = dash_apptest = __import__("streamlit.testing.v1", fromlist=["AppTest"]).AppTest.from_file(
        str(Path(__file__).parent / "dashboard_reunion.py")
    )
    at.run(timeout=30)

    assert not at.exception, f"exception non gérée : {[e.value for e in at.exception]}"
    # Message d'erreur LOCAL à l'onglet Carte (le dégradé propre attendu).
    messages_erreur = [e.value for e in at.error]
    assert any("Registre des installations indisponible" in m for m in messages_erreur), (
        f"message d'erreur attendu absent, obtenu : {messages_erreur}"
    )
    # Les autres onglets restent rendus : le badge du Dashboard (Total non nul,
    # produit par fetch_data mocké normalement) est bien présent.
    tous_les_markdowns = " ".join(m.value for m in at.markdown)
    assert "Dernière donnée" in tous_les_markdowns, "l'onglet Dashboard ne s'est pas rendu normalement"


def test_apptest_carte_nominal_carte_et_tableau_rendus(monkeypatch):
    """(b) Cas nominal (fixture réelle) : carte + tableau rendus, 0 exception."""
    monkeypatch.setattr(dash.requests, "get", _make_dispatch_get(make_registre_get(REGISTRE_PAYLOAD)))

    at = __import__("streamlit.testing.v1", fromlist=["AppTest"]).AppTest.from_file(
        str(Path(__file__).parent / "dashboard_reunion.py")
    )
    at.run(timeout=30)

    assert not at.exception, f"exception non gérée : {[e.value for e in at.exception]}"
    assert len(at.error) == 0, f"aucune erreur attendue en cas nominal, obtenu : {[e.value for e in at.error]}"
    # Le tableau "Détail par commune" doit contenir les 24 communes jointes.
    assert len(at.dataframe) >= 1, "aucun st.dataframe rendu (tableau détail par commune attendu)"
