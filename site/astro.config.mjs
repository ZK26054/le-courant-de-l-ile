// Configuration Astro — site 100 % statique, sans adaptateur serveur.
import { defineConfig } from 'astro/config';
import verifImages from './integrations/verif-images.mjs';

// GitHub Pages (site de projet) : https://<compte>.github.io/le-courant-de-l-ile/
// Surchargeable par variables d'environnement (SITE_URL, BASE_PATH) pour un autre hébergeur.
const site = process.env.SITE_URL ?? 'https://zk26054.github.io';
const base = process.env.BASE_PATH ?? '/le-courant-de-l-ile';

export default defineConfig({
  site,
  base,
  output: 'static',
  trailingSlash: 'ignore',
  build: { format: 'directory' },
  devToolbar: { enabled: false },
  integrations: [verifImages()],
});
