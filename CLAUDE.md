# CLAUDE.md — Dashboard Mix Électrique La Réunion

> Mémoire projet persistante. Lire ce fichier au début de chaque session.
> **Ce fichier décrit le réel, pas la cible.** Toute section démentie par une preuve
> (re-probe, test) doit être corrigée ici *avant* de coder par-dessus.
> Dernier recalage sur preuve : **2026-07-18**.

## Objectif
Dashboard temps réel du mix électrique de La Réunion (Open Data EDF Réunion), enrichi d'agents experts (Claude) qui analysent les données live sous plusieurs angles : électrotechnique, climat, juridique transition énergétique. Phase 0 (ingestion), Phase 1 (contexte enrichi) et Phase 1.5 (reclassement nomenclature/carbone) **livrées et validées**. Prochaine étape : **Phase 4** (git + fixture de régression sur le modèle corrigé), puis Phase 2 (nouveaux experts).

## Stack
Python · Streamlit · Plotly · pandas · requests · anthropic · streamlit-autorefresh.

## Architecture des fichiers
- `dashboard_reunion.py` — app principale, **3 onglets** (`st.tabs`) : Dashboard (`render_dashboard`), Agent expert (`agent_expert.render_agent_tab`), Diagnostic (`render_diagnostic`). Contient `API_URLS`, `fetch_data`, `_fetch_records`, `compute_kpis`, les fabriques Plotly (`make_stacked_area`, `make_total_line`, `make_renewables_pct`, `make_thermal_lines`). Importe la taxonomie depuis `filieres.py`.
- `agent_expert.py` — agents experts Claude (dégelé, intégré). `SYSTEM_PROMPT` multi-expertise, `build_data_context` (contexte live enrichi : instantané, tendance 1h, amplitude, double %ENR, fourchette carbone), `compute_carbon_intensity` (retourne un couple `(low, high)`), `ask_expert`, `render_agent_tab`. Couplage lâche : reçoit `df`/`kpis`, ne manipule que les noms internes capitalisés. Importe la taxonomie depuis `filieres.py`.
- `filieres.py` — **SOURCE UNIQUE DE VÉRITÉ** (voir invariant n°7) : taxonomie 3 familles, `EMISSION_FACTORS_LOW/HIGH`, `DISPLAY_LABELS`/`label()`, `COLORS`. Socle pur, aucun import projet. Importé par les deux fichiers ci-dessus.
- `test_fetch_data.py` (13 tests, ingestion) · `test_filieres.py` (7 tests, taxonomie/facteurs).
- `docs/adr/002-source-unique-taxonomie-filieres.md` — ADR de la source unique.
- `requirements.txt` — dépendances épinglées en `==`.
- `prod-electricite-temps-reel-974.csv` — échantillon de données local.
- `.claude/agents/` — équipe de sous-agents de développement (voir plus bas).

## API EDF — points critiques (re-sondés le 2026-07-17)

> ⚠️ Les faits ci-dessous ont été **prouvés par re-probe indépendant**. Ils remplacent
> une version antérieure de ce fichier qui affirmait l'inverse et a induit les agents en erreur.

- **Seul endpoint valide** :
  `https://opendata-reunion.edf.fr/api/explore/v2.1/catalog/datasets/prod-electricite-temps-reel-974/records`
- **`/api/v1/.../lines` est MORT → 404.** Tout le namespace `/api/v1` a disparu. Ne jamais le réintroduire, quel que soit le slug.
- **Paramètres** : `limit` (nb de lignes) + `order_by=date desc`.
  Le champ de tri est **`date` en MINUSCULE**. `order_by=Date DESC` → **HTTP 400**
  (*« Impossible de trier sur le champ Date, il n'existe pas »*).
- **`limit` est plafonné à 100.** `limit=101` → **HTTP 400** (*« limit should be less than 100 »*),
  et le corps d'erreur est en **`text/plain`**, pas en JSON → un `.json()` naïf lève `JSONDecodeError`.
  Au-delà de 100 lignes, paginer via `offset` (voir `_fetch_records`).
- **Doublons** : l'API sert des lignes de date identique, strictement égales sur les 12 colonnes.
  Dédoublonnage sur `Date` — vérifié : aucune perte de donnée réelle.
- **Trous de données à la source** : certains timestamps 5 min sont absents côté EDF
  (`total_count: 0`) — ce sont de vrais trous, pas un bug d'ingestion.
- **⚠️ Données à statut « Estimé » → tester sur un PAYLOAD UNIQUE.** L'API re-sert la même
  minute avec des valeurs *révisées* entre deux appels (le `statut` vaut « Estimé »).
  Conséquence méthodologique **prouvée le 2026-07-17** : comparer la sortie de `fetch_data`
  à un *second* appel API produit de **faux négatifs** (écarts Hydraulique 68.97 vs 40.24…
  purement dus à la fraîcheur, pas au code). Un test fiable **capture un seul payload** et
  le fait traverser `fetch_data` via `requests.get` patché, puis compare à ce même payload.
  Preuve de mapping ainsi obtenue : **0 discordance sur 873 cellules** (97 lignes × 9 filières),
  8 filières exactes vs API brut, accent `bioenergies`→`Bioénergies` inclus.
  → Le test de régression déterministe de la Phase 4 doit s'appuyer sur une **fixture JSON figée**,
  jamais sur un appel réseau live (validé).
- **Réponse** : `{"total_count": …, "results": [...]}`. Les lignes sont dans `results`
  (le compteur est `total_count`, **pas** `total` — `total` est une colonne de données).
- **Schéma réel = 12 colonnes, toutes en minuscules** :
  `date`, `jour`, `statut`, `total`, `photovoltaique`, `eolien`, `hydraulique`,
  `bioenergies`, `charbon`, `diesel`, `turbines_combustion`, `stockage`.
  Aucun libellé du type `Photovoltaïque (MW)` : ce format n'existe pas dans cette API.
- **Mapping casse** : l'API est en minuscules, les noms internes (clés de `COLORS`) sont
  capitalisés. La conversion est **insensible à la casse et localisée dans `fetch_data`
  uniquement** — le reste du code ne voit que les noms internes.
- **Valeurs négatives possibles** sur `turbines_combustion` et `stockage`
  (observé : `turbines_combustion = -0.3398`). Traiter défensivement — ne jamais supposer ≥ 0.
- **`total` est la somme ALGÉBRIQUE des 8 filières** (négatifs compris) — vérifié sur 100 lignes :
  écart max **0,001 MW** en algébrique, contre **0,2306 MW** avec un `clip(lower=0)`.
  ⚠️ **Ne jamais clipper les négatifs** : ça masque une donnée physiquement réelle
  (stockage négatif = charge) *et* ça casse la cohérence avec `total`.

### Filières — taxonomie 3 familles (recalée sur preuve le 2026-07-18)

> ⚠️ **Les clés API `charbon` et `diesel` sont des libellés HÉRITÉS trompeurs.** Le schéma
> de champs officiel du portail EDF (payload Nuxt, vérifié en source primaire) les renomme :
> - `charbon` → titre EDF **« Biomasse (MW) »** (`x-originalName` = « Charbon »).
> - `diesel`  → titre EDF **« Bioliquide (MW) »** (`x-originalName` = « Diesel »).
>
> **Il n'y a plus de charbon fossile à La Réunion depuis fin 2023** (Bois-Rouge/Le Gol 100 %
> biomasse — pellets bois + bagasse — depuis mars 2024, autorisation CRE 2022, −84 % émissions
> vs charbon / étude Deloitte). **Le « diesel » = huile de colza** (Port-Est, EDF PEI, fournisseur
> Saipol, sans palme ni soja, depuis déc. 2023). `turbines_combustion` reste **fossile** (libellé
> EDF « Turbines à combustion », non renommé). Les **clés Python internes restent** `Charbon`/`Diesel`
> (couplage `fetch_data`/`COLORS`/Plotly) — seul l'AFFICHAGE passe par `label()`.

- **ENR directes** (sans combustion, incontestables) : Photovoltaique, Eolien, Hydraulique.
- **Bioénergies** (ENR au sens réglementaire/OER, neutralité carbone DÉBATTUE) : Bioénergies,
  Charbon (= Biomasse ex-charbon), Diesel (= Bioliquide ex-diesel).
- **Fossile** : Turbines_combustion.
- **Autre** : Stockage, Total.
- **Double %ENR** (jamais l'un sans l'autre) : *strict* = directes / total ; *réglementaire* =
  (directes + bioénergies) / total ≈ **90 %+**. L'écart est l'information : ~84 % du réglementaire
  vient de centrales à combustion bio-étiquetées → ne pas présenter le 90 % seul comme « autonomie ».
- **Facteurs d'émission = FOURCHETTE** (`EMISSION_FACTORS_LOW/HIGH`, ESTIMATIONS) : Biomasse ex-Charbon
  200/230, Bioliquide ex-Diesel 30/150, Bioénergies 35/150, Turbines_combustion 700, ENR directes 0.
  `compute_carbon_intensity` retourne un couple `(low, high)`. Ordre de grandeur mix : ~68-145 gCO₂/kWh.
- ⚠️ **`eolien` est une DONNÉE FIGÉE** : constant à **2,3598 MW** sur 388 mesures / 35h (prouvé),
  cardinalité 1. Le vrai parc (Sainte-Suzanne 19,8 MW, variable) produit ~4 MW moyen ; Sainte-Rose
  démantelé 2023. Le flux API ne reflète PAS la réalité. Compté dans `total` (donc dans %ENR, biais
  fixe +0,78 pt) mais **badgé « donnée figée »** dans l'UI et le contexte agent ; garde-fou prompt :
  l'agent ne commente jamais de dynamique éolienne.
- **Limite épistémique** : les libellés Biomasse/Bioliquide sont *déclaratifs* d'EDF — ils n'attestent
  pas 100 % biogénique à chaque instant (démarrage/incident/appoint fossile résiduel possible).

## Invariants non-négociables
1. **Aucun secret en dur.** Clé API Anthropic via `st.secrets["ANTHROPIC_API_KEY"]` ou saisie runtime. `.streamlit/secrets.toml`, `.env`, `.venv` dans `.gitignore`.
2. **Jamais de `time.sleep()` + `st.rerun()` bloquant.** L'auto-refresh passe par `streamlit-autorefresh` (préserve `session_state`, donc le chat).
3. **Dégradation propre** partout : API down / données vides / clé absente → message clair, jamais de crash brut.
4. **Preuve, pas déclaration** : aucun fix n'est clos sur un message de succès. Test qui échoue avant / passe après, ou re-probe indépendant. (Méthodologie de travail centrale.) **Corollaire API « Estimé »** : une preuve sur données live compare toujours *au sein d'un payload unique* — jamais deux appels séparés (voir section API). Régression déterministe = fixture JSON figée.
5. **Facteurs d'émission = estimations** (en FOURCHETTE bas/haut), pas des chiffres officiels EDF. La neutralité carbone de la biomasse/bagasse/bioliquide est débattue → toujours le préciser.
6. **Dépendances épinglées** en `==` dans `requirements.txt`.
7. **Source unique de vérité filières.** Toute liste de filières (`ENR_DIRECTES`, `BIOENERGIES`, `FOSSILE`, `COMBUSTION_THERMIQUE`), la palette `COLORS`, les `DISPLAY_LABELS` et les `EMISSION_FACTORS_LOW/HIGH` vivent **exclusivement** dans `filieres.py`. `dashboard_reunion.py` et `agent_expert.py` les **importent**, ne les redéfinissent jamais localement — ni copie, ni alias masquant une valeur différente sous un nom identique. `filieres.py` n'importe aucun module projet (socle). Vérifié par `test_filieres.py` + grep de non-régression.

## Faits de référence — système électrique réunionnais
- La Réunion = **ZNI** (Zone Non Interconnectée) : réseau insulaire isolé, faible inertie, stabilité 50 Hz critique.
- Plafond d'injection instantanée PV+éolien ~30 % (arrêté 23 avril 2008), assoupli via stockage.
- Objectif **autonomie énergétique 2030** (100 % électricité renouvelable), loi outre-mer.
- Centrales : **Port-Est** (EDF PEI, converti au **bioliquide huile de colza** déc. 2023, plus de fioul), **Bois-Rouge & Le Gol** (Albioma, conversion **100 % biomasse achevée mars 2024**, plus de charbon), turbines à combustion (fossile, pointe), hydraulique (Rivière de l'Est, Takamaka). Parc **éolien** : Sainte-Suzanne 19,8 MW (repowering TotalEnergies), Sainte-Rose démantelé 2023.
- Ordre de grandeur utile pour valider un KPI : production totale instantanée **≈ 340 MW**
  (mesuré le 2026-07-17). Un `Total = 0` est un **bug**, pas une donnée.

## Équipe de sous-agents (.claude/agents/)
- **architecte-energie** — cadre, décide, découpe, ADR. Ne code pas.
- **concepteur-experts** — conçoit/calibre les personas experts. Travaille dans `agent_expert.py` (gelé).
- **dev-rapports** — moteur de rapports horodatés (HTML/PDF).
- **dev-features** — implémentation Streamlit/Plotly/ingestion au quotidien.
- **gardien-qualite** — sécurité + tests + validation par preuve. Obligatoire avant commit.

## Workflow
Deux-Claude : le chat web = COO (stratégie, brief, validation de diff, interprétation). Claude Code + sous-agents = exécution. L'architecte oriente vers le bon sous-agent selon la tâche.

## Commandes
```bash
pip install -r requirements.txt        # dépendances
streamlit run dashboard_reunion.py     # lancer
python -m py_compile *.py              # vérif compilation
pytest                                 # tests (à mettre en place)
```

## État actuel — Ingestion ✅ RÉPARÉE ET VALIDÉE (2026-07-17)

L'audit initial avait refusé la Phase 0 : le dashboard n'affichait **aucune donnée**
(2 bugs cumulés — endpoint 404 + `order_by="Date DESC"` → 400 ; puis normalisation
casse-sensible écrasant tous les KPI à `0.0`). **Les deux sont corrigés et prouvés.**

Preuves indépendantes (triple mesure : `dev-features`, `gardien-qualite`, puis vérif directe) :
- ✅ **KPI non nuls** : `Total = 389.339 MW`, `pct_ren = 32.6 %`, `Bioénergies = 51.748`
  (le piège de l'accent `bioenergies` → `Bioénergies` est traité). Attendu : `Total ≈ 340-390 MW`.
- ✅ **Test de régression** : `test_fetch_data.py` — **13/13 passés**, les 2 bugs d'origine
  reconstitués échouent bien avant / passent après. Rejouable :
  `./.venv/Scripts/python.exe -m pytest test_fetch_data.py -q`
- ✅ **Invariant n°2** : `time.sleep`/`st.rerun` supprimés, `st_autorefresh` en place.
- ✅ `requirements.txt` épinglé en `==` (+ `anthropic`, `streamlit-autorefresh`).
- ✅ Négatifs préservés (min `-0.3398`), dégradation propre vérifiée (API KO → pas de crash).
- ✅ Aucun secret en dur. `streamlit run` → HTTP 200.

### Dette connue (non bloquante, à traiter)
- ⚠️ **Dérive de pagination** : ~1 ligne réelle sautée par fetch. Le jeu est une fenêtre
  glissante élaguée (`total_count` 300 → 294 en cours de session) : l'`offset` dérive entre
  les pages. Sans impact KPI (`iloc[-1]` = ligne la plus récente), trou de 5 min sur les courbes.
- ⚠️ **Injection HTML** : `statut` (contrôlé par l'API) est injecté dans
  `st.markdown(..., unsafe_allow_html=True)` sans échappement. Faible sévérité (exige EDF
  compromis) mais c'est une entrée non maîtrisée → à échapper.
- `pytest` installé dans `.venv` mais **absent de `requirements.txt`**.
- `use_container_width` déprécié (4 occurrences) → migrer vers `width='stretch'`.
- Imports morts préexistants : `plotly.express as px`, `datetime`.
- **Pas de `.gitignore`** et projet non-git. À créer **avant** tout `git init`, sinon
  l'invariant n°1 n'a aucun garde-fou.

## État actuel — Phases 0 / 1 / 1.5 ✅ LIVRÉES (2026-07-18)

- **Phase 0** (ingestion) : `fetch_data` prouvé vert (endpoint v2.1, mapping casse, négatifs). Test live agent : chaîne verte, clé + modèle `claude-sonnet-5` valides sur le compte ; seul bloquant = **crédits Anthropic** (administratif, pas technique).
- **Phase 1** (contexte enrichi) : `build_data_context` étendu (tendance 1h, amplitude, % par filière). Piège `pct_ren` (absent du df) contourné.
- **Phase 1.5** (reclassement) : taxonomie 3 familles + double %ENR + libellés `ex-Charbon`/`ex-Diesel` + fourchette carbone, dans **`filieres.py`** (source unique, invariant n°7). Prouvé : 20 tests verts (13 fetch + 7 filieres), anti-dup et anti-cycle vérifiés, carbone chuté ~494 → **68-145 gCO₂/kWh**, %ENR réglementaire ~99 %, badge éolien + garde-fou prompt en place.
- App **3 onglets** (`st.tabs`) fonctionnelle, `streamlit run` → HTTP 200.

### Dette connue (non bloquante)
- ⚠️ **Dérive de pagination** : ~1 ligne réelle sautée par fetch (fenêtre glissante). Sans impact KPI (`iloc[-1]`), trou de 5 min sur les courbes.
- ⚠️ **Injection HTML** : `statut` (contrôlé par l'API) dans `st.markdown(..., unsafe_allow_html=True)` sans échappement. Faible sévérité → à échapper.
- ⚠️ **`diesel`/Bioliquide** = point carbone le plus incertain (colza : combustion biogénique mais amont N₂O/transport/ILUC) → fourchette large 30/150, à affiner si source CRE/EDF trouvée.
- `pytest` absent de `requirements.txt`. `use_container_width` déprécié (occurrences). Imports morts préexistants (`plotly.express`, `datetime`).

### Prochaine étape : Phase 4
`git init` propre (`.gitignore` déjà prêt et éprouvé : `secrets.toml` hors-git prouvé par `git check-ignore`) + **fixture JSON figée** pour la régression déterministe (sur le modèle corrigé Phase 1.5, jamais sur appel réseau live — voir section API « Estimé »). Puis Phase 2 (nouveaux experts).
