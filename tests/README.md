# tests/ — fixtures de régression

## `fixtures/payload_edf.json`

- **Capturé le** : 2026-07-20.
- **Endpoint** : `https://opendata-reunion.edf.fr/api/explore/v2.1/catalog/datasets/prod-electricite-temps-reel-974/records`
- **Paramètres** : `limit=100&offset=0&order_by=date desc`.
- **Contenu** : payload brut EDF, structure `{"total_count": 288, "results": [...]}`, 100 lignes,
  12 colonnes minuscules (`date`, `jour`, `statut`, `total`, `photovoltaique`, `eolien`,
  `hydraulique`, `bioenergies`, `charbon`, `diesel`, `turbines_combustion`, `stockage`).
- **Pourquoi cette capture** : `turbines_combustion` est **négatif sur les 100 lignes**
  (entre -0,2598 et -0,1298 MW), `charbon`/`diesel` (Biomasse/Bioliquide) tournent à pleine
  charge (144-176 MW / 57-83 MW), `photovoltaique` varie de 3,7 à 81,9 MW (jour/nuit) —
  matière suffisante pour couvrir les cas négatifs, thermique actif et PV non nul.
- **⚠️ FIGÉ VOLONTAIREMENT.** Cette fixture ne doit **jamais** être régénérée sans raison
  explicite : l'API sert des données à statut « Estimé » qui sont *révisées* entre deux appels
  (voir CLAUDE.md, section API). Un test de régression déterministe doit comparer *au sein
  d'un même payload figé*, jamais contre un nouvel appel réseau. Si régénération nécessaire
  (ex. schéma API cassé), le faire consciemment et mettre à jour cette note (date, raison).

## `fixtures/payload_registre.json`

- **Capturé le** : 2026-07-28.
- **Endpoint** : `https://opendata-reunion.edf.fr/api/explore/v2.1/catalog/datasets/registre-national-des-installations-de-production-et-de-stockage-d-electricite-reunion/records`
- **Paramètres** : `select=codeinseecommune, commune, filiere, sum(puismaxinstallee) as p_kw,
  sum(nbinstallations) as n_inst` + `group_by=codeinseecommune, commune, filiere` +
  `order_by=p_kw desc` + `limit=100`.
- **Contenu** : `{"total_count": 46, "results": [...]}`, 46 lignes (commune × filière), déjà
  sous le plafond de pagination → capturé en un seul appel. `codeinseecommune` toujours
  renseigné (0 ligne exclue dans cette capture — les tests d'exclusion de code INSEE vide
  utilisent des lignes synthétiques, pas cette fixture). `p_kw` en kW (ex. 211000 = 211 MW),
  total agrégé île entière ≈ 1200,7 MW, `sum(n_inst)` = 9878 (≠ `count(*)` = 724 lignes brutes
  du registre non groupé — l'agrégation par lots est réelle, voir CLAUDE.md et ADR-003).
- **Pourquoi cette capture** : matière suffisante pour couvrir la conversion kW→MW, l'écart
  `sum(nbinstallations)` vs `count(*)`, et une jointure réelle 24/24 communes avec
  `geo/communes_974_centroides.json` (aucun orphelin des deux côtés dans les données réelles —
  les cas orphelins sont testés séparément avec des données synthétiques, voir
  `test_registre_installations.py`).
- **⚠️ FIGÉ VOLONTAIREMENT** — registre administratif (pas de statut "Estimé" comme le flux
  temps réel, mais même principe de prudence : ne pas régénérer sans raison explicite, pour
  garder des tests reproductibles).

## Politique zéro réseau

Tous les tests (`test_fetch_data.py`, `test_filieres.py`, `test_taxonomie_carbone.py`,
`test_registre_installations.py`) tournent **sans aucun accès réseau** : `requests.get` est
patché pour servir `payload_edf.json`/`payload_registre.json` (page `offset=0`) puis une page
vide (`{"results": []}`) pour stopper la pagination sans boucle infinie. Voir la fixture pytest
`mock_edf_api` dans `test_fetch_data.py` et les doubles dédiés dans `test_registre_installations.py`.
