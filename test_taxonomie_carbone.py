"""
Phase 4 - tests qui FIGENT le modele Phase 1.5 (taxonomie 3 familles + double
%ENR + fourchette carbone), sur la fixture JSON figee (zero reseau, voir
tests/README.md). Objectif : detecter toute regression de reclassement
(ex. Diesel bascule par erreur en FOSSILE, ou mapping de casse casse).

Choix (justification) : fichier separe plutot qu'ajout dans test_filieres.py,
parce que ces 3 tests traversent TROIS modules (dashboard_reunion.fetch_data,
filieres.py, agent_expert.compute_carbon_intensity) sur des donnees live
figees, alors que test_filieres.py reste un test unitaire pur du socle
(aucune donnee, aucun import dashboard_reunion/agent_expert).

Rejouable : ./.venv/Scripts/python.exe -m pytest test_taxonomie_carbone.py -v
"""
import pytest

import dashboard_reunion as dash
import agent_expert as ae
import filieres as f
from fixture_utils import load_edf_payload, make_paginated_get

PAYLOAD = load_edf_payload()


@pytest.fixture(scope="module")
def df():
    mp = pytest.MonkeyPatch()
    mp.setattr(dash.requests, "get", make_paginated_get(PAYLOAD))
    try:
        d = dash.fetch_data.__wrapped__(limit=200)
    finally:
        mp.undo()
    assert not d.empty
    return d


# ── Test 1 — mapping nomenclature API -> interne -> libelle affiche ────────
def test_mapping_charbon_diesel_vers_bioenergies_et_libelles(df):
    """
    Charbon (cle API `charbon`) alimente bien la filiere interne `Charbon`
    affichee "Biomasse (ex-Charbon)", et Diesel (`diesel`) -> `Diesel` ->
    "Bioliquide (ex-Diesel)". Les deux sont dans BIOENERGIES, PAS dans
    FOSSILE. Turbines_combustion est la SEULE filiere FOSSILE.
    """
    # a) la fixture brute prouve que la cle API existe et alimente la colonne
    #    interne (valeur non nulle, coherente avec le payload source)
    last_raw = PAYLOAD["results"][0]  # order_by=date desc -> index 0 = plus recent
    last_df = df.iloc[-1]             # df trie ascendant -> iloc[-1] = plus recent
    assert last_df["Charbon"] == pytest.approx(last_raw["charbon"])
    assert last_df["Diesel"] == pytest.approx(last_raw["diesel"])

    # b) libelles d'affichage attendus (source unique filieres.py)
    assert f.label("Charbon") == "Biomasse (ex-Charbon)"
    assert f.label("Diesel") == "Bioliquide (ex-Diesel)"

    # c) classement carbone : Charbon/Diesel dans BIOENERGIES, jamais FOSSILE
    assert "Charbon" in f.BIOENERGIES
    assert "Diesel" in f.BIOENERGIES
    assert "Charbon" not in f.FOSSILE
    assert "Diesel" not in f.FOSSILE

    # d) FOSSILE = exactement {Turbines_combustion}, rien d'autre
    assert f.FOSSILE == ["Turbines_combustion"]


# ── Test 2 — double %ENR sur donnees figees ─────────────────────────────
def test_double_pct_enr_strict_inferieur_reglementaire(df):
    """
    %ENR strict < %ENR reglementaire, les deux dans [0, 100], et le
    reglementaire est eleve sur cette fixture (thermique bio-etiquete a
    pleine charge). Seuil fige a 80% : une regression de classement
    (ex. Charbon/Diesel sortis de ENR_REGLEMENTAIRE) ferait chuter le
    reglementaire pres du niveau du strict (~26% observe) et ferait rougir
    ce test.
    """
    k = dash.compute_kpis(df)
    strict = k["pct_ren_strict"]
    reglementaire = k["pct_ren_reglementaire"]

    assert 0 <= strict <= 100
    assert 0 <= reglementaire <= 100
    assert strict < reglementaire
    assert reglementaire >= 80, (
        f"pct_ren_reglementaire={reglementaire:.1f}% : sous 80%, verifier que "
        f"Charbon/Diesel/Bioénergies sont toujours dans ENR_REGLEMENTAIRE"
    )


# ── Test 3 — compute_carbon_intensity retourne (low, high) plausible ───────
def test_compute_carbon_intensity_fourchette_plausible(df):
    """
    compute_carbon_intensity retourne un tuple (low, high), low <= high,
    et les deux sont > 0 des lors que du thermique/bio tourne (c'est le cas
    sur cette fixture : Charbon/Diesel a pleine charge).

    Borne haute figee < 300 gCO2/kWh : si quelqu'un reclassait Bioliquide
    (Diesel) en fossile (facteur ~700 au lieu de 30-150), la borne haute
    grimperait largement au-dessus de 300 et ce test rougirait.
    """
    last = df.iloc[-1]
    low, high = ae.compute_carbon_intensity(last)

    assert isinstance(low, float) and isinstance(high, float)
    assert low <= high
    assert low > 0, "du thermique/bio tourne sur cette fixture : low doit etre > 0"
    assert high > 0
    assert high < 300, (
        f"borne haute={high:.0f} gCO2/kWh : hors ordre de grandeur attendu "
        f"(68-145 selon CLAUDE.md) - verifier que Diesel n'a pas ete reclasse "
        f"avec un facteur fossile (~700)"
    )
