# BACKLOG — Piste "Enrichir l'analyse"

Priorité projet : ajouter de nouveaux experts et un moteur de rapports.
Chaque tâche n'est **close que sur preuve** (test/re-probe/vérif rendu).

## Phase 0 — Valider l'existant (bloquant, à faire d'abord)
- [ ] `pip install -r requirements.txt` OK (anthropic + streamlit-autorefresh installés).
- [ ] `streamlit run dashboard_reunion.py` démarre sans erreur.
- [ ] Onglet **Diagnostic** : l'endpoint `-974/lines` renvoie ✅ 200 + données.
- [ ] Onglet **Dashboard** : KPI et graphiques s'affichent avec de vraies valeurs.
- [ ] Onglet **Agent** : avec une clé API, une question obtient une réponse cohérente.
> Agent : `gardien-qualite` valide la Phase 0 avant d'aller plus loin.

## Phase 1 — Enrichir le contexte data (préalable aux nouveaux experts)
- [ ] Étendre `build_data_context` : ajouter tendance récente (mix il y a 1h vs maintenant), pic/creux sur la période, part de chaque filière en %.
- [ ] Exposer l'intensité carbone sur toute la période (pas seulement l'instantané).
> Agent : `concepteur-experts` spécifie le besoin, `dev-features` implémente, `gardien-qualite` teste.

## Phase 2 — Nouveaux experts
- [ ] **Expert économie de l'énergie** : coût par filière en ZNI, péréquation, coût du MWh évité.
- [ ] **Expert réseau / smart grid** : intermittence, plafond 30 %, stockage, prévision.
- [ ] (option) **Expert prospective 2030** : trajectoire autonomie, points de blocage.
- [ ] Sélecteur d'expert dans l'onglet agent (choisir l'angle d'analyse).
> Agent : `concepteur-experts` pilote. Chaque expert livré avec son jeu de questions-test.

## Phase 3 — Moteur de rapports
- [ ] Module `rapports.py` : synthèse HTML horodatée (mix + KPI + carbone + analyse experte).
- [ ] Bouton "Générer un rapport" dans le dashboard.
- [ ] (option) Export PDF (nécessite `kaleido` pour les graphiques statiques).
- [ ] Test : génération depuis un jeu de données figé → vérifier présence de toutes les sections.
> Agent : `dev-rapports` pilote, `gardien-qualite` valide.

## Phase 4 — Industrialisation légère
- [ ] Mettre en place `pytest` + premiers tests de régression (parsing API, calcul carbone).
- [ ] `.gitignore` complet, `.streamlit/secrets.toml` hors versioning.
- [ ] Vérifier qu'aucun secret n'est dans l'historique git.
> Agent : `gardien-qualite` pilote.
