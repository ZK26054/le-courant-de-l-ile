"""
Le JSON de taxonomie du site (site/src/data/filieres.json) doit être EXACTEMENT
ce que produit scripts/export_filieres_site.py depuis filieres.py — sinon le
site public afficherait des libellés désynchronisés (invariant n°7).
"""
import importlib.util
import json
from pathlib import Path

import dashboard_reunion as dash
import filieres

ROOT = Path(__file__).parent
_spec = importlib.util.spec_from_file_location("export_filieres_site", ROOT / "scripts" / "export_filieres_site.py")
export = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(export)


def test_json_du_site_synchronise_avec_filieres_py():
    committe = (ROOT / "site" / "src" / "data" / "filieres.json").read_text(encoding="utf-8")
    assert committe == export.render(), "filieres.json périmé : relancer scripts/export_filieres_site.py"


def test_libelles_biomasse_bioliquide_dans_le_json():
    data = json.loads((ROOT / "site" / "src" / "data" / "filieres.json").read_text(encoding="utf-8"))
    assert data["libelles"]["Charbon"] == filieres.label("Charbon") == "Biomasse (ex-Charbon)"
    assert data["libelles"]["Diesel"] == filieres.label("Diesel") == "Bioliquide (ex-Diesel)"


def test_correspondance_api_identique_a_fetch_data():
    for api, interne in export.API_KEYS.items():
        assert dash.API_TO_INTERNAL[api] == interne, api
    assert set(export.API_KEYS.values()) == set(filieres.TOUTES_FILIERES + filieres.AUTRES)
