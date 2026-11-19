// Transcriptions des deux vidéos : textes affichés à l'écran, dans l'ordre des scènes,
// extraits de video/scenes.py et video/scenes2.py (valeurs animées relevées dans le code).
// Les « notes de vérification » signalent les écarts avec les sources de niveau 1 du site.

export interface Scene { titre: string; texte: string[] }
export interface Video {
  id: string;
  titre: string;
  fichier: string;
  affiche: string;
  duree: string;
  dureeIso: string;
  resume: string;
  scenes: Scene[];
  sources: string[];
  verification: string[];
}

export const VIDEOS: Video[] = [
  {
    id: 'le-courant-de-l-ile',
    titre: 'Le courant de l’île',
    fichier: 'videos/le-courant-de-l-ile.mp4',
    affiche: 'videos/le-courant-de-l-ile-affiche.webp',
    duree: '3 min 02',
    dureeIso: 'PT3M2S',
    resume: 'De l’eau des barrages à la biomasse importée : comment l’île produit son électricité, de 1981 à 2040.',
    scenes: [
      { titre: 'Titre', texte: ['La Réunion · 974 · de 1981 à 2040.', 'Le courant de l’île.', 'De l’eau des barrages à la biomasse importée : comment l’île produit son électricité, et ce qui l’attend.'] },
      { titre: 'Zone non interconnectée (ZNI)', texte: ['Une île, un réseau.', 'Aucun câble ne relie La Réunion à un autre réseau électrique.', 'Chaque seconde, les centrales de l’île doivent produire exactement ce que l’île consomme. Production, consommation : 50,00 Hz.'] },
      { titre: 'Point de départ : 1981', texte: ['100 % de l’électricité de l’île vient de l’eau.', 'La centrale hydroélectrique de Rivière de l’Est vient d’entrer en service (1980). L’île est alors autonome en électricité.', 'Sources : Région Réunion, plan PRERURE · Connaissance des Énergies.'] },
      { titre: 'Puis la demande explose', texte: ['Graphique du mix électrique : 1981, 100 % hydraulique · 1990, 61 % hydraulique, 3 % bagasse, 36 % fioul et gazole · 1995, 46 % hydraulique, 12 % bagasse, 21 % charbon, 21 % fioul et gazole · 2008, 24,8 % hydraulique, 10,3 % bagasse, 1 % solaire et éolien, 50,6 % charbon, 13,3 % fioul et gazole.', 'En vingt ans, la consommation d’énergie de l’île bondit de 350 %. L’eau ne suffit plus : on importe du charbon et du fioul.', '1992 : Bois-Rouge. 1996 : Le Gol. Deux centrales charbon-bagasse s’installent près des sucreries.', 'Sources : Région Réunion, PRERURE (1981-1995) · INSEE, Tableau économique de La Réunion 2010 (2008).'] },
      { titre: '2015 · le sommet de la dépendance', texte: ['63,5 % de l’électricité produite vient d’énergies fossiles importées.', 'Le charbon, à lui seul, en fournit 40,4 %. Les centrales tournent avec des combustibles arrivés par bateau.', 'Grille de 100 carrés (1 carré = 1 %) : charbon, fioul et gazole, renouvelables.', 'Source : Connaissance des Énergies, d’après l’Observatoire Énergie Réunion (production 2015).'] },
      { titre: 'Le virage', texte: ['2015 : la loi fixe un cap, l’autonomie énergétique des Outre-mer en 2030.', '2017 : première programmation pluriannuelle de l’énergie (PPE) de La Réunion.', '2022 : Bois-Rouge commence à remplacer le charbon par la biomasse.', 'Octobre 2023 : Port-Est (211 MW) remplace le fioul par de l’huile de colza.', '2024 : Le Gol achève sa conversion. Plus aucune centrale ne brûle de charbon.', 'Sources : loi de transition énergétique (2015) · décret PPE (2017) · EDF SEI, Bilan prévisionnel 2024.'] },
      { titre: 'Le mix bascule', texte: ['Part renouvelable de la production d’électricité : 2008, 36,1 % · 2015, 36,5 % · 2022, 38 % · 2023, 57 % · 2024, 92,4 % · 2025, 96,6 %.', 'Pendant quinze ans, la part renouvelable plafonne autour d’un tiers. Avec les conversions, elle dépasse 96 % en trois ans.', 'Sources : INSEE (2008) · Connaissance des Énergies (2015) · EDF SEI, bilans prévisionnels (2022-2023) · Question écrite AN n°15241 (2024) · Leader Réunion, mars 2026 (2025).'] },
      { titre: '2025 · d’où vient l’électricité ?', texte: ['Renouvelable, oui. Local, pas encore.', '26,6 % de production vraiment locale : soleil, eau, bagasse, vent, biogaz.', '≈ 70 % de biomasse importée : huile de colza venue d’Europe, granulés de bois.', 'EDF parle d’un mix renouvelable ; ses critiques, d’une dépendance déplacée du fioul vers d’autres importations.', 'Grille de 100 carrés : solaire 11, hydraulique 8, bagasse 6, éolien 1, biogaz 1, biomasse importée 69, fossile (turbines) 4.', 'Source : Leader Réunion, 23 mars 2026, d’après le bilan électrique 2025 · 1 carré = 1 %, valeurs arrondies.'] },
      { titre: 'Comment ça marche · une journée réelle, 7-8 mars 2026', texte: ['Le réseau, heure par heure : graphique de la production par filière (huile de colza, biomasse, bioénergies, hydraulique, éolien, solaire, turbines à combustion).', 'Fin d’après-midi : le soleil baisse, le solaire recule.', 'Pointe du soir, 413 MW : les barrages montent à 91 MW pour suivre.', 'La nuit : biomasse et huile de colza portent le réseau.', 'Le jour revient : le solaire reprend sa place.', 'Solaire et éolien n’apportent pas d’inertie au réseau : au-delà d’un seuil, la fréquence devient difficile à tenir. Centrales pilotables, barrages et batteries assurent l’équilibre.', 'Données : EDF Réunion open data, production par filière, valeurs estimées · stockage (±5 MW) non représenté · une valeur isolée écartée (01:05).'] },
      { titre: 'Fragilités', texte: ['Le climat met le réseau à l’épreuve.', 'Janvier 2024 : cyclone Belal.', '28 février 2025 : cyclone Garance, 21 pylônes à très haute tension détruits, la prise d’eau qui alimente Rivière de l’Est arrachée.', 'En 2025, l’hydraulique ne fournit plus que 7,7 % de l’électricité.', 'Sources : EDF Réunion · Leader Réunion, mars 2026 · EDF SEI, Bilan prévisionnel 2024.'] },
      { titre: 'Horizon 2040 · scénarios du gestionnaire de réseau', texte: ['Demain : plus de besoins.', 'Consommation d’électricité : +40 à +50 % d’ici 2040 (population, véhicules électriques).', 'Pointe de consommation : 498 → 799 MW, de 2023 à 2040 (737 à 799 MW selon le scénario).', 'Solaire installé : 210 → 980 MWc, de 2024 à 2040 (730 à 980 MWc selon le scénario).', 'Puissance pilotable à trouver : jusqu’à 480 MW en 2040, notamment après la fin du contrat de Port-Est.', 'Source : EDF SEI, Bilan prévisionnel de l’équilibre offre-demande, La Réunion 2024 (horizon 2040, scénarios Azur et Emeraude).'] },
      { titre: 'Les chantiers ouverts', texte: ['Trois questions pour la suite.', 'Stocker : projet Tanika, une station de pompage en eau de mer de 50 MW à Saint-Denis, en concertation depuis 2026.', 'Produire sur l’île : la loi vise l’autonomie énergétique en 2030. En 2025, 7 kWh sur 10 viennent encore de biomasse importée.', 'Électrifier : les transports représentent 63 % de l’énergie finale de l’île, et roulent presque tous aux carburants fossiles.', 'La programmation pluriannuelle de l’énergie de La Réunion est en cours de révision.', 'Sources : EDF Réunion, lettre « EDF & moi » juil.-déc. 2026 (Tanika) · Question écrite AN n°15241 · Région Réunion (PPE).'] },
      { titre: 'Fin', texte: ['Renouvelable : presque fait.', 'Autonome : le prochain défi.', 'Le courant de l’île.'] },
      { titre: 'Sources', texte: ['Chiffres arrondis. Les données temps réel EDF sont des valeurs estimées.'] },
    ],
    sources: [
      'Région Réunion — PRERURE, mode de production 1981-2000',
      'INSEE — Tableau économique de La Réunion 2010',
      'Connaissance des Énergies — mix électrique 2015 ; centrales du Gol et de Rivière de l’Est',
      'EDF SEI — Bilans prévisionnels La Réunion 2023 et 2024',
      'Assemblée nationale — question écrite n°15241, 19 mai 2026',
      'Leader Réunion — « La production d’électricité est restée stable en 2025 », 23 mars 2026',
      'EDF Réunion — open data, production par filière en temps réel',
      'EDF Réunion — lettre « EDF & moi », juillet-décembre 2026 (projet Tanika)',
      'Région Réunion — déclaration d’intention de révision de la PPE, 9 juin 2026',
    ],
    verification: [
      'Les chiffres 2025 de la vidéo (96,6 % renouvelable, 26,6 % local, ≈ 70 % de biomasse importée, hydraulique 7,7 %) viennent de la presse (Leader Réunion, mars 2026). Aucun bilan officiel 2025 n’est publié au 19/11/2026 : ce site n’affiche que les chiffres officiels 2024 (92,4 % renouvelable, 31,2 % local).',
      'Part renouvelable 2023 : la vidéo arrondit à 57 %, la valeur officielle est 56,6 % (OER, EDF open data).',
      'Le Gol : la vidéo indique 1996, Albioma indique « en service depuis 1995 ».',
      'Garance : le retour d’expérience d’EDF SEI (juin 2025) parle de 2 lignes à haute tension détruites (21 supports) et de la prise d’eau n°1 des Orgues totalement détruite.',
    ],
  },
  {
    id: 'les-megawatts-de-l-ile',
    titre: 'Les mégawatts de l’île',
    fichier: 'videos/les-megawatts-de-l-ile.mp4',
    affiche: 'videos/les-megawatts-de-l-ile-affiche.webp',
    duree: '2 min 09',
    dureeIso: 'PT2M9S',
    resume: 'Qui produit l’électricité de La Réunion, où, et avec quelle puissance : le parc de 1 035 MW expliqué.',
    scenes: [
      { titre: 'Titre', texte: ['La Réunion · parc électrique · 2024-2026.', 'Les mégawatts de l’île.', 'Qui produit l’électricité de La Réunion, où, et avec quelle puissance.', '1 035 MW installés fin 2024.'] },
      { titre: 'Deux unités à ne pas confondre', texte: ['Puissance ou énergie ?', 'MW, mégawatt, la puissance : ce qu’une centrale peut fournir à un instant donné. C’est la taille du robinet.', 'MWh, mégawattheure, l’énergie : ce qu’elle produit vraiment dans la durée. C’est l’eau qui a coulé.', '1 MW ouvert en grand : le compteur défile jusqu’à « pendant 24,0 h = 24,0 MWh ».'] },
      { titre: 'Parc installé au 31 décembre 2024', texte: ['1 035 MW, filière par filière : solaire 312,1 MW · huile de colza (Port-Est) 211 MW · biomasse (Le Gol, Bois-Rouge) 196 MW · hydraulique 134,4 MW · turbines à combustion 121 MW · groupes de secours 24 MW · éolien 19,8 MW · batteries 10 MW · biogaz 6,9 MW.', 'Source : Observatoire Énergie Réunion, Bilan énergétique, chiffres clés 2024 (édition 2025) · puissances contractuelles.'] },
      { titre: 'Où sont les mégawatts ?', texte: ['Quelques gros sites, des centaines de toits.', 'Sept centrales thermiques et hydrauliques concentrent 63 % de la puissance installée : Port-Est 211 MW, Le Gol 104 MW, Bois-Rouge 92 MW, TAC La Baie 80 MW, Rivière de l’Est 80 MW, Takamaka 43,4 MW, TAC Saint-Pierre 41 MW.', 'Le solaire, lui, est éparpillé : 312 MW répartis entre fermes solaires, hangars, écoles et maisons.', 'Surface des cercles proportionnelle à la puissance · emplacements approximatifs du solaire.', 'Sources : OER, chiffres clés 2024 · EDF Réunion · Albioma.'] },
      { titre: 'Ce que pèse chaque filière en 2024', texte: ['Un mégawatt n’en vaut pas un autre.', 'Part de la puissance installée / part de l’énergie produite / heures par an à pleine puissance : solaire 30,2 % / 10,1 % / 995 h · huile de colza 20,4 % / 37,9 % / 5 509 h · biomasse 18,9 % / 30,2 % / 4 722 h · hydraulique 13 % / 13,7 % / 3 119 h · turbines à combustion 11,7 % / 6,2 % / 1 561 h.', 'Le solaire : 30 % de la puissance, 10 % de l’énergie. Il ne produit que le jour ; l’huile de colza tourne jour et nuit.', 'Source : OER, chiffres clés 2024 · biomasse = granulés + bagasse + reliquat charbon · turbines = gazole + bioéthanol · calculs : énergie ÷ puissance.'] },
      { titre: 'Pourquoi 1 035 MW ?', texte: ['Deux fois la pointe, et pourtant…', '1 035 MW installés, dont 312 MW de solaire : 723 MW sans le soleil.', '19 h : plus de soleil. Pointe 2023 : 498 MW.', 'Le soir, quand la consommation culmine, le solaire ne produit plus.', 'Il faut une réserve : si la plus grosse machine décroche, une autre doit prendre le relais en quelques secondes.', 'Des centrales sont en maintenance, d’autres peuvent être touchées par un cyclone.', 'Sources : OER, chiffres clés 2024 (parc) · EDF SEI, Bilan prévisionnel 2024 (pointe 2023, réserves).'] },
      { titre: 'Les dernières mises en service · Albioma Solaire Réunion', texte: ['Le solaire pousse toit par toit.', '1er septembre 2026, Saint-Pierre, école Henri La Pierre : 155 kWc, 230 MWh par an.', '9 octobre 2026, Saint-Paul, Gamm Vert Cambaie, rénovée : 161 → 177 kWc.', '5 novembre 2026, Saint-Pierre, SuperCash2 : 100 kWc, 151 MWh par an.', '9 novembre 2026, Saint-Louis, usine du Gol, toits GOL 4 et 6 : 193 kWc, 277 MWh par an.', '12 novembre 2026, Saint-Pierre, école Iris Hoarau : 166 kWc, 261 MWh par an.', 'Récent, Petite-Île, village artisanal Argamasse : 162 kWc, 240 MWh par an.', 'Six chantiers, ≈ 0,8 MWc au total.', 'Ordre de grandeur : pour égaler la puissance de Port-Est (211 MW), il faudrait environ 1 270 toits comme l’école Iris Hoarau, et environ 4 450 pour égaler ce qu’elle a produit en 2024 : le soleil ne brille pas la nuit.', 'Sources : publications Albioma, sept.-nov. 2026 · OER, chiffres clés 2024 (Port-Est : 211 MW, 1 162,5 GWh) · arrondis.'] },
      { titre: 'Les mégawatts à venir', texte: ['Ce qui se prépare.', 'Chantier engagé, Bois-Rouge : une chaudière doit y valoriser près de 70 000 t/an de combustibles issus des déchets (CSR). Mise en service annoncée fin 2026, à confirmer.', 'Jusqu’en 2043, Bois-Rouge : le contrat d’achat de l’électricité de la centrale est prolongé, au lieu de 2027.', 'Exploration, Piton des Neiges : Albioma détient un permis de recherche géothermique de 80 km² sous Salazie et Cilaos.', 'Concertation, Saint-Denis : projet Tanika, une station de pompage en eau de mer de 50 MW.', 'Au 1er janvier 2025, file d’attente : 131 MW de projets renouvelables attendaient leur raccordement au réseau.', 'Sources : Albioma (site La Réunion, 2026) · ThinkGeoEnergy, avr. 2024 · EDF Réunion (Tanika) · EDF SEI, bilan S3REnR au 01/01/2025.'] },
      { titre: 'Fin', texte: ['Installer des mégawatts : c’est la base.', 'Les avoir au bon moment : c’est le défi.', 'Les mégawatts de l’île.'] },
      { titre: 'Sources', texte: ['Puissances contractuelles au 31/12/2024. Chiffres arrondis.'] },
    ],
    sources: [
      'Observatoire Énergie Réunion — Bilan énergétique, chiffres clés 2024 (édition 2025)',
      'EDF SEI — Bilan prévisionnel La Réunion 2024 · Bilan technique et financier S3REnR au 01/01/2025',
      'Albioma — page La Réunion et brochure Solaire 2026 · publications Facebook, sept.-nov. 2026',
      'ThinkGeoEnergy — permis de recherche géothermique Albioma, avril 2024',
      'EDF Réunion — lettre « EDF & moi », juillet-décembre 2026 (projet Tanika)',
    ],
    verification: [
      'Le parc de 1 035 MW, les puissances par filière et les parts d’énergie 2024 ont été revérifiés dans le PDF de l’OER le 19/11/2026. Ils sont exacts (biomasse : 195,8 MW, arrondie à 196).',
      '« 63 % de la puissance dans sept centrales » : 651,4 MW sur 1 035, soit 62,9 % (recalcul de ce site).',
      'Les mises en service d’Albioma proviennent de publications de l’exploitant (niveau 2), non recoupées par une source institutionnelle.',
      'La file d’attente de 131 MW (S3REnR) et la superficie du permis géothermique (80 km²) n’ont pas été revérifiées par ce site.',
    ],
  },
];
