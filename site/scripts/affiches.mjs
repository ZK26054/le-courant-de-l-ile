// Génère les affiches (images fixes) des deux vidéos : fond océan nuit, silhouette de l'île
// (contours des communes, Etalab), titre. Rendu SVG → WebP par sharp (dépendance d'Astro).
// Usage : node scripts/affiches.mjs   (depuis site/)
// Note : ces affiches sont DESSINÉES, pas extraites des vidéos (ffmpeg indisponible le 2026-11-19).
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import sharp from 'sharp';
// Pour que le texte utilise Bricolage Grotesque / JetBrains Mono, pointer fontconfig vers
// src/assets/fonts (variable FONTCONFIG_FILE, voir le CR du 2026-11-19) ; sinon polices système.

const carte = JSON.parse(readFileSync(new URL('../src/data/carte-communes.json', import.meta.url), 'utf-8'));
const [, , vw, vh] = carte.viewBox.split(' ').map(Number);
const W = 1280, H = 720;
const s = 560 / vh;
const ile = carte.communes.map((c) => `<path d="${c.d}"/>`).join('');

const VIDEOS = [
  { fichier: 'le-courant-de-l-ile', l1: 'Le courant', l2: 'de l’île', sous: 'De l’eau des barrages à la biomasse importée', accent: '#38B6CC', duree: '3 min 02' },
  { fichier: 'les-megawatts-de-l-ile', l1: 'Les mégawatts', l2: 'de l’île', sous: 'Qui produit l’électricité, où, avec quelle puissance', accent: '#F5C24C', duree: '2 min 09' },
];

for (const v of VIDEOS) {
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">
  <defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0A1C27"/><stop offset="1" stop-color="#0F2735"/></linearGradient></defs>
  <rect width="${W}" height="${H}" fill="url(#g)"/>
  <g transform="translate(${W - vw * s - 30} ${(H - vh * s) / 2}) scale(${s})" fill="#18282E" stroke="#2C4650" stroke-width="${1.2 / s}">${ile}</g>
  <text x="80" y="140" font-family="JetBrains Mono" font-size="22" letter-spacing="3" fill="#FF6B3D">LA RÉUNION · 974</text>
  <text x="80" y="300" font-family="Bricolage Grotesque" font-weight="800" font-size="96" fill="#EEF2EE">${v.l1}</text>
  <text x="80" y="410" font-family="Bricolage Grotesque" font-weight="800" font-size="96" fill="${v.accent}">${v.l2}</text>
  <text x="80" y="480" font-family="Bricolage Grotesque" font-size="28" fill="#A9BEC5">${v.sous}</text>
  <circle cx="122" cy="590" r="42" fill="#FF6B3D"/><path d="M110 568 L142 590 L110 612 Z" fill="#0A1C27"/>
  <text x="186" y="600" font-family="Bricolage Grotesque" font-size="26" fill="#EEF2EE">Vidéo · ${v.duree}</text>
</svg>`;
  const info = await sharp(Buffer.from(svg)).webp({ quality: 82 }).toFile(fileURLToPath(new URL(`../public/videos/${v.fichier}-affiche.webp`, import.meta.url)));
  console.log(v.fichier, `${info.width}x${info.height}`, `${Math.round(info.size / 1024)} Ko`);
}
