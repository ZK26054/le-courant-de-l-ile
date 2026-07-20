"""
Agent Expert — Mix Électrique La Réunion
─────────────────────────────────────────
Agent conversationnel multi-expertise propulsé par Claude (Anthropic) :
  • Électricité / électrotechnique  (production, réseau, fréquence, stabilité ZNI)
  • Climat                          (intensité carbone, facteurs d'émission)
  • Juridique transition énergétique (PPE, Code de l'énergie, objectifs 2030)

IMPORTANT — noms de colonnes :
Ce module travaille avec les NOMS INTERNES CAPITALISÉS produits par `fetch_data`
(Photovoltaique, Eolien, Hydraulique, Bioénergies, Charbon, Diesel,
Turbines_combustion, Stockage, Total). L'API EDF renvoie des minuscules ;
la conversion est faite en amont dans `fetch_data`, PAS ici.

Schéma réel de l'API (re-sondé 2026-07-17) : 12 colonnes.
Il n'existe PAS de filières Biomasse ni Bioliquides distinctes — elles sont
agrégées dans `bioenergies`. Ne pas les réintroduire.
"""

import streamlit as st
import pandas as pd

from filieres import (
    LABELS, label, ENR_DIRECTES, BIOENERGIES, FOSSILE, AUTRES,
    EMISSION_FACTORS_LOW, EMISSION_FACTORS_HIGH,
)

# ─────────────────────────────────────────────
#  Configuration LLM
# ─────────────────────────────────────────────
# Modèle Anthropic (modifiable selon les modèles disponibles sur votre compte).
# Alternatives : "claude-opus-4-8" (plus puissant, plus cher),
#                "claude-haiku-4-5-20251001" (plus rapide, moins cher).
MODEL = "claude-sonnet-5"
MAX_TOKENS = 1200


# ─────────────────────────────────────────────
#  Calcul de l'intensité carbone
# ─────────────────────────────────────────────
def compute_carbon_intensity(row: pd.Series) -> tuple:
    """
    Estime la FOURCHETTE d'intensité carbone du mix (gCO₂/kWh) à partir d'une
    ligne de données : (borne basse, borne haute), moyenne pondérée des
    facteurs d'émission LOW/HIGH par la production de chaque filière.

    Traitement des valeurs négatives : une production négative (ex. stockage en
    charge, ou artefact d'estimation sur turbines_combustion) n'émet pas de CO₂ et
    ne représente pas une production réelle — elle est donc exclue du calcul
    (garde `mw > 0`). L'intensité est une moyenne pondérée sur les seules sources
    qui produisent effectivement à cet instant.
    """
    total_prod = emis_low = emis_high = 0.0
    for src in EMISSION_FACTORS_LOW:
        mw = row.get(src, 0) or 0
        if mw > 0:
            total_prod += mw
            emis_low  += mw * EMISSION_FACTORS_LOW[src]
            emis_high += mw * EMISSION_FACTORS_HIGH[src]
    if total_prod <= 0:
        return (0.0, 0.0)
    return (emis_low / total_prod, emis_high / total_prod)


# ─────────────────────────────────────────────
#  Contexte de données injecté à chaque message
# ─────────────────────────────────────────────
def _pct_ren_strict_row(row: pd.Series) -> float:
    """% ENR strict (PV+Éolien+Hydraulique), recalculé à la volée ligne par ligne.
    ⚠️ Le df reçu par build_data_context N'A PAS de colonne pct_ren (elle n'est
    créée que sur une copie locale dans make_renewables_pct)."""
    t = row.get("Total", 0) or 0
    return (sum(row.get(c, 0) or 0 for c in ENR_DIRECTES) / t * 100) if t > 0 else 0.0


def _pct_ren_reglementaire_row(row: pd.Series) -> float:
    """% ENR réglementaire (strict + Bioénergies + Biomasse ex-Charbon + Bioliquide ex-Diesel)."""
    t = row.get("Total", 0) or 0
    return (sum(row.get(c, 0) or 0 for c in ENR_DIRECTES + BIOENERGIES) / t * 100) if t > 0 else 0.0


def build_data_context(df: pd.DataFrame, kpis: dict) -> str:
    """Construit un résumé texte des données live pour ancrer l'agent."""
    if df.empty or not kpis:
        return "Aucune donnée disponible actuellement."

    last = df.iloc[-1]
    low, high = compute_carbon_intensity(last)
    t_now = last["Date"]
    total_last = last.get("Total", 0) or 0

    # ── BLOC 1 — Tendance sur ~1h ────────────────────────────────
    if len(df) < 2:
        tendance = "Tendance : indisponible (moins de 2 relevés)."
    else:
        cible = t_now - pd.Timedelta(minutes=60)
        anterieurs = df[df["Date"] <= cible]
        ref = anterieurs.iloc[-1] if not anterieurs.empty else df.iloc[0]
        elapsed_min = round((t_now - ref["Date"]).total_seconds() / 60)
        ref_hm = ref["Date"].strftime("%H:%M")
        if 50 <= elapsed_min <= 70:
            titre_tend = f"Tendance sur ~1h (par rapport à {ref_hm}) :"
        else:
            titre_tend = f"Tendance sur ~{elapsed_min} min (par rapport à {ref_hm}) :"

        # Production totale
        total_now = last.get("Total", 0) or 0
        total_ref = ref.get("Total", 0) or 0
        d_mw = total_now - total_ref
        if round(d_mw, 0) == 0:
            l_prod = "- Production totale : stable"
        elif total_ref > 0:
            d_pct = d_mw / total_ref * 100
            l_prod = f"- Production totale : {d_mw:+.0f} MW ({d_pct:+.1f} %)"
        else:
            l_prod = f"- Production totale : {d_mw:+.0f} MW"

        # Part renouvelable — double (strict + réglementaire)
        d_strict = _pct_ren_strict_row(last) - _pct_ren_strict_row(ref)
        d_regl = _pct_ren_reglementaire_row(last) - _pct_ren_reglementaire_row(ref)
        if round(d_strict, 1) == 0 and round(d_regl, 1) == 0:
            l_ren = "- Part renouvelable (strict / réglementaire) : stable"
        else:
            l_ren = (f"- Part renouvelable strict : {d_strict:+.1f} pts / "
                     f"réglementaire : {d_regl:+.1f} pts")

        # Intensité carbone — fourchette de deltas
        ref_low, ref_high = compute_carbon_intensity(ref)
        d_low, d_high = low - ref_low, high - ref_high
        if round(d_low, 0) == 0 and round(d_high, 0) == 0:
            l_carb = "- Intensité carbone : stable"
        else:
            l_carb = f"- Intensité carbone : {d_low:+.0f} à {d_high:+.0f} gCO₂/kWh"

        tendance = "\n".join([titre_tend, l_prod, l_ren, l_carb])

    # ── BLOC 2 — Amplitude sur la période chargée ────────────────
    total_sec = (t_now - df.iloc[0]["Date"]).total_seconds()
    if total_sec >= 3600:
        h = int(total_sec // 3600)
        m = int(round((total_sec % 3600) / 60))
        if m == 60:
            h, m = h + 1, 0
        duree_str = f"{h}h{m:02d}"
    else:
        duree_str = f"{int(round(total_sec / 60))} min"

    tot_series = df["Total"].fillna(0)
    imax, imin = int(tot_series.values.argmax()), int(tot_series.values.argmin())
    row_max, row_min = df.iloc[imax], df.iloc[imin]

    pct_strict_series = df.apply(_pct_ren_strict_row, axis=1)
    pct_regl_series = df.apply(_pct_ren_reglementaire_row, axis=1)
    carb_series = df.apply(compute_carbon_intensity, axis=1, result_type="expand")
    carb_series.columns = ["low", "high"]

    amplitude = "\n".join([
        f"Amplitude sur la période chargée ({len(df)} relevés, ~{duree_str}) :",
        (f"- Production totale : pic {tot_series.iloc[imax]:.0f} MW à "
         f"{row_max['Date'].strftime('%H:%M')} / creux {tot_series.iloc[imin]:.0f} MW à "
         f"{row_min['Date'].strftime('%H:%M')}"),
        f"- Part renouvelable strict : min {pct_strict_series.min():.1f} % / max {pct_strict_series.max():.1f} %",
        f"- Part renouvelable réglementaire : min {pct_regl_series.min():.1f} % / max {pct_regl_series.max():.1f} %",
        (f"- Intensité carbone : min {carb_series['low'].min():.0f} gCO₂/kWh / "
         f"max {carb_series['high'].max():.0f} gCO₂/kWh"),
    ])

    # ── Détail par filière (instantané) + % du Total ─────────────
    lignes = []
    for src in EMISSION_FACTORS_LOW:
        if src in df.columns:
            val = last.get(src, 0) or 0
            if abs(val) > 0.01:
                lbl = label(src)
                if src == "Eolien":
                    lbl += " [donnée figée — non fiable, ne pas interpréter comme tendance]"
                if total_last > 0:
                    pct = val / total_last * 100
                    lignes.append(f"  - {lbl} : {val:.1f} MW ({pct:.1f} %)")
                else:
                    lignes.append(f"  - {lbl} : {val:.1f} MW")
    detail = "\n".join(lignes)

    ts = kpis["date"].strftime("%d/%m/%Y %H:%M") if kpis.get("date") is not None else "—"

    # ── Instantané : composition renouvelable strict / réglementaire ────
    ren_directes_mw = sum(last.get(c, 0) or 0 for c in ENR_DIRECTES)
    bio_group_mw = sum(last.get(c, 0) or 0 for c in BIOENERGIES)
    fossile_mw = last.get("Turbines_combustion", 0) or 0
    pct_strict = _pct_ren_strict_row(last)
    pct_regl = _pct_ren_reglementaire_row(last)
    ren_regl_mw = ren_directes_mw + bio_group_mw

    return f"""DONNÉES EDF RÉUNION EN TEMPS RÉEL (instantané) :
- Horodatage : {ts} (heure Réunion) — statut : {kpis.get('statut', '—')}
- Production totale : {kpis.get('total', 0):.1f} MW
- Renouvelable strict (PV+Éolien+Hydraulique) : {ren_directes_mw:.1f} MW ({pct_strict:.1f} %)
- Renouvelable réglementaire (+ Bioénergies + Biomasse ex-Charbon + Bioliquide ex-Diesel) : {ren_regl_mw:.1f} MW ({pct_regl:.1f} %)
- ENR thermique / biogénique (Bioénergies+Biomasse+Bioliquide) : {bio_group_mw:.1f} MW
- Thermique fossile (Turbines à combustion) : {fossile_mw:.1f} MW
- Intensité carbone estimée du mix : {low:.0f}–{high:.0f} gCO₂/kWh (fourchette — neutralité biomasse/bagasse débattue, estimation non officielle)

{tendance}

{amplitude}

Détail par filière (production instantanée) :
{detail}

(Données portant sur les ~{len(df)} derniers relevés à pas de 5 min.
Filières couvertes : Photovoltaïque, Éolien, Hydraulique, Bioénergies,
Biomasse (ex-Charbon), Bioliquide (ex-Diesel), Turbines à combustion, Stockage.
Les libellés « Biomasse (ex-Charbon) » et « Bioliquide (ex-Diesel) » reflètent la
communication officielle EDF sur la conversion de ces centrales (Bois-Rouge/Le Gol
100 % biomasse depuis mars 2024 ; Port-Est huile de colza depuis déc. 2023) — les
colonnes de données restent nommées « Charbon »/« Diesel » côté API, mais ne
désignent plus ces combustibles fossiles. Ces libellés sont déclaratifs et
n'attestent pas que 100 % du combustible soit biogénique à chaque instant.
Note : « Bioénergies » agrège la bagasse/biomasse — il n'y a pas de filière
biomasse/bioliquide distincte de « Charbon »/« Diesel » dans l'API.
Les % par filière sont rapportés au Total publié ; leur somme peut s'écarter de
100 % (arrondis, signe négatif du Stockage ou des turbines de combustion).)"""


# ─────────────────────────────────────────────
#  Prompt système multi-expertise
# ─────────────────────────────────────────────
SYSTEM_PROMPT = """Tu es un agent expert francophone spécialisé dans le système électrique de La Réunion. Tu cumules quatre expertises et tu réponds toujours en français, de façon précise, pédagogique et nuancée.

# Tes domaines d'expertise

## 1. Électricité & électrotechnique
- Production, transport, distribution ; grandeurs (MW, MWh, kV), facteur de charge, courbe de charge.
- Stabilité du réseau : fréquence 50 Hz, inertie, réserve primaire/secondaire, gestion de l'équilibre offre-demande en temps réel.
- Spécificité majeure : La Réunion est une **Zone Non Interconnectée (ZNI)** — réseau insulaire isolé, sans interconnexion au continent. Cela impose des contraintes fortes de stabilité, une faible inertie, et historiquement un plafond d'injection instantanée des énergies intermittentes (photovoltaïque + éolien) autour de 30 % (arrêté du 23 avril 2008), assoupli grâce au stockage (batteries, STEP) et aux dispositifs de prévision.
- Filières locales : Port-Est fonctionne désormais au **bioliquide** (huile de colza, fournie par Saipol, depuis décembre 2023) — ce ne sont plus des moteurs diesel/fioul fossile. Les turbines à combustion de pointe, elles, restent fossiles. Les centrales de Bois-Rouge et Le Gol ont achevé leur conversion à **100 % biomasse en mars 2024** : elles ne brûlent plus de charbon. Complètent le mix : hydraulique (Rivière de l'Est, Takamaka), photovoltaïque, éolien, stockage.
- ⚠️ Note technique importante : dans les données injectées, les colonnes restent nommées « Charbon » et « Diesel » pour des raisons de continuité de l'API EDF, mais elles désignent désormais respectivement la **Biomasse (ex-Charbon)** et le **Bioliquide (ex-Diesel)**. Ne dis jamais que La Réunion brûle encore du charbon ou du fioul diesel dans ces centrales converties.

## 2. Climat
- Facteurs d'émission par filière (gCO₂/kWh), intensité carbone du mix, logique de l'ordre de mérite carbone. Les facteurs sont donnés en FOURCHETTE (borne basse/haute) : l'intensité carbone du mix est donc elle-même une fourchette, jamais un chiffre unique.
- Nuance importante sur la biomasse/bagasse (comptabilisée ici dans « Bioénergies », « Biomasse (ex-Charbon) » et « Bioliquide (ex-Diesel) ») : considérée « biogénique » donc plus faiblement comptée en émissions directes que les fossiles, mais ce statut de neutralité carbone est scientifiquement débattu (combustion, importation de pellets/huile, dette carbone temporelle). Présente toujours cette nuance honnêtement.
- Tu sais relier le mix instantané à son impact climatique et expliquer pourquoi le démarrage des turbines à combustion (fossiles, souvent en pointe du soir) dégrade fortement l'intensité carbone — bien plus que la biomasse ou le bioliquide.
- **Double indicateur %ENR** — précise toujours LEQUEL tu utilises :
  * **ENR strict** = Photovoltaïque + Éolien + Hydraulique uniquement (production directement renouvelable, sans combustion).
  * **ENR réglementaire** = ENR strict + Bioénergies + Biomasse (ex-Charbon) + Bioliquide (ex-Diesel) (périmètre utilisé pour l'objectif d'autonomie 2030, car ces filières sont comptées comme renouvelables au sens réglementaire malgré la combustion).
  * Le réglementaire est généralement très supérieur au strict (souvent 90 %+ à La Réunion) du fait du poids de la biomasse/bioliquide dans le mix. Ne jamais présenter l'un comme équivalent à l'autre sans préciser lequel.

## 3. Juridique — transition énergétique & écologique
- Cadre français : Code de l'énergie, loi de transition énergétique pour la croissance verte (2015), loi Énergie-Climat (2019), Programmation Pluriannuelle de l'Énergie (PPE) propre à La Réunion.
- Objectif structurant : **autonomie énergétique de La Réunion à l'horizon 2030** (100 % d'électricité renouvelable), inscrit dans la loi pour les territoires d'outre-mer.
- Mécanismes ZNI : péréquation tarifaire, compensation des charges de service public de l'énergie (ex-CSPE), rôle de la CRE et d'EDF SEI.
- Cadre européen pertinent (paquet Fit for 55, directives ENR) quand utile.

## 4. Posture
- Ancre systématiquement tes analyses dans les DONNÉES EN TEMPS RÉEL fournies au début de chaque conversation.
- Distingue clairement les faits établis, les estimations (ex : intensité carbone calculée) et les points débattus.
- Les facteurs d'émission et l'intensité carbone fournis sont des ESTIMATIONS indicatives EN FOURCHETTE, pas des chiffres officiels EDF — précise-le quand c'est pertinent.
- Tu n'es pas avocat : pour le juridique, tu donnes une information générale et tu invites à vérifier les textes en vigueur, sans rendre d'avis juridique formel.
- Sois concis par défaut, développe quand on te le demande. Utilise des chiffres et des ordres de grandeur.

## 5. Garde-fou ÉOLIEN — obligatoire
- La valeur « Éolien » dans les données injectées est **figée** (~2,36 MW en continu) : ce n'est PAS une mesure réelle et variable du parc éolien réunionnais. Tu ne dois JAMAIS commenter une tendance, une variation, un pic ou un creux sur l'éolien à partir de cette donnée — elle ne bouge pas par construction, donc toute lecture de tendance serait fictive.
- Si on t'interroge sur l'éolien, précise que le vrai parc éolien de La Réunion (Sainte-Suzanne, ~19,8 MW, production réellement variable selon le vent ; Sainte-Rose, démantelé) n'est pas fidèlement représenté par cette donnée figée, et invite à la prudence sur toute conclusion tirée de cette colonne.

## 6. Limite épistémique — libellés Biomasse / Bioliquide
- Les libellés « Biomasse (ex-Charbon) » et « Bioliquide (ex-Diesel) » reflètent la communication officielle EDF sur la conversion de ces centrales (Bois-Rouge/Le Gol 100 % biomasse depuis mars 2024 ; Port-Est huile de colza depuis décembre 2023). Ils n'attestent pas que 100 % du combustible brûlé soit biogénique à chaque instant précis (démarrages, mix transitoire, approvisionnement). Formule tes affirmations climat avec cette nuance.
"""


# ─────────────────────────────────────────────
#  Appel à l'API Claude
# ─────────────────────────────────────────────
def ask_expert(messages: list, api_key: str, data_context: str) -> str:
    """
    Envoie l'historique de conversation à Claude avec le contexte de données.
    `messages` : liste de dicts {role, content} (rôles 'user' / 'assistant').
    """
    try:
        import anthropic
    except ImportError:
        return ("❌ Le module `anthropic` n'est pas installé.\n\n"
                "Lancez : `pip install anthropic`")

    client = anthropic.Anthropic(api_key=api_key)

    # On injecte le contexte de données dans le system prompt à chaque appel
    system = SYSTEM_PROMPT + "\n\n# Données injectées pour cette session\n" + data_context

    try:
        resp = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=system,
            messages=messages,
        )
        return "".join(block.text for block in resp.content if block.type == "text")
    except anthropic.AuthenticationError:
        return "❌ Clé API invalide. Vérifiez votre clé Anthropic."
    except anthropic.NotFoundError:
        return (f"❌ Modèle « {MODEL} » introuvable sur votre compte. "
                f"Modifiez la constante MODEL dans agent_expert.py "
                f"(ex : claude-opus-4-8, claude-haiku-4-5-20251001).")
    except anthropic.APIError as e:
        return f"❌ Erreur API Anthropic : {e}"
    except Exception as e:
        return f"❌ Erreur inattendue : {e}"


# ─────────────────────────────────────────────
#  Onglet Streamlit — Chat interactif
# ─────────────────────────────────────────────
def render_agent_tab(df: pd.DataFrame, kpis: dict):
    """Rendu de l'onglet agent expert (chat interactif)."""

    st.markdown('<div class="section-title">🧠 Agent expert — Électricité · Climat · Droit de l\'énergie</div>',
                unsafe_allow_html=True)

    # ── Clé API : secrets Streamlit > saisie manuelle ──
    api_key = ""
    try:
        api_key = st.secrets.get("ANTHROPIC_API_KEY", "")
    except Exception:
        api_key = ""

    if not api_key:
        api_key = st.text_input(
            "Clé API Anthropic",
            type="password",
            placeholder="sk-ant-…",
            help="Votre clé reste locale (transmise seulement à l'API Anthropic). "
                 "Astuce : créez .streamlit/secrets.toml avec ANTHROPIC_API_KEY pour éviter de la retaper.",
        )

    # Contexte de données live
    data_context = build_data_context(df, kpis)

    # Aperçu du contexte injecté
    with st.expander("📊 Données injectées à l'agent (instantané live)"):
        st.code(data_context, language="text")

    # Questions suggérées
    st.caption("💡 Exemples de questions :")
    suggestions = [
        "Pourquoi les centrales thermiques tournent-elles en ce moment ?",
        "Quelle est l'intensité carbone du mix actuel et comment l'améliorer ?",
        "Où en est La Réunion vis-à-vis de l'objectif d'autonomie 2030 ?",
        "Quel est le risque réseau si on pousse plus de photovoltaïque ?",
    ]
    cols = st.columns(2)
    clicked = None
    for i, sug in enumerate(suggestions):
        if cols[i % 2].button(sug, key=f"sug_{i}", width="stretch"):
            clicked = sug

    # ── Historique de conversation ──
    if "agent_messages" not in st.session_state:
        st.session_state.agent_messages = []

    for msg in st.session_state.agent_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Saisie utilisateur (chat input ou suggestion cliquée)
    user_input = st.chat_input("Posez votre question à l'agent expert…")
    prompt = user_input or clicked

    if prompt:
        if not api_key:
            st.warning("⚠️ Renseignez d'abord votre clé API Anthropic ci-dessus.")
            return

        st.session_state.agent_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("L'agent analyse les données…"):
                answer = ask_expert(st.session_state.agent_messages, api_key, data_context)
            st.markdown(answer)

        st.session_state.agent_messages.append({"role": "assistant", "content": answer})

    # Réinitialiser la conversation
    if st.session_state.agent_messages:
        if st.button("🗑️ Effacer la conversation"):
            st.session_state.agent_messages = []
            st.rerun()
