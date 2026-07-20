"""
Dashboard Temps Réel - Mix Électrique de La Réunion
Source : API Open Data EDF Réunion
Mise à jour automatique toutes les 5 minutes
"""

import html
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import requests
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

import agent_expert  # onglet Agent expert (Claude) — noms internes capitalisés attendus
from filieres import (
    ENR_DIRECTES, BIOENERGIES, FOSSILE, AUTRES,
    ENR_STRICT, ENR_REGLEMENTAIRE, TOUTES_FILIERES,
    COMBUSTION_THERMIQUE, COLORS, label,
)

# ─────────────────────────────────────────────
#  Configuration de la page
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Mix Électrique – La Réunion",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
#  CSS personnalisé
# ─────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Sora:wght@300;400;600;700&display=swap');

  html, body, [data-testid="stAppViewContainer"] {
      background-color: #0a0f1e;
      color: #e8f4f8;
      font-family: 'Sora', sans-serif;
  }
  [data-testid="stHeader"] { background: transparent; }

  .block-container { padding: 1.5rem 2.5rem 2rem; max-width: 1400px; }

  h1, h2, h3 { font-family: 'Space Mono', monospace; }

  /* KPI cards */
  .kpi-card {
      background: linear-gradient(135deg, #111827 0%, #1a2540 100%);
      border: 1px solid #1e3a5f;
      border-radius: 12px;
      padding: 1.2rem 1.5rem;
      text-align: center;
      box-shadow: 0 4px 24px rgba(0,0,0,0.4);
      transition: transform .2s;
  }
  .kpi-card:hover { transform: translateY(-2px); }
  .kpi-label {
      font-size: 0.72rem;
      letter-spacing: .12em;
      text-transform: uppercase;
      color: #6b8cae;
      margin-bottom: .4rem;
  }
  .kpi-value {
      font-family: 'Space Mono', monospace;
      font-size: 2rem;
      font-weight: 700;
      color: #38bdf8;
      line-height: 1.1;
  }
  .kpi-unit  { font-size: 0.85rem; color: #94a3b8; margin-top: .2rem; }
  .kpi-green .kpi-value { color: #4ade80; }
  .kpi-orange .kpi-value { color: #fb923c; }

  /* section titles */
  .section-title {
      font-family: 'Space Mono', monospace;
      font-size: .75rem;
      letter-spacing: .15em;
      text-transform: uppercase;
      color: #38bdf8;
      border-left: 3px solid #38bdf8;
      padding-left: .6rem;
      margin-bottom: 1rem;
      margin-top: 1.5rem;
  }

  /* last update badge */
  .update-badge {
      font-family: 'Space Mono', monospace;
      font-size: .65rem;
      color: #475569;
      text-align: right;
      margin-top: -.5rem;
      margin-bottom: .5rem;
  }

  div[data-testid="stPlotlyChart"] { border-radius: 10px; overflow: hidden; }
  .stSpinner > div { border-top-color: #38bdf8 !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  Constantes
# ─────────────────────────────────────────────
# API EDF Réunion — explore v2.1 uniquement.
# Le namespace /api/v1/.../lines est MORT (404) : ne pas le réintroduire.
# Le tri se fait sur le champ `date` en MINUSCULE ("Date DESC" → HTTP 400).
API_URLS = [
    # slug principal
    "https://opendata-reunion.edf.fr/api/explore/v2.1/catalog/datasets/prod-electricite-temps-reel-974/records",
    # alias du même jeu de données, gardé en secours
    "https://opendata-reunion.edf.fr/api/explore/v2.1/catalog/datasets/prod-electricite-temps-reel/records",
]

# Plafond dur imposé par l'API explore v2.1 : limit > 100 → HTTP 400
# ("limit should be less than 100"), corps en text/plain. Au-delà, on pagine
# par curseur (`where=date < ...`, voir _fetch_records) — pas par `offset`.
API_MAX_LIMIT = 100

# Correspondance colonnes API (minuscules) → noms internes (clés de COLORS).
# Localisée ici : le reste du code ne manipule que les noms internes capitalisés.
# Piège : `bioenergies` (API, sans accent) → `Bioénergies` (interne, avec accent).
API_TO_INTERNAL = {
    "date"               : "Date",
    "total"              : "Total",
    "photovoltaique"     : "Photovoltaique",
    "eolien"             : "Eolien",
    "hydraulique"        : "Hydraulique",
    "bioenergies"        : "Bioénergies",
    "charbon"            : "Charbon",
    "diesel"             : "Diesel",
    "turbines_combustion": "Turbines_combustion",
    "stockage"           : "Stockage",
    "statut"             : "statut",
    "jour"               : "jour",
}

# Taxonomie des filières, palette de couleurs et libellés d'affichage :
# source unique de vérité dans filieres.py (importé ci-dessus), pour éviter
# toute duplication/désynchronisation entre dashboard_reunion.py et agent_expert.py.

REFRESH_INTERVAL = 300  # secondes (5 min)

# ─────────────────────────────────────────────
#  Récupération des données via l'API
# ─────────────────────────────────────────────
def _fetch_records(url: str, limit: int) -> list:
    """
    Récupère `limit` lignes sur un endpoint explore v2.1, en paginant si besoin
    (l'API refuse limit > API_MAX_LIMIT). Lève l'exception au premier échec :
    c'est fetch_data qui décide de basculer sur l'URL suivante.

    Pagination par CURSEUR (keyset), pas par `offset` : le jeu de données est
    une fenêtre glissante élaguée (nouvelles lignes en tête, anciennes hors
    fenêtre en queue, `total_count` observé variable en cours de session).
    Un `offset` numérique désigne une POSITION, qui ne correspond plus à la
    même ligne d'un appel à l'autre si la fenêtre a bougé entre-temps → une
    ligne réelle peut être sautée (dette connue, prouvée par régression).
    Le curseur ancre au contraire la page suivante sur une VALEUR déjà reçue
    (`where=date < '<date la plus ancienne de la page précédente>'`),
    insensible au glissement. Syntaxe validée par appel réel le 2026-07-20
    (HTTP 200, page suivante correcte, aucun trou).
    """
    records = []
    cursor = None  # date (str) de la ligne la plus ancienne reçue jusqu'ici
    while len(records) < limit:
        page_size = min(API_MAX_LIMIT, limit - len(records))
        params = {"limit": page_size, "order_by": "date desc"}
        if cursor is not None:
            params["where"] = f"date < '{cursor}'"
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        page = resp.json().get("results", [])   # `results` = lignes ; `total_count` = compteur
        if not page:
            break                               # jeu de données épuisé
        records.extend(page)
        cursor = page[-1].get("date")            # dernière ligne = la plus ancienne (order_by date desc)
        if len(page) < page_size:
            break                               # dernière page
    return records


@st.cache_data(ttl=REFRESH_INTERVAL)
def fetch_data(limit: int = 200) -> pd.DataFrame:
    """
    Récupère les données via l'API explore v2.1 d'EDF Open Data Réunion.
    Traduit les colonnes API (minuscules) en noms internes capitalisés :
    cette traduction est LOCALISÉE ICI, le reste du code ne voit que l'interne.
    Les données sont mises en cache pendant REFRESH_INTERVAL secondes.
    """
    last_error = None

    for url in API_URLS:
        try:
            records = _fetch_records(url, limit)
            if not records:
                continue

            df = pd.DataFrame(records)

            # ── Traduction API → interne, insensible à la casse ──
            # L'API renvoie tout en minuscules ; on tolère une casse différente
            # au cas où le fournisseur la changerait sans prévenir.
            rename = {}
            for col in df.columns:
                key = col.strip().lower()
                if key in API_TO_INTERNAL:
                    rename[col] = API_TO_INTERNAL[key]
            df = df.rename(columns=rename)

            if "Date" not in df.columns:
                last_error = f"colonne date absente (reçu : {list(df.columns)})"
                continue

            df["Date"] = pd.to_datetime(df["Date"], utc=True, errors="coerce")
            df = df.dropna(subset=["Date"])
            if df.empty:
                continue
            df["Date"] = df["Date"].dt.tz_convert("Indian/Reunion")

            # Colonnes numériques attendues par les KPI et les graphiques.
            # Une colonne réellement absente de l'API tombe à 0 et le signale.
            for col in list(COLORS.keys()) + ["Total"]:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
                else:
                    df[col] = 0.0
                    last_error = f"colonne '{col}' absente de l'API"

            # ── Valeurs négatives : on NE clippe PAS ──
            # `turbines_combustion` et `stockage` peuvent être négatifs
            # (auxiliaires/bruit de mesure pour les turbines ; charge des batteries
            # pour le stockage = soutirage sur le réseau). Ces valeurs sont
            # physiquement significatives et l'API les intègre dans `total` :
            # vérifié sur données réelles, somme algébrique des 8 filières == Total
            # à 0,001 MW près, alors qu'un clip(lower=0) introduit un écart de 0,23 MW.
            # Clipper masquerait la donnée ET casserait la cohérence avec Total.

            # Dédoublonnage sur la date, pour deux raisons vérifiées sur l'API réelle :
            #  1. l'API sert parfois deux fois la même minute, lignes strictement
            #     identiques sur les 12 colonnes (donc rien de réel n'est perdu ici) ;
            #  2. le jeu est glissant : entre deux pages, de nouvelles lignes arrivent
            #     et décalent l'`offset`, ce qui fait réapparaître des lignes déjà vues.
            # Conséquence assumée : on obtient un peu moins de lignes que `limit`.
            df = df.drop_duplicates(subset=["Date"], keep="last")
            df = df.sort_values("Date").reset_index(drop=True)
            return df   # ✅ Succès

        except requests.exceptions.RequestException as e:
            last_error = f"{url} → {e}"
            continue
        except ValueError as e:
            # Corps non-JSON (l'API répond en text/plain sur certaines erreurs)
            last_error = f"{url} → réponse illisible : {e}"
            continue
        except Exception as e:
            last_error = f"{url} → {e}"
            continue

    # Tous les endpoints ont échoué → dégradation propre, pas de stack trace
    st.error(f"⚠️ Tous les endpoints API ont échoué. Dernière erreur : {last_error}")
    return pd.DataFrame()


def compute_kpis(df: pd.DataFrame) -> dict:
    """
    Calcule les KPI à partir de la dernière ligne disponible.
    Deux %ENR distincts, sans 3e variante (décision COO) :
      - ren_directes     : Photovoltaique + Eolien + Hydraulique (ENR_STRICT)
      - ren_reglementaire: + Bioénergies + Charbon (biomasse) + Diesel (bioliquide)
                           (ENR_REGLEMENTAIRE — périmètre objectif autonomie 2030)
    """
    if df.empty:
        return {}
    last = df.iloc[-1]
    total = last.get("Total", 0)
    ren_directes      = sum(last.get(c, 0) for c in ENR_STRICT)
    ren_reglementaire = sum(last.get(c, 0) for c in ENR_REGLEMENTAIRE)
    pct_strict        = (ren_directes / total * 100) if total > 0 else 0
    pct_reglementaire = (ren_reglementaire / total * 100) if total > 0 else 0
    return {
        "total"               : total,
        "ren_directes"        : ren_directes,
        "ren_reglementaire"   : ren_reglementaire,
        "pct_ren_strict"      : pct_strict,
        "pct_ren_reglementaire": pct_reglementaire,
        "date"                : last["Date"],
        "statut"              : last.get("statut", "—"),
    }

# ─────────────────────────────────────────────
#  Graphiques
# ─────────────────────────────────────────────

def make_stacked_area(df: pd.DataFrame) -> go.Figure:
    """Graphique en aire empilée du mix électrique complet."""
    fig = go.Figure()
    all_sources = TOUTES_FILIERES + AUTRES

    for src in all_sources:
        if src not in df.columns:
            continue
        lbl = label(src)
        fig.add_trace(go.Scatter(
            x=df["Date"], y=df[src],
            name=lbl,
            mode="lines",
            stackgroup="one",
            line=dict(width=0),
            fillcolor=COLORS.get(src, "#888"),
            hovertemplate=f"<b>{lbl}</b>: %{{y:.1f}} MW<extra></extra>",
        ))

    # Ligne production totale
    fig.add_trace(go.Scatter(
        x=df["Date"], y=df["Total"],
        name="Production totale",
        mode="lines",
        line=dict(color="#e2e8f0", width=2, dash="dot"),
        hovertemplate="<b>Total</b>: %{y:.1f} MW<extra></extra>",
    ))

    fig.update_layout(**_dark_layout("Mix électrique – Production par filière (MW)"))
    return fig


def make_total_line(df: pd.DataFrame) -> go.Figure:
    """Graphique courbe de la production totale."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["Date"], y=df["Total"],
        mode="lines",
        fill="tozeroy",
        line=dict(color="#38bdf8", width=2),
        fillcolor="rgba(56,189,248,0.12)",
        hovertemplate="<b>Total</b>: %{y:.1f} MW<extra></extra>",
        name="Production totale",
    ))
    fig.update_layout(**_dark_layout("Production totale (MW)"))
    return fig


def make_renewables_pct(df: pd.DataFrame) -> go.Figure:
    """
    Graphique pourcentage renouvelables dans le temps.
    Choix : périmètre RÉGLEMENTAIRE (ENR_REGLEMENTAIRE = ENR strict + Bioénergies
    + Biomasse ex-Charbon + Bioliquide ex-Diesel), cohérent avec l'objectif
    d'autonomie énergétique 2030 (100 % électricité renouvelable) qui compte ces
    filières comme renouvelables au sens réglementaire malgré la combustion.
    """
    df = df.copy()
    df["pct_ren"] = df[ENR_REGLEMENTAIRE].sum(axis=1) / df["Total"].replace(0, pd.NA) * 100
    df["pct_ren"] = df["pct_ren"].fillna(0)

    fig = go.Figure()
    fig.add_hrect(y0=0, y1=100, fillcolor="rgba(74,222,128,0.04)", line_width=0)
    fig.add_trace(go.Scatter(
        x=df["Date"], y=df["pct_ren"],
        mode="lines",
        fill="tozeroy",
        line=dict(color="#4ade80", width=2),
        fillcolor="rgba(74,222,128,0.12)",
        hovertemplate="<b>Renouvelables (réglementaire)</b>: %{y:.1f} %<extra></extra>",
        name="% Renouvelables (réglementaire)",
    ))
    fig.update_layout(
        yaxis_range=[0, 105],
        **_dark_layout("Part des énergies renouvelables — périmètre réglementaire (%)"),
    )
    return fig


def make_thermal_lines(df: pd.DataFrame) -> go.Figure:
    """
    Bonus : évolution des centrales thermiques.
    Permet d'observer les démarrages des turbines, diesel et charbon.
    """
    fig = go.Figure()
    for src in COMBUSTION_THERMIQUE:
        if src not in df.columns:
            continue
        lbl = label(src)
        fig.add_trace(go.Scatter(
            x=df["Date"], y=df[src],
            name=lbl,
            mode="lines",
            line=dict(color=COLORS.get(src, "#888"), width=2),
            hovertemplate=f"<b>{lbl}</b>: %{{y:.1f}} MW<extra></extra>",
        ))

    fig.update_layout(**_dark_layout("Centrales thermiques – Démarrage & charge (MW)"))
    return fig


def _dark_layout(title: str) -> dict:
    """Paramètres de mise en forme communs (thème sombre)."""
    return dict(
        title=dict(text=title, font=dict(family="Space Mono, monospace", size=13, color="#94a3b8")),
        paper_bgcolor="#0f172a",
        plot_bgcolor ="#0f172a",
        font=dict(family="Sora, sans-serif", color="#94a3b8", size=11),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02,
            xanchor="right", x=1,
            bgcolor="rgba(0,0,0,0)",
            font=dict(size=10),
        ),
        margin=dict(l=40, r=20, t=60, b=40),
        xaxis=dict(
            gridcolor="#1e293b", zeroline=False,
            showline=True, linecolor="#1e3a5f",
        ),
        yaxis=dict(
            gridcolor="#1e293b", zeroline=False,
            showline=True, linecolor="#1e3a5f",
        ),
        hovermode="x unified",
    )

# ─────────────────────────────────────────────
#  Interface principale
# ─────────────────────────────────────────────

def render_kpi(label: str, value: str, unit: str = "", extra_class: str = "") -> str:
    # Défense en profondeur : label/value/unit sont normalement des libellés
    # statiques ou des nombres déjà formatés (donc sûrs), mais on échappe
    # quand même — cette fonction est un point d'entrée générique et rien ne
    # garantit qu'une valeur d'origine API n'y transitera jamais un jour.
    label = html.escape(str(label))
    value = html.escape(str(value))
    unit = html.escape(str(unit))
    return f"""
    <div class="kpi-card {extra_class}">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-unit">{unit}</div>
    </div>"""


def build_update_badge_html(kpis: dict) -> str:
    """
    Construit le HTML du badge « dernière donnée ». Fonction séparée (et non
    inline dans render_dashboard) pour être testable indépendamment de
    Streamlit : `statut` provient de l'API EDF (donnée NON maîtrisée) et est
    injecté dans du HTML brut (`unsafe_allow_html=True`) — sans échappement,
    un statut malveillant (ex. `<script>...`) serait interprété comme du HTML
    par le navigateur (XSS). `html.escape` neutralise ce risque tout en
    préservant l'affichage normal (« Estimé » reste « Estimé »).
    """
    ts = kpis["date"].strftime("%d/%m/%Y %H:%M") if kpis else "—"
    statut = html.escape(str(kpis.get("statut", "—")))
    return f'<div class="update-badge">Dernière donnée : {ts} (heure Réunion) · statut : {statut}</div>'


def render_dashboard(df, kpis):
    """Onglet Dashboard : reçoit df/kpis déjà chargés par main (ne les recharge pas)."""
    # ── Timestamp ──────────────────────────────
    st.markdown(build_update_badge_html(kpis), unsafe_allow_html=True)

    # ── KPI cards ──────────────────────────────
    # Deux %ENR distincts (décision COO, pas de 3e variante) : strict (ENR
    # directes uniquement) et réglementaire (+ Bioénergies/Biomasse/Bioliquide,
    # périmètre de l'objectif d'autonomie 2030).
    st.markdown('<div class="section-title">Instantané</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(render_kpi("Production totale", f"{kpis['total']:.0f}", "MW"), unsafe_allow_html=True)
    with c2:
        pct_color = "kpi-green" if kpis["pct_ren_strict"] >= 50 else "kpi-orange"
        st.markdown(render_kpi("Renouvelable strict (PV+Éolien+Hydraulique)",
                                f"{kpis['pct_ren_strict']:.1f}", "%", pct_color), unsafe_allow_html=True)
    with c3:
        pct_color = "kpi-green" if kpis["pct_ren_reglementaire"] >= 50 else "kpi-orange"
        st.markdown(render_kpi("Renouvelable réglementaire (+ Bioénergies/Biomasse/Bioliquide)",
                                f"{kpis['pct_ren_reglementaire']:.1f}", "%", pct_color), unsafe_allow_html=True)
    with c4:
        fossile_mw = df["Turbines_combustion"].iloc[-1] if "Turbines_combustion" in df.columns and not df.empty else 0
        st.markdown(render_kpi("Thermique fossile (Turbines à combustion)",
                                f"{fossile_mw:.0f}", "MW", "kpi-orange"), unsafe_allow_html=True)

    st.caption("⚠️ Éolien : donnée figée / non fiable (valeur constante ~2,36 MW, ne reflète pas la production réelle du parc éolien réunionnais).")

    # ── Graphique principal : mix empilé ───────
    st.markdown('<div class="section-title">Mix énergétique</div>', unsafe_allow_html=True)
    st.plotly_chart(make_stacked_area(df), width='stretch')

    # ── Ligne : production totale + % ENR ──────
    st.markdown('<div class="section-title">Production totale & renouvelables</div>', unsafe_allow_html=True)
    col_left, col_right = st.columns(2)
    with col_left:
        st.plotly_chart(make_total_line(df), width='stretch')
    with col_right:
        st.plotly_chart(make_renewables_pct(df), width='stretch')

    # ── Bonus : centrales thermiques ───────────
    st.markdown('<div class="section-title">🔥 Bonus — Démarrage des centrales thermiques</div>',
                unsafe_allow_html=True)
    st.caption("Observer les pics de Biomasse (ex-Charbon), Bioliquide (ex-Diesel) et Turbines à combustion lors des montées de charge.")
    st.plotly_chart(make_thermal_lines(df), width='stretch')

    # ── Pied de page ───────────────────────────
    st.markdown("""
    <hr style="border-color:#1e293b;margin-top:2rem;">
    <p style="color:#334155;font-size:.7rem;text-align:center;">
      Source : <a href="https://opendata-reunion.edf.fr" style="color:#38bdf8;">Open Data EDF Réunion</a>
      · Dashboard généré avec Streamlit & Plotly
    </p>
    """, unsafe_allow_html=True)


def render_diagnostic():
    """Onglet Diagnostic : re-sonde chaque endpoint API (son rôle = tester à froid)."""
    st.markdown('<div class="section-title">🔧 Diagnostic API</div>', unsafe_allow_html=True)
    st.markdown("**Test de chaque endpoint :**")
    for url in API_URLS:
        try:
            r = requests.get(url, params={"limit": 1, "order_by": "date desc"}, timeout=8)
            if r.status_code == 200:
                data = r.json()
                nb = len(data.get("results", []))
                st.success(f"✅ **{r.status_code}** — {url} → {nb} résultat(s)")
                if nb > 0:
                    st.json(data["results"][0])
            else:
                st.error(f"❌ **{r.status_code}** — {url}")
                st.code(r.text[:300])
        except Exception as e:
            st.error(f"💥 Erreur — {url} : {e}")


def main():
    # ── Rafraîchissement automatique ───────────
    # Non bloquant : le composant re-déclenche un run côté client toutes les
    # REFRESH_INTERVAL secondes. Contrairement à time.sleep()+st.rerun(), il ne
    # gèle pas le script et préserve session_state (donc le chat agent).
    st_autorefresh(interval=REFRESH_INTERVAL * 1000, key="auto_refresh")

    # ── Titre ──────────────────────────────────
    st.markdown("""
    <h1 style="font-family:'Space Mono',monospace;font-size:1.6rem;
               color:#38bdf8;margin-bottom:.2rem;letter-spacing:.04em;">
      ⚡ Mix Électrique · La Réunion
    </h1>
    <p style="color:#475569;font-size:.85rem;margin-top:0;">
      Données temps réel — Open Data EDF Réunion · Rafraîchissement auto toutes les 5 min
    </p>
    """, unsafe_allow_html=True)

    # ── Chargement (une seule fois, avant les onglets) ──
    with st.spinner("Récupération des données EDF…"):
        df = fetch_data(limit=200)

    # ── Dégradation propre (invariant 3) ──
    # Choix : si l'API est muette, on n'affiche PAS des onglets vides mais on
    # bascule directement sur le Diagnostic — c'est l'outil qui aide l'exploitant
    # à identifier l'endpoint fautif, plus utile ici qu'un dashboard sans données.
    if df.empty:
        st.error("Aucune donnée disponible. Vérifiez votre connexion ou l'état de l'API.")
        render_diagnostic()
        st.stop()

    kpis = compute_kpis(df)

    # ── Navigation par onglets ─────────────────
    tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "🧠 Agent expert", "🔧 Diagnostic"])
    with tab1:
        render_dashboard(df, kpis)
    with tab2:
        agent_expert.render_agent_tab(df, kpis)
    with tab3:
        render_diagnostic()


if __name__ == "__main__":
    main()
