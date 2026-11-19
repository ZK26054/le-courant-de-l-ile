# Photos à obtenir — « Le courant de l’île »

État au **19/11/2026**. 10 fiches sur 21 ont une photo sous licence libre (Wikimedia Commons, licence revérifiée via l’API). Les autres affichent un dessin « Photo à venir ».

**Règle** : une photo n’entre dans le site que si elle est déclarée dans `src/data/images.json` avec auteur, licence (CC0, CC BY, CC BY-SA, domaine public ou « Autorisation écrite » avec sa référence), URL source, date et légende. Sinon le build échoue. **Aucune image d’EDF, d’Albioma, de presse ou de Facebook** sans autorisation écrite enregistrée.

## 1. Fiches sans aucune photo

| Fiche | Piste 1 : demander | Piste 2 : photo par Z depuis l’espace public |
|---|---|---|
| Turbines à combustion de La Baie (Le Port) | EDF Réunion (service communication) | Vue depuis la voie publique autour de la zone portuaire de Port-Est |
| Turbine à combustion de Saint-Pierre | Albioma | Vue depuis la voie publique, zone de Pierrefonds |
| Groupes électrogènes de secours | EDF Réunion : demander d’abord **où** ils sont | — (emplacement inconnu) |
| Centrales biogaz (Sainte-Suzanne, Pierrefonds, Grand Prado, distillerie Rivière du Mât) | Exploitants des sites (à identifier) ; SYDNE / ILEVA pour les sites de déchets | Vue extérieure depuis la voie publique |
| Bras des Lianes (Bras-Panon) | EDF Réunion | Vue depuis un chemin public |
| Picocentrales RT4, RT8, Ligne Paradis | Exploitant à identifier | — (emplacements inconnus) |
| Batterie de Saint-Leu | EDF Réunion (EDF SEI) : confirmer aussi l’emplacement exact | Vue extérieure si visible depuis la voie publique |
| Batterie du Cratère | Exploitant (Corsica Sole selon une base de projets) : confirmer l’emplacement | — (emplacement inconnu) |
| Chaudière CSR de Bois-Rouge | Albioma ; SYDNE (photos de la visite de chantier du 15/04/2025) | Vue extérieure du site de Bois-Rouge depuis la route |
| Projet Tanika (STEP) | Porteur du projet (visuels de concertation, **avec autorisation écrite**) | Le site actuel, si l’emplacement est public |
| Géothermie du Piton des Neiges | Albioma | Paysage des cirques (une photo de Salazie ou Cilaos sous licence libre suffit, légendée comme vue de la zone du permis) |

## 2. Fiches dont la photo est à remplacer ou compléter

| Fiche | Photo actuelle | Pourquoi la remplacer |
|---|---|---|
| Centrale de Port-Est | Vue d’ensemble du Port, 2015 (Chaoborus, CC BY-SA 4.0) | La centrale est lointaine. Une vue plus rapprochée serait plus utile (un candidat de Commons a été écarté parce que son titre évoque un lot de photos d’EDF). |
| Centrale du Gol | Usine du Gol, 2007 (B.navez, CC BY-SA 3.0) | Photo antérieure à la conversion biomasse (charbon jusqu’en 2024). |
| Centrale de Bois-Rouge | Sucrerie de Bois-Rouge, 2008 (B.navez, CC BY-SA 3.0) | Photo antérieure à la conversion biomasse. |
| Parc éolien de Sainte-Rose | Parc en 2009 (Thierry Caro, CC BY-SA 3.0) | Parc démantelé pour repowering. Une photo des nouvelles machines, si elles sont installées, confirmerait aussi leur statut. |
| Solaire | Ferme au sol à Saint-Benoît, 2015 (regulator974, CC BY-SA 3.0) | Exploitant non identifié. Une photo de toiture récente (école, hangar) illustrerait mieux le « solaire toit par toit ». |

## 3. Demander une autorisation (EDF, Albioma, porteurs de projets)

Modèle de demande (à envoyer par Z) : préciser le site (« Le courant de l’île », site d’information non commercial), la ou les photos voulues et l’usage (fiche de l’installation, avec crédit). Demander **une licence écrite** : idéalement CC BY 4.0, sinon une autorisation d’usage nominative pour ce site.

Une fois l’accord reçu :
1. Garder l’e-mail ou le courrier d’autorisation (hors du dépôt public).
2. Ajouter l’image dans `public/images/photos/` (1 600 px au plus, en WebP).
3. La déclarer dans `src/data/images.json` avec `"licence": "Autorisation écrite"` et un champ `"autorisation"` qui donne la référence (date, signataire, objet). Le build refuse une « Autorisation écrite » sans ce champ.

## 4. Photos prises par Z

- Photographier **depuis l’espace public** uniquement. Ne pas entrer sur les sites industriels (installations classées, périmètres de sécurité).
- Éviter les personnes reconnaissables et les plaques d’immatriculation.
- Choisir la licence de ses propres photos (CC BY 4.0 conseillée) et la déclarer dans `images.json` avec `"auteur": "Z"`.
- **Drone : avant tout vol, vérifier la carte des restrictions de vol (« Restrictions UAS catégorie Ouverte et aéromodélisme ») sur Géoportail** (geoportail.gouv.fr). À La Réunion, beaucoup de zones sont interdites ou réglementées : aéroports Roland-Garros et Pierrefonds, cœur du Parc national, zones militaires, sites industriels. Respecter aussi les règles de la catégorie Ouverte (enregistrement, formation, hauteur maximale de 120 m, vol à vue, pas de survol de personnes). Les centrales thermiques et les postes électriques sont en général interdits de survol.
