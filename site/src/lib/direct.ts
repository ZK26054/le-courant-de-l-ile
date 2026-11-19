// Nettoyage des relevés temps réel EDF (fonction pure, testée par tests/direct.test.mjs).
// - garde la fenêtre des 24 h précédant le relevé le plus récent ;
// - dédoublonne par date (l'API sert des lignes de date identique) ;
// - écarte les relevés incomplets (champ vide) ou incohérents : le total publié est la
//   somme ALGÉBRIQUE des 8 filières (écart observé ≤ 0,001 MW), négatifs compris.
//   Un relevé écarté n'est jamais tracé à zéro.
// - ne modifie aucune valeur : les négatifs (stockage en recharge) sont conservés.

export type Ligne = { t: number; statut: string; total: number; v: Record<string, number> };

export function nettoyer(brut: any[], api2int: Record<string, string>, fenetreMs = 24 * 3600e3): { lignes: Ligne[]; ecartees: number } {
  if (!brut.length) return { lignes: [], ecartees: 0 };
  const fin = Math.max(...brut.map((r) => Date.parse(r.date)).filter((t) => !Number.isNaN(t)));
  const champs = Object.keys(api2int);
  const vu = new Map<number, Ligne>();
  let ecartees = 0;
  for (const r of brut) {
    const t = Date.parse(r.date);
    if (Number.isNaN(t) || t < fin - fenetreMs || vu.has(t)) continue;
    if (champs.some((c) => r[c] === null || r[c] === undefined || r[c] === '') || r.total == null) { ecartees++; continue; }
    const v: Record<string, number> = {};
    for (const [api, k] of Object.entries(api2int)) v[k] = Number(r[api]);
    const total = Number(r.total);
    const somme = Object.values(v).reduce((s, x) => s + x, 0);
    if (!Number.isFinite(total) || !Number.isFinite(somme) || Math.abs(somme - total) > Math.max(5, 0.02 * Math.abs(total))) { ecartees++; continue; }
    vu.set(t, { t, statut: String(r.statut ?? ''), total, v });
  }
  return { lignes: [...vu.values()].sort((a, b) => a.t - b.t), ecartees };
}
