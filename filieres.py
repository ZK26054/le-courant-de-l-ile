"""
filieres.py — Taxonomie et facteurs d'émission du mix électrique La Réunion.
Socle partagé, importé par dashboard_reunion.py ET agent_expert.py.
Noms internes capitalisés (issus de fetch_data). AUCUN import projet.

Limite épistémique : les libellés « Biomasse (ex-Charbon) » / « Bioliquide (ex-Diesel) »
reflètent la communication officielle EDF sur la conversion de ces centrales
(Bois-Rouge/Le Gol 100% biomasse, conversion du parc achevée mi-2024 ;
Port-Est : conversion à l'huile de colza achevée en octobre 2023).
Ils n'attestent pas que 100% du combustible soit biogénique à chaque instant.
"""

# ── Libellés d'affichage (nom interne → libellé humain) ──
LABELS = {
    "Photovoltaique"      : "Photovoltaïque",
    "Eolien"              : "Éolien",
    "Hydraulique"         : "Hydraulique",
    "Bioénergies"         : "Bioénergies",
    "Charbon"             : "Biomasse (ex-Charbon)",
    "Diesel"              : "Bioliquide (ex-Diesel)",
    "Turbines_combustion" : "Turbines à combustion",
    "Stockage"            : "Stockage",
}

def label(key: str) -> str:
    """Libellé humain d'une filière (identité si non mappé)."""
    return LABELS.get(key, key)

# ── Taxonomie 3 familles (décision COO) ──
ENR_DIRECTES = ["Photovoltaique", "Eolien", "Hydraulique"]
BIOENERGIES  = ["Bioénergies", "Charbon", "Diesel"]   # groupe (≠ la filière "Bioénergies" seule)
FOSSILE      = ["Turbines_combustion"]
AUTRES       = ["Stockage"]

ENR_STRICT        = ENR_DIRECTES
ENR_REGLEMENTAIRE = ENR_DIRECTES + BIOENERGIES
TOUTES_FILIERES   = ENR_DIRECTES + BIOENERGIES + FOSSILE   # ordre canonique d'itération/affichage

# Regroupement PHYSIQUE (centrales pilotables à combustion) — usage make_thermal_lines
# uniquement, indépendant du classement carbone. À NE PAS confondre avec FOSSILE.
COMBUSTION_THERMIQUE = ["Charbon", "Diesel", "Turbines_combustion"]

# ── Facteurs d'émission FOURCHETTE (gCO2eq/kWh) — ESTIMATIONS, pas des chiffres officiels EDF ──
EMISSION_FACTORS_LOW = {
    "Photovoltaique": 0, "Eolien": 0, "Hydraulique": 0,
    "Bioénergies": 35, "Charbon": 200, "Diesel": 30,
    "Turbines_combustion": 700, "Stockage": 0,
}
EMISSION_FACTORS_HIGH = {
    "Photovoltaique": 0, "Eolien": 0, "Hydraulique": 0,
    "Bioénergies": 150, "Charbon": 230, "Diesel": 150,
    "Turbines_combustion": 700, "Stockage": 0,
}

# ── Couleurs Plotly (migrées telles quelles depuis dashboard_reunion.py) ──
COLORS = {
    "Photovoltaique"    : "#facc15",
    "Eolien"            : "#60a5fa",
    "Hydraulique"       : "#34d399",
    "Bioénergies"       : "#a3e635",
    "Charbon"           : "#64748b",
    "Diesel"            : "#f97316",
    "Turbines_combustion": "#ef4444",
    "Stockage"          : "#a78bfa",
}
