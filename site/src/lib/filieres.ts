// Présentation des filières sur le site. Les LIBELLÉS du flux temps réel viennent de
// src/data/filieres.json, généré depuis filieres.py (source unique, invariant n°7).
import taxo from '../data/filieres.json';

// Filières des fiches installations (nomenclature éditoriale du site).
export const FILIERES_SITE = {
  'hydraulique': { libelle: 'Hydraulique', couleur: 'var(--f-hydro)' },
  'solaire': { libelle: 'Solaire', couleur: 'var(--f-solaire)' },
  'eolien': { libelle: 'Éolien', couleur: 'var(--f-eolien)' },
  'bagasse-granules': { libelle: 'Biomasse (bagasse et granulés)', couleur: 'var(--f-granules)' },
  'colza': { libelle: 'Bioliquide (huile de colza)', couleur: 'var(--f-colza)' },
  'turbines': { libelle: 'Turbines à combustion', couleur: 'var(--f-turbines)' },
  'biogaz': { libelle: 'Biogaz', couleur: 'var(--f-biogaz)' },
  'secours': { libelle: 'Groupes de secours', couleur: 'var(--f-secours)' },
  'batteries': { libelle: 'Batteries', couleur: 'var(--f-batteries)' },
  'csr': { libelle: 'Combustibles solides de récupération', couleur: 'var(--f-bagasse)' },
  'stockage-step': { libelle: 'Stockage par pompage (STEP)', couleur: 'var(--f-hydro)' },
  'geothermie': { libelle: 'Géothermie', couleur: 'var(--f-turbines)' },
} as const;
export type FiliereSite = keyof typeof FILIERES_SITE;

// Couleurs des 8 colonnes du flux EDF (noms internes de filieres.py).
export const COULEURS_FLUX: Record<string, string> = {
  Photovoltaique: '#F5C24C',
  Eolien: '#A9DCD0',
  Hydraulique: '#38B6CC',
  'Bioénergies': '#5E9E4A',
  Charbon: '#C9874C',
  Diesel: '#B3A64A',
  Turbines_combustion: '#FF6B3D',
  Stockage: '#A08CE6',
};
export const TAXO = taxo;
