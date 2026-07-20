"""
Tests deterministes du socle filieres.py (source unique de verite taxonomie).
Aucun reseau requis. Rejouable :
  ./.venv/Scripts/python.exe -m pytest test_filieres.py -v
"""
import pytest

import filieres as f


def test_memes_cles_colors_labels_emissions():
    """COLORS, LABELS, EMISSION_FACTORS_LOW, EMISSION_FACTORS_HIGH portent
    exactement le meme jeu de cles (les 8 filieres internes)."""
    cles_colors = set(f.COLORS.keys())
    cles_labels = set(f.LABELS.keys())
    cles_low = set(f.EMISSION_FACTORS_LOW.keys())
    cles_high = set(f.EMISSION_FACTORS_HIGH.keys())
    assert cles_colors == cles_labels == cles_low == cles_high


def test_low_inferieur_ou_egal_high():
    """Pour toute filiere, la borne basse d'emission <= la borne haute."""
    for src in f.EMISSION_FACTORS_LOW:
        assert f.EMISSION_FACTORS_LOW[src] <= f.EMISSION_FACTORS_HIGH[src], (
            f"{src} : LOW={f.EMISSION_FACTORS_LOW[src]} > HIGH={f.EMISSION_FACTORS_HIGH[src]}"
        )


def test_enr_strict_inclus_dans_enr_reglementaire():
    """ENR_STRICT est un sous-ensemble strict de ENR_REGLEMENTAIRE."""
    assert set(f.ENR_STRICT).issubset(set(f.ENR_REGLEMENTAIRE))
    # et la difference doit correspondre exactement au groupe BIOENERGIES
    assert set(f.ENR_REGLEMENTAIRE) - set(f.ENR_STRICT) == set(f.BIOENERGIES)


def test_aucune_valeur_negative_dans_facteurs():
    """Aucun facteur d'emission (low ou high) n'est negatif."""
    for src, val in f.EMISSION_FACTORS_LOW.items():
        assert val >= 0, f"{src} LOW negatif : {val}"
    for src, val in f.EMISSION_FACTORS_HIGH.items():
        assert val >= 0, f"{src} HIGH negatif : {val}"


def test_toutes_filieres_sans_doublon():
    """TOUTES_FILIERES ne contient aucun doublon."""
    assert len(f.TOUTES_FILIERES) == len(set(f.TOUTES_FILIERES))


def test_label_fonction():
    """label() renvoie le libelle humain mappe, ou l'identite si cle inconnue."""
    assert f.label("Charbon") == "Biomasse (ex-Charbon)"
    assert f.label("Diesel") == "Bioliquide (ex-Diesel)"
    assert f.label("Eolien") == "Éolien"
    assert f.label("Inconnu_XYZ") == "Inconnu_XYZ"


def test_pas_de_biomasse_bioliquide_distinctes():
    """Regression : Biomasse et Bioliquide ne doivent PAS exister comme cles
    internes distinctes (elles sont agregees dans Charbon/Diesel)."""
    toutes_cles = set(f.COLORS.keys())
    assert "Biomasse" not in toutes_cles
    assert "Bioliquide" not in toutes_cles
