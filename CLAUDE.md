# CLAUDE.md — Dashboard Mix Électrique La Réunion

> Mémoire projet persistante. Lire ce fichier au début de chaque session.
> **Ce fichier décrit le réel, pas la cible.** Toute section démentie par une preuve
> (re-probe, test) doit être corrigée ici *avant* de coder par-dessus.
> Dernier recalage sur preuve : **2026-07-18**.

## Objectif
Dashboard temps réel du mix électrique de La Réunion (Open Data EDF Réunion), enrichi d'agents experts (Claude) qui analysent les données live sous plusieurs angles : électrotechnique, climat, juridique transition énergétique, **souveraineté/résilience**, et d'une **carte des installations** à la maille communale (registre EDF). Phases 0 (ingestion), 1 (contexte enrichi), 1.5 (reclassement nomenclature/carbone), 4 (git + fixture de régression), 1.75 (sprint dette : XSS, `width`, pagination curseur), **2 (expert souveraineté + sélecteur d'expert)** et **Carte installations V1 (registre, maille communale)** **livrées et validées** (Phase 2 : validation live des réponses en attente de crédits Anthropic). Prochaine étape possible : autres experts (économie ZNI, réseau/smart-grid, prospective 2040).

## Stack
Python · Streamlit · Plotly · pandas · requests · anthropic · streamlit-autorefresh.

## Architecture des fichiers
- `dashboard_reunion.py` — app principale, **4 onglets** (`st.tabs`) : Dashboard (`render_dashboard`), Carte (`registre_installations.render_carte_tab`, 2e position), Agent expert (`agent_expert.render_agent_tab`), Diagnostic (`render_diagnostic`). Contient `API_URLS`, `fetch_data`, `_fetch_records`, `compute_kpis`, les fabriques Plotly (`make_stacked_area`, `make_total_line`, `make_renewables_pct`, `make_thermal_lines`). Importe la taxonomie depuis `filieres.py`.
- `agent_expert.py` — intégration agent Claude. `build_data_context` (contexte live enrichi : instantané, tendance 1h, amplitude, double %ENR, fourchette carbone), `compute_carbon_intensity` (retourne un couple `(low, high)`), `ask_expert(messages, api_key, data_context, system_prompt)` (le prompt est passé explicitement — plus de `SYSTEM_PROMPT` monolithique), `render_agent_tab` (avec **sélecteur d'expert** `st.selectbox`, reset de l'historique au changement de persona). Couplage lâche : reçoit `df`/`kpis`, ne manipule que les noms internes capitalisés. Importe la taxonomie depuis `filieres.py`, les personas depuis `experts.py`.
- `experts.py` — **SOCLE CONTENU** (personas, miroir de `filieres.py`) : `BASE_PROMPT` (posture + garde-fous éolien & limite épistémique biomasse/bioliquide, communs à TOUTES les personas), `DOMAINE_*` (électrotechnique, climat, juridique, **souveraineté/résilience**), `EXPERTS = {"generaliste", "souverainete", …}`. Texte pur, aucun import projet, aucune donnée filière (invariant n°7).
- `filieres.py` — **SOURCE UNIQUE DE VÉRITÉ** (voir invariant n°7) : taxonomie 3 familles, `EMISSION_FACTORS_LOW/HIGH`, `DISPLAY_LABELS`/`label()`, `COLORS`. Socle pur, aucun import projet. Importé par les deux fichiers ci-dessus. **Non touché** par la Carte installations (registre) — voir ADR-003, nomenclature de filières différente.
- `registre_installations.py` — **module ISOLÉ** (voir `docs/adr/003-*.md`), un seul consommateur (`dashboard_reunion.py`) : `fetch_registre_par_commune_filiere` (registre EDF agrégé commune×filière, kW→MW, cache TTL long), `load_centroides`/`joindre_centroides` (jointure sur `codeinseecommune` string strict), `make_bubble_map` (`go.Scattermap`, bulles ∝ MW échelle racine carrée), `render_carte_tab` (LAZY, dégradation locale). Palette `FILIERE_COLORS` locale, non fusionnée avec `filieres.COLORS` (nomenclature différente : Solaire/Thermique non renouvelable/etc., pas de Charbon/Diesel).
- `geo/communes_974_centroides.json` + `geo/README.md` — 24 centroïdes communaux (INSEE→lat/lon), source `geo.api.gouv.fr` (Etalab), donnée de référence administrative publique, **pas** un hardcode par installation (voir invariant data-driven ADR-003).
- **Tests — 62 au total, tous déterministes et HORS RÉSEAU** (fixtures figées, `anthropic` mocké) :
  `test_fetch_data.py` (18, ingestion + pagination curseur + échappement XSS) ·
  `test_filieres.py` (7, taxonomie/facteurs) · `test_taxonomie_carbone.py` (3, fige le modèle Phase 1.5) ·
  `test_experts.py` (14, personas + garde-fous transverses + ancrage dates sourcées + transmission du bon prompt) ·
  `test_registre_installations.py` (20, centroïdes/fetch kW→MW/`sum(nbinstallations)`≠`count(*)`/jointure/carte à bulles/`AppTest`).
  `fixture_utils.py` — doubles de test partagés (flux temps réel) · `tests/fixtures/payload_edf.json` — payload EDF **figé volontairement** (ne pas régénérer sans raison) · `tests/fixtures/payload_registre.json` — payload registre **figé volontairement** (capturé 2026-07-28, voir tests/README.md).
- `docs/sources/SOURCE_bilan-previsionnel-2024.md` — **source primaire** (Bilan Prévisionnel EDF SEI 2024), référence factuelle de l'expert souveraineté.
- `docs/adr/002-source-unique-taxonomie-filieres.md` — ADR de la source unique (filières temps réel).
- `docs/adr/003-carte-installations-registre-communal.md` — ADR de la carte des installations (registre, maille communale).
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
  Au-delà de 100 lignes, paginer via **CURSEUR** (`where=date < '<date la plus ancienne reçue>'`),
  **pas** via `offset` — voir `_fetch_records`. ⚠️ L'`offset` est piégeux ici : le jeu est une
  **fenêtre glissante élaguée** (de nouvelles lignes arrivent en tête, d'anciennes sont supprimées
  en queue pendant la pagination), donc l'`offset` désigne une ligne différente d'une page à l'autre
  → ~1 ligne réelle sautée par fetch (bug corrigé en Phase 1.75). Le curseur est ancré sur une
  **donnée**, pas sur une position : il est insensible au glissement.
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
> **Il n'y a plus de charbon fossile à La Réunion** (Bois-Rouge/Le Gol 100 % biomasse — pellets
> bois + bagasse ; autorisation CRE 2022, −84 % émissions vs charbon / étude Deloitte).
> **Le « diesel » = huile de colza** (Port-Est, EDF PEI, fournisseur Saipol, sans palme ni soja).
> `turbines_combustion` reste **fossile** (libellé EDF « Turbines à combustion », non renommé) :
> ce sont les **TAC de La Baie (80 MW, GNR) + TAC Sud (41 MW)**. Les **clés Python internes restent**
> `Charbon`/`Diesel` (couplage `fetch_data`/`COLORS`/Plotly) — seul l'AFFICHAGE passe par `label()`.
>
> 📅 **Dates exactes (recalées sur source primaire EDF SEI, 2026-07-20)** — voir
> `docs/sources/SOURCE_bilan-previsionnel-2024.md` : Port-Est converti **oct. 2023** ;
> Bois-Rouge tranche 2 en 2022, tranches 1.1/1.2 mi-2023 ; **Le Gol A.1/A.2 finalisées
> fév. et juil. 2024** → la conversion de TOUT le parc charbon/fioul est achevée **mi-2024**
> (et non « mars 2024 », correction d'une version antérieure de ce fichier).

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
   **Corollaire « filet décoratif » (leçon Phase 4, 2026-07-20)** : *un test qui reconstitue la fonction ≠ un test de la vraie fonction de prod.* Un test doit **importer et exercer le code de production réel**, pas une copie recollée dans le fichier de test. Découvert en dur : `test_AVANT_bug1/bug2` validaient une copie locale et n'auraient **jamais** attrapé une régression réelle du `order_by` de `_fetch_records` — le filet était décoratif sur ce point depuis la Phase 0, sans qu'on le sache. **Prouver qu'un test ROUGIT quand on casse volontairement le code est le seul moyen de savoir s'il teste vraiment quelque chose.** Même famille que : « fichier créé ≠ migration appliquée », « déployé ≠ prouvé ».
5. **Facteurs d'émission = estimations** (en FOURCHETTE bas/haut), pas des chiffres officiels EDF. La neutralité carbone de la biomasse/bagasse/bioliquide est débattue → toujours le préciser.
6. **Dépendances épinglées** en `==` dans `requirements.txt`.
7. **Source unique de vérité filières.** Toute liste de filières (`ENR_DIRECTES`, `BIOENERGIES`, `FOSSILE`, `COMBUSTION_THERMIQUE`), la palette `COLORS`, les `DISPLAY_LABELS` et les `EMISSION_FACTORS_LOW/HIGH` vivent **exclusivement** dans `filieres.py`. `dashboard_reunion.py` et `agent_expert.py` les **importent**, ne les redéfinissent jamais localement — ni copie, ni alias masquant une valeur différente sous un nom identique. `filieres.py` n'importe aucun module projet (socle). Vérifié par `test_filieres.py` + grep de non-régression.

## Faits de référence — système électrique réunionnais
- La Réunion = **ZNI** (Zone Non Interconnectée) : réseau insulaire isolé, faible inertie, stabilité 50 Hz critique.
- Plafond d'injection instantanée PV+éolien ~30 % (arrêté 23 avril 2008), assoupli via stockage.
- Objectif **autonomie énergétique 2030** (100 % électricité renouvelable), loi outre-mer.
- **Parc au 01/07/2024 = 563 MW** (source primaire EDF SEI) : bioénergie pilotable ~**415 MW** (l'ossature) · hydraulique **136 MW** (Rivière de l'Est 80, Takamaka I+II 43,4) · PV **210 MWc** · éolien (Perrière 8,8 MW après repowering partiel ; Sainte-Rose 0 MW, travaux jusqu'en 2026) · stockage batterie (Batrun 5 MW, Cratère 5 MW/10 MWh — **pas de STEP opérationnelle documentée**).
- Centrales : **Port-Est** (EDF PEI, 211 MW, **bioliquide huile de colza** depuis oct. 2023, ≈40 % des besoins), **Bois-Rouge** (94,1 MW) **& Le Gol** (~105 MW) — Albioma, biomasse + bagasse, conversion du parc achevée **mi-2024** ; **TAC La Baie 80 MW (GNR) + TAC Sud 41 MW = seul fossile** ; groupes de secours 24 MW maintenus.
- **Chiffres ENR ANNUELS officiels** (≠ instantané du dashboard) : **57 % en 2023**, en hausse depuis les conversions. Non-synchrone (PV+éolien) 2023 : dépassait rarement 40 % instantané, ~11 % de la conso annuelle. ⚠️ Ne jamais présenter un instantané (« 99 % ce soir ») comme la performance annuelle de l'île.
- **Souveraineté** : le bioliquide est du **colza importé d'Europe** (Saipol, RED), la biomasse repose sur des **pellets importés** ; la bagasse locale ne couvre que la saison sucrière (~201 GWh sur 923 en 2023). La dépendance au fioul a été **déplacée**, pas supprimée.
- **Vulnérabilités** (constats EDF) : Rivière de l'Est fragilisée par les cyclones Cheneso (2023) et Belal (2024) + lave torrentielle → travaux lourds ; fiabilité des centrales converties « à démontrer dans la durée » (S1 2024 compliqué) ; maintenance lourde Takamaka.
- **Inertie/ZNI** : PV, éolien et batteries sont **non-synchrones** → pas d'inertie ; réserve primaire ~50 MW, secondaire jusqu'à ~200 MW (2033) ; critère de défaillance PPE = **3 h/an**.
- **Trajectoire** : fossile 118 MW (2024) → 41 MW (Azur 2040) ou 0 dès 2027 (Emeraude) ; bioénergie reste ~415 MW jusqu'en 2040 (**la base combustion et la dépendance import perdurent**) ; pilotable complémentaire requis 80 MW (2033) → 480 MW (2040, fin contrat Port-Est) ; conso +40/+50 %, pointe 737-799 MW vs 498 MW en 2023.
- Ordre de grandeur utile pour valider un KPI : production totale instantanée **≈ 340 MW**
  (mesuré le 2026-07-17). Un `Total = 0` est un **bug**, pas une donnée.

## Équipe de sous-agents (.claude/agents/)
- **architecte-energie** — cadre, décide, découpe, ADR. Ne code pas.
- **concepteur-experts** — conçoit/calibre les personas experts. Travaille dans `agent_expert.py` / `experts.py` (**dégelés** — le FREEZE de la Phase 0/1 est levé depuis l'intégration).
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

> *(La dette listée ici à l'époque — pagination, injection HTML, `pytest`, `use_container_width`,
> `.gitignore`/git — a été intégralement soldée depuis. Voir la section « Dette restante » en fin
> de fichier, seule à faire autorité.)*

## État actuel — Phases 0 / 1 / 1.5 ✅ LIVRÉES (2026-07-18)

- **Phase 0** (ingestion) : `fetch_data` prouvé vert (endpoint v2.1, mapping casse, négatifs). Test live agent : chaîne verte, clé + modèle `claude-sonnet-5` valides sur le compte ; seul bloquant = **crédits Anthropic** (administratif, pas technique).
- **Phase 1** (contexte enrichi) : `build_data_context` étendu (tendance 1h, amplitude, % par filière). Piège `pct_ren` (absent du df) contourné.
- **Phase 1.5** (reclassement) : taxonomie 3 familles + double %ENR + libellés `ex-Charbon`/`ex-Diesel` + fourchette carbone, dans **`filieres.py`** (source unique, invariant n°7). Prouvé : 20 tests verts (13 fetch + 7 filieres), anti-dup et anti-cycle vérifiés, carbone chuté ~494 → **68-145 gCO₂/kWh**, %ENR réglementaire ~99 %, badge éolien + garde-fou prompt en place.
- App **3 onglets** (`st.tabs`) fonctionnelle, `streamlit run` → HTTP 200.

## État actuel — Phase 4 ✅ LIVRÉE (2026-07-20) — git + régression figée

- **Gate sécurité passé du premier coup** : `git init` puis double preuve **avant** tout commit —
  `git ls-files --error-unmatch .streamlit/secrets.toml` → *did not match any file(s) known to git*,
  `git check-ignore -v` → règle `.gitignore:2`, et `git grep` sur **tout** l'historique → aucune clé.
  La clé API réelle n'est jamais entrée dans git. (Dividende d'avoir préparé et éprouvé le
  `.gitignore` **avant** le `git init`.)
- **Fixture déterministe** : `tests/fixtures/payload_edf.json` (payload EDF figé volontairement).
  Toute la suite tourne **hors réseau** (vérifié en bloquant `socket.socket.connect`).
- **Filet prouvé par la casse** : reclasser `Diesel` en FOSSILE → test rouge ; remettre
  `order_by="Date DESC"` → test rouge ; restauration → vert. Voir la leçon en invariant n°4.

## État actuel — Phase 2 ✅ LIVRÉE (2026-07-21) — expert souveraineté + sélecteur

- **Expert Souveraineté/Résilience** ajouté, sourcé sur le **Bilan Prévisionnel EDF SEI 2024**
  (`docs/sources/`) : signature analytique = 3 niveaux de lecture (%ENR strict / réglementaire /
  **moyenne annuelle officielle 57 % en 2023**), dépendance import (colza + pellets), vulnérabilités
  (Rivière de l'Est, cyclones), inertie/non-synchrone, trajectoire 2040. Neutralité politique imposée
  (position EDF ET critique « dépendance déplacée », sans militer).
- **Architecture** : nouveau socle `experts.py` (personas), `EXPERTS = {"generaliste", "souverainete"}`,
  sélecteur `st.selectbox` dans l'UI (défaut `generaliste`), reset historique au changement.
  `ask_expert` prend le prompt en paramètre explicite. `filieres.py` **intact** (non touché).
  Garde-fous éolien + limite épistémique dans `BASE_PROMPT` → hérités par TOUTE persona (testé transverse).
- **Expert électrotechnique enrichi** : cadre synchrone/non-synchrone, inertie, réserves 50/200 MW,
  critère PPE 3 h/an. Correction factuelle : **aucune STEP opérationnelle** (seulement batteries).
- **Preuves** : **42 tests verts** (28 + 14 `test_experts.py`), hors réseau, `anthropic` mocké.
  Filet prouvé par casse : réintroduire « mars 2024 » → `test_aucune_persona_naffirme_la_date_erronee`
  rougit. `streamlit run` → HTTP 200, sélecteur fonctionnel (`AppTest`).
- ⚠️ **Régression attrapée par `gardien-qualite`** : le commit initial corrigeait la date de conversion
  dans CLAUDE.md mais laissait « mars 2024 » (faux) **en dur dans les prompts LLM**. Corrigé (mi-2024,
  Port-Est oct. 2023) + 2 tests d'ancrage ajoutés. Illustre : *un fait corrigé dans la doc mais pas
  dans le code envoyé au modèle reste un mensonge servi à l'utilisateur.*
- **Reste à valider en LIVE** (COO, dès crédits Anthropic) : la **qualité** des réponses sur les
  5-6 questions-test de `concepteur-experts` — « La Réunion est-elle autonome ? » (doit exposer
  l'écart strict/réglementaire/annuel + imports, ne pas dire « oui à 99 % »), « Port-Est au fioul ? »
  (→ colza oct. 2023), « risque Rivière de l'Est ? » (→ cyclones + travaux). Prompts prouvés corrects ;
  exécution par le modèle non testable sans crédits.

## État actuel — Carte installations (registre) ✅ LIVRÉE (2026-07-28)

- **Nouveau flux de données, isolé du temps réel** : registre EDF
  `registre-national-des-installations-de-production-et-de-stockage-d-electricite-reunion`
  (slug suffixé `-reunion`, 724 lignes brutes agrégées par lots, toutes en 974). Endpoint :
  `https://opendata-reunion.edf.fr/api/explore/v2.1/catalog/datasets/registre-national-des-installations-de-production-et-de-stockage-d-electricite-reunion/records`.
  **Aucune coordonnée dans ce jeu** : localisation = `codeinseecommune` (string "974xx") +
  `commune` ; `nominstallation` = "Confidentiel" partout (pas de nom de site).
- **Requête validée** : `select=codeinseecommune, commune, filiere, sum(puismaxinstallee) as
  p_kw, sum(nbinstallations) as n_inst` + `group_by=codeinseecommune, commune, filiere` +
  `order_by=p_kw desc` → **46 lignes** (commune × filière), un seul appel API, 0 code INSEE
  vide. Total agrégé ≈ **1200,7 MW**, `sum(nbinstallations)` = **9878**.
- **Pièges** : `puismaxinstallee` en **kW** (conversion kW→MW UNE SEULE FOIS, à la source,
  dans `fetch_registre_par_commune_filiere`) ; **`sum(nbinstallations)` (9878) ≠ `count(*)`
  (724 lignes brutes non groupées)** — l'agrégation par lots du registre est réelle, un
  comptage naïf des lignes sous-compte massivement le parc réel ; corps d'erreur parfois
  `text/plain` (comme le flux temps réel) → géré explicitement (`ValueError` typée, pas de
  `JSONDecodeError` brute).
- **Filières du registre** (nomenclature DIFFÉRENTE du flux temps réel) : Solaire, Hydraulique,
  Bioénergies, Thermique non renouvelable, Eolien, Stockage non hydraulique. Palette locale
  `FILIERE_COLORS` dans `registre_installations.py`, **non fusionnée** avec `filieres.COLORS`
  (les deux classifications ne sont pas bijectives — voir ADR-003).
- **Invariant data-driven (non-négociable, ADR-003)** : V1 n'a **aucune coordonnée de centrale
  saisie à la main, ni aucune identité de site déduite**. La table de centroïdes communaux
  (`geo/communes_974_centroides.json`, 24 lignes, source `geo.api.gouv.fr`/Etalab) contient des
  coordonnées, mais à la maille COMMUNE — donnée de référence administrative publique et
  sourcée, pas un hardcode par installation. L'affectation installation → lieu reste 100 %
  pilotée par l'API via `codeinseecommune`, en jointure **string strict** (zéros initiaux
  préservés des deux côtés).
- **Rendu** : bulles proportionnelles (`go.Scattermap`, MapLibre, style `open-street-map`
  token-free — préféré à `go.Scattermapbox`, legacy bien que fonctionnel en Plotly 6.9.0), aire
  ∝ MW (échelle racine carrée du rayon, pas linéaire), couleur = filière dominante par commune.
  Pas de choroplèthe (déformerait une quantité absolue par l'aire du territoire communal).
- **Nouvel onglet `🗺️ Carte`, 2e position** (Dashboard, Carte, Agent expert, Diagnostic).
  `render_carte_tab()` est **LAZY** (appelé uniquement dans le corps de l'onglet, jamais dans
  le fetch eager de `main()`), cache `@st.cache_data(ttl=REGISTRE_TTL_SECONDS=86400)` distinct
  de `REFRESH_INTERVAL` (300 s, temps réel). Dégradation **locale** à l'onglet (panne registre,
  centroïdes absents, 0 ligne) : jamais de `st.stop()` global, les 3 autres onglets restent
  fonctionnels. Aucun autorefresh/`time.sleep`/`st.rerun` sur cet onglet (registre = snapshot
  administratif, pas un flux temps réel — invariant n°2 hors-sujet ici mais respecté).
- **Preuves** : **62 tests verts** (42 existants inchangés + 20 nouveaux dans
  `test_registre_installations.py`), hors réseau (vérifié en bloquant `socket.socket.connect`).
  Filet prouvé par casse volontaire sur le VRAI code de prod (`registre_installations.
  fetch_registre_par_commune_filiere`) : retirer le `/1000` (kW→MW) → le test dédié rougit
  (`256043.85` au lieu de `256`) ; restaurer → vert. Remplacer `sum(nbinstallations)` par un
  comptage de lignes (`n_inst = 1`) → le test dédié rougit (`46` au lieu de `9878`) ; restaurer
  → vert. `py_compile` OK sur `dashboard_reunion.py`/`registre_installations.py`. `streamlit run
  --server.headless` → HTTP 200 ; `AppTest` confirme les **4 onglets** dans l'ordre attendu et
  **0 exception**, y compris en cas de panne réseau simulée du registre (message d'erreur
  localisé à l'onglet Carte, badge du Dashboard toujours rendu normalement en parallèle).
  `git diff --stat` : **0 changement** sur `filieres.py`/`agent_expert.py`/`experts.py`/
  `fetch_data` — fonctionnalité greffée par un import et un onglet supplémentaires uniquement.
- **Reste hors V1** (assumé, voir ADR-003) : pas d'identité de site (registre 100 %
  `Confidentiel`), pas de maille plus fine que la commune (pas de `shapely`/GeoJSON de
  polygones), pas de choroplèthe.

## État actuel — Phase 1.75 ✅ LIVRÉE (2026-07-20) — sprint dette

Fermeture des 3 items de dette identifiés en Phase 0/1.5, avant ouverture publique (Streamlit Cloud) :

- ✅ **Injection HTML** : badge « dernière donnée » extrait dans `build_update_badge_html()`
  (`dashboard_reunion.py`), `statut` (origine API non maîtrisée) passé par `html.escape()`.
  `render_kpi()` échappe aussi label/value/unit en défense en profondeur. Preuve AVANT/APRÈS :
  reconstitution pré-fix → `<script>alert(1)</script>` brut dans le HTML ; code de prod actuel →
  `&lt;script&gt;alert(1)&lt;/script&gt;` (neutralisé), affichage normal non dégradé (`Estimé`
  reste `Estimé`). Audit complet : seul point réel était le badge ; `agent_expert.py` n'injecte
  aucune donnée API dans `unsafe_allow_html` (le contexte agent passe par `st.code`, pas de HTML).
- ✅ **`use_container_width` → `width='stretch'`** : les 4 `st.plotly_chart` (`dashboard_reunion.py`)
  et le `st.button` des suggestions (`agent_expert.py`) migrés. Validé réellement supporté par les
  deux widgets en Streamlit 1.59.2 (signature `inspect.signature`), puis prouvé par exécution
  réelle via `streamlit.testing.v1.AppTest` (0 exception, 4 `plotly_chart` + 4 `button` rendus) et
  par `streamlit run --server.headless` → HTTP 200, logs sans warning de dépréciation.
- ✅ **Dérive de pagination** : `_fetch_records` bascule d'`offset` à un **curseur** (`where=date <
  '<date la plus ancienne reçue>'`), ancré sur une donnée et non une position — insensible au
  glissement de la fenêtre. Syntaxe validée par appel réel (HTTP 200, page suivante correcte).
  Preuve par reproduction : sur une fenêtre glissante synthétique (nouvelle ligne en tête entre 2
  appels), l'ancienne logique offset perd réellement 1 ligne (129/130 lignes uniques, la plus
  ancienne demandée absente) ; la nouvelle logique curseur récupère les 130 lignes sans doublon —
  confirmé en forçant l'ancienne logique dans `dash._fetch_records` (le test cursor rougit alors).
- ✅ **Tests** : 24 → **28 tests verts**, zéro réseau (vérifié en bloquant `socket.socket.connect` :
  la suite passe toujours). 4 nouveaux : 2 injection (AVANT casse brute / APRÈS échappée), 2
  pagination (AVANT logique offset reconstituée perd une ligne / APRÈS `dash._fetch_records` réel
  n'en perd aucune).

### Dette restante (SEULE SECTION FAISANT AUTORITÉ — vérifiée le 2026-07-20)
- ⚠️ **`diesel`/Bioliquide = point carbone le plus incertain** (colza : combustion biogénique mais
  amont N₂O sols / transport bateau / ILUC) → fourchette volontairement large **30/150**, à affiner
  si une source CRE/EDF opérationnelle est trouvée. C'est la principale incertitude du modèle.
- ⚠️ **Éolien figé** : cause exacte non tranchable par la donnée (capteur bloqué vs remontée EDF).
  Traité défensivement (badge UI + garde-fou prompt), pas résolu à la source.
- Imports morts préexistants dans `dashboard_reunion.py` : `plotly.express as px` (l.11),
  `from datetime import datetime` (l.13) — cosmétique.
- **Validation live de l'agent en attente de crédits Anthropic** : la chaîne est prouvée verte
  (clé + modèle `claude-sonnet-5` acceptés ; l'échec est un HTTP 400 « credit balance too low »,
  pas un problème de code). Les 5 questions-test de `concepteur-experts` sont prêtes pour juger
  la qualité des réponses sur le modèle corrigé.

> ✅ **Soldé** en Phase 4 / 1.75, ne pas réinscrire comme dette : `pytest` (épinglé `pytest==9.1.1`),
> `use_container_width` (migré `width='stretch'`, 0 occurrence), injection HTML (`html.escape`),
> dérive de pagination (curseur `where`), `.gitignore` + `git init`.
