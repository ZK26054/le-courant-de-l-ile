# Ligne éditoriale — « Le courant de l’île »

Ce fichier n’est pas publié (il est exclu de la collection `articles`). Il fixe les règles que **tout article** doit respecter avant de passer en `draft: false`.

## 1. Sources

- **Tout chiffre repose sur une source de niveau 1** (institution : OER, EDF SEI, CRE, État, Assemblée nationale, open data EDF) dès qu’elle existe.
- Une source de **niveau 2** (exploitant, porteur de projet : Albioma, EDF PEI, Hydro Tanika…) est toujours **attribuée** dans le texte : « selon Albioma… ».
- Une source de **niveau 3** (presse, OpenStreetMap, base de données) ne fonde jamais seule un chiffre clé. Si c’est la seule disponible, l’article le dit.
- Chaque source est **numérotée** dans le texte (appel `[1]`) et listée en bas de page avec son titre, son éditeur, sa date et son lien.

## 2. Dates

- **Toujours dater les chiffres** : « 92,4 % d’électricité renouvelable **en 2024** (OER) ».
- Ne jamais présenter un instantané (« 99 % ce soir ») comme une moyenne annuelle.
- Le champ `derniere_verification` donne la date à laquelle tous les chiffres de l’article ont été revérifiés.

## 3. Neutralité

- Les positions des acteurs sont **rapportées sans prendre parti**. Exemple : EDF parle d’un « mix essentiellement renouvelable » ; ses critiques parlent d’une dépendance « déplacée » vers les importations de colza et de granulés. Les deux sont présentées avec leurs chiffres.
- Pas d’adjectifs militants, pas de verdict politique. Les faits, leurs limites, et ce qui reste inconnu.

## 4. Vocabulaire

- « Renouvelable » (92,4 % en 2024) et « local » (31,2 % en 2024) ne sont pas synonymes.
- « Biomasse (ex-Charbon) » et « Bioliquide (ex-Diesel) » : les centrales ne brûlent plus de charbon ni de fioul ; seules les colonnes de données gardent les anciens noms.
- Aucune STEP n’est en service à La Réunion : Tanika est un **projet** (mise en service visée en 2033 selon le porteur).
- Intensité carbone : citer la valeur officielle (77 gCO₂/kWh en 2024, émissions directes, OER) et préciser la convention (biomasse comptée à zéro).

## 5. Images

- Seules les images déclarées dans `src/data/images.json` avec une licence autorisée (CC0, CC BY, CC BY-SA, domaine public, autorisation écrite enregistrée) peuvent être utilisées. Le build échoue sinon.

## 6. Publication

- Un article est publié quand son fichier passe en `draft: false`. Tant qu’aucun article n’est publié, la page `/articles` affiche « Premiers articles bientôt ».
- Les textes sont fournis par le COO. Aucun article n’est rédigé automatiquement.

Modèle de fichier : `_gabarit.md` (non publié).
