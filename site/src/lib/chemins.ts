// Préfixe un chemin interne par le base path (GitHub Pages sert le site sous /le-courant-de-l-ile/).
// Les pages reçoivent une barre finale (format « directory ») : pas de redirection 301 côté hébergeur,
// et les liens relatifs des fiches Markdown (« ../autre-fiche/ ») restent justes.
export function lien(chemin: string): string {
  const base = import.meta.env.BASE_URL.replace(/\/+$/, '');
  let c = chemin.startsWith('/') ? chemin : `/${chemin}`;
  const [p, ancre] = c.split('#');
  c = /\.[a-z0-9]+$/i.test(p) || p.endsWith('/') ? p : `${p}/`;
  return `${base}${c}${ancre ? `#${ancre}` : ''}`;
}
