# ADR 003 — Carte des installations de production (registre EDF, maille communale)

Date : 2026-07-28
Statut : Acceptée

## Contexte

Le dashboard ne montre que le mix électrique **temps réel agrégé île entière**
(`prod-electricite-temps-reel-974`) : aucune vue géographique de l'implantation
du parc de production/stockage. EDF Open Data Réunion publie par ailleurs un
second jeu de données, le **registre national des installations de production
et de stockage d'électricité** (`registre-national-des-installations-de-
production-et-de-stockage-d-electricite-reunion`), qui liste 724 lignes brutes
(agrégées par lots), avec pour seule information de localisation le code INSEE
de la commune (`codeinseecommune`) et son nom (`commune`) — **aucune
coordonnée, aucun nom de site** (`nominstallation` = "Confidentiel" partout).

Re-sondage (2026-07-28) :
- Requête `group_by=codeinseecommune, commune, filiere` +
  `select=sum(puismaxinstallee) as p_kw, sum(nbinstallations) as n_inst`
  → **46 lignes** (commune × filière), sous le plafond de pagination →
  **un seul appel API**, 0 code INSEE manquant.
- `puismaxinstallee` est en **kW** (ex. 211000 = 211 MW).
- **`sum(nbinstallations)` (9878) ≠ `count(*)` (724)** : l'agrégation par lots
  est réelle, le second nombre sous-compte largement le parc réel.
- Filières du registre : Solaire, Hydraulique, Bioénergies, Thermique non
  renouvelable, Eolien, Stockage non hydraulique — nomenclature **différente**
  de celle du flux temps réel (`Photovoltaique`/`Charbon`/`Diesel`/…).

## Décision

### Deux flux de données séparés

1. **Installations** (dynamique) : requête group_by ci-dessus contre l'API
   registre, cache `@st.cache_data(ttl=REGISTRE_TTL_SECONDS)` avec un TTL
   **long** (24 h) — c'est un instantané administratif, pas un flux temps réel,
   distinct de `REFRESH_INTERVAL` (5 min) du dashboard principal.
2. **Géographie communale** (statique) : table de 24 centroïdes (un point par
   commune de La Réunion), bundlée dans `geo/communes_974_centroides.json`,
   régénérable depuis `geo.api.gouv.fr` (voir `geo/README.md`).

### Invariant data-driven (non-négociable)

**V1 n'a aucune coordonnée de centrale saisie à la main, ni aucune identité de
site déduite.** La table de centroïdes communaux (24 lignes, INSEE → lat/lon)
contient des coordonnées, mais ce sont des données de **référence
cartographique administrative publiques et sourcées**, à la **maille
commune** — ce n'est **pas** un hardcode par installation. L'affectation
installation → lieu reste **100 % pilotée par l'API** via
`codeinseecommune`. Si EDF ajoute, déplace ou retire une installation dans le
registre, la carte se met à jour sans toucher une seule ligne de code — seule
la liste des 24 communes (stable, administrative) est figée.

### Métrique et rendu

- Métrique principale : **puissance installée (MW) par commune**, dérivée de
  `sum(puismaxinstallee)` converti kW→MW une seule fois à la source.
- Métrique secondaire (hover) : nombre réel d'installations
  (`sum(nbinstallations)`, jamais `count(*)`) + détail du mix par filière.
- Rendu : **bulles proportionnelles** (aire ∝ MW, échelle **racine carrée**
  du rayon — pas linéaire, pour ne pas exagérer visuellement les écarts de
  puissance), couleur = filière dominante de la commune (palette locale au
  module, distincte de `filieres.COLORS`). **Pas de choroplèthe** : une
  choroplèthe déforme une quantité absolue (MW) par l'aire du territoire
  communal, qui n'a aucun rapport avec la puissance installée — c'est un biais
  de lecture classique (une petite commune très équipée serait écrasée
  visuellement par une grande commune peu équipée).
- Centroïdes = table précalculée bundlée. **Pas de `shapely`, pas de GeoJSON
  de polygones en V1** : une carte à bulles ne nécessite qu'un point par
  commune, pas un contour. Économie de dépendance et de poids de fichier pour
  un gain de fidélité nul à cette échelle (24 communes).

### Nouvel onglet

`🗺️ Carte`, en **2e position** (Dashboard, Carte, Agent expert, Diagnostic) —
avant l'agent expert, pour rester proche du dashboard temps réel dans le
parcours de lecture ; avant Diagnostic, outil de dépannage technique qui
reste en dernier.

### Module `registre_installations.py`

Fichier unique regroupant fetch, jointure, fabrique Plotly et rendu Streamlit
de l'onglet. **Un seul consommateur** (`dashboard_reunion.py`) → pas de
scission socle/UI comme pour `filieres.py`/`experts.py` (qui ont deux
consommateurs, `dashboard_reunion.py` ET `agent_expert.py` — voir ADR-002).
Palette `FILIERE_COLORS` **volontairement locale**, non fusionnée avec
`filieres.COLORS` : les deux jeux de données ont des nomenclatures de
filières différentes (`Photovoltaique` vs `Solaire`, pas de `Charbon`/`Diesel`
côté registre) — les fusionner créerait une fausse impression d'équivalence
entre deux classifications distinctes.

`filieres.py`, `experts.py`, `agent_expert.py` et `fetch_data`/le temps réel
ne sont **pas touchés** : fonctionnalité isolée, greffée sur `main()` par un
onglet et un import supplémentaires uniquement.

## Conséquences

- Un nouveau fichier de données bundlé (`geo/communes_974_centroides.json`,
  24 lignes) entre dans le dépôt : statique, sourcé, revu à chaque
  régénération volontaire (voir `geo/README.md`).
- Une nouvelle fixture de test figée (`tests/fixtures/payload_registre.json`,
  capturée le 2026-07-28) pour des tests hors réseau, sur le même modèle que
  `payload_edf.json` (voir `tests/README.md`).
- La palette `FILIERE_COLORS` doit être maintenue en cohérence avec les
  valeurs réelles de la colonne `filiere` du registre — un test dédié vérifie
  qu'aucune filière observée ne tombe dans le défaut gris silencieusement à
  l'insu de l'auteur (couverture des 6 valeurs connues).
- Si EDF enrichit un jour ce registre avec des coordonnées précises par
  installation, une V2 pourra migrer d'une maille communale à une maille
  fine, en remplaçant `joindre_centroides`/`make_bubble_map` — sans toucher
  au reste du dashboard, grâce à l'isolement du module.

## Alternatives rejetées

- **Choroplèthe (par commune, teintée selon la puissance)** : rejetée, déforme
  une quantité absolue par la surface du territoire (biais de lecture), et
  nécessiterait un GeoJSON de polygones (dépendance supplémentaire,
  `shapely`) pour un gain d'exactitude nul à l'échelle de 24 communes.
- **Déduire/nommer les centrales à partir de la puissance et de la commune**
  (ex. "211 MW à Bioénergies au Port ⇒ doit être Port-Est") : rejeté
  explicitement — c'est une déduction d'identité de site que le brief V1
  interdit. `nominstallation` = "Confidentiel" doit rester traité comme tel.
- **`shapely` + GeoJSON de polygones communaux dès la V1** : rejeté, complexité
  et poids disproportionnés pour un rendu à bulles qui ne nécessite qu'un
  centroïde par commune.
- **Fusionner `FILIERE_COLORS` avec `filieres.COLORS`** : rejeté, les deux
  jeux de données ont des nomenclatures de filières distinctes et non
  bijectives (le registre n'a pas de `Charbon`/`Diesel`, le flux temps réel
  n'a pas de `Solaire`/`Thermique non renouvelable`) — un mapping commun
  masquerait cette différence réelle plutôt que de la documenter.
- **`go.Scattermapbox`** : rejetée au profit de `go.Scattermap` (MapLibre GL,
  introduite en Plotly 5.24) — les deux traces existent en Plotly 6.9.0
  (vérifié), mais `Scattermap` est la voie que Plotly recommande désormais
  pour un rendu de carte sans jeton Mapbox, `Scattermapbox` étant maintenue
  en compatibilité mais legacy.
