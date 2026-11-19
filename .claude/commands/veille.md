---
description: Veille complète (institutions + données) et synthèse pour le COO, sans rien modifier dans le produit
---
1. Lance EN PARALLÈLE les sous-agents veille-institutionnelle, sentinelle-donnees et veille-albioma.
2. Quand les trois ont rendu : transmets à gardien-qualite toute ligne marquée « impact experts.py / filieres.py » ou listée en CONTRADICTIONS. Il ne fait pas confiance : il revérifie chaque point (fais toi-même les WebFetch dont il a besoin, il n'a pas d'accès web) et rend CONFIRMÉ / INFIRMÉ / NON PROUVABLE.
3. Écris docs/veille/AAAA-MM-JJ-SYNTHESE.md : (a) alertes données ; (b) faits nouveaux confirmés ; (c) contradictions avec le projet ; (d) propositions de mise à jour au format « fichier · ligne · texte actuel → texte proposé · source niveau 1 » + test d'ancrage à ajouter — SANS les appliquer ; (e) idées d'articles (dont celles issues de la veille Albioma).
4. Commit uniquement les fichiers de docs/veille/, nommés un par un. STOP : aucune modification de experts.py, filieres.py, docs/sources ou CLAUDE.md sans GO du COO.
