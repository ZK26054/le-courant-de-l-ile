# Veille institutionnelle — 2026-11-19

> ⚠️ **Rapport brut, revérifié par gardien-qualite. La synthèse `2026-11-19-SYNTHESE.md` fait foi.** Errata (§f) n°1 à 5 et 12 :
> - le « 2023 ≈ 81 % » est faux, l'officiel est 56,6 % ;
> - la série carbone a les années inversées : 740 en 2021, 597 en 2022 ;
> - les puissances du §6 sont mal lues : 312,1 MW = PV ;
> - la reprise de Rivière de l'Est le 09/05/2025 a été manquée ;
> - la divergence C4 sur les dates se tranche : mars 2024 = combustible, juillet 2024 = travaux.

Première veille (aucune veille précédente dans `docs/veille/`). Base de comparaison : `CLAUDE.md`, `docs/sources/SOURCE_bilan-previsionnel-2024.md`, `experts.py`, `filieres.py`.
Légende : N1/N2/N3 = niveau de source. « Impact » = fichier du projet concerné. Pages PDF = index de page du fichier PDF (pas la pagination imprimée).

## 0. Verdict sur les 8 pistes du COO

| # | Piste | Statut |
|---|---|---|
| 1 | Bilan 2025 (3 064 GWh, ENR 96,6 %, autonomie 26,6 %…) | **NON CONFIRMÉE niveau 1.** Chiffres retrouvés uniquement dans la presse (Leader, 23/03/2026), sans source citée. Le bilan OER 2025 n'existe pas encore (dernier BER = données 2024, publié le 31/03/2026). |
| 2 | Bilan 2024 (ENR 92,4 %, 61,2 % importé, 31,2 % local) | **CONFIRMÉE N1** (OER chiffres clés 2024 + BER 2024 éd. 2025). Pas de réponse ministérielle à la QE 15241 à ce jour. |
| 3 | Révision PPE, déclaration d'intention 09/06/2026 | **Existence confirmée par recherche ; contenu NON lu** (« source niveau 1 non trouvée » en lecture directe : URL tentée 404). Calendrier/concertation : non trouvés. |
| 4 | Tanika | **Confirmée (N2, porteur de projet)** : concertation terminée, bilan publié 23/09/2026, en phase d'études/autorisation. Rien d'autorisé ni en service. |
| 5 | Heures Creuses Solaires | **Lancement confirmé (N3). Résultats : rien trouvé.** Dates divergentes entre sources. |
| 6 | Carbone | Hors périmètre ; chiffres croisés notés en section 9. |
| 7 | Plan d'électrification / CSPE | QE 15241 (N1) confirme le plan du 10/04/2026. CRE CP 20/07/2026 (N1) : impact ZNI/La Réunion chiffré. |
| 8 | Bilan prévisionnel EDF SEI 2025 | **Aucune édition 2025 trouvée.** Dernière = édition « 2024 », publiée le 29/04/2025. |

## 1. Production/mix annuel 2024 (N1)

- **2025-09-24 (chiffres clés) / 2026-03-31 (BER technique) · OER / Énergies Réunion · N1**
  URLs : https://oer.energies-reunion.com/sites/observatoire-energie-reunion/files/2025-09/ENERGIESREUNION-CHIFFRESCLES%202024%20120x300%20Page%20a%20Page_4.pdf ; https://oer.energies-reunion.com/sites/observatoire-energie-reunion/files/2026-03/BER_TECHNIQUE-EXPORT-WEB.pdf
  Fait : production électrique nette 2024 = 3 067,3 GWh (−0,6 % vs 2023) ; 7,6 % d'énergies fossiles (pétrole + dernier stock de charbon) et **92,4 % d'ENR, dont 31,2 % d'ENR locales** ; ENR importées = 61,2 % de la production (BER p. 28 ; fiche chiffres clés). Détail GWh : biodiesel 1 162,5 (37,9 %), pellets 710,9 (23,2 %), hydraulique 419,2 (13,7 %), PV 310,6 (10,1 %), bagasse 174,1 (5,7 %), GNR 186,1 (6,1 %), éolien 35,4 (1,2 %), biogaz 18,8 (0,6 %), charbon/huiles usagées 40,6 (1,3 %), batteries 3,1. Pointe 496 MW (février). Part ENR en hausse de +11,2 points vs 2023 (BER p. 28) ; sur cette base, 2023 ≈ 81 % selon la méthode OER (valeur dérivée, non lue telle quelle).
  Impact : CLAUDE.md, docs/sources, experts.py (voir CONTRADICTIONS C1, C2). Confiance : haute.
- **Note de méthode importante** : le 92,4 % de l'OER est un taux de **production** (ENR importées + locales) ; l'**autonomie électrique** officielle OER = ENR **locales** (31,2 % en 2024). Ce n'est ni notre « %ENR strict » (PV + éolien + hydraulique) ni notre « réglementaire ».
  Calcul de contrôle sur chiffres OER 2024 : PV + éolien + hydraulique = (310,6 + 35,4 + 419,2) / 3 067,3 ≈ 25,0 % ; l'« autonomie » OER 31,2 % ajoute bagasse (5,7 %) et biogaz (0,6 %). Calcul fait par la veille, pas un chiffre publié.

## 2. Année 2025 (piste 1) — niveau 3 seulement

- **2026-03-23 · Leader Réunion · N3** · https://www.leaderreunion.fr/en/la-production-delectricite-est-restee-stable-en-2025/ (page ouverte)
  Fait rapporté : production 2025 = 3 064 GWh (l'article écrit « gigawatts »), quasi stable ; ENR 96,6 % ; autonomie électrique 26,6 % (31 % en 2024) ; hydraulique 7,7 % (cyclone Garance : 21 pylônes détruits, prise d'eau des Orgues endommagée) ; bagasse 5,9 % ; PV 11 % ; éolien 1,4 % (renforcement du parc à Sainte-Suzanne) ; biogaz 0,7 % ; TAC 3,8 %. **Aucune source citée** dans l'article.
  Impact : aucun pour l'instant (N3 non corroboré). Confiance : moyenne pour l'ordre de grandeur (cohérent avec 31,2 % N1 en 2024 et avec les dégâts N1 de Garance), faible pour les décimales.
  Remarque : « hydraulique 7,7 % » est une baisse de ~6 points vs 13,7 % en 2024 (N1) — cohérent avec la perte de Rivière de l'Est.
- OER : « source niveau 1 non trouvée » pour 2025. La page des publications (https://oer.energies-reunion.com/presentation-de-loer/nos-publications/bilan-energetique-de-la-reunion) ne liste aucun bilan 2025 ; dernière édition = BER 2024 éd. 2025, 31/03/2026. À re-vérifier à la prochaine veille (le BER 2025 sortira vraisemblablement début 2027).
- EDF (reunion.edf.fr) : sites bloqués en lecture automatisée (HTTP 403) sur les pages et PDF tentés ; aucun communiqué EDF avec le bilan 2025 trouvé via recherche.

## 3. Cyclone Garance (28/02/2025) et Rivière de l'Est

- **2025-06-12 · EDF SEI (retex hébergé par la DEAL) · N1** · https://www.reunion.developpement-durable.gouv.fr/IMG/pdf/5b_edf_retex_post_garance_electricite.pdf (PDF lu)
  Fait : prise d'eau n°1 des Orgues (centrale de Sainte-Rose / Rivière de l'Est) **totalement détruite** (elle l'était déjà partiellement par Belal) ; prise d'eau n°2 obturée par des blocs rocheux, grilles détruites ; passe latérale obturée. Réseau : 30 % du HTB impacté (12 lignes 63 kV sur 42, 165 km sur 520), **2 lignes HTB détruites avec 21 supports ruinés** ; 340 défauts sur 82 départs HTA ; réalimentation : 96 % des clients 1 semaine après la sortie d'alerte rouge, 98 % à 10 jours. Pic : 58 % des clients réalimentés selon le graphique de la 1re phase (diapo 8).
  Impact : **CLAUDE.md / docs/sources / experts.py** (Garance absent ; voir C3). Confiance : haute. (La date exacte 28/02/2025 vient du COO et d'un CP EDF listé par recherche, non ouvert ; le retex place l'atterrissage à 10 h sur Sainte-Suzanne.)
- **2026-03-31 · OER BER 2024 (p. 28) · N1** : en 2024 déjà, avarie sur la centrale de Rivière Sainte-Rose après Belal (jan. 2024) : prise d'eau assurant 80 % de la production endommagée ; la centrale n'a fonctionné que 3 mois sur la 2e prise (20 %). Hydraulique 2024 = 13,7 %.
- Remise en service de la prise d'eau / calendrier de travaux : **rien trouvé** (N1 non trouvée).
- Incident réseau majeur 2026 : rien de nouveau trouvé.

## 4. Révision de la PPE (piste 3)

- **2024-12-02/03 · Région Réunion + État · annonce publiée par Imaz Press et Outremers 360 · N3 (relai d'un événement N1)** · https://imazpress.com/zoom/la-region-reunion-annonce-la-revision-de-la-programmation-pluriannuelle-de-l-energie
  Fait : révision de la PPE 2019-2028 annoncée conjointement ; la présidente de Région propose une « concertation régionale » de l'énergie la première année ; cadastre solaire finalisé, schéma régional éolien en cours. L'article cite 57 % d'ENR (probablement 2023) et un mix « 100 % renouvelable » sans les concilier. Aucune échéance. Confiance : moyenne.
- **2026-06-09 · Région Réunion · déclaration d'intention · N1** · https://www.regionreunion.com/IMG/pdf/2026-06-09_decintentppe-2.pdf
  **Source niveau 1 non lue** : l'URL renvoie 404 (page non trouvée) à la lecture directe ; seul l'extrait de recherche est disponible. Ce que l'extrait indique : PPE élaborée conjointement par la présidente de Région et le préfet ; publiée au titre des art. L.121-18 et R.121-25 du code de l'environnement (participation du public) ; PPE actuelle = décret n°2022-575 du 20/04/2022, périodes 2019-2023 et 2024-2028. Ni calendrier, ni modalités de concertation, ni garant CNDP identifiés. Impact : CLAUDE.md/experts.py (trajectoire PPE) une fois le contenu lu. Confiance : moyenne sur l'existence, aucune sur le contenu.
- Rien de nouveau trouvé sur un éventuel décalage de l'objectif 2030.

## 5. Tanika — STEP marine 50 MW, Saint-Denis (piste 4)

- **2026-05 à 2026-10 · Hydro Tanika (filiale EDF / Banque des Territoires) · N2** · https://hydro-tanika.re/ et https://hydro-tanika.re/concertation/ (pages ouvertes)
  Fait : projet 50 MW, jusqu'à 8 h de stockage, usine souterraine. Concertation préalable du 20/05 au 02/07/2026 (plénière de lancement 20/05, clôture 02/07, 8 réunions listées, toutes « Terminé ») ; plus de 600 participants (annonce du 06/07/2026) ; **bilan de la concertation publié le 23/09/2026** ; la Banque des Territoires prend 35 % du capital de Hydro Tanika (annonce du 01/10/2026). Calendrier du porteur : études 2025-2026, autorisations 2026-2028, **construction 2028-2033, mise en service 2033**. Statut exact : **annoncé / en concertation terminée / autorisations à venir ; ni autorisé ni en service.** Mention CNDP : non trouvée sur la page. Un cabinet d'avocats (Addleshaw Goddard, 06/10/2026, N3) corrobore l'entrée de la CDC à 35 %.
  Impact : experts.py:44 et CLAUDE.md:136, 216 restent corrects (« aucune STEP opérationnelle ») ; idée d'ajouter « STEP marine Tanika 50 MW prévue 2033 » à la trajectoire. Confiance : haute sur le statut (calendrier = prévision du porteur N2).

## 6. Éolien, PV, stockage

- **2026-06-10 · EDF power solutions · N2 (via relais presse EnergyNews, N3)** · https://energynews.pro/en/edf-power-solutions-inaugurates-88-mw-wind-farm-on-reunion-island (page non ouvrable : vérification anti-bot ; contenu lu uniquement dans l'extrait de recherche)
  Fait rapporté : inauguration du parc de **Sainte-Rose repowered, 8,8 MW (4 éoliennes) + batterie 4,6 MWh**, en remplacement de 23 machines de 2004 ; production ×6 revendiquée par l'exploitant. Impact : CLAUDE.md:136 (« Sainte-Rose 0 MW, travaux jusqu'en 2026 »), experts.py:30 (« Sainte-Rose, démantelé/en travaux »), docs/sources:33. **Non corroboré N1** : confiance moyenne ; à confirmer par EDF SEI/OER (BER 2024 p. 19 : Sainte-Rose démantelée depuis 2023, filière éolienne néanmoins en hausse via Sainte-Suzanne).
- **2025/2026 · OER BER 2024 · N1** : puissance PV contractuelle 211 MW (fiche chiffres clés), 312,1 MW cité pour la puissance totale PV dans l'extrait de recherche mais **non confirmé** à la lecture (la fiche liste 312,1 sous « hydraulique/PV » dans un tableau à lecture ambiguë ; à ne pas utiliser). Éolien 19,8 MW, biogaz 6,9 MW, biodiesel 195,8 MW, hydraulique 134,4 MW.
- Open data EDF Réunion (opendata-reunion.edf.fr) : rien de nouveau trouvé (aucune annonce de correction du flux éolien figé). Le registre national est publié par ailleurs sur data.gouv.fr (version « au 30/06/2026 ») : à surveiller pour la carte installations.

## 7. Tarifs et expérimentations (piste 5)

- **2025-10-28 · Leader Réunion · N3** · https://www.leaderreunion.fr/en/edf-experimente-les-heures-creuses-solaires/ (ouverte) : expérimentation d'heures creuses diurnes (9 h-14 h) pour clients volontaires déjà en option heures creuses, **annoncée pour 3 mois à partir d'octobre 2025**. Le COO indique janvier-juin 2026 (lettre « EDF & moi » ; PDF EDF bloqué en 403, non lu) : **dates divergentes**. Nombre de participants : 2 000 à 3 000 selon sources non datées. **Résultats : rien trouvé.** Confiance : faible.
- **CRE · délibération 2026-147 du 15/07/2026 (via recherche, non lue)** : suppression de l'option Base des tarifs Bleus+ au 01/08/2026 dans les DOM, dont La Réunion (N1 par extrait seulement, à confirmer).

## 8. Plan d'électrification et CSPE (piste 7)

- **2026-05-19 · Assemblée nationale · QE n°15241 de F. Maillot (GDR, Réunion) · N1** · https://questions.assemblee-nationale.fr/q17/17-15241QE.htm (ouverte)
  Fait : JO du 19/05/2026 p. 4343, adressée au ministère des Outre-mer ; elle rappelle le plan d'électrification annoncé le **10/04/2026** ; cite ENR 92,4 % en 2024 mais majoritairement importées (biodiesel + pellets = 61,2 %) ; demande, entre autres, que La Réunion soit territoire d'expérimentation parmi la centaine prévue. **Aucune réponse ministérielle publiée** à ce jour. Position d'un parlementaire : rapportée sans trancher. Impact : aucun (chiffres alignés avec OER N1). Confiance : haute.
- Une autre source indexée donne le 23/04/2026 pour la publication du plan (22 mesures, « 100 territoires d'électrification », financés surtout par CEE) : **dates divergentes 10/04 vs 23/04, texte officiel du plan non trouvé** ; aucune mesure spécifique à La Réunion trouvée.
- **2026-07-20 · CRE · communiqué sur la délibération n°2026-149 du 15/07/2026 · N1** · https://www.cre.fr/fileadmin/Documents/Communiques_de_presse/2026/260720_CP_CSPE.pdf (PDF lu)
  Fait : charges de service public 2026 = 12,3 Md€ (dont 3,25 Md€ ZNI, par une part de l'accise) ; 2027 = 14,2 Md€ (dont 3,56 Md€ ZNI). Charges ZNI en hausse de 0,2 Md€ « en raison principalement de la mise en service de nouveaux moyens de production renouvelable, en Guyane et à La Réunion » ; demande +2 % ; ces actifs se substituent à des moyens thermiques fossiles. Montant propre à La Réunion non trouvé (annexes non lues). Impact : idée d'article ; aucun changement de prompt. Confiance : haute.

## 9. Bilan prévisionnel EDF SEI (piste 8) et carbone croisé

- **2025-04-29 · EDF SEI · N1** · https://reunion.edf.fr/sites/sei_reu/files/2025-04/2025-04-29-reunion-bp-2024.pdf (**PDF non lu : HTTP 403** ; date déduite de l'URL de dépôt + page EDF)
  Fait : l'édition intitulée « 2024 » (horizon 2024-2040, scénarios Azur/Emeraude, informations début 2024) a été mise en ligne le **29/04/2025**. `docs/sources/SOURCE_bilan-previsionnel-2024.md` (l.7, « Publié avril 2025 ») est donc cohérent. **Aucune édition 2025 trouvée** (page EDF « bilan prévisionnel » : 403, recherche sans résultat). Rien de nouveau trouvé. Les chiffres du BP (parc 563 MW, 57 % en 2023…) n'ont pas pu être re-vérifiés dans le PDF lors de cette veille.
- **Carbone (croisé, piste 6 hors périmètre)** · OER BER 2024 p. 109 et fiche chiffres clés · N1 : ratio moyen d'émission directe = **77 gCO2/kWh** consommé en 2024 (−78,8 % vs 2023 ; série : 740 en 2022, 597 en 2021 [*], **365 en 2023**). Méthode : émissions directes déclarées (quotas : 90 kt CO2 en 2024, 0 % dû à la combustion de charbon) ; la combustion de biomasse/biodiesel n'est donc pas comptée, ce qui n'est pas une analyse cycle de vie. Le BER 2024 note que le charbon résiduel a été liquidé début 2024. [*] la ligne de la série est lue telle qu'extraite du PDF ; l'alignement année/valeur est à vérifier par l'agent carbone.
  Rapprochement : 77 g est dans notre fourchette 68-145 (CLAUDE.md:113, 189) mais mesure autre chose (directe vs ACV estimée) ; ne pas confondre.
- OER BER 2024 p. 28 : « depuis mars 2024 » les unités charbon de Bois-Rouge/Le Gol « fonctionnent à 100 % biomasse » ; biodiesel introduit à Port-Est en **juin 2023** (CLAUDE.md : oct. 2023). Voir C4.

## CONTRADICTIONS

Chaque entrée : phrase du projet (fichier:ligne), ce que disent les sources, niveau.

- **C1 — « 57 % en 2023 » comme ancre annuelle**
  - `experts.py:84` : « Moyenne annuelle officielle : 57 % d'ENR en 2023 (Bilan Prévisionnel EDF SEI), en hausse depuis les conversions achevées mi-2024, mais aucun chiffre officiel plus récent n'est disponible — ne l'invente jamais. »
  - `CLAUDE.md:138` : « Chiffres ENR ANNUELS officiels : 57 % en 2023 … » ; `CLAUDE.md:208` ; `docs/sources/SOURCE_bilan-previsionnel-2024.md:39,45`.
  - Faits : (a) **faux dans « aucun chiffre officiel plus récent n'est disponible »** : l'OER (N1) publie 92,4 % d'ENR pour 2024 (31,2 % locales), et une presse N3 donne 96,6 % pour 2025 (non corroboré). (b) Les 57 % (EDF SEI, 2023) et le taux OER (2023 ≈ 81 % dérivé de +11,2 pts) reposent sur des **périmètres différents** ; la proximité de « 57 % » avec l'annonce Région de 12/2024 (N3, « 57 % ») montre que le chiffre circule sans définition. Recommandation (à décider par le COO, pas appliquée) : présenter aux experts les deux séries avec leur définition.
- **C2 — Notion d'« autonomie » / %ENR**
  - `CLAUDE.md:109-110` et `experts.py:60-61, 83-84` : double %ENR (strict = PV+éolien+hydraulique ; réglementaire = + bioénergies) ; « ne pas présenter le 90 % seul comme autonomie ».
  - Faits N1 : l'« autonomie électrique » officielle (OER) = **ENR locales**, **bagasse et biogaz inclus** : 31,2 % en 2024. Notre « strict » (≈ 25 % en 2024 par calcul de la veille) l'exclut. Le projet n'a **aucun** équivalent de l'indicateur officiel, et `experts.py:84` oriente vers « 57 % » pour répondre à « La Réunion est-elle autonome ? ». Le 92,4 % de l'OER est un taux de production (importé + local), proche de notre « réglementaire ».
- **C3 — Rivière de l'Est : Garance absent**
  - `experts.py:93` : « fragilisée par les cyclones Cheneso (2023) et Belal (2024) + une lave torrentielle en 2023 → travaux lourds de réparation/sécurisation » ; `CLAUDE.md:140` ; `docs/sources/…:56`.
  - Faits N1 (EDF retex 12/06/2025) : **Garance (28/02/2025)** a totalement détruit la prise d'eau n°1 et obturé la n°2 ; 2 lignes HTB détruites. Conséquence mesurable : hydraulique de 13,7 % (2024, N1) à 7,7 % (2025, N3 non corroboré). Les prompts décrivent un état antérieur à 2025. De plus `CLAUDE.md:136` / `experts.py:44` : hydraulique 136 MW, mais le BER 2024 donne 134,4 MW (périmètre différent possible).
- **C4 — Dates de conversion biomasse/biodiesel (trois versions)**
  - `CLAUDE.md:100-101, 137` et `experts.py:33` : conversion « mi-2024 », Port-Est « oct. 2023 » ; `CLAUDE.md:101` et `CLAUDE.md:218-221` déclarent « mars 2024 » **faux**.
  - `filieres.py:8` : « Bois-Rouge/Le Gol 100% biomasse mars 2024 ; Port-Est huile de colza déc. 2023 » (docstring, non vérifié par les tests d'ancrage).
  - Faits : OER N1 (BER 2024 p. 28) : « depuis mars 2024 » 100 % biomasse, biodiesel à Port-Est depuis **juin 2023**. EDF SEI (docs/sources) : Le Gol A.1/A.2 fév. et juil. 2024, Port-Est oct. 2023. **Divergence N1 vs N1 non tranchée** ; le projet est incohérent avec lui-même (filieres.py vs CLAUDE.md/experts.py). À arbitrer par le COO avant toute correction.
- **C5 — « pas de STEP opérationnelle »**
  - `experts.py:44`, `CLAUDE.md:136, 216`. **Toujours exact** (Tanika : mise en service prévue 2033, N2). Pas de contradiction ; ajout possible de la trajectoire.
- **C6 — Éolien Sainte-Rose**
  - `CLAUDE.md:136` (« Sainte-Rose 0 MW, travaux jusqu'en 2026 »), `experts.py:30` (« démantelé/en travaux »), `docs/sources:33`. Inauguration d'un parc repowered 8,8 MW + batterie 4,6 MWh le 10/06/2026 (N2/N3, non corroboré N1). Si confirmé, le projet est périmé sur ce point ; et la phrase « Perrière 8,8 MW » (`CLAUDE.md:136`) coexiste avec « Sainte-Suzanne 19,8 MW » (`CLAUDE.md:115`, `experts.py:30`) : mélange possible Perrière / Sainte-Rose à clarifier (8,8 MW = chiffre attribué aux deux sites selon les documents).
- **C7 — Trajectoire PPE**
  - `experts.py:69` et `CLAUDE.md:135` : « autonomie énergétique 2030 (100 % électricité renouvelable) » ; `CLAUDE.md:142` trajectoire EDF 2024-2040. La PPE est **en révision** (déclaration d'intention 09/06/2026, contenu non lu) : l'objectif 2030 et les périodes 2024-2028 pourraient changer. À indiquer comme « en cours de révision » ; aucune évolution d'objectif confirmée.
- **C8 — « Aucun chiffre officiel plus récent » vs fourchette carbone**
  - `CLAUDE.md:113, 189` (68-145 gCO2/kWh, estimation) : l'OER publie 77 gCO2/kWh (émission directe 2024, 365 en 2023). Pas de contradiction, mais le projet n'indique pas l'existence de ce chiffre officiel et sa méthode.

## IDÉES D'ARTICLES (3 max)

1. **« 92,4 % renouvelable, 31,2 % local : de quoi parle-t-on ? »** — OER 2024 : taux de production (importé + local), autonomie = ENR locales, calcul PV+éolien+hydro ≈ 25 %, biodiesel 37,9 % + pellets 23,2 % ; QE 15241. Faits N1.
2. **Garance et l'hydraulique : la fragilité d'une source locale** — retex EDF (prise d'eau détruite, 21 supports HTB) + hydraulique 13,7 % en 2024 (N1) ; chiffre 2025 à confirmer quand le BER 2025 sortira.
3. **Tanika et le stockage 2033** — calendrier du porteur N2 (concertation, bilan 23/09/2026), contexte CRE N1 (charges ZNI en hausse par mise en service de nouveaux moyens renouvelables à La Réunion), et lien avec l'inertie/non-synchrone du Bilan prévisionnel.

## Limites de cette veille

- EDF (`reunion.edf.fr`) : tous les PDF/pages tentés ont renvoyé HTTP 403 ; faits EDF issus du retex DEAL, de recherches (extraits) ou non vérifiés.
- Non lus faute d'accès : déclaration d'intention PPE (404), annexes CRE par opérateur, BP SEI 2024 (PDF), lettre « EDF & moi » 2026, communiqué EDF PS Sainte-Rose.
