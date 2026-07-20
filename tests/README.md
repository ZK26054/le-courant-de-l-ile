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

## Politique zéro réseau

Tous les tests (`test_fetch_data.py`, `test_filieres.py`, `test_taxonomie_carbone.py`) tournent
**sans aucun accès réseau** : `requests.get` est patché pour servir `payload_edf.json` (page
`offset=0`) puis une page vide (`{"results": []}`) pour stopper la pagination de `_fetch_records`
sans boucle infinie. Voir la fixture pytest `mock_edf_api` dans `test_fetch_data.py`.
