// Nettoyage des relevés temps réel : exerce la VRAIE fonction src/lib/direct.ts
// (Node 24 exécute le TypeScript en retirant les types).
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { nettoyer } from '../src/lib/direct.ts';

const taxo = JSON.parse(readFileSync(new URL('../src/data/filieres.json', import.meta.url), 'utf-8'));
const API2INT = taxo.api_vers_interne;
const COLS = Object.keys(API2INT);

function releve(date, vals = {}) {
  const r = { date, statut: 'Estimé' };
  for (const c of COLS) r[c] = vals[c] ?? 40;
  r.stockage = vals.stockage ?? -0.34;
  r.total = vals.total ?? COLS.reduce((s, c) => s + r[c], 0);
  return r;
}

test('relevé valide conservé, négatif du stockage préservé (jamais écrêté)', () => {
  const { lignes, ecartees } = nettoyer([releve('2026-11-19T10:00:00+00:00')], API2INT);
  assert.equal(ecartees, 0);
  assert.equal(lignes.length, 1);
  assert.equal(lignes[0].v.Stockage, -0.34);
  assert.equal(lignes[0].v.Charbon, 40);
});

test('relevé avec un champ vide écarté (pas tracé à zéro)', () => {
  const trou = releve('2026-11-19T10:05:00+00:00');
  trou.diesel = null;
  const { lignes, ecartees } = nettoyer([releve('2026-11-19T10:00:00+00:00'), trou], API2INT);
  assert.equal(ecartees, 1);
  assert.equal(lignes.length, 1);
});

test('relevé incohérent (somme des filières ≠ total publié) écarté', () => {
  const faux = releve('2026-11-19T10:05:00+00:00', { total: 330 });
  for (const c of COLS) faux[c] = 0; // champs à zéro mais total renseigné
  const { ecartees } = nettoyer([releve('2026-11-19T10:00:00+00:00'), faux], API2INT);
  assert.equal(ecartees, 1);
});

test('dates en double dédoublonnées, tri chronologique, fenêtre de 24 h', () => {
  const brut = [releve('2026-11-19T10:00:00+00:00'), releve('2026-11-19T10:00:00+00:00'), releve('2026-11-18T09:55:00+00:00'), releve('2026-11-19T09:55:00+00:00')];
  const { lignes } = nettoyer(brut, API2INT);
  assert.deepEqual(lignes.map((l) => new Date(l.t).toISOString()), ['2026-11-19T09:55:00.000Z', '2026-11-19T10:00:00.000Z']);
});

test('payload EDF figé du dépôt (tests/fixtures/payload_edf.json) : aucune ligne valide écartée', () => {
  const payload = JSON.parse(readFileSync(new URL('../../tests/fixtures/payload_edf.json', import.meta.url), 'utf-8'));
  const { lignes, ecartees } = nettoyer(payload.results, API2INT);
  assert.equal(ecartees, 0);
  assert.ok(lignes.length > 50, `${lignes.length} lignes`);
});
