import { getCollection } from 'astro:content';

// Seuls les articles explicitement passés en draft: false sont publiés.
export async function articlesPublies() {
  return (await getCollection('articles', (a) => a.data.draft === false)).sort((a, b) => b.data.date.localeCompare(a.data.date));
}

// Temps de lecture : ~200 mots par minute, arrondi à la minute supérieure.
export function tempsDeLecture(texte = ''): number {
  const mots = texte.replace(/---[\s\S]*?---/, '').split(/\s+/).filter(Boolean).length;
  return Math.max(1, Math.ceil(mots / 200));
}

export const dateFr = (iso: string) =>
  new Date(`${iso}T12:00:00Z`).toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric', timeZone: 'UTC' });
