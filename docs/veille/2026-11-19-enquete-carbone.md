# Enquête carbone — 365 gCO2/kWh (comparatif ZNI) vs 68-145 (notre fourchette)

> ⚠️ **Rapport brut, revérifié par gardien-qualite. La synthèse `2026-11-19-SYNTHESE.md` fait foi.** Errata (§f) n°6 à 8 :
> - « 122-177 g » n'est pas reproductible, les valeurs justes sont 103-172 selon la convention retenue pour le charbon ;
> - le 365 de 2023 est publié tel quel dans le BER 2024 (série recalculée avec le GNR de Saint-Pierre) ;
> - les « 90 kt » figurent aussi dans le PDF du BER.
>
> La conclusion qualitative (i) est confirmée.

Date : 2026-11-19 · Veilleur institutionnel · Aucune modification du projet.
Fichiers lus : `filieres.py` l.43-52 (`EMISSION_FACTORS_LOW/HIGH`), `agent_expert.py` l.41-62 (`compute_carbon_intensity` : moyenne pondérée instantanée par la production positive de chaque filière, fourchette bas/haut, sans pertes réseau, sans amont explicite).

## 1. Tableau des valeurs trouvées

| Valeur (gCO2/kWh) | Année des données | Méthode | Organisme | Niveau | URL | Page |
|---|---|---|---|---|---|---|
| **365** | **2023** (production 3 085 GWh ; 1,12 tCO2/hab) | « Contenu carbone électrique » ; facteurs ADEME Base Carbone par source (note de la synthèse p.7). Source citée pour La Réunion : « OER » (chiffres 2023). Chiffre repris de l'OER, non recalculé par l'OREC | OREC/Synergiles Guadeloupe (DEAL Guadeloupe), reprenant l'OER | 1 (reprise d'un niveau 1) | https://www.guadeloupe.developpement-durable.gouv.fr/IMG/pdf/bilan-de-lenergie-2024-orec-synergiles.pdf | p.34 (tableau « Émissions de GES du secteur de l'énergie dans les ZNI en 2023 ») |
| 365 (même chiffre) | « chiffres 2023 » ; le libellé « (2021) » du graphique est collé à Guadeloupe/Corse (ambigu) | idem | idem, synthèse | 1 | https://www.guadeloupe.developpement-durable.gouv.fr/IMG/pdf/synthese-de-lenergie-2024-orec-synergiles.pdf | p.7, « Émissions d'un kWh électrique consommé dans les ZNI » |
| **591** | 2022 (prod. 3 064,3 GWh ; cons. 2 820 GWh) | « Ratio moyen d'émission directe par kWh consommé, toutes sources confondues » ; CO2 déclaré quotas 1 665 kt (EDF, Albioma), dont 50 % dû au charbon | OER / SPL Horizon Réunion (BER 2022, éd. 2023) | 1 | https://oer.energies-reunion.com/sites/observatoire-energie-reunion/files/2024-02/HORIZON%20REUNION-0823-BER2022.pdf | p.82 (série 2008-2022 : 679 en 2018, 719, 735, 732 en 2021, 591 en 2022) ; comparatif ZNI p.93 |
| **≈ 363 (dérivé)** | 2023 | La page OER 2024 dit 77 g = « -78,8 % par rapport à 2023 » → 77/(1-0,788) ≈ 363. Calcul du veilleur, pas un chiffre publié tel quel. BER 2023 (éd. 2024) non ouvert ; une page « erratum BER 2023 » existe (https://oer.energies-reunion.com/evenements/erratum-ber-2023-edition-2024), non lue | OER (calcul veilleur) | 1 (à confirmer) | https://oer.energies-reunion.com/emissions-de-ges/co2-combustion-produits-energetiques | page web |
| **77** | **2024** (prod. 3 067,3 GWh ; cons. 2 797 GWh) | « Ratio moyen d'émission directe par kWh consommé » ; CO2 production électrique 216 648 t (8 % du CO2 énergétique). Note : RED II, « les émissions lors de la combustion sont directement réabsorbées » | OER / Énergies Réunion (chiffres clés 2024, éd. 2025) | 1 | https://oer.energies-reunion.com/sites/observatoire-energie-reunion/files/2025-09/ENERGIESREUNION-CHIFFRESCLES%202024%20120x300%20Page%20a%20Page_4.pdf | p.8 du PDF |
| **218 kt** (CO2 absolu) | 2024 | « émissions directes totales annuelles de CO2 liées à la production d'électricité insulaire, périmètre quota CO2 » | EDF SEI Réunion, open data | 1 | https://opendata-reunion.edf.fr/api/explore/v2.1/catalog/datasets/emissions-annuelles-de-c02-974/records | API |
| série EDF (kt) | 2014 à 2024 : 1989, 1912, 1953, 2054, 1926, 2078, 2008, 2098, **1696 (2022), 1092 (2023), 218 (2024)** | idem. Relevé par le veilleur le 2026-11-19, identique à celui du COO (11 lignes). Jeu virtuel, `updatedAt` 2026-10-06 | EDF SEI | 1 | idem ; métadonnées https://opendata-reunion.edf.fr/data-fair/api/v1/datasets/zmuebeju721pnwjf7g6m1cdg | API |
| 679 | 2018 | ratio moyen (PPE) | État/Région (PPE 2019-2028) | 1 | https://www.reunion.developpement-durable.gouv.fr/IMG/pdf/5.1_synthese_ppe2.pdf | non rouvert (extrait de recherche) ; la série OER p.82 confirme 679 en 2018 |
| 502 | 2022 | estimation d'agrégateur | LowCarbonPower | 3 | https://lowcarbonpower.org/fr/region/La_Réunion | non retenu |
| ADEME Base Empreinte, facteur « électricité Réunion » | — | **NON TROUVÉ** | ADEME | — | tentatives : recherche web « Base Empreinte facteur électricité La Réunion » ; https://www.data.gouv.fr/datasets/base-carbone-r-2/ (non ouvert) ; base-empreinte.ademe.fr (non interrogé) | — |
| EDF SEI « contenu CO2 du kWh » (bilan prévisionnel) | — | **NON TROUVÉ** en g/kWh ; le BP renvoie à l'open data pour les émissions annuelles | EDF SEI | — | tentative : https://reunion.edf.fr/sites/sei_reu/files/2023-12/BP_23_La_Reunion.pdf (non relu pour ce point) | — |
| CRE | — | **NON TROUVÉ** | CRE | — | recherches sans résultat spécifique Réunion | — |
| OER 2023 (BER 2023, éd. 2024) et OER 2025 | — | **NON OUVERT / indisponible** ; le dernier édité vu sur la page d'accueil OER est « BER 2024, éd. 2025 » | OER | — | https://oer.energies-reunion.com/presentation-de-loer/nos-publications/bilan-energetique-de-la-reunion | — |

Incohérence interne OER : la page web « CO2 combustion » indique « total émis déclaré en 2024 : 90 kt », alors que le PDF chiffres clés donne 216 648 t et que 77 g x 2 797 GWh = 215 kt. Le 90 kt semble une coquille ou un autre périmètre ; non tranché.

## 2. Ce que 365 mesure exactement

- Un chiffre **2023** (le « (2021) » de la synthèse p.7 est l'étiquette d'autres territoires ; le tableau p.34 du bilan ne marque « chiffres 2022 » que pour Martinique et Guyane).
- Une **moyenne annuelle**, pas une valeur instantanée.
- Le chiffre de l'OER repris tel quel par l'OREC Guadeloupe. Côté OER la base est « par kWh **consommé** ».
- Méthode OER : **émissions directes de combustion déclarées au registre des quotas**, pas une ACV. Preuve : 2024, 216 648 t / 2 797 GWh = 77,5 g (calcul veilleur) = le 77 publié.

## 3. Analyse de l'écart, hypothèse par hypothèse

Rappel de notre calcul : instantané, facteurs Biomasse ex-charbon 200/230, Bioliquide 30/150, Bioénergies 35/150, TAC 700, ENR directes 0, par kWh produit, sans pertes.

**(a) Année antérieure aux conversions : PROUVÉE (cause principale).**
- EDF open data, CO2 direct (périmètre quotas) : 2021 2 098 kt · 2022 1 696 · **2023 1 092** · 2024 **218**. L'effondrement suit les conversions (Bois-Rouge/Le Gol terminées en juillet 2024 d'après l'OER ; Port-Est au bioliquide en oct. 2023).
- Rapporté à la production (calcul reproductible du veilleur) : 2023 : 1 092 kt / 3 085 GWh = **354 g/kWh produit** (365 publié par kWh consommé) ; 2022 : 1 696 / 3 064,3 = 553 (OER : 1 665 kt / 2 820 GWh = 590, publié 591) ; 2024 : 218 / 3 067,3 = **71 g produit**, 218 / 2 797 = 78 g consommé (OER 77).
- L'hypothèse du COO est donc confirmée : environ 354 en 2023 et environ 71 en 2024.
- Limite : la production 2023 (3 085 GWh) vient du tableau de l'OREC Guadeloupe, pas d'un document OER ouvert.

**(b) Comptage de la combustion biomasse/bioliquide à son CO2 réel : INFIRMÉE.**
- Ordre de grandeur (hypothèses du veilleur, non sourcées : biodiesel 0,255 kgCO2/kWh combustible, rendement 40 % soit ~640 g/kWh ; bois et bagasse 0,39 kg/kWh combustible, rendement 30 % soit ~1 300 g/kWh) appliqué au mix 2024 de l'OER : environ **670 g/kWh**, soit près de 9 fois le 77 publié et presque le double du 365. Si le CO2 biogénique était compté, ni le 77 de 2024 ni le 365 de 2023 ne seraient possibles.
- Preuve directe : l'OER écrit en note (chiffres clés 2024, p.8) que pour la biomasse RED II « les émissions lors de la combustion sont directement réabsorbées ». Le 77 exclut le CO2 biogénique.
- Règle EU ETS : le règlement d'exécution (UE) 2018/2066 (MRR), modifié par 2020/2085, applique un facteur d'émission **zéro** à la biomasse qui respecte les critères de durabilité et de réduction de GES de la directive RED II (2018/2001, art. 29) ; la biomasse non conforme est comptée comme fossile. **Statut de la preuve : résultats de recherche secondaires (EPA Irlande, Commission européenne, legislation.gov.uk). Je n'ai pas pu ouvrir le texte primaire** (PDF illisible via l'outil) : article précis (probablement art. 38) à vérifier sur EUR-Lex.
- Implication : le « périmètre quota » d'EDF exclut le CO2 biogénique durable. C'est cohérent avec 218 kt en 2024, mais ce périmètre dépend du statut de durabilité déclaré (colza RED, pellets), non vérifiable depuis nos données.

**(c) Cycle de vie (amont, transport pellets/colza) : INFIRMÉE comme explication du 365 ; valeur NON PROUVABLE.**
- Aucune source (OER, EDF open data, OREC) n'applique d'ACV : toutes disent « émissions directes ». L'OREC ne recalcule rien.
- Aucune valeur ACV réunionnaise sourcée trouvée (ADEME non trouvé). Nos bornes hautes (150 bioliquide/bioénergies) sont un choix de prudence incluant de l'amont (invariant n°5), pas une mesure publiée.

**(d) Produit vs consommé (pertes réseau) : PROUVÉE mais mineure.**
- 2024 : production 3 067,3 GWh, consommation 2 797 GWh (OER p.8), écart 9,7 %. 218 kt donne 71 g produit ou 78 g consommé. Environ +10 % : très insuffisant pour expliquer 365 vs 68-145.

**(e) Autre : nature du chiffre (annuel direct rétrospectif vs instantané avec part biogénique) : PROUVÉE.**
- Nos facteurs appliqués au mix annuel 2024 de l'OER (GWh, p.8 : biodiesel 1 162,5 ; pellets 710,9 ; bagasse 174,1 ; hydro 419,2 ; PV 310,6 ; éolien 35,4 ; biogaz 18,8 ; bioéthanol 2,8 ; GNR 186,1 ; charbon/huiles 40,6 ; secours 3,4 ; batteries 3,1) donnent **122-177 g/kWh**, contre 77 publié. Nos facteurs non nuls sur biomasse et bioliquide ajoutent environ 70-100 g/kWh au périmètre officiel.
- La seule part fossile (230 GWh à 700 g) donne 52 g/kWh, même ordre que le 77. L'écart restant (~161 kt reconstitués contre ~217 kt déclarés) est **non tranchable** (facteur GNR/fioul, démarrages, périmètre ETS).
- Le 68-145 instantané décrit donc un mix récent avec un autre périmètre ; il n'est pas comparable à un 365 annuel 2023.

## 4. Conclusion

**(i) Notre fourchette est cohérente avec une méthode différente** ; elle n'est pas fausse.
- 365 = moyenne annuelle **2023**, émissions directes (périmètre quotas, biogénique durable à zéro), avant la fin des conversions ; vérifié par EDF open data (1 092 kt, ~354 g par kWh produit).
- Même périmètre en **2024** : **77** (OER), 71-78 (EDF selon produit/consommé).
- Notre 68-145 est instantané, par kWh produit, avec une part biogénique/amont non nulle (estimations). Il encadre le 77, mais sa borne haute compte des émissions que les sources officielles ne comptent pas.
- Non tranchable : l'ACV réelle des bioénergies réunionnaises ; l'écart résiduel fossile reconstitué vs déclaré.
- Vigilance : présenter 68-145 comme « l'intensité officielle » serait trompeur ; l'officiel 2024 est 77 (direct), et 365 est un chiffre 2023 périmé pour décrire le parc actuel.

## 5. Proposition (non appliquée)

Texte proposé (UI et prompts, rédaction unique) :

> « Intensité carbone du mix, deux lectures. **Émissions directes (méthode officielle OER/EDF, biomasse et bioliquide durables comptés à zéro)** : 77 gCO2/kWh en 2024 (365 en 2023, avant la fin de la conversion des centrales charbon et fioul). **Notre estimation instantanée** : 68-145 gCO2/kWh, fourchette qui compte une part d'émissions des bioénergies (amont, transport, neutralité débattue). Les deux ne sont pas comparables : l'une est une moyenne annuelle déclarée, l'autre une estimation du mix à l'instant. »

Test d'ancrage pytest (à adapter à la structure réelle de `experts.EXPERTS`, sur le vrai code de prod) :

```python
import re
import experts

def _textes():
    return {k: str(v) for k, v in experts.EXPERTS.items()}  # adapter à la structure réelle

def test_365_toujours_date_2023():
    for nom, prompt in _textes().items():
        for m in re.finditer(r"\b365\s*g", prompt):
            ctx = prompt[max(0, m.start() - 120): m.end() + 120]
            assert "2023" in ctx, f"{nom}: 365 g sans année 2023"

def test_pas_de_chiffre_perime_comme_intensite_actuelle():
    for nom, prompt in _textes().items():
        assert not re.search(r"\b(591|679|732|735)\s*g", prompt), nom

def test_officiel_2024_present_si_chiffre_carbone_cite():
    for nom, prompt in _textes().items():
        if re.search(r"gCO", prompt):
            assert "77" in prompt and "2024" in prompt, nom
```

Preuve par casse volontaire (invariant n°4) : réinjecter « 365 g/kWh » sans année doit rougir le 1er test ; « 591 g/kWh » le 2e ; retirer le 77 le 3e.

## 6. Reste à faire / limites

- Ouvrir le BER 2023 (éd. 2024) et l'erratum OER pour confirmer le 365 à la source primaire et sa base (consommé).
- Ouvrir le texte primaire MRR 2018/2066 sur EUR-Lex et RED II art. 29.
- Jeux EDF des autres ZNI : `emissions-annuelles-de-c02-guadeloupe` répond (11 lignes) ; `-martinique`, `-guyane`, `-corse` renvoient 404 sur le portail opendata-reunion (sondés 2026-11-19 ; hébergement possible sur d'autres portails EDF, non testé). Comparatif ZNI homogène non faisable à ce stade.
- Impact projet à décider (non fait) : CLAUDE.md « Ordre de grandeur mix : ~68-145 gCO₂/kWh » devrait citer l'officiel 77 (2024, direct, OER) ; concerne aussi `experts.py` / `agent_expert.py`.
