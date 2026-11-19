---
ordre: 10
nom: "Centrale de Port-Est"
exploitant: "EDF PEI"
filiere: "colza"
statut: "en service"
puissance_mw: 211
puissance_source: "OER, puissance installée au 31/12/2024 (« Centrale du Port Est - Moteurs Diesel 211,0 MW »)"
puissances_divergentes: [{"valeur": "211 MW (12 moteurs de 17,6 MW)", "date": "01/07/2024", "perimetre": "parc EDF SEI", "source": "Bilan prévisionnel EDF SEI 2024"}]
mise_en_service: "2012"
mise_en_service_source: "OpenStreetMap (start_date 2012-12-12), non corroboré par une source institutionnelle lue"
combustible: "Huile de colza (biodiesel) importée de France, fournisseur Saipol ; conversion achevée en octobre 2023"
commune: "Le Port"
coordonnees: {"lat": -20.93013, "lon": 55.32773, "precision": "osm", "osm": "way/718019336"}
resume: "La plus grosse centrale de l’île : 12 moteurs, 211 MW, alimentés depuis 2023 à l’huile de colza importée. Elle a produit 37,9 % de l’électricité réunionnaise en 2024."
sources: [{"titre": "Bilan énergétique de La Réunion, chiffres clés 2024 (édition 2025)", "editeur": "Observatoire Énergie Réunion", "niveau": "N1", "date": "2025-09", "url": "https://oer.energies-reunion.com/sites/observatoire-energie-reunion/files/2025-09/ENERGIESREUNION-CHIFFRESCLES%202024%20120x300%20Page%20a%20Page_4.pdf"}, {"titre": "Bilan énergétique de La Réunion 2024 (document technique)", "editeur": "Observatoire Énergie Réunion", "niveau": "N1", "date": "2026-03-31", "url": "https://oer.energies-reunion.com/sites/observatoire-energie-reunion/files/2026-03/BER_TECHNIQUE-EXPORT-WEB.pdf"}, {"titre": "Bilan prévisionnel de l'équilibre offre-demande d'électricité, La Réunion, édition 2024", "editeur": "EDF Systèmes énergétiques insulaires (EDF SEI)", "niveau": "N1", "date": "2025-04-29", "url": "https://reunion.edf.fr/sites/sei_reu/files/2025-04/2025-04-29-reunion-bp-2024.pdf"}, {"titre": "OpenStreetMap, objet way/718019336", "editeur": "Contributeurs OpenStreetMap (ODbL)", "niveau": "N3", "date": "données du 2026-06-01, consultées le 2026-11-19", "url": "https://www.openstreetmap.org/way/718019336"}]
derniere_verification: "2026-11-19"
image: "images/photos/port-est.webp"
---

## Ce qu’elle fait

Port-Est est la base du système électrique : ses moteurs tournent jour et nuit. En 2024, la filière « biodiesel », c’est-à-dire Port-Est, a produit **1 162,5 GWh, soit 37,9 % de la production électrique de l’île** (OER, chiffres clés 2024).

## Combustible

Jusqu’en 2023, la centrale brûlait du fioul. Elle fonctionne désormais au **bioliquide** : de l’huile de colza produite en France (OER) et fournie par Saipol (Bilan prévisionnel EDF SEI 2024). La conversion est datée d’**octobre 2023** par EDF SEI. L’OER date l’introduction du biodiesel de **juin 2023**. Les deux dates correspondent à deux étapes d’un même passage.

Dans les données temps réel d’EDF, cette production apparaît dans la colonne héritée `diesel`, renommée « Bioliquide » par EDF.

## Points d’attention

- **Combustible importé.** Ce combustible est renouvelable au sens réglementaire, mais il est importé. Les bioénergies importées (biodiesel et granulés de bois) ont représenté 61,2 % de la production de 2024 (OER).
- **Fin de contrat.** EDF SEI signale que la fin du contrat de Port-Est fait partie des besoins en puissance pilotable à remplacer à l’horizon 2040 (Bilan prévisionnel 2024).
