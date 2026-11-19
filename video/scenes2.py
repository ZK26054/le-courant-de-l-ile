"""Vidéo 2 : la puissance installée sur l'île (parc au 31/12/2024, OER) + nouveautés 2026."""
import math, random
import cairo
from core import *

C.update({'secours': '#5C6E77', 'bat': '#A08CE6'})
X0 = 120

# Parc au 31/12/2024 — Observatoire Énergie Réunion, chiffres clés 2024 (éd. 2025)
PARC = [
    ('pv', 'Solaire', 312.1),
    ('colza', 'Huile de colza · Port-Est', 211.0),
    ('pellets', 'Biomasse · Le Gol, Bois-Rouge', 196.0),
    ('hydro', 'Hydraulique', 134.4),
    ('tac', 'Turbines à combustion', 121.0),
    ('secours', 'Groupes de secours', 24.0),
    ('eolien', 'Éolien', 19.8),
    ('bat', 'Batteries', 10.0),
    ('biogaz', 'Biogaz', 6.9),
]

# ───────── S0 · Titre
def s_title(ctx, t, D):
    background(ctx)
    isl = Island(1400, 560, 1250)
    isl.draw(ctx, appear(t, 0.2, 1.0))
    eyebrow(ctx, 'La Réunion · parc électrique · 2024-2026', X0, 330, t, 0.5)
    p1, p2 = appear(t, 0.8, 1.0), appear(t, 1.15, 1.0)
    text(ctx, 'Les mégawatts', X0, 470, 120, 'display', 800, C['text'], p1, reveal=p1)
    text(ctx, 'de l\'île', X0, 590, 120, 'display', 800, C['text'], p2, reveal=p2)
    para(ctx, 'Qui produit l\'électricité de La Réunion, où, et avec quelle puissance.', X0, 680, t, 2.0, 32, 640, color=C['muted'])
    v = 1035 * eio(prog(t, 2.6, 2.4))
    a = appear(t, 2.5, .6)
    text(ctx, f'{v:,.0f} MW'.replace(',', ' '), 1400, 575, 110, 'display', 800, C['lava'], a, 'c')
    text(ctx, 'INSTALLÉS FIN 2024', 1400, 630, 24, 'mono', 600, C['text'], appear(t, 4.0, .6), 'c', spacing=3)

# ───────── S1 · Puissance ou énergie ?
def s_units(ctx, t, D):
    background(ctx)
    eyebrow(ctx, 'Deux unités à ne pas confondre', X0, 220, t, .3)
    text(ctx, 'Puissance ou énergie ?', X0, 310, 76, 'display', 800, C['text'], appear(t, .5, .8), reveal=appear(t, .5, .9))
    # colonne MW
    cx = [X0, 1000]
    a1 = appear(t, 1.5, .7)
    text(ctx, 'MW', cx[0], 470, 110, 'display', 800, C['lava'], a1)
    text(ctx, 'mégawatt · la puissance', cx[0], 525, 28, 'mono', 500, C['muted'], a1)
    para(ctx, 'Ce qu\'une centrale peut fournir à un instant donné. C\'est la taille du robinet.', cx[0], 590, t, 2.0, 34, 760)
    a2 = appear(t, 4.6, .7)
    text(ctx, 'MWh', cx[1], 470, 110, 'display', 800, C['hydro'], a2)
    text(ctx, 'mégawattheure · l\'énergie', cx[1], 525, 28, 'mono', 500, C['muted'], a2)
    para(ctx, 'Ce qu\'elle produit vraiment dans la durée. C\'est l\'eau qui a coulé.', cx[1], 590, t, 5.1, 34, 760)
    # robinet / réservoir animé
    ga = appear(t, 2.6, .6)
    bx, by, bw = X0, 780, 640
    rrect(ctx, bx, by, bw, 26, 13); fill(ctx, C['grid'], ga)
    rrect(ctx, bx, by, bw * 0.8 * ga, 26, 13); fill(ctx, C['lava'], ga)
    text(ctx, '1 MW ouvert en grand', bx, by + 70, 24, 'mono', 500, C['muted'], ga)
    fa = appear(t, 5.6, .6)
    if fa > 0:
        hrs = 24 * eio(prog(t, 5.8, 4.5))
        tx, ty, tw, th = 1000, 700, 640, 110
        rrect(ctx, tx, ty, tw, th, 10)
        ctx.set_source_rgba(*hx(C['hydro'], fa)); ctx.set_line_width(2); ctx.stroke()
        rrect(ctx, tx + 4, ty + th - 4 - (th - 8) * hrs / 24, tw - 8, (th - 8) * hrs / 24, 7) if hrs > 0.2 else None
        if hrs > 0.2:
            fill(ctx, C['hydro'], 0.85 * fa)
        text(ctx, f'pendant {hrs:4.1f} h = {hrs:4.1f} MWh'.replace('.', ','), tx, ty + 150, 24, 'mono', 500, C['muted'], fa)

# ───────── S2 · Treemap du parc
def squarify(items, x, y, w, h):
    """items: liste (clé, valeur) triée décroissante -> rectangles (clé, x, y, w, h)."""
    out = []
    items = list(items)
    total = sum(v for _, v in items)
    scale = w * h / total
    vals = [(k, v * scale) for k, v in items]

    def worst(row, side):
        s = sum(a for _, a in row)
        return max(max(side * side * a / (s * s), (s * s) / (side * side * a)) for _, a in row)

    while vals:
        side = min(w, h)
        row = [vals.pop(0)]
        while vals and worst(row + [vals[0]], side) <= worst(row, side):
            row.append(vals.pop(0))
        s = sum(a for _, a in row)
        if w >= h:
            cw = s / h
            yy = y
            for k, a in row:
                out.append((k, x, yy, cw, a / cw)); yy += a / cw
            x += cw; w -= cw
        else:
            rh = s / w
            xx = x
            for k, a in row:
                out.append((k, xx, y, a / rh, rh)); xx += a / rh
            y += rh; h -= rh
    return out

SHORT = {'colza': 'Huile de colza', 'pellets': 'Biomasse', 'secours': 'Secours'}
RECTS = squarify([(k, v) for k, _, v in PARC], 120, 330, 1680, 620)
LAB = {k: (lab, v) for k, lab, v in PARC}

def s_treemap(ctx, t, D):
    background(ctx)
    eyebrow(ctx, 'Parc installé au 31 décembre 2024', X0, 200, t, .3)
    text(ctx, '1 035 MW, filière par filière.', X0, 285, 70, 'display', 800, C['text'], appear(t, .5, .8), reveal=appear(t, .5, .9))
    g = 4
    for i, (k, x, y, w, h) in enumerate(RECTS):
        p = eo(prog(t, 1.3 + i * 0.45, 0.8))
        if p <= 0:
            continue
        cx, cy = x + w / 2, y + h / 2
        ww, hh = (w - g) * p, (h - g) * p
        rrect(ctx, cx - ww / 2, cy - hh / 2, ww, hh, 8)
        fill(ctx, C[k], 0.95)
        lab, v = LAB[k]
        lab = SHORT.get(k, lab)
        dark = k in ('pv', 'eolien', 'bagasse', 'hydro', 'colza', 'pellets', 'bat')
        tc = C['bg'] if dark else C['text']
        la = appear(t, 1.3 + i * 0.45 + 0.6, .5)
        if w > 300 and h > 160:
            text(ctx, fmt(v, 1 if v != int(v) else 0) + ' MW', x + 26, y + 80, 58, 'display', 800, tc, la)
            text(ctx, lab, x + 28, y + 122, 26, 'body', 600, tc, la)
            text(ctx, fmt(v / 1035 * 100, 0) + ' % du parc', x + 28, y + 158, 22, 'mono', 500, tc, la * 0.85)
        elif w > 120 and h > 70:
            text(ctx, fmt(v, 1 if v != int(v) else 0), x + 14, y + 38, 28, 'display', 800, tc, la)
            text(ctx, lab.split(' ')[0], x + 14, y + 66, 18, 'body', 600, tc, la)
        else:
            text(ctx, fmt(v, 1 if v != int(v) else 0), x + w / 2, y + h / 2 + 7, 18, 'mono', 700, tc, la, 'c')
    # légende des petits blocs
    la = appear(t, 6.0, .8)
    small = [k for k, x, y, w, h in RECTS if not (w > 120 and h > 70)]
    xx = X0
    for k in small:
        rrect(ctx, xx, 984, 18, 18, 3); fill(ctx, C[k], la)
        wd = text(ctx, LAB[k][0], xx + 28, 1000, 22, 'body', 500, C['muted'], la)
        xx += wd + 60
    source(ctx, 'Source : Observatoire Énergie Réunion, Bilan énergétique, chiffres clés 2024 (édition 2025) · puissances contractuelles', t, y=H - 32)

# ───────── S3 · Carte des puissances
MAP_SITES = [  # clé couleur, lon, lat, MW, nom, côté étiquette
    ('colza', 55.300, -20.936, 211.0, 'Port-Est', 't'),
    ('tac', 55.275, -20.962, 80.0, 'TAC La Baie', 'l'),
    ('pellets', 55.392, -21.282, 104.0, 'Le Gol', 'l'),
    ('pellets', 55.652, -20.915, 92.0, 'Bois-Rouge', 'r'),
    ('tac', 55.505, -21.334, 41.0, 'TAC Saint-Pierre', 'b'),
    ('hydro', 55.765, -21.135, 80.0, 'Rivière de l\'Est', 'b'),
    ('hydro', 55.625, -21.075, 43.4, 'Takamaka', 'l'),
    ('eolien', 55.598, -20.906, 19.8, 'Éolien Sainte-Suzanne', 't'),
    ('hydro', 55.470, -21.250, 4.6, '', 'l'),
    ('hydro', 55.640, -21.350, 3.6, '', 'b'),
    ('bat', 55.290, -21.170, 5.0, 'Batterie Saint-Leu', 'l'),
]

def pip(x, y, poly):
    inside = False
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]; x2, y2 = poly[(i + 1) % n]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            inside = not inside
    return inside

random.seed(974)
PV_DOTS = []
while len(PV_DOTS) < 420:
    lon = random.uniform(55.22, 55.84); lat = random.uniform(-21.39, -20.87)
    if not pip(lon, lat, COAST):
        continue
    # densité : près des côtes urbanisées (nord, ouest, sud), faible dans les Hauts et sur la côte sud-est
    d = min(math.hypot((lon - a) * COSL, lat - b) for a, b in COAST)
    w = math.exp(-d / 0.035)
    if lon > 55.72 and lat < -21.17:
        w *= 0.15
    if random.random() < w:
        PV_DOTS.append((lon, lat, random.random()))

def s_map(ctx, t, D):
    background(ctx)
    isl = Island(1410, 600, 1150)
    isl.draw(ctx, appear(t, 0, .6))
    eyebrow(ctx, 'Où sont les mégawatts ?', X0, 220, t, .3)
    text(ctx, 'Quelques gros sites,', X0, 305, 60, 'display', 800, C['text'], appear(t, .5, .8), reveal=appear(t, .5, .9))
    text(ctx, 'des centaines de toits.', X0, 375, 60, 'display', 800, C['pv'], appear(t, 9.0, .8), reveal=appear(t, 9.0, .9))
    para(ctx, 'Sept centrales thermiques et hydrauliques concentrent 63 % de la puissance installée.',
         X0, 460, t, 1.4, 32, 560)
    para(ctx, 'Le solaire, lui, est éparpillé : 312 MW répartis entre fermes solaires, hangars, écoles et maisons.',
         X0, 640, t, 9.6, 32, 560)
    # points solaires
    for i, (lon, lat, r) in enumerate(PV_DOTS):
        a = appear(t, 9.2 + r * 3.0, .4)
        if a <= 0:
            continue
        x, y = isl.xy(lon, lat)
        ctx.arc(x, y, 3.2, 0, 2 * math.pi)
        fill(ctx, C['pv'], 0.85 * a)
    # cercles proportionnels
    for i, (k, lon, lat, mw, name, side) in enumerate(MAP_SITES):
        x, y = isl.xy(lon, lat)
        p = eo(prog(t, 1.8 + i * 0.5, 0.7))
        r = 5.6 * math.sqrt(mw) * p
        if r <= 0:
            continue
        ctx.arc(x, y, r, 0, 2 * math.pi)
        fill(ctx, C[k], 0.55)
        ctx.arc(x, y, r, 0, 2 * math.pi)
        ctx.set_source_rgba(*hx(C[k], 1)); ctx.set_line_width(2); ctx.stroke()
        la = appear(t, 2.2 + i * 0.5, .5) * (1 - 0.6 * appear(t, 9.0, .6) if mw < 10 else 1)
        if not name:
            continue
        lbl = f'{name} · {fmt(mw, 1 if mw != int(mw) else 0)} MW'
        R = 5.6 * math.sqrt(mw)
        if side == 'l':
            text(ctx, lbl, x - R - 10, y + 8, 22, 'body', 600, C['text'], la, 'r')
        elif side == 'r':
            text(ctx, lbl, x + R + 10, y + 8, 22, 'body', 600, C['text'], la)
        elif side == 't':
            text(ctx, lbl, x, y - R - 12, 22, 'body', 600, C['text'], la, 'c')
        else:
            text(ctx, lbl, x, y + R + 30, 22, 'body', 600, C['text'], la, 'c')
    text(ctx, 'Surface des cercles proportionnelle à la puissance · emplacements approximatifs du solaire',
         X0, H - 70, 19, 'mono', 400, C['faint'], appear(t, 3, 1))
    source(ctx, 'Sources : OER, chiffres clés 2024 · EDF Réunion · Albioma', t, y=H - 36)

# ───────── S4 · Puissance ≠ énergie
ROWS = [  # clé, libellé, % puissance, % énergie 2024, heures équivalentes pleine puissance
    ('pv', 'Solaire', 30.2, 10.1, 995),
    ('colza', 'Huile de colza', 20.4, 37.9, 5509),
    ('pellets', 'Biomasse', 18.9, 30.2, 4722),
    ('hydro', 'Hydraulique', 13.0, 13.7, 3119),
    ('tac', 'Turbines à combustion', 11.7, 6.2, 1561),
]

def s_energy(ctx, t, D):
    background(ctx)
    eyebrow(ctx, 'Ce que pèse chaque filière en 2024', X0, 200, t, .3)
    text(ctx, 'Un mégawatt n\'en vaut pas un autre.', X0, 285, 66, 'display', 800, C['text'], appear(t, .5, .8), reveal=appear(t, .5, .9))
    bx, bw, vmax = 640, 900, 40.0
    la = appear(t, 1.0, .6)
    # légende
    rrect(ctx, bx, 352, 40, 14, 4); ctx.set_source_rgba(*hx(C['muted'], la)); ctx.set_line_width(2); ctx.stroke()
    text(ctx, 'part de la puissance installée', bx + 54, 366, 22, 'body', 500, C['muted'], la)
    rrect(ctx, bx + 460, 352, 40, 14, 4); fill(ctx, C['text'], la)
    text(ctx, 'part de l\'énergie produite', bx + 514, 366, 22, 'body', 500, C['muted'], la)
    text(ctx, 'heures/an à pleine puissance', 1790, 366, 20, 'mono', 500, C['muted'], la, 'r')
    for i, (k, lab, pc, pe, hrs) in enumerate(ROWS):
        y = 440 + i * 108
        t0 = 1.6 + i * 1.3
        a = appear(t, t0, .6)
        text(ctx, lab, X0, y + 30, 32, 'body', 600, C['text'], a)
        g1 = eio(prog(t, t0 + 0.2, 1.0))
        g2 = eio(prog(t, t0 + 0.7, 1.0))
        w1, w2 = bw * pc / vmax * g1, bw * pe / vmax * g2
        if w1 > 1:
            rrect(ctx, bx, y, w1, 22, 5)
            ctx.set_source_rgba(*hx(C[k], a)); ctx.set_line_width(2.5); ctx.stroke()
        text(ctx, fmt(pc * g1) + ' %', bx + w1 + 14, y + 18, 22, 'mono', 500, C['muted'], a)
        if w2 > 1:
            rrect(ctx, bx, y + 32, w2, 22, 5); fill(ctx, C[k], 1)
        text(ctx, fmt(pe * g2) + ' %', bx + w2 + 14, y + 51, 24, 'mono', 700, C['text'], appear(t, t0 + .7, .5))
        text(ctx, f'{hrs:,}'.replace(',', ' ') + ' h', 1790, y + 40, 30, 'display', 700, C[k], appear(t, t0 + 1.0, .5), 'r')
    para(ctx, 'Le solaire : 30 % de la puissance, 10 % de l\'énergie. Il ne produit que le jour ; l\'huile de colza tourne jour et nuit.',
         X0, 985, t, 9.0, 28, 1720, color=C['lava'], wght=500)
    source(ctx, 'Source : OER, chiffres clés 2024 · biomasse = granulés + bagasse + reliquat charbon · turbines = gazole + bioéthanol · calculs : énergie ÷ puissance', t, y=H - 32)

# ───────── S5 · Pourquoi autant de MW ?
def s_margin(ctx, t, D):
    background(ctx)
    eyebrow(ctx, 'Pourquoi 1 035 MW ?', X0, 200, t, .3)
    text(ctx, 'Deux fois la pointe, et pourtant…', X0, 285, 66, 'display', 800, C['text'], appear(t, .5, .8), reveal=appear(t, .5, .9))
    bx, by, bw, bh = X0, 470, 1680, 90
    s = bw / 1035
    g = eio(prog(t, 1.2, 1.4))
    rrect(ctx, bx, by, bw * g, bh, 10); fill(ctx, C['grid'], 1)
    # partie solaire, qui s'éteint à 19 h
    night = prog(t, 5.0, 1.2)
    pvw = 312.1 * s * g
    rrect(ctx, bx + bw * g - pvw, by, pvw, bh, 10)
    fill(ctx, C['pv'], 1 - 0.8 * night)
    rrect(ctx, bx, by, (1035 - 312.1) * s * g, bh, 10); fill(ctx, C['hydro'], 0.85)
    a = appear(t, 2.4, .6)
    text(ctx, '1 035 MW installés', bx, by - 22, 26, 'mono', 600, C['muted'], a)
    text(ctx, 'dont 312 MW de solaire', bx + bw, by - 22, 26, 'mono', 600, C['pv'], a, 'r')
    na = appear(t, 5.4, .6)
    text(ctx, '723 MW sans le soleil', bx + (1035 - 312.1) * s, by + bh + 46, 26, 'mono', 700, C['text'], na, 'r')
    text(ctx, '19 h : plus de soleil', bx + bw, by + bh + 46, 26, 'mono', 500, C['muted'], na, 'r') if False else None
    # pointe
    pa = appear(t, 3.4, .6)
    px = bx + 498 * s
    line(ctx, px, by - 70, px, by + bh + 14, C['lava'], pa, 3)
    text(ctx, 'Pointe 2023 : 498 MW', px + 12, by - 52, 26, 'mono', 700, C['lava'], pa)
    y = 720
    for i, s_ in enumerate([
        'Le soir, quand la consommation culmine, le solaire ne produit plus.',
        'Il faut une réserve : si la plus grosse machine décroche, une autre doit prendre le relais en quelques secondes.',
        'Des centrales sont en maintenance, d\'autres peuvent être touchées par un cyclone.',
    ]):
        ia = appear(t, 6.6 + i * 1.6, .6)
        ctx.arc(X0 + 8, y - 10, 6 * ia, 0, 2 * math.pi); fill(ctx, C['lava'], ia)
        y = para(ctx, s_, X0 + 40, y, t, 6.6 + i * 1.6, 36, 1500) + 20
    source(ctx, 'Sources : OER, chiffres clés 2024 (parc) · EDF SEI, Bilan prévisionnel 2024 (pointe 2023, réserves)', t, y=H - 32)

# ───────── S6 · Les nouveautés solaires
NEWS = [
    ('1er sept. 2026', 'Saint-Pierre', 'École Henri La Pierre', '155 kWc', '230 MWh/an'),
    ('9 oct. 2026', 'Saint-Paul', 'Gamm Vert Cambaie, rénovée', '161 → 177 kWc', ''),
    ('5 nov. 2026', 'Saint-Pierre', 'SuperCash2', '100 kWc', '151 MWh/an'),
    ('9 nov. 2026', 'Saint-Louis', 'Usine du Gol, toits GOL 4 et 6', '193 kWc', '277 MWh/an'),
    ('12 nov. 2026', 'Saint-Pierre', 'École Iris Hoarau', '166 kWc', '261 MWh/an'),
    ('Récent', 'Petite-Île', 'Village artisanal Argamasse', '162 kWc', '240 MWh/an'),
]

def s_news(ctx, t, D):
    background(ctx)
    eyebrow(ctx, 'Les dernières mises en service · Albioma Solaire Réunion', X0, 190, t, .3)
    text(ctx, 'Le solaire pousse toit par toit.', X0, 270, 64, 'display', 800, C['text'], appear(t, .5, .8), reveal=appear(t, .5, .9))
    y0 = 350
    for i, (d, place, what, kw, mwh) in enumerate(NEWS):
        y = y0 + i * 78
        a = appear(t, 1.3 + i * 0.7, .6)
        line(ctx, X0, y - 4, 1180, y - 4, C['grid'], a, 1.5)
        text(ctx, d.upper(), X0, y + 40, 21, 'mono', 600, C['muted'], a, spacing=1)
        text(ctx, place, X0 + 220, y + 40, 26, 'body', 700, C['text'], a)
        text(ctx, what, X0 + 420, y + 40, 26, 'body', 400, C['text'], a)
        text(ctx, kw, 1180, y + 42, 32, 'display', 800, C['pv'], a, 'r')
        if mwh:
            text(ctx, mwh, 1210, y + 40, 21, 'mono', 500, C['muted'], a)
    tot = appear(t, 6.0, .6)
    line(ctx, X0, y0 + 6 * 78 - 4, 1180, y0 + 6 * 78 - 4, C['grid'], tot, 1.5)
    text(ctx, 'Six chantiers, ≈ 0,8 MWc au total', X0, y0 + 6 * 78 + 44, 28, 'body', 700, C['text'], tot)
    # comparaison Port-Est
    cx = 1440
    ca = appear(t, 8.0, .8)
    text(ctx, 'ORDRE DE GRANDEUR', cx, 420, 21, 'mono', 600, C['lava'], ca, spacing=2)
    para(ctx, 'Pour égaler la puissance de Port-Est (211 MW), il faudrait environ', cx, 470, t, 8.2, 28, 420)
    v1 = 1270 * eio(prog(t, 9.0, 1.6))
    text(ctx, f'{v1:,.0f}'.replace(',', ' '), cx, 640, 96, 'display', 800, C['pv'], appear(t, 8.9, .5))
    text(ctx, 'toits comme l\'école Iris Hoarau.', cx, 685, 26, 'body', 500, C['text'], appear(t, 9.2, .6))
    v2 = 4450 * eio(prog(t, 11.8, 1.6))
    text(ctx, f'{v2:,.0f}'.replace(',', ' '), cx, 830, 96, 'display', 800, C['colza'], appear(t, 11.6, .5))
    para(ctx, 'pour égaler ce qu\'elle a produit en 2024 : le soleil ne brille pas la nuit.', cx, 875, t, 11.9, 26, 420)
    source(ctx, 'Sources : publications Albioma, sept.-nov. 2026 · OER, chiffres clés 2024 (Port-Est : 211 MW, 1 162,5 GWh) · arrondis', t, y=H - 32)

# ───────── S7 · Ce qui arrive
NEXT = [
    ('CHANTIER ENGAGÉ', 'Bois-Rouge', 'Une chaudière doit y valoriser près de 70 000 t/an de combustibles issus des déchets (CSR). Mise en service annoncée fin 2026, à confirmer.'),
    ('JUSQU\'EN 2043', 'Bois-Rouge', 'Le contrat d\'achat de l\'électricité de la centrale est prolongé, au lieu de 2027.'),
    ('EXPLORATION', 'Piton des Neiges', 'Albioma détient un permis de recherche géothermique de 80 km² sous Salazie et Cilaos.'),
    ('CONCERTATION', 'Saint-Denis', 'Projet Tanika : une station de pompage en eau de mer de 50 MW.'),
    ('AU 1ER JANV. 2025', 'File d\'attente', '131 MW de projets renouvelables attendaient leur raccordement au réseau.'),
]

def s_next(ctx, t, D):
    background(ctx)
    eyebrow(ctx, 'Les mégawatts à venir', X0, 190, t, .3)
    text(ctx, 'Ce qui se prépare.', X0, 270, 66, 'display', 800, C['text'], appear(t, .5, .8), reveal=appear(t, .5, .9))
    for i, (tag, place, body) in enumerate(NEXT):
        y = 360 + i * 124
        a = appear(t, 1.4 + i * 1.5, .6)
        text(ctx, tag, X0, y + 30, 22, 'mono', 700, C['lava'], a, spacing=2, reveal=a)
        text(ctx, place, X0 + 330, y + 30, 32, 'display', 700, C['text'], a)
        para(ctx, body, X0 + 330, y + 74, t, 1.6 + i * 1.5, 28, 1300, color=C['muted'])
    source(ctx, 'Sources : Albioma (site La Réunion, 2026) · ThinkGeoEnergy, avr. 2024 · EDF Réunion (Tanika) · EDF SEI, bilan S3REnR au 01/01/2025', t, y=H - 32)

# ───────── S8 · Fin
def s_end(ctx, t, D):
    background(ctx)
    isl = Island(W / 2, 560, 1200)
    isl.draw(ctx, 0.35 * appear(t, 0, 1.0))
    p1, p2 = appear(t, 0.6, 1.0), appear(t, 2.2, 1.0)
    text(ctx, 'Installer des mégawatts : c\'est la base.', W / 2, 500, 70, 'display', 800, C['text'], p1, 'c')
    text(ctx, 'Les avoir au bon moment : c\'est le défi.', W / 2, 600, 70, 'display', 800, C['lava'], p2, 'c')
    text(ctx, 'LES MÉGAWATTS DE L\'ÎLE', W / 2, 760, 24, 'mono', 600, C['muted'], appear(t, 4.0, 1.0), 'c', spacing=4)

SOURCES = [
    'Observatoire Énergie Réunion — Bilan énergétique, chiffres clés 2024 (édition 2025)',
    'EDF SEI — Bilan prévisionnel La Réunion 2024 · Bilan technique et financier S3REnR au 01/01/2025',
    'Albioma — page La Réunion et brochure Solaire 2026 · publications Facebook, sept.-nov. 2026',
    'ThinkGeoEnergy — permis de recherche géothermique Albioma, avril 2024',
    'EDF Réunion — lettre « EDF & moi », juillet-décembre 2026 (projet Tanika)',
]

def s_sources(ctx, t, D):
    background(ctx)
    eyebrow(ctx, 'Sources', X0, 220, t, 0.2)
    for i, s in enumerate(SOURCES):
        text(ctx, s, X0, 320 + i * 70, 28, 'body', 400, C['text'], appear(t, 0.5 + i * 0.15, .6))
    text(ctx, 'Puissances contractuelles au 31/12/2024. Chiffres arrondis.', X0, 320 + len(SOURCES) * 70 + 40,
         24, 'mono', 400, C['faint'], appear(t, 1.6, .8))

SCENES = [
    (7, s_title), (12, s_units), (14, s_treemap), (17, s_map), (16, s_energy), (15, s_margin),
    (18, s_news), (15, s_next), (8, s_end), (7, s_sources),
]
