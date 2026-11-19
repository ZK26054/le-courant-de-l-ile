import sys, os, subprocess
import cairo
from core import W, H, FPS, C, hx
import importlib
SCENES = importlib.import_module(os.environ.get('SCN','scenes')).SCENES

FADE = 0.45
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get('OUTDIR', os.path.join(HERE, 'out'))
FFMPEG = os.environ.get('FFMPEG', 'ffmpeg')  # chemin complet de ffmpeg.exe si absent du PATH
os.makedirs(OUT, exist_ok=True)

def draw_frame(surf, idx, t):
    D, fn = SCENES[idx]
    ctx = cairo.Context(surf)
    fn(ctx, t, D)
    a = 1.0
    if t < FADE and idx > 0:
        a = t / FADE
    if t > D - FADE and idx < len(SCENES) - 1:
        a = min(a, (D - t) / FADE)
    if idx == 0 and t < 0.3:
        a = t / 0.3
    if idx == len(SCENES) - 1 and t > D - 1.0:
        a = (D - t) / 1.0
    if a < 1:
        ctx.set_source_rgba(*hx(C['bg'], 1 - max(0, a)))
        ctx.paint()
    return surf

def still(idx, t, path):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    draw_frame(surf, idx, t)
    surf.write_to_png(path)

def render(idx):
    D, _ = SCENES[idx]
    n = int(round(D * FPS))
    tmp = os.path.join(OUT, f'scene_{idx:02d}.tmp.mp4')
    final = os.path.join(OUT, f'scene_{idx:02d}.mp4')
    p = subprocess.Popen([FFMPEG, '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgra',
                          '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast',
                          '-crf', '18', '-pix_fmt', 'yuv420p', '-r', str(FPS), tmp], stdin=subprocess.PIPE)
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    for f in range(n):
        draw_frame(surf, idx, f / FPS)
        surf.flush()
        p.stdin.write(bytes(surf.get_data()))
    p.stdin.close()
    if p.wait() == 0:
        os.replace(tmp, final)
        print('ok', idx, n, flush=True)
    else:
        print('FAIL', idx, flush=True)

if __name__ == '__main__':
    if sys.argv[1] == 'still':
        still(int(sys.argv[2]), float(sys.argv[3]), sys.argv[4])
    else:
        for i in sys.argv[2:]:
            render(int(i))
