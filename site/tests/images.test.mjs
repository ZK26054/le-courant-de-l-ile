// Contrôle des licences d'images : exerce le VRAI module integrations/verif-images.mjs,
// sur le vrai registre et le vrai dist/ (lancer `npm run build` avant), puis sur des cas
// synthétiques qui DOIVENT échouer.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, mkdtempSync, writeFileSync, mkdirSync, existsSync } from 'node:fs';
import { join } from 'node:path';
import { tmpdir } from 'node:os';
import { fileURLToPath } from 'node:url';
import { verifierRegistre, verifierPages, licenceAutorisee } from '../integrations/verif-images.mjs';

const RACINE = fileURLToPath(new URL('..', import.meta.url));
const registre = JSON.parse(readFileSync(join(RACINE, 'src/data/images.json'), 'utf-8')).images;
const BASE = '/le-courant-de-l-ile';

test('le registre réel ne contient que des licences autorisées, auteurs non vides, fichiers présents', () => {
  assert.deepEqual(verifierRegistre(registre, join(RACINE, 'public')), []);
});

test('le dist réel : chaque <img> est déclarée dans images.json avec une licence autorisée', () => {
  assert.ok(existsSync(join(RACINE, 'dist')), 'dist/ absent : lancer npm run build');
  const { erreurs, nbImg } = verifierPages(join(RACINE, 'dist'), registre, BASE);
  assert.deepEqual(erreurs, []);
  assert.ok(nbImg >= registre.length, `au moins ${registre.length} <img> attendues, ${nbImg} trouvées`);
});

test('licences : seules CC0 / CC BY / CC BY-SA / domaine public / autorisation écrite passent', () => {
  for (const ok of ['CC0', 'CC BY 4.0', 'CC BY-SA 3.0', 'CC BY-SA 4.0', 'Domaine public', 'Autorisation écrite']) assert.ok(licenceAutorisee(ok), ok);
  for (const ko of ['CC BY-NC 4.0', 'CC BY-ND 4.0', 'CC BY-NC-SA 4.0', 'GFDL', 'Tous droits réservés', '', undefined]) assert.ok(!licenceAutorisee(ko), String(ko));
});

function distSynthetique(html) {
  const d = mkdtempSync(join(tmpdir(), 'dist-'));
  mkdirSync(join(d, 'x'));
  writeFileSync(join(d, 'x', 'index.html'), `<!doctype html><html><body>${html}</body></html>`);
  return d;
}

test('une image non déclarée fait échouer le contrôle', () => {
  const d = distSynthetique(`<img src="${BASE}/images/photos/inconnue.webp" alt="">`);
  assert.equal(verifierPages(d, registre, BASE).erreurs.length, 1);
});

test('une image externe (hotlink EDF, presse…) fait échouer le contrôle', () => {
  const d = distSynthetique('<img src="https://www.edf.fr/photo.jpg" alt="">');
  assert.match(verifierPages(d, registre, BASE).erreurs[0], /externe/);
});

test('une image déclarée avec une licence NC, ou sans auteur, fait échouer le registre', () => {
  const faux = [
    { fichier: 'a.webp', installation: 'x', auteur: 'X', licence: 'CC BY-NC 4.0', url_source: 'u', date_recuperation: 'd', legende: 'l' },
    { fichier: 'b.webp', installation: 'x', auteur: ' ', licence: 'CC BY 4.0', url_source: 'u', date_recuperation: 'd', legende: 'l' },
    { fichier: 'c.webp', installation: 'x', auteur: 'Y', licence: 'Autorisation écrite', url_source: 'u', date_recuperation: 'd', legende: 'l' },
  ];
  const e = verifierRegistre(faux);
  assert.ok(e.some((m) => m.includes('a.webp') && m.includes('licence')));
  assert.ok(e.some((m) => m.includes('b.webp') && m.includes('auteur')));
  assert.ok(e.some((m) => m.includes('c.webp') && m.includes('autorisation')));
});
