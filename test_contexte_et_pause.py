"""
test_contexte_et_pause.py — Lot S0 (19/11/2026).

Tests déterministes, hors réseau, sur le VRAI code de production :
- D7 : le contexte envoyé au modèle (`agent_expert.build_data_context`, nourri
  par la fixture via `fetch_data` → `compute_kpis`) et la docstring de
  `filieres.py` ne servent plus les dates « mars 2024 / déc. 2023 ».
- D9 : le badge « donnée figée » de l'éolien n'apparaît que si la colonne est
  constante sur la fenêtre (fixture = constante ; df synthétique = variable).
- D11 : `API_URLS` ne contient plus l'alias mort (404).
- Pause de l'agent : `AGENT_ENABLED = False` → l'onglet affiche « Agent en
  pause », aucun champ de clé, aucun appel LLM (AppTest sur l'app complète).
"""
from pathlib import Path
from unittest.mock import patch

import pandas as pd

import agent_expert
import dashboard_reunion as dash
import filieres
from fixture_utils import FakeResponse, load_edf_payload, make_paginated_get


def _df_fixture():
    with patch("requests.get", return_value=FakeResponse(200, load_edf_payload())):
        # contourne st.cache_data, même convention que test_fetch_data.py
        return dash.fetch_data.__wrapped__(limit=100)


def _ctx(df):
    return agent_expert.build_data_context(df, dash.compute_kpis(df))


def _df_eolien_variable():
    df = _df_fixture().copy()
    df["Eolien"] = [0.5 + (i % 7) * 0.4 for i in range(len(df))]
    return df


# ── D7 ─────────────────────────────────────────────────────────────
def test_contexte_llm_sans_dates_de_conversion_perimees():
    ctx = _ctx(_df_fixture())
    assert "mars 2024" not in ctx and "déc. 2023" not in ctx


def test_contexte_llm_affirme_les_dates_retenues():
    ctx = _ctx(_df_fixture())
    assert "conversion du parc achevée mi-2024" in ctx
    assert "achevée en octobre 2023" in ctx


def test_docstring_filieres_alignee():
    assert "mars 2024" not in filieres.__doc__
    assert "déc. 2023" not in filieres.__doc__
    assert "mi-2024" in filieres.__doc__


# ── D6 (ligne carbone du contexte) ─────────────────────────────────
def test_contexte_llm_distingue_estimation_et_reference_officielle():
    ctx = _ctx(_df_fixture())
    assert "estimation instantanée du projet" in ctx
    assert "77 g en 2024" in ctx


# ── D9 ─────────────────────────────────────────────────────────────
def test_fixture_eolien_constant_est_detecte_fige():
    df = _df_fixture()
    assert df["Eolien"].nunique() == 1, "prémisse : la fixture figée a un éolien constant"
    assert agent_expert.eolien_est_fige(df) is True
    assert "donnée figée" in _ctx(df)
    assert dash.build_eolien_caption(df) is not None


def test_eolien_variable_sans_badge_fige():
    df = _df_eolien_variable()
    assert agent_expert.eolien_est_fige(df) is False
    assert "donnée figée" not in _ctx(df)
    assert dash.build_eolien_caption(df) is None


def test_eolien_fige_robuste_aux_cas_limites():
    assert agent_expert.eolien_est_fige(pd.DataFrame()) is False
    assert agent_expert.eolien_est_fige(pd.DataFrame({"Eolien": [2.36]})) is False


# ── D11 ────────────────────────────────────────────────────────────
def test_api_urls_ne_contient_que_le_slug_974():
    assert dash.API_URLS, "API_URLS vide"
    assert all("-974/records" in u for u in dash.API_URLS)


# ── Pause de l'agent ───────────────────────────────────────────────
def test_drapeau_agent_desactive():
    assert agent_expert.AGENT_ENABLED is False


def test_apptest_onglet_agent_en_pause_sans_cle_ni_appel(monkeypatch):
    from streamlit.testing.v1 import AppTest

    monkeypatch.setattr(dash.requests, "get", make_paginated_get(load_edf_payload()))

    def _interdit(*a, **k):
        raise AssertionError("ask_expert ne doit jamais être appelé quand l'agent est en pause")
    monkeypatch.setattr(agent_expert, "ask_expert", _interdit)

    at = AppTest.from_file(str(Path(__file__).parent / "dashboard_reunion.py"))
    at.run(timeout=30)

    assert not at.exception, f"exception non gérée : {[e.value for e in at.exception]}"
    assert len(at.tabs) == 4
    assert [t.label for t in at.tabs] == ["📊 Dashboard", "🗺️ Carte", "🧠 Agent expert", "🔧 Diagnostic"]
    assert any("Agent en pause" in i.value for i in at.info), [i.value for i in at.info]
    # Aucun champ de saisie de clé, aucun chat.
    assert not [t for t in at.text_input if "Clé API" in (t.label or "")]
    assert len(at.chat_input) == 0
