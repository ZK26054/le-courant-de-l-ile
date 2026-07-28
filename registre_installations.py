"""
registre_installations.py — Carte des installations de production/stockage
d'électricité à La Réunion, maille COMMUNE (V1).

Module ISOLÉ (voir docs/adr/003-carte-installations-registre-communal.md) :
un seul consommateur (l'onglet Carte de dashboard_reunion.py), donc pas de
scission socle/UI comme filieres.py/experts.py. Palette LOCALE à ce module,
volontairement NON fusionnée avec filieres.COLORS (nomenclature de filières
différente entre le flux temps réel et le registre — voir plus bas).

⚠️ INVARIANT V1 (data-driven, ADR-003) : aucune coordonnée de centrale n'est
saisie à la main ici, aucune identité de site n'est déduite. La seule
donnée géographique en dur est `geo/communes_974_centroides.json`, une table
de RÉFÉRENCE ADMINISTRATIVE PUBLIQUE à la maille commune (24 lignes), pas un
hardcode par installation. L'affectation installation → lieu est entièrement
pilotée par l'API via `codeinseecommune`.

Sources de données :
- Registre EDF (dynamique, cache TTL long) :
  https://opendata-reunion.edf.fr/api/explore/v2.1/catalog/datasets/
    registre-national-des-installations-de-production-et-de-stockage-d-electricite-reunion/records
  Champs clés : `codeinseecommune`, `commune`, `filiere`, `puismaxinstallee` (kW),
  `nbinstallations`. `nominstallation` = "Confidentiel" partout (pas de nom de site).
- Centroïdes communaux (statique, bundlée) : geo/communes_974_centroides.json
  (voir geo/README.md — source geo.api.gouv.fr, Licence Ouverte Etalab).

Pièges connus (voir CLAUDE.md / brief) :
- `puismaxinstallee` est en **kW** : conversion kW→MW faite UNE SEULE FOIS, ici,
  à la source (`fetch_registre_par_commune_filiere`). Le reste du module ne
  manipule que des MW.
- Le total réel d'installations par commune est `sum(nbinstallations)`,
  JAMAIS `count(*)` : l'API agrège les lignes du registre par lots
  (`sum(nbinstallations)` = 9878 sur l'île entière, `count(*)` = 724 lignes
  brutes — ce sont deux nombres différents, le second sous-compte largement).
- La pagination par CURSEUR `date` du flux temps réel (`dashboard_reunion.
  _fetch_records`) NE S'APPLIQUE PAS ici : ce registre n'a pas de champ de tri
  temporel glissant, c'est un instantané figé (snapshot). La pagination ici
  (si jamais nécessaire au-delà d'une page) est un simple `offset` croissant —
  sans risque de dérive de fenêtre glissante, puisqu'il n'y en a pas.
- Un corps d'erreur HTTP peut être `text/plain` (comme le flux temps réel) :
  `.json()` peut lever une erreur de décodage, gérée explicitement.
"""

import json
import math
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

# ─────────────────────────────────────────────
#  Constantes
# ─────────────────────────────────────────────
REGISTRE_URL = (
    "https://opendata-reunion.edf.fr/api/explore/v2.1/catalog/datasets/"
    "registre-national-des-installations-de-production-et-de-stockage-d-electricite-reunion/records"
)

# Plafond dur mesuré sur l'API explore v2.1 (identique au flux temps réel :
# limit > 100 sans group_by -> HTTP 400 "limit should be less than 100").
# Avec `group_by`, l'API tolère davantage (101 group_by testé -> 200 OK),
# mais on reste défensif et on plafonne quand même chaque page à cette valeur.
REGISTRE_MAX_LIMIT = 100

# Snapshot figé (registre administratif, pas un flux temps réel) : cache
# TTL LONG, volontairement distinct de REFRESH_INTERVAL (300 s, temps réel).
REGISTRE_TTL_SECONDS = 86400  # 24 h

CENTROIDES_PATH = Path(__file__).parent / "geo" / "communes_974_centroides.json"

# ── Palette LOCALE (nomenclature `filiere` du REGISTRE, différente de
# filieres.COLORS qui porte sur les colonnes du flux temps réel) ──
# Valeurs observées : Solaire, Hydraulique, Bioénergies, Thermique non
# renouvelable, Eolien, Stockage non hydraulique.
FILIERE_COLORS = {
    "Solaire"                    : "#facc15",
    "Eolien"                     : "#60a5fa",
    "Hydraulique"                : "#34d399",
    "Bioénergies"                : "#a3e635",
    "Thermique non renouvelable" : "#ef4444",
    "Stockage non hydraulique"   : "#a78bfa",
}
FILIERE_COLOR_DEFAUT = "#94a3b8"  # filière inconnue/imprévue -> gris neutre


# ─────────────────────────────────────────────
#  T3 — Récupération du registre (commune × filière)
# ─────────────────────────────────────────────
def _fetch_registre_page(offset: int, limit: int) -> list:
    """Une page de la requête group_by (voir en-tête de module). Lève
    l'exception réseau/HTTP au premier échec — géré par l'appelant."""
    params = {
        "select": "codeinseecommune, commune, filiere, "
                  "sum(puismaxinstallee) as p_kw, sum(nbinstallations) as n_inst",
        "group_by": "codeinseecommune, commune, filiere",
        "order_by": "p_kw desc",
        "limit": limit,
        "offset": offset,
    }
    resp = requests.get(REGISTRE_URL, params=params, timeout=20)
    resp.raise_for_status()
    try:
        data = resp.json()
    except ValueError as e:
        # Corps text/plain (erreur API) que raise_for_status() n'aurait pas
        # interceptée si le status était 200 mais le corps non-JSON.
        raise ValueError(f"réponse illisible (non-JSON) : {e}") from e
    return data.get("results", [])


@st.cache_data(ttl=REGISTRE_TTL_SECONDS)
def fetch_registre_par_commune_filiere(limit: int = 500) -> tuple:
    """
    Récupère le registre EDF agrégé par (commune, filière), converti en MW.

    Retourne (df, n_exclus) :
      - df : colonnes `codeinseecommune` (str), `commune`, `filiere`,
        `mw` (float, converti kW->MW), `n_inst` (int, = nbinstallations réel,
        JAMAIS un count(*) de lignes brutes).
      - n_exclus : nombre de lignes exclues car `codeinseecommune` vide/null
        (compté, jamais silencieusement ignoré).

    Pagination par simple `offset` croissant (pas de curseur `date` : ce
    registre n'est pas une fenêtre glissante temporelle, voir en-tête).
    Prouvé par re-probe : 46 lignes groupées au total -> tient en un seul
    appel, mais la boucle reste générique si le registre grossit.
    """
    rows = []
    offset = 0
    while len(rows) < limit:
        page_size = min(REGISTRE_MAX_LIMIT, limit - len(rows))
        page = _fetch_registre_page(offset, page_size)
        if not page:
            break  # jeu de données épuisé
        rows.extend(page)
        offset += len(page)
        if len(page) < page_size:
            break  # dernière page

    n_exclus = 0
    records = []
    for r in rows:
        code = r.get("codeinseecommune")
        if code is None or str(code).strip() == "":
            n_exclus += 1
            continue
        p_kw = r.get("p_kw") or 0
        records.append({
            "codeinseecommune": str(code).strip(),
            "commune": r.get("commune", "—"),
            "filiere": r.get("filiere", "—"),
            "mw": float(p_kw) / 1000.0,  # kW -> MW, UNE SEULE FOIS, ici
            "n_inst": int(r.get("n_inst") or 0),
        })

    df = pd.DataFrame(records, columns=["codeinseecommune", "commune", "filiere", "mw", "n_inst"])
    return df, n_exclus


# ─────────────────────────────────────────────
#  T1/T4 — Centroïdes communaux + jointure
# ─────────────────────────────────────────────
@st.cache_data(ttl=REGISTRE_TTL_SECONDS)
def load_centroides(path: Path = CENTROIDES_PATH) -> pd.DataFrame:
    """Charge la table de centroïdes communaux (statique, bundlée). Colonnes :
    `codeinseecommune` (str, renommé depuis `code` pour matcher le registre),
    `nom`, `lat`, `lon`."""
    with open(path, encoding="utf-8") as f:
        rows = json.load(f)
    df = pd.DataFrame(rows)
    df = df.rename(columns={"code": "codeinseecommune"})
    df["codeinseecommune"] = df["codeinseecommune"].astype(str).str.strip()
    return df


def joindre_centroides(df_registre: pd.DataFrame, df_centroides: pd.DataFrame):
    """
    Agrège le registre (long-format commune×filière) à la maille commune,
    puis joint aux centroïdes sur `codeinseecommune`, en STRING STRICT
    (zéros initiaux préservés des deux côtés — cast déjà fait en amont dans
    fetch_registre_par_commune_filiere / load_centroides).

    Retourne (df_joint, orphelines_sans_centroide, communes_sans_donnee) :
      - df_joint : une ligne par commune trouvée DES DEUX CÔTÉS. Colonnes :
        codeinseecommune, commune, lat, lon, mw_total, n_inst_total,
        filiere_dominante, mix (texte lisible pour le hover).
      - orphelines_sans_centroide : liste de codes INSEE présents dans le
        registre mais absents des centroïdes (pas de NaN silencieux : la
        commune est explicitement signalée, jamais droppée en silence).
      - communes_sans_donnee : liste de codes INSEE présents dans les
        centroïdes mais sans aucune installation dans le registre.
    """
    if df_registre.empty:
        codes_centroides = df_centroides["codeinseecommune"].tolist()
        return (
            pd.DataFrame(columns=["codeinseecommune", "commune", "lat", "lon",
                                   "mw_total", "n_inst_total", "filiere_dominante", "mix"]),
            [],
            codes_centroides,
        )

    # ── Agrégation à la maille commune ──
    def _agrege(g: pd.DataFrame) -> pd.Series:
        g_sorted = g.sort_values("mw", ascending=False)
        dominante = g_sorted.iloc[0]["filiere"] if not g_sorted.empty else "—"
        mix = ", ".join(f"{row.filiere}: {row.mw:.1f} MW" for row in g_sorted.itertuples())
        return pd.Series({
            "commune": g["commune"].iloc[0],
            "mw_total": g["mw"].sum(),
            "n_inst_total": int(g["n_inst"].sum()),
            "filiere_dominante": dominante,
            "mix": mix,
        })

    agg = (
        df_registre.groupby("codeinseecommune", as_index=False)
        .apply(_agrege, include_groups=False)
        .reset_index(drop=True)
    )

    codes_registre = set(agg["codeinseecommune"])
    codes_centroides = set(df_centroides["codeinseecommune"])

    orphelines_sans_centroide = sorted(codes_registre - codes_centroides)
    communes_sans_donnee = sorted(codes_centroides - codes_registre)

    df_joint = agg.merge(df_centroides, on="codeinseecommune", how="inner")
    df_joint = df_joint[[
        "codeinseecommune", "commune", "lat", "lon",
        "mw_total", "n_inst_total", "filiere_dominante", "mix",
    ]].sort_values("mw_total", ascending=False).reset_index(drop=True)

    return df_joint, orphelines_sans_centroide, communes_sans_donnee


# ─────────────────────────────────────────────
#  T5 — Carte à bulles
# ─────────────────────────────────────────────
def _bubble_sizes(mw: pd.Series, min_px: float = 10.0, max_px: float = 60.0) -> pd.Series:
    """Aire de bulle ∝ MW -> rayon (donc taille Plotly) ∝ sqrt(MW), pour ne
    pas exagérer visuellement les écarts de puissance (une bulle 4x plus
    grosse en MW ne doit occuper que 2x plus de rayon, pas 4x)."""
    if mw.empty:
        return mw
    racine = mw.clip(lower=0).apply(math.sqrt)
    max_racine = racine.max()
    if max_racine == 0:
        return pd.Series([min_px] * len(mw), index=mw.index)
    echelle = (max_px - min_px) / max_racine
    return min_px + racine * echelle


def make_bubble_map(df_joint: pd.DataFrame) -> go.Figure:
    """
    Carte à bulles proportionnelles (aire ∝ MW, échelle racine carrée),
    couleur = filière dominante par commune, hover = commune + MW + nombre
    d'installations réel + mix filière.

    Choix technique : `go.Scattermap` (MapLibre GL, plotly >= 5.24), PAS
    `go.Scattermapbox`. Les deux existent en plotly 6.9.0 (vérifié), mais
    Scattermap est la trace recommandée par Plotly pour ce cas : rendu
    MapLibre sans jeton (style `open-street-map` gratuit, pas de compte
    Mapbox requis), alors que Scattermapbox reste utilisable mais legacy.
    Vérifié par construction réelle de figure + `fig.to_dict()` sans
    exception (aucun rendu navigateur possible dans cet environnement).
    """
    fig = go.Figure()

    if df_joint.empty:
        fig.update_layout(map=dict(style="open-street-map", center=dict(lat=-21.1, lon=55.5), zoom=8))
        return fig

    sizes = _bubble_sizes(df_joint["mw_total"])
    colors = df_joint["filiere_dominante"].map(FILIERE_COLORS).fillna(FILIERE_COLOR_DEFAUT)

    hover_text = [
        f"<b>{row.commune}</b><br>"
        f"Puissance installée : {row.mw_total:.1f} MW<br>"
        f"Installations : {row.n_inst_total}<br>"
        f"Filière dominante : {row.filiere_dominante}<br>"
        f"Mix : {row.mix}"
        for row in df_joint.itertuples()
    ]

    fig.add_trace(go.Scattermap(
        lat=df_joint["lat"],
        lon=df_joint["lon"],
        mode="markers",
        marker=dict(size=sizes, color=colors, opacity=0.75, sizemode="diameter"),
        text=hover_text,
        hovertemplate="%{text}<extra></extra>",
    ))

    fig.update_layout(
        map=dict(
            style="open-street-map",
            center=dict(lat=-21.13, lon=55.53),  # centre approximatif de La Réunion
            zoom=8.4,
        ),
        margin=dict(l=0, r=0, t=30, b=0),
        showlegend=False,
        title=dict(
            text="Installations de production/stockage — puissance installée par commune (MW)",
            font=dict(family="Space Mono, monospace", size=13, color="#94a3b8"),
        ),
        paper_bgcolor="#0f172a",
        font=dict(family="Sora, sans-serif", color="#94a3b8", size=11),
    )
    return fig


# ─────────────────────────────────────────────
#  T6 — Onglet Streamlit (LAZY, dégradation locale)
# ─────────────────────────────────────────────
def render_carte_tab():
    """
    Onglet Carte : appelé UNIQUEMENT depuis l'onglet (jamais dans le fetch
    eager de main()) — LAZY par construction, puisque cette fonction n'est
    invoquée que lorsque `with tab_carte:` s'exécute. Aucun autorefresh, pas
    de time.sleep()/st.rerun() (invariant n°2, hors-sujet ici : ce n'est pas
    du temps réel). Dégradation LOCALE à cet onglet uniquement : jamais de
    st.stop() global qui geler ait les 3 autres onglets.
    """
    st.markdown('<div class="section-title">🗺️ Carte des installations (registre EDF)</div>',
                unsafe_allow_html=True)

    # ── 1. Récupération du registre ──
    try:
        with st.spinner("Récupération du registre des installations…"):
            df_registre, n_exclus = fetch_registre_par_commune_filiere()
    except requests.exceptions.RequestException as e:
        st.error(f"⚠️ Registre des installations indisponible : {e}")
        return
    except ValueError as e:
        st.error(f"⚠️ Réponse du registre illisible : {e}")
        return

    if df_registre.empty:
        st.warning("Aucune donnée renvoyée par le registre des installations.")
        return

    # ── 2. Centroïdes communaux ──
    try:
        df_centroides = load_centroides()
    except (FileNotFoundError, json.JSONDecodeError) as e:
        st.error(f"⚠️ Table de centroïdes communaux indisponible : {e}")
        return

    # ── 3. Jointure ──
    df_joint, orphelines, communes_sans_donnee = joindre_centroides(df_registre, df_centroides)

    if df_joint.empty:
        st.warning("Aucune commune n'a pu être localisée (jointure registre ↔ centroïdes vide).")
        return

    if n_exclus:
        st.caption(f"⚠️ {n_exclus} ligne(s) du registre exclue(s) : code INSEE commune vide/absent.")
    if orphelines:
        st.caption(f"⚠️ {len(orphelines)} commune(s) du registre sans centroïde connu (non affichée(s)) : "
                   + ", ".join(orphelines))

    # ── 4. Carte ──
    st.plotly_chart(make_bubble_map(df_joint), width="stretch")

    # ── 5. Tableau ──
    st.markdown('<div class="section-title">Détail par commune</div>', unsafe_allow_html=True)
    tableau = df_joint[["commune", "mw_total", "n_inst_total", "filiere_dominante"]].rename(columns={
        "commune": "Commune",
        "mw_total": "Puissance installée (MW)",
        "n_inst_total": "Nb installations",
        "filiere_dominante": "Filière dominante",
    })
    st.dataframe(tableau, width="stretch", hide_index=True)

    # ── 6. Note méthodo ──
    st.caption(
        "Méthodologie : puissance installée en MW (convertie depuis les kW du registre EDF, "
        "une seule fois à la source). Le nombre d'installations par commune est la somme réelle "
        "`sum(nbinstallations)` de l'API (l'agrégation par lots du registre fait que ce nombre "
        "diffère du simple compte de lignes). Aucune identité de site n'est affichée : le champ "
        "`nominstallation` du registre est confidentiel pour toutes les installations. Snapshot "
        "figé (registre administratif, pas un flux temps réel) — voir docs/adr/003."
    )
