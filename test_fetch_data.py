"""
Harnais de regression - gardien-qualite.
Prouve que les 2 bugs d'origine echouaient ET que le code actuel passe.
Rejouable : ./.venv/Scripts/python.exe -m pytest test_fetch_data.py -v
Necessite le reseau (re-probe reel de l'API EDF).
"""
import pandas as pd
import pytest
import requests

import dashboard_reunion as dash

BASE = "https://opendata-reunion.edf.fr/api/explore/v2.1/catalog/datasets/prod-electricite-temps-reel-974/records"


# ── Reconstitution du code FAUTIF d'origine ────────────────────────
COLORS_CAPITALISE = list(dash.COLORS.keys()) + ["Total"]


def fetch_data_ORIGINE_BUG1(limit=200):
    """Bug n1 : order_by='Date DESC' -> HTTP 400 -> DataFrame vide."""
    r = requests.get(BASE, params={"limit": limit, "order_by": "Date DESC"}, timeout=15)
    r.raise_for_status()
    return pd.DataFrame(r.json().get("results", []))


def fetch_data_ORIGINE_BUG2(limit=100):
    """Bug n2 : colonnes API minuscules comparees aux cles COLORS capitalisees
    -> le `else` ecrase tout a 0.0 -> tous les KPI a zero."""
    r = requests.get(BASE, params={"limit": limit, "order_by": "date desc"}, timeout=15)
    df = pd.DataFrame(r.json().get("results", []))
    for col in COLORS_CAPITALISE:
        if col in df.columns:          # 'Total' vs 'total' -> jamais vrai
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
        else:
            df[col] = 0.0              # <-- la faille
    return df


# ── ECHEC AVANT ────────────────────────────────────────────────────
def test_AVANT_bug1_order_by_capitalise_leve_400():
    with pytest.raises(requests.exceptions.HTTPError) as e:
        fetch_data_ORIGINE_BUG1()
    assert e.value.response.status_code == 400


def test_AVANT_bug2_normalisation_met_tous_les_kpi_a_zero():
    df = fetch_data_ORIGINE_BUG2()
    assert not df.empty, "l'API doit repondre pour que le test soit valide"
    for col in COLORS_CAPITALISE:
        assert (df[col] == 0.0).all(), f"{col} devrait etre ecrase a 0 par le bug"


# ── SUCCES APRES (code actuel, cache Streamlit contourne) ──────────
@pytest.fixture(scope="module")
def df():
    d = dash.fetch_data.__wrapped__(limit=200)
    assert not d.empty, "REFUS : fetch_data renvoie un DataFrame vide sur donnees reelles"
    return d


def test_APRES_total_non_nul_ordre_de_grandeur_reunion(df):
    total = df["Total"].iloc[-1]
    assert total > 0, "CRITERE PHASE 0 : Total ne doit PAS etre 0"
    assert 150 < total < 700, f"Total hors plage plausible ZNI Reunion : {total}"


def test_APRES_aucune_filiere_ecrasee_a_zero(df):
    for col in dash.COLORS:
        assert not (df[col] == 0.0).all(), f"{col} entierement a zero -> bug n2 de retour"


def test_APRES_bioenergies_non_nul_accent_preserve(df):
    assert "Bioénergies" in df.columns
    assert df["Bioénergies"].iloc[-1] > 0


def test_APRES_kpi_coherents(df):
    # NOTE Phase 1.5 : compute_kpis ne renvoie plus 'ren'/'pct_ren' (unique) mais
    # 'ren_directes'/'pct_ren_strict' et 'ren_reglementaire'/'pct_ren_reglementaire'
    # (source unique de verite filieres.py, cf. dashboard_reunion.py T3-b).
    k = dash.compute_kpis(df)
    assert k["total"] > 0 and k["ren_reglementaire"] > 0
    assert 0 < k["pct_ren_reglementaire"] <= 100
    assert 0 <= k["pct_ren_strict"] <= 100
    assert k["ren_reglementaire"] <= k["total"]
    assert k["ren_directes"] <= k["ren_reglementaire"]


def test_APRES_somme_filieres_egale_total(df):
    """Sans clip(lower=0) : la somme algebrique des 8 filieres == Total."""
    last = df.iloc[-1]
    somme = sum(last[c] for c in dash.COLORS)
    assert abs(somme - last["Total"]) < 0.01, f"somme={somme} vs Total={last['Total']}"


def test_APRES_negatifs_preserves_non_clippes(df):
    """turbines_combustion / stockage peuvent etre negatifs : ne pas clipper."""
    assert (df[["Turbines_combustion", "Stockage"]].min() < 0).any(), \
        "aucune valeur negative dans l'echantillon : test non concluant"


def test_APRES_pagination_depasse_le_plafond_100(df):
    assert len(df) > 100, f"pagination inoperante : {len(df)} lignes"


def test_APRES_dates_triees_et_uniques(df):
    assert df["Date"].is_monotonic_increasing
    assert df["Date"].is_unique
    assert str(df["Date"].dt.tz) == "Indian/Reunion"


# ── Invariant n3 : degradation propre ──────────────────────────────
def test_degradation_propre_api_injoignable(monkeypatch):
    """API down -> DataFrame vide, PAS de crash."""
    monkeypatch.setattr(dash, "API_URLS", ["https://invalid.invalid/nope"])
    monkeypatch.setattr(dash.st, "error", lambda *a, **k: None)
    out = dash.fetch_data.__wrapped__(limit=10)
    assert isinstance(out, pd.DataFrame) and out.empty


def test_degradation_propre_reponse_vide(monkeypatch):
    class FakeResp:
        status_code = 200
        def raise_for_status(self): pass
        def json(self): return {"results": []}
    monkeypatch.setattr(dash.requests, "get", lambda *a, **k: FakeResp())
    monkeypatch.setattr(dash.st, "error", lambda *a, **k: None)
    out = dash.fetch_data.__wrapped__(limit=10)
    assert isinstance(out, pd.DataFrame) and out.empty


def test_degradation_propre_compute_kpis_df_vide():
    assert dash.compute_kpis(pd.DataFrame()) == {}
