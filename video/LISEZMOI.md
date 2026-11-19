# Sources des vidéos motion design

- `core.py` : moteur de dessin (cairo + Pillow), palette, île, textes.
- `scenes.py` : vidéo 1 « Le courant de l'île » (14 scènes, 182 s).
- `scenes2.py` : vidéo 2 « Les mégawatts de l'île » (10 scènes, 129 s).
- `render.py` : encode les scènes, ou produit une image fixe (`still`).
- `audio.py` : musique synthétisée (mêmes variables `SCN` et `OUTDIR`).
- `fonts/` : Bricolage Grotesque et JetBrains Mono (licence OFL 1.1). **Inter est requise aussi** : déposer `Inter-Light.otf`, `Inter-Regular.otf`, `Inter-Medium.otf`, `Inter-SemiBold.otf`, `Inter-Bold.otf` et `Inter-ExtraBold.otf` (OFL, https://github.com/rsms/inter) dans `video/fonts/`.
- `prod-electricite-temps-reel-974.csv` : journée réelle EDF (7-8 mars 2026) utilisée par la scène « une journée réelle » de la vidéo 1.

Les rendus finaux (MP4) sont publiés dans `site/public/videos/`.

## Chemins (corrigés le 19/11/2026 pour Windows)

Les chemins Linux codés en dur (`/root/.fonts`, `/usr/share/fonts`, `/mnt/user-data/uploads`, `/home/claude/video/out`) ont été remplacés par des chemins **relatifs au dossier `video/`** :

| Élément | Emplacement | Surcharge possible |
|---|---|---|
| Polices | `video\fonts\` | variable `FONT_DIR` |
| CSV EDF | `video\prod-electricite-temps-reel-974.csv` | — |
| Sorties (scènes, musique) | `video\out\` | variable `OUTDIR` |
| ffmpeg | `ffmpeg` dans le PATH | variable `FFMPEG` (chemin complet de `ffmpeg.exe`) |

## Relancer un rendu sous Windows (PowerShell)

Prérequis : Python 3.12 avec `pycairo`, `Pillow` et `numpy`, ainsi que ffmpeg. Les commandes se lancent depuis le dossier `video\`.

```powershell
cd C:\Users\Fdinf\dashboard-reunion\video
# Vidéo 1, scènes 0 à 2 :
$env:SCN = "scenes"; $env:OUTDIR = "out1"; python render.py render 0 1 2
# Vidéo 2 :
$env:SCN = "scenes2"; $env:OUTDIR = "out2"; python render.py render 0 1 2
# Image fixe : scène 3 à t = 5 s
python render.py still 3 5.0 image.png
# Musique :
python audio.py
```

## Assemblage

Concaténer les `scene_XX.mp4` avec ffmpeg (fichier liste + `-f concat`), puis ajouter `music.wav` :

```powershell
Get-ChildItem out1\scene_*.mp4 | Sort-Object Name | ForEach-Object { "file '$($_.FullName)'" } | Set-Content -Encoding ascii out1\liste.txt
ffmpeg -f concat -safe 0 -i out1\liste.txt -i out1\music.wav -c:v copy -c:a aac -shortest Le-courant-de-l-ile.mp4
```

Aucun rendu n'a été relancé lors de la correction des chemins.
