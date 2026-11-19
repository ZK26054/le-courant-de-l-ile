"""Moteur de rendu : cairo pour les formes, Pillow pour le texte (polices variables)."""
import math, os, re
from pathlib import Path
import numpy as np
import cairo
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1920, 1080, 30

# ── Palette : océan Indien de nuit, basalte, couleurs des filières ──
def hx(h, a=1.0):
    h = h.lstrip('#')
    return (int(h[0:2], 16) / 255, int(h[2:4], 16) / 255, int(h[4:6], 16) / 255, a)

C = {
    'bg': '#0A1C27', 'bg2': '#0F2735', 'grid': '#173444',
    'island': '#18282E', 'contour': '#2C4650', 'coast': '#6F8F98',
    'text': '#EEF2EE', 'muted': '#8EA6AE', 'faint': '#4E6A75',
    'lava': '#FF6B3D',
    'hydro': '#38B6CC', 'pv': '#F5C24C', 'eolien': '#A9DCD0',
    'bagasse': '#8CC65A', 'biogaz': '#5E9E4A',
    'pellets': '#C9874C', 'colza': '#B3A64A',
    'charbon': '#6E7882', 'fioul': '#C8463B', 'tac': '#FF6B3D',
}

# Chemins relatifs au dossier video/ (portables Windows / Linux / macOS).
# FONT_DIR peut être surchargé par variable d'environnement.
HERE = Path(__file__).resolve().parent
FONT_DIR = Path(os.environ.get('FONT_DIR', HERE / 'fonts'))
FONT_PATHS = {
    'display': str(FONT_DIR / 'BricolageGrotesque[opsz,wdth,wght].ttf'),
    'mono': str(FONT_DIR / 'JetBrainsMono[wght].ttf'),
}
INTER = {300: 'Light', 400: 'Regular', 500: 'Medium', 600: 'SemiBold', 700: 'Bold', 800: 'ExtraBold'}
# Inter n'est pas fournie dans l'archive : déposer Inter-Light.otf … Inter-ExtraBold.otf
# (licence OFL, https://github.com/rsms/inter) dans video/fonts/.

_fonts = {}
def font(kind, size, wght):
    key = (kind, size, wght)
    if key in _fonts:
        return _fonts[key]
    if kind == 'display':
        f = ImageFont.truetype(FONT_PATHS['display'], size)
        f.set_variation_by_axes([max(12, min(96, size)), wght, 100])
    elif kind == 'mono':
        f = ImageFont.truetype(FONT_PATHS['mono'], size)
        f.set_variation_by_axes([wght])
    else:
        f = ImageFont.truetype(str(FONT_DIR / f'Inter-{INTER[wght]}.otf'), size)
    _fonts[key] = f
    return f

_tcache = {}
def text_surface(s, kind, size, wght, color, spacing=0):
    key = (s, kind, size, wght, color, spacing)
    if key in _tcache:
        return _tcache[key]
    f = font(kind, size, wght)
    asc, desc = f.getmetrics()
    pad = 6
    if spacing:
        widths = [f.getlength(ch) + spacing for ch in s]
        tw = sum(widths) - (spacing if s else 0)
    else:
        tw = f.getlength(s)
    w = int(math.ceil(tw)) + 2 * pad
    h = asc + desc + 2 * pad
    img = Image.new('RGBA', (max(w, 1), h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    r, g, b, _ = hx(color)
    col = (int(r * 255), int(g * 255), int(b * 255), 255)
    if spacing:
        x = pad
        for ch, cw in zip(s, widths):
            d.text((x, pad + asc), ch, font=f, fill=col, anchor='ls')
            x += cw
    else:
        d.text((pad, pad + asc), s, font=f, fill=col, anchor='ls')
    arr = np.asarray(img).astype(np.float32)
    a = arr[..., 3:4] / 255.0
    pm = np.concatenate([arr[..., 2:3] * a, arr[..., 1:2] * a, arr[..., 0:1] * a, arr[..., 3:4]], axis=2)
    buf = bytearray(pm.astype(np.uint8).tobytes())
    surf = cairo.ImageSurface.create_for_data(buf, cairo.FORMAT_ARGB32, img.width, img.height, img.width * 4)
    res = (surf, tw, pad, pad + asc, buf)
    if len(_tcache) > 4000:
        _tcache.clear()
    _tcache[key] = res
    return res

def text_width(s, kind, size, wght, spacing=0):
    f = font(kind, size, wght)
    if spacing:
        return sum(f.getlength(ch) + spacing for ch in s) - spacing
    return f.getlength(s)

def text(ctx, s, x, y, size=40, kind='body', wght=400, color=None, alpha=1.0, align='l', reveal=1.0, spacing=0):
    """Dessine s avec sa ligne de base en y. reveal<1 : volet de gauche à droite."""
    if alpha <= 0.003 or not s:
        return 0
    color = color or C['text']
    surf, tw, pad, base, _ = text_surface(s, kind, size, wght, color, spacing)
    if align == 'c':
        x -= tw / 2
    elif align == 'r':
        x -= tw
    ox, oy = x - pad, y - base
    ctx.save()
    if reveal < 1:
        ctx.rectangle(ox, oy - 4, pad + tw * max(0, reveal) + 2, surf.get_height() + 8)
        ctx.clip()
    ctx.set_source_surface(surf, ox, oy)
    ctx.paint_with_alpha(min(1, alpha))
    ctx.restore()
    return tw

def nbsp(s):
    s = re.sub(r'(\d) ', '\\1\u00a0', s)
    return re.sub(r' ([:;!?%»])', '\u00a0\\1', s)

def wrap(s, size, maxw, kind='body', wght=400):
    s = nbsp(s)
    words, lines, cur = s.split(' '), [], ''
    for wd in words:
        trial = (cur + ' ' + wd).strip()
        if text_width(trial, kind, size, wght) <= maxw or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines

# ── Temps / easing ──
def clamp(v, a=0.0, b=1.0):
    return max(a, min(b, v))

def prog(t, t0, d):
    return clamp((t - t0) / d) if d > 0 else (1.0 if t >= t0 else 0.0)

def eo(p):  # ease out cubic
    return 1 - (1 - p) ** 3

def eio(p):
    return 4 * p ** 3 if p < 0.5 else 1 - (-2 * p + 2) ** 3 / 2

def lerp(a, b, p):
    return a + (b - a) * p

def appear(t, t0, d=0.7):
    return eo(prog(t, t0, d))

def para(ctx, s, x, y, t, t0, size=40, maxw=700, kind='body', wght=400, color=None, lh=1.32, stagger=0.18, align='l', out=None):
    """Paragraphe révélé ligne par ligne (glisse + fondu). Retourne y après le bloc."""
    lines = wrap(s, size, maxw, kind, wght)
    for i, ln in enumerate(lines):
        p = appear(t, t0 + i * stagger, 0.8)
        a = p if out is None else p * (1 - appear(t, out, 0.5))
        text(ctx, ln, x, y + (1 - p) * 26, size, kind, wght, color, a, align)
        y += size * lh
    return y

def eyebrow(ctx, s, x, y, t, t0, color=None, align='l'):
    p = appear(t, t0, 0.8)
    text(ctx, s.upper(), x, y, 22, 'mono', 500, color or C['lava'], p, align, reveal=p, spacing=3)

def source(ctx, s, t, t0=0.6, x=120, y=H - 64):
    text(ctx, s, x, y, 19, 'mono', 400, C['faint'], appear(t, t0, 1.0))

# ── Fond ──
def background(ctx, grid=False):
    g = cairo.LinearGradient(0, 0, 0, H)
    g.add_color_stop_rgba(0, *hx(C['bg']))
    g.add_color_stop_rgba(1, *hx(C['bg2']))
    ctx.set_source(g)
    ctx.paint()
    if grid:
        ctx.set_line_width(1)
        ctx.set_source_rgba(*hx(C['grid'], 0.55))
        for gx in range(0, W + 1, 120):
            ctx.move_to(gx + .5, 0); ctx.line_to(gx + .5, H)
        for gy in range(0, H + 1, 120):
            ctx.move_to(0, gy + .5); ctx.line_to(W, gy + .5)
        ctx.stroke()

# ── Île de La Réunion (trait de côte simplifié, lon/lat WGS84) ──
COAST = [
    (55.448, -20.876), (55.53, -20.893), (55.605, -20.905), (55.665, -20.945), (55.715, -21.000),
    (55.762, -21.060), (55.800, -21.120), (55.835, -21.200), (55.840, -21.270), (55.800, -21.355),
    (55.730, -21.385), (55.640, -21.386), (55.560, -21.370), (55.480, -21.345), (55.420, -21.300),
    (55.360, -21.275), (55.310, -21.210), (55.280, -21.160), (55.240, -21.080), (55.220, -21.040),
    (55.250, -21.000), (55.285, -20.940), (55.320, -20.930), (55.370, -20.920), (55.410, -20.877),
]
ISL_C = (55.53, -21.13)
COSL = math.cos(math.radians(21.13))

class Island:
    def __init__(self, cx, cy, scale):
        self.cx, self.cy, self.s = cx, cy, scale

    def xy(self, lon, lat):
        return (self.cx + (lon - ISL_C[0]) * COSL * self.s, self.cy - (lat - ISL_C[1]) * self.s)

    def path(self, ctx, shrink=1.0, center=None):
        cen = center or ISL_C
        pts = []
        for lon, lat in COAST:
            lo = cen[0] + (lon - cen[0]) * shrink
            la = cen[1] + (lat - cen[1]) * shrink
            pts.append(self.xy(lo, la))
        n = len(pts)
        ctx.move_to(*pts[0])
        for i in range(n):  # Catmull-Rom fermé
            p0, p1, p2, p3 = pts[i - 1], pts[i], pts[(i + 1) % n], pts[(i + 2) % n]
            c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
            c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
            ctx.curve_to(*c1, *c2, *p2)
        ctx.close_path()

    def draw(self, ctx, alpha=1.0, draw_p=1.0, relief=True):
        if draw_p < 1:  # tracé progressif du trait de côte
            self.path(ctx)
            flat = ctx.copy_path_flat()
            ctx.new_path()
            pts = [(p[1][0], p[1][1]) for p in flat if p[0] in (0, 1)]
            k = max(2, int(len(pts) * draw_p))
            ctx.move_to(*pts[0])
            for p in pts[1:k]:
                ctx.line_to(*p)
            ctx.set_source_rgba(*hx(C['coast'], alpha))
            ctx.set_line_width(2.5)
            ctx.stroke()
            return
        self.path(ctx)
        ctx.set_source_rgba(*hx(C['island'], alpha))
        ctx.fill_preserve()
        ctx.set_source_rgba(*hx(C['coast'], 0.9 * alpha))
        ctx.set_line_width(2)
        ctx.stroke()
        if relief:  # courbes de niveau : Piton des Neiges et Piton de la Fournaise
            ctx.set_line_width(1.2)
            for k in (0.78, 0.58, 0.40, 0.24):
                self.path(ctx, k, (55.48, -21.10))
                ctx.set_source_rgba(*hx(C['contour'], alpha * 0.9))
                ctx.stroke()
            for k in (0.30, 0.18, 0.08):
                self.path(ctx, k, (55.71, -21.24))
                ctx.set_source_rgba(*hx(C['contour'], alpha * 0.9))
                ctx.stroke()

SITES = {
    'riviere_est': (55.765, -21.135, 'Rivière de l\'Est'),
    'takamaka': (55.625, -21.075, 'Takamaka'),
    'port_est': (55.298, -20.937, 'Port-Est'),
    'bois_rouge': (55.652, -20.915, 'Bois-Rouge'),
    'le_gol': (55.395, -21.282, 'Le Gol'),
    'st_pierre': (55.505, -21.335, 'TAC Saint-Pierre'),
    'la_baie': (55.282, -20.950, 'TAC La Baie'),
    'orgues': (55.735, -21.165, ''),
}

def marker(ctx, x, y, color, a=1.0, r=11, pulse=None):
    if a <= 0:
        return
    if pulse is not None:
        pr = r + 26 * pulse
        ctx.arc(x, y, pr, 0, 2 * math.pi)
        ctx.set_source_rgba(*hx(color, a * (1 - pulse) * 0.8))
        ctx.set_line_width(2)
        ctx.stroke()
    ctx.arc(x, y, r, 0, 2 * math.pi)
    ctx.set_source_rgba(*hx(color, a))
    ctx.fill()
    ctx.arc(x, y, r * 0.38, 0, 2 * math.pi)
    ctx.set_source_rgba(*hx(C['bg'], a))
    ctx.fill()

def mix(c1, c2, p):
    a, b = hx(c1), hx(c2)
    r = [lerp(a[i], b[i], p) for i in range(3)]
    return '#%02X%02X%02X' % tuple(int(v * 255) for v in r)

def rrect(ctx, x, y, w, h, r):
    r = min(r, w / 2, h / 2)
    ctx.new_sub_path()
    ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    ctx.arc(x + r, y + r, r, math.pi, 1.5 * math.pi)
    ctx.close_path()

def fill(ctx, color, a=1.0):
    ctx.set_source_rgba(*hx(color, a))
    ctx.fill()

def line(ctx, x1, y1, x2, y2, color, a=1.0, w=1.5, dash=None):
    ctx.save()
    if dash:
        ctx.set_dash(dash)
    ctx.move_to(x1, y1); ctx.line_to(x2, y2)
    ctx.set_source_rgba(*hx(color, a)); ctx.set_line_width(w); ctx.stroke()
    ctx.restore()

def fmt(v, dec=1):
    s = f'{v:.{dec}f}'.replace('.', ',')
    return s
