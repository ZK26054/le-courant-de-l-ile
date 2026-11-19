// Contrôle BLOQUANT des droits des images (Lot S3).
// Règle : toute <img> d'une page publiée doit pointer vers un fichier déclaré dans
// src/data/images.json, avec une licence de la liste autorisée et un auteur non vide.
// Utilisé (1) par l'intégration Astro à la fin du build (le build échoue sinon)
// et (2) par les tests node (tests/images.test.mjs).
import { readFileSync, readdirSync, statSync, existsSync } from 'node:fs';
import { join, relative, sep } from 'node:path';
import { fileURLToPath } from 'node:url';

export const LICENCES_AUTORISEES = [
  /^CC0( 1\.0)?$/,
  /^CC BY( [1-4]\.0)?$/,
  /^CC BY-SA( [1-4]\.0)?$/,
  /^Domaine public$/,
  /^Autorisation écrite$/,
];

export function licenceAutorisee(licence) {
  return typeof licence === 'string' && LICENCES_AUTORISEES.some((re) => re.test(licence.trim()));
}

// Vérifie le registre lui-même (indépendamment des pages).
export function verifierRegistre(images, publicDir) {
  const erreurs = [];
  const vus = new Set();
  for (const [i, im] of images.entries()) {
    const ref = im?.fichier || `entrée #${i}`;
    if (!im?.fichier) erreurs.push(`${ref} : champ « fichier » manquant`);
    if (vus.has(im?.fichier)) erreurs.push(`${ref} : fichier déclaré deux fois`);
    vus.add(im?.fichier);
    if (!licenceAutorisee(im?.licence)) erreurs.push(`${ref} : licence non autorisée « ${im?.licence} »`);
    if (!im?.auteur || !String(im.auteur).trim()) erreurs.push(`${ref} : auteur vide`);
    for (const champ of ['installation', 'url_source', 'date_recuperation', 'legende']) {
      if (!im?.[champ] || !String(im[champ]).trim()) erreurs.push(`${ref} : champ « ${champ} » vide`);
    }
    if (im?.licence === 'Autorisation écrite' && !im?.autorisation) {
      erreurs.push(`${ref} : « Autorisation écrite » sans référence d'autorisation enregistrée`);
    }
    if (publicDir && im?.fichier && !existsSync(join(publicDir, im.fichier))) {
      erreurs.push(`${ref} : fichier absent de public/`);
    }
  }
  return erreurs;
}

function* fichiersHtml(dir) {
  for (const nom of readdirSync(dir)) {
    const p = join(dir, nom);
    if (statSync(p).isDirectory()) yield* fichiersHtml(p);
    else if (nom.endsWith('.html')) yield p;
  }
}

// Normalise un src en chemin relatif à public/ (retire le base path et la query).
function normaliser(src, base) {
  let s = src.split('?')[0].split('#')[0];
  if (/^(https?:)?\/\//.test(s) || s.startsWith('data:')) return { externe: true, chemin: s };
  if (base && base !== '/' && s.startsWith(base)) s = s.slice(base.length);
  return { externe: false, chemin: s.replace(/^\/+/, '') };
}

// Vérifie toutes les pages générées.
export function verifierPages(distDir, images, base = '/') {
  const erreurs = [];
  const index = new Map(images.map((im) => [im.fichier.replace(/^\/+/, ''), im]));
  let nbImg = 0;
  for (const page of fichiersHtml(distDir)) {
    const html = readFileSync(page, 'utf-8');
    const rel = relative(distDir, page).split(sep).join('/');
    for (const m of html.matchAll(/<img\b[^>]*?\bsrc\s*=\s*["']([^"']+)["'][^>]*>/gi)) {
      nbImg++;
      const { externe, chemin } = normaliser(m[1], base);
      if (externe) { erreurs.push(`${rel} : image externe interdite ${chemin}`); continue; }
      const im = index.get(chemin);
      if (!im) { erreurs.push(`${rel} : image non déclarée dans images.json → ${chemin}`); continue; }
      if (!licenceAutorisee(im.licence)) erreurs.push(`${rel} : licence non autorisée pour ${chemin}`);
      if (!im.auteur || !String(im.auteur).trim()) erreurs.push(`${rel} : auteur vide pour ${chemin}`);
    }
    // Interdit aussi les images d'arrière-plan CSS inline et les srcset non contrôlés.
    if (/\bsrcset\s*=/.test(html)) erreurs.push(`${rel} : srcset non contrôlé par le registre`);
  }
  return { erreurs, nbImg };
}

export default function verifImagesIntegration() {
  let base = '/';
  let racine;
  return {
    name: 'verif-licences-images',
    hooks: {
      'astro:config:done': ({ config }) => {
        base = config.base || '/';
        racine = fileURLToPath(config.root);
      },
      'astro:build:done': ({ dir, logger }) => {
        const images = JSON.parse(readFileSync(join(racine, 'src/data/images.json'), 'utf-8')).images;
        const e1 = verifierRegistre(images, join(racine, 'public'));
        const { erreurs: e2, nbImg } = verifierPages(fileURLToPath(dir), images, base);
        const erreurs = [...e1, ...e2];
        if (erreurs.length) {
          throw new Error(`Contrôle des licences d'images : ${erreurs.length} erreur(s)\n- ${erreurs.join('\n- ')}`);
        }
        logger.info(`licences d'images OK : ${images.length} image(s) déclarée(s), ${nbImg} balise(s) <img> vérifiée(s)`);
      },
    },
  };
}
