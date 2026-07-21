"""
test_experts.py — Tests déterministes du socle de personas (`experts.py`) et
de leur intégration dans `agent_expert.py`.

Zéro réseau, zéro appel LLM réel : `anthropic` est simulé via un module factice
injecté dans `sys.modules` (import différé dans `ask_expert`), pour prouver que
le bon `system_prompt` de persona est bien transmis, sans consommer de crédits.
"""

import sys
import types

import experts
import agent_expert


# ─────────────────────────────────────────────
#  Structure du registre EXPERTS
# ─────────────────────────────────────────────
def test_experts_contient_generaliste_et_souverainete():
    assert "generaliste" in experts.EXPERTS
    assert "souverainete" in experts.EXPERTS


def test_chaque_persona_a_label_prompt_suggestions_non_vides():
    for key, expert in experts.EXPERTS.items():
        assert expert.get("label"), f"{key}: label vide"
        assert expert.get("prompt"), f"{key}: prompt vide"
        assert expert.get("suggestions"), f"{key}: suggestions vides"
        assert isinstance(expert["suggestions"], list)
        assert all(isinstance(s, str) and s for s in expert["suggestions"])


# ─────────────────────────────────────────────
#  Ancres factuelles du prompt Souveraineté
# ─────────────────────────────────────────────
def test_prompt_souverainete_contient_les_ancres_factuelles_clefs():
    prompt = experts.EXPERTS["souverainete"]["prompt"]
    ancres = ["57 %", "colza", "pellets", "Rivière de l'Est"]
    for ancre in ancres:
        assert ancre in prompt, f"Ancre factuelle manquante dans le prompt souveraineté : {ancre!r}"


def test_aucune_persona_naffirme_la_date_erronee_mars_2024():
    """
    Régression Phase 2 (trouvée par gardien-qualite) : « mars 2024 » était codé en dur
    dans BASE_PROMPT et DOMAINE_ELECTROTECHNIQUE, alors que la source primaire
    (docs/sources/SOURCE_bilan-previsionnel-2024.md) établit que la conversion de TOUT
    le parc charbon/fioul est achevée **mi-2024** (Le Gol A.1/A.2 : fév. et juil. 2024).
    Le prompt affirmait donc au LLM une date que le projet avait corrigée ailleurs.
    Ce test ancre la date pour qu'elle ne puisse plus régresser silencieusement.
    """
    for key, expert in experts.EXPERTS.items():
        assert "mars 2024" not in expert["prompt"], (
            f"{key} : date erronée « mars 2024 » — la source primaire dit mi-2024"
        )


def test_conversion_parc_datee_mi_2024_dans_toutes_les_personas():
    """La bonne date doit être présente, pas seulement l'absence de la mauvaise."""
    for key, expert in experts.EXPERTS.items():
        assert "mi-2024" in expert["prompt"], (
            f"{key} : la date de conversion du parc (mi-2024) doit être affirmée"
        )


def test_prompt_souverainete_contient_le_garde_fou_instantane_vs_annuel():
    prompt = experts.EXPERTS["souverainete"]["prompt"]
    assert "JAMAIS" in prompt, "Garde-fou instantané/annuel absent (mot-clé JAMAIS introuvable)"
    # Le garde-fou doit porter spécifiquement sur l'autonomie instantanée vs annuelle.
    assert "autonome à 99" in prompt or "instantané" in prompt


# ─────────────────────────────────────────────
#  Garde-fous transverses — DOIVENT être dans TOUTES les personas
# ─────────────────────────────────────────────
def test_garde_fou_eolien_present_dans_toutes_les_personas():
    for key, expert in experts.EXPERTS.items():
        prompt = expert["prompt"]
        assert "figée" in prompt, f"{key}: garde-fou éolien (donnée figée) absent"
        assert "2,36" in prompt, f"{key}: valeur figée éolienne (2,36 MW) absente"
        assert "JAMAIS" in prompt, f"{key}: interdiction de commenter une tendance éolienne absente"


def test_limite_epistemique_biomasse_bioliquide_presente_dans_toutes_les_personas():
    for key, expert in experts.EXPERTS.items():
        prompt = expert["prompt"]
        assert "Biomasse" in prompt and "Bioliquide" in prompt, f"{key}: mention Biomasse/Bioliquide absente"
        assert "biogénique" in prompt, f"{key}: limite épistémique (100% biogénique) absente"


# ─────────────────────────────────────────────
#  Correction factuelle STEP — aucune persona n'affirme une STEP en service
# ─────────────────────────────────────────────
def test_aucune_persona_naffirme_une_step_operationnelle():
    # L'ancienne formulation fautive ("assoupli grâce au stockage (batteries, STEP)")
    # laissait entendre qu'une STEP est en service. Elle ne doit plus apparaître.
    formulation_fautive = "grâce au stockage (batteries, STEP)"
    for key, expert in experts.EXPERTS.items():
        assert formulation_fautive not in expert["prompt"], (
            f"{key}: formulation affirmant une STEP en service détectée"
        )


def test_domaine_electrotechnique_precise_absence_de_step():
    # Le domaine électrotechnique doit porter la correction factuelle explicite.
    assert "STEP" in experts.DOMAINE_ELECTROTECHNIQUE
    assert "Aucune STEP" in experts.DOMAINE_ELECTROTECHNIQUE or "aucune STEP" in experts.DOMAINE_ELECTROTECHNIQUE
    assert "Batrun" in experts.DOMAINE_ELECTROTECHNIQUE
    assert "Cratère" in experts.DOMAINE_ELECTROTECHNIQUE


def test_domaine_electrotechnique_nuance_plafond_30_pct():
    txt = experts.DOMAINE_ELECTROTECHNIQUE
    assert "30 %" in txt
    assert "40 %" in txt  # nuance empirique 2023


def test_domaine_electrotechnique_contient_inertie_et_reserves():
    txt = experts.DOMAINE_ELECTROTECHNIQUE
    for terme in ["inertie", "50 MW", "200 MW", "3 heures"]:
        assert terme in txt, f"terme attendu absent du domaine électrotechnique : {terme!r}"
    assert "non-synchrone" in txt


# ─────────────────────────────────────────────
#  ask_expert reçoit bien le prompt de la persona sélectionnée
# ─────────────────────────────────────────────
class _FakeTextBlock:
    def __init__(self, text):
        self.type = "text"
        self.text = text


class _FakeResponse:
    def __init__(self, text):
        self.content = [_FakeTextBlock(text)]


class _FakeMessages:
    def __init__(self, capture: dict):
        self._capture = capture

    def create(self, model, max_tokens, system, messages):
        # Capture le system prompt effectivement transmis, pour vérification.
        self._capture["system"] = system
        self._capture["model"] = model
        self._capture["messages"] = messages
        return _FakeResponse("réponse simulée")


class _FakeAnthropicClient:
    def __init__(self, api_key, capture):
        self.api_key = api_key
        self.messages = _FakeMessages(capture)


def _install_fake_anthropic(monkeypatch, capture: dict):
    """Injecte un module `anthropic` factice dans sys.modules (zéro réseau)."""
    fake_module = types.ModuleType("anthropic")

    class AuthenticationError(Exception):
        pass

    class NotFoundError(Exception):
        pass

    class APIError(Exception):
        pass

    fake_module.AuthenticationError = AuthenticationError
    fake_module.NotFoundError = NotFoundError
    fake_module.APIError = APIError
    fake_module.Anthropic = lambda api_key: _FakeAnthropicClient(api_key, capture)

    monkeypatch.setitem(sys.modules, "anthropic", fake_module)


def test_ask_expert_transmet_le_prompt_de_la_persona_selectionnee(monkeypatch):
    capture = {}
    _install_fake_anthropic(monkeypatch, capture)

    system_prompt = experts.EXPERTS["souverainete"]["prompt"]
    reponse = agent_expert.ask_expert(
        messages=[{"role": "user", "content": "test"}],
        api_key="sk-ant-fake",
        data_context="Contexte factice.",
        system_prompt=system_prompt,
    )

    assert reponse == "réponse simulée"
    assert "system" in capture
    # Le system transmis contient bien la signature de la persona souveraineté.
    assert "Souveraineté & résilience énergétique" in capture["system"]
    assert "colza" in capture["system"]


def test_ask_expert_transmet_un_prompt_different_selon_la_persona(monkeypatch):
    capture_generaliste = {}
    _install_fake_anthropic(monkeypatch, capture_generaliste)
    agent_expert.ask_expert(
        messages=[{"role": "user", "content": "test"}],
        api_key="sk-ant-fake",
        data_context="Contexte factice.",
        system_prompt=experts.EXPERTS["generaliste"]["prompt"],
    )

    capture_souverainete = {}
    _install_fake_anthropic(monkeypatch, capture_souverainete)
    agent_expert.ask_expert(
        messages=[{"role": "user", "content": "test"}],
        api_key="sk-ant-fake",
        data_context="Contexte factice.",
        system_prompt=experts.EXPERTS["souverainete"]["prompt"],
    )

    assert capture_generaliste["system"] != capture_souverainete["system"]
