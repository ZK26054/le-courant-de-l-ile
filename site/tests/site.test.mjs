// Tests du site généré (dist/) : pages présentes, aucune ressource tierce, aucun traceur,
// articles non publiés, taxonomie issue de filieres.py, fiches complètes et sourcées.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, readdirSync, existsSync, statSync } from 'node:fs';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';

const RACINE = fileURLToPath(new URL('..', import.meta.url));
const DIST = join(RACINE, 'dist');
const lire = (p) => readFileSync(join(DIST, p), 'utf-8');
function* tous(dir, ext) {
  for (const n of readdirSync(dir)) {
    const p = join(dir, n);
    if (statSync(p).isDirectory()) yield* tous(p, ext);
    else if (n.endsWith(ext)) yield p;
  }
}

test('dist existe (lancer npm run build avant npm test)', () => assert.ok(existsSync(DIST)));

test('les pages principales sont générées', () => {
  for (const p of ['index.html', 'installations/index.html', 'reseau/index.html', 'comprendre/index.html', 'articles/index.html', 'sources/index.html', 'mentions-legales/index.html', '404.html']) {
    assert.ok(existsSync(join(DIST, p)), p);
  }
});

test('une page par fiche installation, chacune avec ses sources', () => {
  const fiches = readdirSync(join(RACINE, 'src/content/installations')).filter((f) => f.endsWith('.md'));
  assert.ok(fiches.length >= 20, `${fiches.length} fiches`);
  for (const f of fiches) {
    const html = lire(`installations/${f.replace(/\.md$/, '')}/index.html`);
    assert.match(html, /<h2 id="src-t"[^>]*>Sources<\/h2>/, f);
    assert.match(html, /class="niveau"[^>]*>N1</, `${f} : aucune source de niveau 1`);
    assert.match(html, /Dernière vérification/, f);
  }
});

test('toutes les pages sont en français et ne chargent aucune ressource tierce', () => {
  for (const p of tous(DIST, '.html')) {
    const html = readFileSync(p, 'utf-8');
    assert.match(html, /<html lang="fr"/, p);
    // aucun script, feuille de style, police ou image externe
    assert.doesNotMatch(html, /<script[^>]+src="(https?:)?\/\//i, `${p} : script externe`);
    assert.doesNotMatch(html, /<link[^>]+href="(https?:)?\/\/[^"]+"[^>]*rel="(stylesheet|preload)"/i, `${p} : CSS externe`);
    assert.doesNotMatch(html, /<link[^>]+rel="(stylesheet|preload)"[^>]+href="(https?:)?\/\//i, `${p} : CSS externe`);
    assert.doesNotMatch(html, /fonts\.googleapis|fonts\.gstatic|google-analytics|googletagmanager|gtag\(|plausible|matomo|facebook\.net|hotjar/i, `${p} : tiers/traceur`);
    assert.doesNotMatch(html, /document\.cookie/i, `${p} : cookie`);
  }
});

test('les bundles JS ne déposent pas de cookie et ne contactent que l’open data EDF', () => {
  const hotes = new Set();
  for (const p of tous(DIST, '.js')) {
    const js = readFileSync(p, 'utf-8');
    assert.doesNotMatch(js, /document\.cookie|localStorage\.setItem|navigator\.sendBeacon/, p);
    for (const m of js.matchAll(/https:\/\/([a-z0-9.-]+)\//gi)) hotes.add(m[1]);
  }
  for (const h of hotes) assert.equal(h, 'opendata-reunion.edf.fr', `hôte inattendu : ${h}`);
});

test('les polices sont auto-hébergées (fichiers servis par le site)', () => {
  const css = [...tous(DIST, '.css')].map((p) => readFileSync(p, 'utf-8')).join('\n');
  assert.match(css, /font-family:\s*Bricolage Grotesque/);
  assert.match(css, /font-family:\s*JetBrains Mono/);
  assert.match(css, /font-family:\s*Inter/);
  assert.doesNotMatch(css, /url\((https?:)?\/\//, 'police chargée depuis un tiers');
});

test('aucun article publié → « Premiers articles bientôt »', () => {
  assert.match(lire('articles/index.html'), /Premiers articles bientôt/);
  const dossiers = readdirSync(join(DIST, 'articles')).filter((n) => statSync(join(DIST, 'articles', n)).isDirectory());
  assert.deepEqual(dossiers, [], 'aucune page d’article ne doit être générée');
});

test('l’encart en direct utilise les libellés de filieres.py (via filieres.json)', () => {
  const taxo = JSON.parse(readFileSync(join(RACINE, 'src/data/filieres.json'), 'utf-8'));
  const html = lire('index.html');
  for (const k of taxo.ordre) assert.ok(html.includes(taxo.libelles[k]), taxo.libelles[k]);
  assert.ok(html.includes('Biomasse (ex-Charbon)') && html.includes('Bioliquide (ex-Diesel)'));
  assert.match(html, /EDF Réunion, open data/);
  assert.match(html, /estimé/);
});

test('chiffres clés 2024 affichés avec leur source OER', () => {
  const html = lire('index.html');
  for (const v of ['92,4 %', '31,2 %', '1 035 MW', '77 g']) assert.ok(html.includes(v), v);
  assert.match(html, /oer\.energies-reunion\.com/);
});

test('les vidéos sont servies par le site, avec lecteur natif et transcription', () => {
  const html = lire('comprendre/index.html');
  assert.equal((html.match(/<video /g) || []).length, 2);
  assert.match(html, /preload="metadata"/);
  assert.doesNotMatch(html, /youtube|vimeo|dailymotion/i);
  for (const f of ['le-courant-de-l-ile.mp4', 'les-megawatts-de-l-ile.mp4', 'le-courant-de-l-ile-affiche.webp', 'les-megawatts-de-l-ile-affiche.webp']) {
    assert.ok(existsSync(join(DIST, 'videos', f)), f);
  }
  assert.match(html, /Transcription/);
  assert.match(html, /Glossaire/);
});

test('mentions légales : contact laissé à compléter, jamais inventé', () => {
  const html = lire('mentions-legales/index.html');
  assert.match(html, /À_COMPLÉTER_PAR_Z/);
  assert.doesNotMatch(html, /[\w.+-]+@[\w-]+\.[a-z]{2,}/i, 'aucune adresse e-mail ne doit apparaître');
  assert.match(html, /GitHub Inc\./);
});

test('aucune STEP présentée comme en service, Tanika daté 2033', () => {
  const html = lire('installations/tanika/index.html');
  assert.match(html, /2033/);
  assert.match(html, /aucune STEP n’est en service/i);
});
