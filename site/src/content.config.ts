// Collections de contenu — schémas VALIDÉS au build (zod) : une fiche incomplète
// ou mal sourcée fait échouer la compilation.
import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

const niveau = z.enum(['N1', 'N2', 'N3']); // N1 institutionnel, N2 exploitant/porteur, N3 presse/contributif

const source = z.object({
  titre: z.string().min(3),
  editeur: z.string().min(2),
  niveau,
  date: z.string().min(4), // date de publication ou « consulté le … »
  url: z.string().url().optional(),
});

const valeurSourcee = z.object({
  valeur: z.string().min(1),
  date: z.string().min(4),
  perimetre: z.string().min(3),
  source: z.string().min(3),
});

const installations = defineCollection({
  loader: glob({ pattern: '*.md', base: './src/content/installations' }),
  schema: z
    .object({
      nom: z.string().min(3),
      exploitant: z.string().min(2),
      filiere: z.enum([
        'solaire', 'hydraulique', 'eolien', 'bagasse-granules', 'colza', 'turbines', 'biogaz', 'secours', 'batteries', 'csr', 'stockage-step', 'geothermie',
      ]),
      statut: z.enum(['en service', 'à l’arrêt', 'engagé', 'annoncé', 'projet', 'permis de recherche']),
      statut_detail: z.string().optional(),
      puissance_mw: z.number().nonnegative().nullable(),
      puissance_source: z.string().min(5),
      puissances_divergentes: z.array(valeurSourcee).default([]),
      mise_en_service: z.string().min(4), // année/date, ou « non documentée »
      mise_en_service_source: z.string().optional(),
      combustible: z.string().min(2), // ou « aucun (…) »
      commune: z.string().min(2),
      coordonnees: z.object({
        lat: z.number().min(-21.45).max(-20.8).nullable(),
        lon: z.number().min(55.15).max(55.9).nullable(),
        precision: z.enum(['osm', 'approximative', 'inconnue']),
        osm: z.string().optional(), // ex. « way/718019336 »
      }),
      sources: z.array(source).min(1),
      derniere_verification: z.string().regex(/^\d{4}-\d{2}-\d{2}$/),
      image: z.string().optional(), // chemin déclaré dans src/data/images.json
      resume: z.string().min(10),
      ordre: z.number().default(100),
    })
    .superRefine((d, ctx) => {
      if (d.coordonnees.precision !== 'inconnue' && (d.coordonnees.lat === null || d.coordonnees.lon === null)) {
        ctx.addIssue({ code: 'custom', message: 'coordonnées obligatoires sauf précision « inconnue »' });
      }
      if (d.coordonnees.precision === 'osm' && !d.coordonnees.osm) {
        ctx.addIssue({ code: 'custom', message: 'précision « osm » sans identifiant d’objet OSM' });
      }
      if (d.puissance_mw === null && d.statut === 'en service') {
        ctx.addIssue({ code: 'custom', message: 'une installation en service doit avoir une puissance' });
      }
    }),
});

const articles = defineCollection({
  // LIGNE-EDITORIALE.md et les fichiers commençant par « _ » ne sont pas des articles.
  loader: glob({ pattern: ['*.md', '!LIGNE-EDITORIALE.md', '!_*.md'], base: './src/content/articles' }),
  schema: z.object({
    titre: z.string().min(5),
    date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/),
    derniere_verification: z.string().regex(/^\d{4}-\d{2}-\d{2}$/),
    auteur: z.string().min(2),
    chapo: z.string().min(10),
    draft: z.boolean().default(true),
    sources: z.array(source).min(1),
  }),
});

export const collections = { installations, articles };
