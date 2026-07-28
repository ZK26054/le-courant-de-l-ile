# geo/ — Centroïdes communaux de La Réunion (974)

## `communes_974_centroides.json`

- **Source** : API découpage administratif [geo.api.gouv.fr](https://geo.api.gouv.fr)
  (Etalab / DINUM), endpoint :
  `https://geo.api.gouv.fr/departements/974/communes?fields=nom,code,centre&format=json&geometry=centre`
- **Récupéré le** : 2026-07-28.
- **Licence** : [Licence Ouverte / Open Licence 2.0 (Etalab)](https://www.etalab.gouv.fr/licence-ouverte-open-licence/).
- **Contenu** : 24 lignes (24 communes de La Réunion), champs `code` (INSEE, string
  `"974xx"`), `nom`, `lat`, `lon` (issus du GeoJSON `Point` `centre` = `[lon, lat]`,
  reprojeté ici en deux champs scalaires `lat`/`lon` pour un usage direct en `pandas`).
- **Nom exact de la propriété INSEE côté API** : `code` (pas `codeinseecommune` —
  ce nom-là est propre au registre EDF, voir `registre_installations.py`). La jointure
  entre les deux jeux de données se fait sur ces deux champs, comparés en **string**.

## Portée (invariant data-driven — voir ADR-003)

Cette table contient des **coordonnées**, mais ce sont des données de référence
cartographique administrative **publiques et sourcées**, à la **maille commune**
(24 centroïdes, un point par commune). Ce n'est **pas** un hardcode par installation :
V1 n'a aucune coordonnée de centrale saisie à la main, ni aucune identité de site
déduite. L'affectation installation → lieu reste pilotée à 100 % par l'API du
registre EDF via `codeinseecommune`. Voir `docs/adr/003-carte-installations-registre-communal.md`.

## Régénération

Si nécessaire (ex. évolution du découpage communal, fusion de communes) :

```bash
python -c "
import requests, json
r = requests.get('https://geo.api.gouv.fr/departements/974/communes',
                  params={'fields': 'nom,code,centre', 'format': 'json', 'geometry': 'centre'},
                  timeout=15)
r.raise_for_status()
rows = []
for d in r.json():
    lon, lat = d['centre']['coordinates']
    rows.append({'code': d['code'], 'nom': d['nom'], 'lat': lat, 'lon': lon})
rows.sort(key=lambda x: x['code'])
with open('geo/communes_974_centroides.json', 'w', encoding='utf-8', newline='\n') as f:
    json.dump(rows, f, ensure_ascii=False, indent=2)
    f.write('\n')
"
```
