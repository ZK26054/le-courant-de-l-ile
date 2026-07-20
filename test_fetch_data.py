"""
Harnais de regression - gardien-qualite.
Prouve que les 2 bugs d'origine echouaient ET que le code actuel passe.
Rejouable : ./.venv/Scripts/python.exe -m pytest test_fetch_data.py -v

ZERO RESEAU (Phase 4) : tous les tests s'executent sur la fixture JSON figee
tests/fixtures/payload_edf.json (capturee le 2026-07-20, voir tests/README.md).
`requests.get` est systematiquement patche - aucun appel reseau reel n'est
emis, y compris pour les 2 bugs d'origine et les tests de degradation.
Raison (CLAUDE.md) : l'API sert des donnees a statut "Estime" qui sont
REVISEES entre deux appels -> comparer a un second appel produit de faux
negatifs. Un test fiable capture UN SEUL payload et le fait traverser le
code via `requests.get` patche.
"""
import pandas as pd
import pytest
import requests

import dashboard_reunion as dash
from fixture_utils import (
    load_edf_payload,
    make_paginated_get,
    make_order_by_sensitive_get,
    make_synthetic_two_page_get,
    make_sliding_window_rows,
    make_sliding_window_get,
)

PAYLOAD = load_edf_payload()


# ── Reconstitution du code FAUTIF d'origine ────────────────────────
COLORS_CAPITALISE = list(dash.COLORS.keys()) + ["Total"]


def fetch_data_ORIGINE_BUG1(limit=200):
    """Bug n1 : order_by='Date DESC' -> HTTP 400 -> DataFrame vide."""
    r = requests.get(dash.API_URLS[0], params={"limit": limit, "order_by": "Date DESC"}, timeout=15)
    r.raise_for_status()
    return pd.DataFrame(r.json().get("results", []))


def _fetch_records_ORIGINE_OFFSET(url, limit):
    """
    Reconstitution de l'ANCIENNE pagination par `offset` (dette Phase 0/1.5,
    remplacee par une pagination par curseur en Phase 1.75). Sur un jeu de
    donnees stable, elle fonctionne ; sur une fenetre GLISSANTE (nouvelles
    lignes en tete pendant qu'on pagine), l'offset numerique ne pointe plus
    la meme ligne d'un appel a l'autre -> une ligne reelle est sautee.
    """
    records = []
    offset = 0
    while len(records) < limit:
        page_size = min(dash.API_MAX_LIMIT, limit - len(records))
        resp = requests.get(
            url,
            params={"limit": page_size, "offset": offset, "order_by": "date desc"},
            timeout=15,
        )
        resp.raise_for_status()
        page = resp.json().get("results", [])
        if not page:
            break
        records.extend(page)
        offset += len(page)
        if len(page) < page_size:
            break
    return records


def fetch_data_ORIGINE_BUG2(limit=100):
    """Bug n2 : colonnes API minuscules comparees aux cles COLORS capitalisees
    -> le `else` ecrase tout a 0.0 -> tous les KPI a zero."""
    r = requests.get(dash.API_URLS[0], params={"limit": limit, "order_by": "date desc"}, timeout=15)
    df = pd.DataFrame(r.json().get("results", []))
    for col in COLORS_CAPITALISE:
        if col in df.columns:          # 'Total' vs 'total' -> jamais vrai
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
        else:
            df[col] = 0.0              # <-- la faille
    return df


# ── ECHEC AVANT (reconstitue hors reseau, via requests.get patche) ─
def test_AVANT_bug1_order_by_capitalise_leve_400(monkeypatch):
    monkeypatch.setattr(dash.requests, "get", make_order_by_sensitive_get(PAYLOAD))
    with pytest.raises(requests.exceptions.HTTPError) as e:
        fetch_data_ORIGINE_BUG1()
    assert e.value.response.status_code == 400


def test_AVANT_bug2_normalisation_met_tous_les_kpi_a_zero(monkeypatch):
    monkeypatch.setattr(dash.requests, "get", make_paginated_get(PAYLOAD))
    df = fetch_data_ORIGINE_BUG2()
    assert not df.empty, "la fixture doit fournir des lignes pour que le test soit valide"
    for col in COLORS_CAPITALISE:
        assert (df[col] == 0.0).all(), f"{col} devrait etre ecrase a 0 par le bug"


# ── SUCCES APRES (code actuel, sur la fixture figee) ────────────────
@pytest.fixture(scope="module")
def df():
    mp = pytest.MonkeyPatch()
    mp.setattr(dash.requests, "get", make_paginated_get(PAYLOAD))
    try:
        d = dash.fetch_data.__wrapped__(limit=200)
    finally:
        mp.undo()
    assert not d.empty, "REFUS : fetch_data renvoie un DataFrame vide sur la fixture"
    return d


def test_APRES_production_envoie_order_by_minuscule(monkeypatch):
    """
    Teste le VRAI chemin de production (_fetch_records/fetch_data), pas la
    fonction ORIGINE_BUG1 reconstituee : sert la fixture uniquement si
    order_by="date desc" (minuscule), sinon HTTP 400 - comme l'API reelle.
    Si le code de production regresse vers "Date DESC", ce test doit rougir
    (fetch_data degrade en DataFrame vide, st.error est appele).
    """
    monkeypatch.setattr(dash.requests, "get", make_order_by_sensitive_get(PAYLOAD))
    monkeypatch.setattr(dash.st, "error", lambda *a, **k: None)
    out = dash.fetch_data.__wrapped__(limit=200)
    assert not out.empty, (
        "fetch_data a degrade en DataFrame vide : le code de production "
        "n'envoie plus order_by='date desc' (minuscule) - regression du bug n1"
    )


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
    """turbines_combustion / stockage peuvent etre negatifs : ne pas clipper.
    (Fixture 2026-07-20 : turbines_combustion est negatif sur les 100 lignes.)"""
    assert (df[["Turbines_combustion", "Stockage"]].min() < 0).any(), \
        "aucune valeur negative dans la fixture : test non concluant"


def test_APRES_pagination_assemble_plusieurs_pages(monkeypatch):
    """
    Unit-test du MECANISME de pagination de _fetch_records : donnees
    synthetiques (2 pages de 100 + 30), independantes de la fixture reelle,
    pour prouver que l'offset avance et que les pages sont assemblees
    au-dela du plafond API_MAX_LIMIT=100 - sans dependre du volume reel
    disponible dans la capture figee du 2026-07-20 (qui plafonne a 100
    lignes brutes, ~97 apres dedup).
    """
    monkeypatch.setattr(dash.requests, "get", make_synthetic_two_page_get(100, 30))
    records = dash._fetch_records(dash.API_URLS[0], limit=130)
    assert len(records) == 130, f"pagination inoperante : {len(records)} lignes assemblees"


# ── Phase 1.75 — pagination par curseur (remplace l'offset) ────────
def test_AVANT_pagination_offset_saute_une_ligne_sur_fenetre_glissante(monkeypatch):
    """
    Reproduit le bug de derive documente dans CLAUDE.md : entre le 1er et le
    2e appel de pagination, une nouvelle ligne apparait en tete de la fenetre
    (glissement observe sur l'API reelle, total_count variable en cours de
    session). Avec l'ANCIENNE logique par `offset`, la 2e page pointe alors
    sur une position decalee : elle re-sert la derniere ligne de la 1ere page
    (doublon, slot gaspille) et NE RECUPERE JAMAIS la ligne la plus ancienne
    demandee -> perte reelle d'une ligne.
    """
    before_rows, after_rows = make_sliding_window_rows(n_before=130)
    monkeypatch.setattr(dash.requests, "get", make_sliding_window_get(before_rows, after_rows))

    records = _fetch_records_ORIGINE_OFFSET(dash.API_URLS[0], limit=130)

    dates = [r["date"] for r in records]
    missing_date = before_rows[-1]["date"]  # ligne la plus ancienne demandee
    assert len(set(dates)) < 130, (
        "le doublon d'offset devrait consommer un slot (moins de 130 lignes uniques) "
        "- si ce test echoue, la fenetre synthetique ne reproduit plus la derive"
    )
    assert missing_date not in dates, (
        "BUG NON REPRODUIT : la ligne la plus ancienne est presente malgre la "
        "fenetre glissante -> verifier make_sliding_window_rows/_get"
    )


def test_APRES_pagination_curseur_aucune_ligne_perdue_sur_fenetre_glissante(monkeypatch):
    """
    Meme scenario de fenetre glissante, mais en exercant le VRAI code de
    production (dash._fetch_records, pagination par curseur `where=date < ...`).
    Preuve du fix : les 130 lignes demandees sont toutes recuperees, sans
    doublon - y compris la ligne que l'ancienne logique par offset perdait
    (test precedent). Si `_fetch_records` regresse vers l'offset, ce test
    doit rougir exactement comme le precedent.
    """
    before_rows, after_rows = make_sliding_window_rows(n_before=130)
    monkeypatch.setattr(dash.requests, "get", make_sliding_window_get(before_rows, after_rows))

    records = dash._fetch_records(dash.API_URLS[0], limit=130)

    dates = [r["date"] for r in records]
    assert len(dates) == 130, f"pagination par curseur incomplete : {len(dates)} lignes recuperees"
    assert len(set(dates)) == 130, "doublon detecte malgre la pagination par curseur"
    missing_date = before_rows[-1]["date"]
    assert missing_date in dates, (
        "la ligne que l'ancienne logique par offset perdait doit etre recuperee ici"
    )


# ── Phase 1.75 — echappement HTML du statut (origine API non maitrisee) ────
def test_AVANT_statut_api_non_echappe_serait_interprete_comme_html():
    """
    Documente le vecteur XSS de la construction PRE-FIX du badge (statut
    injecte tel quel dans du HTML, sans html.escape) : une balise malveillante
    apparaitrait brute dans le HTML genere, donc interpretee par le navigateur.
    Reconstitue l'ancienne ligne inline de render_dashboard (avant refactor
    vers build_update_badge_html) - ne teste PAS le code de prod actuel,
    seulement la preuve que le risque etait reel.
    """
    kpis = {
        "date": pd.Timestamp("2026-07-20 10:00", tz="Indian/Reunion"),
        "statut": "<script>alert(1)</script>",
    }
    ts = kpis["date"].strftime("%d/%m/%Y %H:%M")
    html_avant = (
        f'<div class="update-badge">Dernière donnée : {ts} (heure Réunion) '
        f'· statut : {kpis.get("statut","—")}</div>'
    )
    assert "<script>alert(1)</script>" in html_avant, (
        "la reconstitution pre-fix devrait contenir la balise brute (non echappee)"
    )


def test_APRES_statut_api_echappe_dans_badge_html():
    """
    Preuve que le VRAI code de prod (dash.build_update_badge_html, appele
    par render_dashboard) echappe le `statut` d'origine API : la balise brute
    ne doit JAMAIS apparaitre dans le HTML produit, seule sa version echappee.
    """
    kpis = {
        "date": pd.Timestamp("2026-07-20 10:00", tz="Indian/Reunion"),
        "statut": "<script>alert(1)</script>",
    }
    out = dash.build_update_badge_html(kpis)
    assert "<script>alert(1)</script>" not in out, "balise brute presente : injection HTML non neutralisee"
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in out, "version echappee absente du HTML produit"

    # L'echappement ne doit pas degrader l'affichage normal (statut legitime).
    kpis_ok = {"date": kpis["date"], "statut": "Estimé"}
    out_ok = dash.build_update_badge_html(kpis_ok)
    assert "Estimé" in out_ok, "un statut legitime doit s'afficher normalement, non echappe visuellement"


def test_APRES_dates_triees_et_uniques(df):
    assert df["Date"].is_monotonic_increasing
    assert df["Date"].is_unique
    assert str(df["Date"].dt.tz) == "Indian/Reunion"


# ── Invariant n3 : degradation propre ──────────────────────────────
def test_degradation_propre_api_injoignable(monkeypatch):
    """API injoignable -> DataFrame vide, PAS de crash. `requests.get` leve
    directement l'exception reseau : aucune tentative de connexion reelle
    (meme vouee a l'echec) n'est emise."""
    def raise_connexion(*a, **k):
        raise requests.exceptions.ConnectionError("simulated: host unreachable")
    monkeypatch.setattr(dash.requests, "get", raise_connexion)
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
