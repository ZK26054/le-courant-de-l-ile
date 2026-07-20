# SOURCE — Bilan Prévisionnel EDF SEI 2024 (La Réunion, horizon 2024-2040)

> Fiche de référence factuelle pour le projet. Faits reformulés à partir du
> **Bilan Prévisionnel de l'équilibre offre-demande d'électricité — La Réunion**,
> édition 2024, EDF Systèmes Énergétiques Insulaires (gestionnaire de réseau ZNI).
> Source primaire officielle. À utiliser par l'agent expert (surtout souveraineté/résilience).
> Publié avril 2025.

## 1. Conversions charbon/fioul → biomasse (achevées mi-2024)

À mi-2024, **toutes les installations charbon et fioul de La Réunion ont été converties
à la biomasse**. Détail par site :

| Site (exploitant) | Puissance | Combustible actuel | Date conversion |
|---|---|---|---|
| Port-Est (EDF PEI) | 211 MW (12×17,6) | **Bioliquide — huile de colza** (fournisseur Saipol) | oct. 2023 |
| Bois-Rouge (Albioma) | 94,1 MW | Bagasse (juil-déc, saison sucrière) + biomasse solide le reste de l'année | tranche 2 en 2022, tranches 1.1/1.2 mi-2023 |
| Le Gol (Albioma) | ~105 MW (B 48,5 + A.1/A.2 56,9) | Biomasse solide + bagasse | Le Gol B avant ; A.1/A.2 finalisées fév. & juil. 2024 |
| TAC Saint-Pierre / Sud (Albioma) | 41 MW | Bioéthanol / **GNR** (gasoil) | en service 2019 |
| TAC de La Baie (EDF) | 80 MW (2×40) | **GNR (gasoil) — FOSSILE** | pointe & secours |
| Groupes électrogènes de secours | 24 MW | secours | maintenus post-conversion |

**Implication pour notre taxonomie (CONFIRMÉE par la source) :**
- Colonne API `diesel` = **Bioliquide** (colza, Port-Est). Renouvelable, carbone débattu.
- Colonne API `charbon` = **Biomasse/Bagasse** (Albioma). Renouvelable, carbone débattu.
- Colonne API `turbines_combustion` = **TAC (La Baie GNR + TAC Sud)** = **seule filière fossile**. ✓

## 2. Parc installé au 01/07/2024 — capacité totale 563 MW

- **Bioénergie pilotable** (biomasse/bagasse/bioliquide/bioéthanol/biogaz) : ~415 MW — l'ossature du système.
- **Hydraulique** : 136 MW — Rivière de l'Est 80 MW, Takamaka I+II 43,4 MW, Bras de la Plaine + petite hydro.
- **Photovoltaïque** : 210 MWc (dont ~39 MWc en PV + stockage).
- **Éolien** : Perrière 8,8 MW (repowering partiel) + Sainte-Rose **0 MW** (travaux/repowering, fin prévue 2026). Régime de vent perturbé par le relief → filière modeste.
- **Stockage** : Batrun 5 MW (réserve primaire) + Cratère 5 MW / 10 MWh (report de charge).

## 3. Part ENR — chiffres annuels officiels (≠ instantané dashboard)

- **2022** : le fioul représentait encore 43 % du mix.
- **2023** : **57 % d'ENR** sur l'année (en forte progression, portée par la bioénergie post-conversions partielles).
- **Mi-2024** : conversions achevées → mix « **essentiellement renouvelable**, hormis quelques heures de l'année » où des moyens de pointe non renouvelables (TAC GNR) restent nécessaires.
- **Non-synchrone** (PV + éolien) en 2023 : dépassait **rarement 40 % instantané** ; ~**11 % de la consommation annuelle**.

**⚠️ Garde-fou honnêteté (annuel vs instantané) :**
Le dashboard affiche un **instantané** qui varie énormément selon l'heure et le PV.
Le **chiffre honnête pour un titre** est la **moyenne annuelle** (57 % en 2023, plus élevée depuis).
Ne JAMAIS présenter un « 99 % ce soir » comme « La Réunion est à 99 % renouvelable ».

## 4. Souveraineté & résilience — le cœur de l'analyse

**Dépendance au combustible importé** (la tension centrale de l'autonomie 2030) :
- Le **bioliquide** (Port-Est, 40 % des besoins de l'île) fonctionne à l'**huile de colza importée d'Europe** (parfois OGM), acheminée par navires au fioul lourd. Contrat Saipol, certifié RED.
- La **biomasse solide** (Albioma) repose sur des **pellets importés** ; la **bagasse locale** ne couvre que la saison sucrière (~201 GWh sur 923 GWh en 2023).
- Autrement dit : La Réunion atteint « 100 % renouvelable » mais sa base pilotable dépend de **chaînes logistiques longues** — la dépendance au fioul a été *déplacée* vers le colza/les pellets, pas supprimée.

**Vulnérabilités physiques identifiées par EDF :**
- **Rivière de l'Est** (80 MW hydro, stratégique) fragilisée par les cyclones **Cheneso (2023)** et **Belal (2024)** + lave torrentielle 2023 → gros travaux de réparation/sécurisation.
- Centrales converties à la biomasse : fiabilité « à démontrer dans la durée », **premier semestre 2024 compliqué**.
- Maintenance lourde de Takamaka en cours.
- Groupes de secours (24 MW) conservés pour sécuriser l'équilibre offre-demande.

**Enjeu technique — inertie et stabilité (ZNI) :**
- PV, éolien et batteries sont **non-synchrones** : ne fournissent **pas d'inertie**, très peu de courant de court-circuit. Leur montée fait baisser l'inertie globale → risque pour la stabilité en fréquence.
- Solutions : **compensateurs synchrones**, **stockage** (batteries, STEP), grid-forming.
- Besoins de réserve : **primaire ~50 MW** (perte du plus gros groupe), **secondaire jusqu'à ~200 MW** aux heures de forte production PV/éolien (horizon 2033, scénario Emeraude).
- Critère de défaillance ZNI (PPE) : **3 heures/an** en moyenne.

## 5. Trajectoire 2030-2040 (scénarios Azur & Emeraude)

- **Thermique fossile** : 118 MW (2024) → 41 MW (Azur 2040) ou **0 MW dès 2027** (Emeraude).
- **Bioénergie** : reste ~415 MW — la base combustion perdure (donc la dépendance import aussi).
- **PV** : jusqu'à 730 MW (Azur) / 980 MW (Emeraude) en 2040. **Éolien** : 40-120 MW en 2040.
- **Besoin de puissance pilotable complémentaire** : 80 MW dès 2033 (Azur), jusqu'à **480 MW en 2040** — tiré notamment par la fin de contrat de Port-Est (211 MW) et l'arrêt/conversion des TAC.
- **Consommation 2040** : +40 % à +50 % (démographie + mobilité électrique). Pointe → 737-799 MW (vs 498 MW en 2023).

## 6. Autres flux Open Data EDF (pistes d'enrichissement futur)

Le portail publie aussi, au-delà du mix temps réel :
- **Émissions annuelles directes de CO₂** liées à la production — chiffres RÉELS EDF (pourraient, à terme, remplacer nos estimations de facteurs pour un bilan annuel ; ne remplacent pas la fourchette instantanée).
- Signal **« Météo de l'électricité »** (vert / orange / rouge) — tension du système, J et J+3.
- Signal **« véhicule électrique »** — heures favorables à la recharge (coût + CO₂).
- File d'attente producteurs, registre des installations, déconnexion max du PV.

---

*Cette fiche capture les faits saillants. Le document complet reste la référence en cas de doute.
Les chiffres annuels (57 %, GWh par filière) portent sur 2023 ; le parc sur le 01/07/2024.*
