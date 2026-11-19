import carte from '../data/carte-communes.json';

const p = carte.projection;
// Même projection que les contours (équirectangulaire corrigée de cos(lat0)).
export function projeter(lat: number, lon: number): [number, number] {
  return [(lon - p.minlon) * p.kx * p.scale + p.pad, (p.maxlat - lat) * p.scale + p.pad];
}
// Rayon ∝ racine de la puissance : l'AIRE du disque est proportionnelle aux MW.
export function rayon(mw: number | null): number {
  if (!mw || mw <= 0) return 5;
  return Math.max(5, Math.sqrt(mw) * 3.2);
}
export const CARTE = carte;
