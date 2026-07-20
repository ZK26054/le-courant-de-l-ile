# ADR 002 — Source unique de vérité pour la taxonomie des filières (`filieres.py`)

Date : 2026-07-18
Statut : Acceptée

## Contexte

`dashboard_reunion.py` et `agent_expert.py` dupliquaient chacun leur propre
définition de la taxonomie des filières électriques (`RENOUVELABLES`,
`THERMIQUES`, `COLORS`, `EMISSION_FACTORS`), avec des valeurs déjà
partiellement désynchronisées entre les deux fichiers.

Une investigation a par ailleurs établi que la nomenclature interne
(`Charbon`, `Diesel`) ne correspond plus à la réalité physique des centrales :
- **Bois-Rouge / Le Gol** ont achevé leur conversion à **100 % biomasse**
  en mars 2024 — la colonne `Charbon` désigne donc de la biomasse, pas du
  charbon fossile.
- **Port-Est** fonctionne au **bioliquide** (huile de colza, Saipol) depuis
  décembre 2023 — la colonne `Diesel` ne désigne plus du gazole/fioul fossile.
- **Éolien** est une donnée figée (~2,36 MW constant), non représentative du
  parc réel (Sainte-Suzanne, variable ; Sainte-Rose, démantelé).

Ce changement de nomenclature devait être répercuté à deux endroits qui
n'avaient jusqu'ici aucun lien de dépendance explicite, avec un risque
avéré de divergence silencieuse si chaque fichier était corrigé séparément.

## Décision

Créer un module `filieres.py`, socle **pur** (aucun import projet : ni
`streamlit`, ni `pandas`, ni `dashboard_reunion`, ni `agent_expert` — que des
littéraux Python), importé par les deux fichiers consommateurs. Il centralise :

- `LABELS` / `label()` : libellé humain affiché (ex. `Charbon` →
  « Biomasse (ex-Charbon) »), découplé de la clé Python interne.
- La taxonomie en 3 familles : `ENR_DIRECTES`, `BIOENERGIES` (groupe),
  `FOSSILE`, plus `AUTRES` (Stockage). Dérivées : `ENR_STRICT`,
  `ENR_REGLEMENTAIRE`, `TOUTES_FILIERES`.
- `COMBUSTION_THERMIQUE` : regroupement **physique** (centrales pilotables
  à combustion), volontairement distinct de `FOSSILE` (classement carbone),
  pour ne pas mélanger deux critères de regroupement différents.
- `EMISSION_FACTORS_LOW` / `EMISSION_FACTORS_HIGH` : facteurs d'émission en
  **fourchette** (et non plus une valeur unique), pour représenter
  honnêtement l'incertitude et le débat scientifique sur la neutralité
  carbone de la biomasse/bagasse.
- `COLORS` : palette Plotly partagée.

**Décision explicite : ne PAS renommer les clés Python internes**
(`Charbon`, `Diesel` restent des clés internes). Seul l'affichage change,
via `label()`. Renommer les clés aurait exigé de toucher `fetch_data`,
`COLORS` et tous les appels Plotly — surface de régression bien plus large
pour un bénéfice cosmétique, alors que le couplage `fetch_data` →
`API_TO_INTERNAL` → clés capitalisées est un invariant déjà prouvé stable
(13/13 tests `test_fetch_data.py`).

**Décision explicite : aucun alias `RENOUVELABLES`/`THERMIQUES` conservé.**
Chaque site d'appel doit choisir explicitement la bonne liste
(`ENR_STRICT`, `ENR_REGLEMENTAIRE`, `COMBUSTION_THERMIQUE`, etc.). Garder
un ancien nom en changeant sa valeur aurait produit une régression
silencieuse (code appelant `RENOUVELABLES` sans savoir que sa définition a
changé de périmètre).

## Conséquences

- `dashboard_reunion.py` expose désormais deux indicateurs %ENR distincts
  (`pct_ren_strict`, `pct_ren_reglementaire`) au lieu d'un seul `pct_ren`
  ambigu — impact sur `compute_kpis` et sur l'affichage des cartes KPI.
- `agent_expert.py` calcule une **fourchette** d'intensité carbone
  (`compute_carbon_intensity` renvoie un tuple `(low, high)`) au lieu d'une
  valeur ponctuelle trompeuse.
- Un test déterministe (`test_filieres.py`) garantit la cohérence interne du
  socle (mêmes clés dans `COLORS`/`LABELS`/facteurs, `LOW <= HIGH`,
  `ENR_STRICT ⊆ ENR_REGLEMENTAIRE`, pas de doublon, pas de valeur négative).
- Toute évolution future de la taxonomie (ex. ajout d'une filière) se fait
  en un seul endroit, avec un test qui rougit immédiatement en cas d'oubli
  dans l'un des dictionnaires.

## Alternatives rejetées

- **Dupliquer la correction dans les deux fichiers séparément** : rejeté,
  c'est exactement le problème à l'origine de cet ADR (désynchronisation
  déjà constatée).
- **Renommer les clés internes `Charbon`→`Biomasse`, `Diesel`→`Bioliquide`** :
  rejeté, régression de grande ampleur (fetch_data, COLORS, Plotly) pour un
  gain purement cosmétique déjà obtenu via `label()`.
- **Conserver `RENOUVELABLES`/`THERMIQUES` en changeant leur contenu** :
  rejeté, risque de régression silencieuse sur tout code appelant sans
  relire la nouvelle définition.
- **Un facteur d'émission carbone unique par filière** (comme avant) :
  rejeté, masque l'incertitude réelle et surestime artificiellement la
  précision de l'estimation (ce ne sont pas des chiffres officiels EDF).
