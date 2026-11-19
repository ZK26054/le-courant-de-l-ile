"""
Exporte la taxonomie des filières (filieres.py, SOURCE UNIQUE — invariant n°7)
vers site/src/data/filieres.json, lu par le site statique « Le courant de l'île ».

Le JSON est un ARTEFACT GÉNÉRÉ : ne jamais l'éditer à la main. Le test
test_export_filieres_site.py rougit si le JSON committé diverge de filieres.py.

Usage : python scripts/export_filieres_site.py
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import filieres  # noqa: E402

OUT = ROOT / "site" / "src" / "data" / "filieres.json"

# Correspondance colonnes API (minuscules) → noms internes. Copie EXACTE de
# dashboard_reunion.API_TO_INTERNAL pour les 8 filières ; vérifiée par test
# (on n'importe pas dashboard_reunion ici pour ne pas charger Streamlit).
API_KEYS = {
    "photovoltaique": "Photovoltaique",
    "eolien": "Eolien",
    "hydraulique": "Hydraulique",
    "bioenergies": "Bioénergies",
    "charbon": "Charbon",
    "diesel": "Diesel",
    "turbines_combustion": "Turbines_combustion",
    "stockage": "Stockage",
}


def build() -> dict:
    ordre = filieres.TOUTES_FILIERES + filieres.AUTRES
    return {
        "_avertissement": "Fichier généré par scripts/export_filieres_site.py depuis filieres.py. Ne pas éditer.",
        "ordre": ordre,
        "api_vers_interne": API_KEYS,
        "libelles": {k: filieres.label(k) for k in ordre},
        "familles": {
            "enr_directes": filieres.ENR_DIRECTES,
            "bioenergies": filieres.BIOENERGIES,
            "fossile": filieres.FOSSILE,
            "autres": filieres.AUTRES,
        },
    }


def render() -> str:
    return json.dumps(build(), ensure_ascii=False, indent=2) + "\n"


if __name__ == "__main__":
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(render(), encoding="utf-8", newline="\n")
    print(f"écrit : {OUT}")
