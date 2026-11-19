import { getCollection, type CollectionEntry } from 'astro:content';
import fermes from '../data/fermes-solaires.json';

export type Fiche = CollectionEntry<'installations'>;

export async function toutesLesFiches(): Promise<Fiche[]> {
  return (await getCollection('installations')).sort((a, b) => a.data.ordre - b.data.ordre);
}

// Points de carte : fiches localisées (+ fermes solaires OSM, rattachées à la fiche « solaire »).
export function points(fiches: Fiche[], avecFermes = true) {
  const pts = fiches
    .filter((f) => f.data.coordonnees.precision !== 'inconnue')
    .map((f) => ({
      id: f.id,
      nom: f.data.nom,
      filiere: f.data.filiere,
      puissance_mw: f.data.puissance_mw,
      statut: f.data.statut,
      lat: f.data.coordonnees.lat as number,
      lon: f.data.coordonnees.lon as number,
      approximative: f.data.coordonnees.precision === 'approximative',
    }));
  if (avecFermes) {
    for (const s of fermes.fermes) {
      pts.push({
        id: 'solaire', nom: `Ferme solaire ${s.nom} (${s.commune})`, filiere: 'solaire', puissance_mw: s.mw,
        statut: 'en service', lat: s.lat, lon: s.lon, approximative: false,
      });
    }
  }
  return pts;
}

export const FERMES = fermes;

export const fmtMW = (v: number | null) => (v === null ? 'non définie' : `${v.toLocaleString('fr-FR')} MW`);

const CLASSES: Record<string, string> = {
  'en service': 'statut-en-service',
  'à l’arrêt': 'statut-arret',
  'engagé': 'statut-engage',
  'annoncé': 'statut-annonce',
  'projet': 'statut-projet',
  'permis de recherche': 'statut-permis',
};
export const classeStatut = (s: string) => CLASSES[s] ?? '';
