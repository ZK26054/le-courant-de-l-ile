import csv, math
import cairo
from core import *

X0 = 120  # marge gauche

# ───────────────────────── S0 · Titre
def s_title(ctx, t, D):
    background(ctx)
    isl = Island(1390, 545, 1280)
    if t < 2.4:
        isl.draw(ctx, 1, draw_p=eo(prog(t, 0.2, 2.2)))
    a = appear(t, 2.0, 1.0)
    if a > 0:
        isl.draw(ctx, a)
    order = ['riviere_est', 'takamaka', 'bois_rouge', 'port_est', 'la_baie', 'le_gol', 'st_pierre']
    cols = {'riviere_est': 'hydro', 'takamaka': 'hydro', 'bois_rouge': 'pellets', 'port_est': 'colza',
            'la_baie': 'tac', 'le_gol': 'pellets', 'st_pierre': 'tac'}
    for i, k in enumerate(order):
        lon, lat, _ = SITES[k]
        x, y = isl.xy(lon, lat)
        p = appear(t, 3.0 + i * 0.22, 0.5)
        marker(ctx, x, y, C[cols[k]], p, 10 * (0.6 + 0.4 * p))
    eyebrow(ctx, 'La Réunion · 974 · de 1981 à 2040', X0, 330, t, 0.6)
    p1, p2 = appear(t, 0.9, 1.1), appear(t, 1.25, 1.1)
    text(ctx, 'Le courant', X0, 470, 132, 'display', 800, C['text'], p1, reveal=p1)
    text(ctx, 'de l\'île', X0, 600, 132, 'display', 800, C['text'], p2, reveal=p2)
    para(ctx, 'De l\'eau des barrages à la biomasse importée : comment l\'île produit son électricité, et ce qui l\'attend.',
         X0, 700, t, 2.4, 32, 660, color=C['muted'])

# ───────────────────────── S1 · Une île, un réseau
def s_zni(ctx, t, D):
    background(ctx)
    isl = Island(560, 560, 900)
    # ondes : l'île isolée dans l'océan
    for k in range(4):
        ph = ((t * 0.22 + k / 4) % 1)
        ctx.arc(560, 560, 330 + ph * 420, 0, 2 * math.pi)
        ctx.set_source_rgba(*hx(C['grid'], (1 - ph) * 0.9 * appear(t, 0.2, 1)))
        ctx.set_line_width(2)
        ctx.stroke()
    isl.draw(ctx, appear(t, 0, 0.6))
    xr = 1060
    eyebrow(ctx, 'Zone non interconnectée (ZNI)', xr, 250, t, 0.4)
    text(ctx, 'Une île, un réseau.', xr, 340, 76, 'display', 800, C['text'], appear(t, 0.7, 0.8), reveal=appear(t, 0.7, 0.9))
    y = para(ctx, 'Aucun câble ne relie La Réunion à un autre réseau électrique.', xr, 430, t, 1.8, 36, 720)
    para(ctx, 'Chaque seconde, les centrales de l\'île doivent produire exactement ce que l\'île consomme.',
         xr, y + 18, t, 3.6, 36, 720)
    # balance production / consommation + 50 Hz
    a = appear(t, 5.6, 0.8)
    if a > 0:
        by = 790
        wob = 0.012 * math.sin(t * 2.3)
        for i, (lab, col, val) in enumerate([('Production', C['text'], 1 + wob), ('Consommation', C['muted'], 1)]):
            yy = by + i * 52
            text(ctx, lab, xr, yy + 9, 24, 'mono', 500, col, a)
            rrect(ctx, xr + 230, yy - 12, 380 * val * a, 26, 4)
            fill(ctx, C['lava'] if i == 0 else C['faint'], a)
        # fréquence
        ctx.save()
        ctx.rectangle(xr, by + 100, 610, 70)
        ctx.clip()
        ctx.move_to(xr, by + 135)
        for xx in range(0, 611, 4):
            ctx.line_to(xr + xx, by + 135 + 22 * math.sin(xx / 22 - t * 6) * a)
        ctx.set_source_rgba(*hx(C['hydro'], a))
        ctx.set_line_width(2.5)
        ctx.stroke()
        ctx.restore()
        text(ctx, '50,00 Hz', xr + 640, by + 146, 34, 'mono', 700, C['hydro'], a)

# ───────────────────────── S2 · 1981
def s_1981(ctx, t, D):
    background(ctx)
    isl = Island(1400, 560, 1150)
    isl.draw(ctx, appear(t, 0, 0.6))
    for i, k in enumerate(['riviere_est', 'takamaka']):
        lon, lat, name = SITES[k]
        x, y = isl.xy(lon, lat)
        a = appear(t, 2.6 + i * 0.4, 0.6)
        marker(ctx, x, y, C['hydro'], a, 12, pulse=((t * 0.7 + i * 0.5) % 1))
        text(ctx, name, x + 26, y + 8, 26, 'body', 600, C['text'], a)
    eyebrow(ctx, 'Point de départ', X0, 250, t, 0.3)
    pa = appear(t, 0.5, 0.9)
    text(ctx, '1981', X0, 410, 170, 'display', 800, C['text'], pa, reveal=pa)
    v = 100 * eio(prog(t, 1.4, 1.6))
    text(ctx, f'{v:.0f} %', X0, 600, 150, 'display', 800, C['hydro'], appear(t, 1.3, 0.5))
    y = para(ctx, 'de l\'électricité de l\'île vient de l\'eau.', X0, 680, t, 2.6, 40, 740, wght=500)
    para(ctx, 'La centrale hydroélectrique de Rivière de l\'Est vient d\'entrer en service (1980). L\'île est alors autonome en électricité.',
         X0, y + 20, t, 4.2, 32, 700, color=C['muted'])
    source(ctx, 'Sources : Région Réunion, plan PRERURE · Connaissance des Énergies', t)

# ───────────────────────── S3 · 1981 → 2008
STACK_ORDER = [('hydro', 'Hydraulique'), ('bagasse', 'Bagasse'), ('pv', 'Solaire et éolien'),
               ('charbon', 'Charbon'), ('fioul', 'Fioul et gazole')]
YEARS_MIX = [
    ('1981', {'hydro': 100}),
    ('1990', {'hydro': 61, 'bagasse': 3, 'fioul': 36}),
    ('1995', {'hydro': 46, 'bagasse': 12, 'charbon': 21, 'fioul': 21}),
    ('2008', {'hydro': 24.8, 'bagasse': 10.3, 'pv': 1.0, 'charbon': 50.6, 'fioul': 13.3}),
]

def s_growth(ctx, t, D):
    background(ctx)
    eyebrow(ctx, '1981 → 2008', X0, 250, t, 0.3)
    text(ctx, 'Puis la demande', X0, 340, 72, 'display', 800, C['text'], appear(t, 0.5, .8), reveal=appear(t, 0.5, .9))
    text(ctx, 'explose.', X0, 420, 72, 'display', 800, C['lava'], appear(t, 0.8, .8), reveal=appear(t, 0.8, .9))
    y = para(ctx, 'En vingt ans, la consommation d\'énergie de l\'île bondit de 350 %. L\'eau ne suffit plus : on importe du charbon et du fioul.',
             X0, 510, t, 1.6, 32, 560)
    para(ctx, '1992 : Bois-Rouge. 1996 : Le Gol. Deux centrales charbon-bagasse s\'installent près des sucreries.',
         X0, y + 30, t, 8.2, 30, 560, color=C['muted'])
    # graphique : parts de la production (100 %)
    gx, gb, gh, cw, gap = 820, 900, 540, 150, 105
    la = appear(t, 1.2, 0.8)
    lx = gx
    for key, lab in STACK_ORDER:
        rrect(ctx, lx, 268, 18, 18, 3); fill(ctx, C[key], la)
        w = text(ctx, lab, lx + 28, 284, 22, 'body', 500, C['muted'], la)
        lx += w + 70
    line(ctx, gx - 20, gb + .5, gx + 4 * cw + 3 * gap + 20, gb + .5, C['faint'], la, 1.5)
    for i, (yr, mixd) in enumerate(YEARS_MIX):
        x = gx + i * (cw + gap)
        p = eio(prog(t, 2.2 + i * 1.5, 1.3))
        text(ctx, yr, x + cw / 2, gb + 48, 34, 'mono', 600, C['text'], appear(t, 2.0 + i * 1.5, .5), 'c')
        y = gb
        for key, _ in STACK_ORDER:
            v = mixd.get(key, 0)
            if not v:
                continue
            h = gh * v / 100 * p
            ctx.rectangle(x, y - h, cw, h - 2)
            fill(ctx, C[key])
            if v >= 8 and p > 0.95:
                lc = C['bg'] if key in ('pv', 'bagasse', 'hydro', 'pellets') else C['text']
                text(ctx, fmt(v, 0 if v == int(v) else 1) + ' %', x + cw / 2, y - h / 2 + 9, 24, 'mono', 700, lc,
                     appear(t, 2.2 + i * 1.5 + 1.2, .4), 'c')
            y -= h
    source(ctx, 'Sources : Région Réunion, PRERURE (1981-1995) · INSEE, Tableau économique de La Réunion 2010 (2008)', t)

# ───────────────────────── S4 · 2015
def waffle(ctx, x0, y0, cell, gap, counts, t, t0, dur=2.6, alpha_map=None):
    seq = []
    for col, n in counts:
        seq += [col] * n
    for i, col in enumerate(seq):
        r, c = divmod(i, 10)
        p = eo(prog(t, t0 + i * dur / 100, 0.35))
        if p <= 0:
            continue
        s = cell * (0.5 + 0.5 * p)
        x = x0 + c * (cell + gap) + (cell - s) / 2
        y = y0 + (9 - r) * (cell + gap) + (cell - s) / 2
        rrect(ctx, x, y, s, s, 5)
        a = (alpha_map or {}).get(col, 1.0)
        fill(ctx, C.get(col, col), p * a)

def s_2015(ctx, t, D):
    background(ctx)
    eyebrow(ctx, '2015 · le sommet de la dépendance', X0, 250, t, 0.3)
    v = 63.5 * eio(prog(t, 0.8, 2.0))
    text(ctx, fmt(v) + ' %', X0, 450, 190, 'display', 800, C['lava'], appear(t, 0.6, .5))
    y = para(ctx, 'de l\'électricité produite vient d\'énergies fossiles importées.', X0, 540, t, 2.0, 40, 820, wght=500)
    para(ctx, 'Le charbon, à lui seul, en fournit 40,4 %. Les centrales tournent avec des combustibles arrivés par bateau.',
         X0, y + 20, t, 3.8, 32, 820, color=C['muted'])
    waffle(ctx, 1180, 230, 54, 8, [('charbon', 40), ('fioul', 24), ('hydro', 36)], t, 0.9, 2.4, {'hydro': 0.35})
    la = appear(t, 3.4, .8)
    for i, (k, lab) in enumerate([('charbon', 'Charbon'), ('fioul', 'Fioul et gazole'), ('hydro', 'Renouvelables')]):
        xx = 1180 + i * 210
        rrect(ctx, xx, 880, 18, 18, 3); fill(ctx, C[k], la * (0.35 if k == 'hydro' else 1))
        text(ctx, lab, xx + 28, 896, 22, 'body', 500, C['muted'], la)
    text(ctx, '1 carré = 1 %', 1180, 940, 20, 'mono', 400, C['faint'], la)
    source(ctx, 'Source : Connaissance des Énergies, d\'après l\'Observatoire Énergie Réunion (production 2015)', t)

# ───────────────────────── S5 · Le virage
TIMELINE = [
    ('2015', 'La loi fixe un cap : l\'autonomie énergétique des Outre-mer en 2030.'),
    ('2017', 'Première programmation pluriannuelle de l\'énergie (PPE) de La Réunion.'),
    ('2022', 'Bois-Rouge commence à remplacer le charbon par la biomasse.'),
    ('oct. 2023', 'Port-Est (211 MW) remplace le fioul par de l\'huile de colza.'),
    ('2024', 'Le Gol achève sa conversion. Plus aucune centrale ne brûle de charbon.'),
]

def s_turn(ctx, t, D):
    background(ctx)
    eyebrow(ctx, '2015 → 2024', X0, 200, t, 0.3)
    text(ctx, 'Le virage', X0, 280, 76, 'display', 800, C['text'], appear(t, .5, .8), reveal=appear(t, .5, .9))
    lx, y0, step = X0 + 8, 352, 136
    T = [1.5 + i * 2.1 for i in range(5)]
    lp = eio(prog(t, 1.2, 9.5))
    line(ctx, lx, y0 - 10, lx, y0 - 10 + (step * 4 + 20) * lp, C['faint'], 1, 2)
    for i, (yr, txt) in enumerate(TIMELINE):
        a = appear(t, T[i], .7)
        yy = y0 + i * step
        ctx.arc(lx, yy, 8 * a, 0, 2 * math.pi); fill(ctx, C['lava'], a)
        text(ctx, yr, lx + 34, yy + 9, 28, 'mono', 700, C['lava'], a, reveal=a)
        para(ctx, txt, lx + 34, yy + 54, t, T[i] + 0.2, 30, 720)
    isl = Island(1440, 590, 960)
    isl.draw(ctx, appear(t, 0.3, .8))
    flips = {'bois_rouge': ('charbon', 'pellets', T[2]), 'port_est': ('fioul', 'colza', T[3]),
             'le_gol': ('charbon', 'pellets', T[4])}
    for k in ['riviere_est', 'takamaka', 'bois_rouge', 'port_est', 'le_gol', 'la_baie', 'st_pierre']:
        lon, lat, name = SITES[k]
        x, y = isl.xy(lon, lat)
        a = appear(t, 0.8, .6)
        if k in flips:
            c0, c1, tf = flips[k]
            fp = prog(t, tf, 0.8)
            col = mix(C[c0], C[c1], eio(fp))
            pulse = fp if 0 < fp < 1 else None
            marker(ctx, x, y, col, a, 12, pulse=pulse)
            if k == 'port_est':
                text(ctx, name, x + 24, y - 14, 24, 'body', 600, C['text'], a)
            else:
                text(ctx, name, x + 24 if k != 'le_gol' else x - 24, y + 8, 24, 'body', 600, C['text'], a,
                     'l' if k != 'le_gol' else 'r')
        else:
            col = C['hydro'] if k in ('riviere_est', 'takamaka') else C['tac']
            marker(ctx, x, y, col, a * 0.85, 9)
    la = appear(t, 1.0, .8)
    for i, (k, lab) in enumerate([('charbon', 'Charbon'), ('fioul', 'Fioul'), ('pellets', 'Biomasse'), ('colza', 'Huile de colza')]):
        xx = 1120 + i * 185
        ctx.arc(xx + 9, 958, 9, 0, 2 * math.pi); fill(ctx, C[k], la)
        text(ctx, lab, xx + 26, 966, 21, 'body', 500, C['muted'], la)
    source(ctx, 'Sources : loi de transition énergétique (2015) · décret PPE (2017) · EDF SEI, Bilan prévisionnel 2024', t, y=H - 44)

# ───────────────────────── S6 · Le mix bascule
ENR = [('2008', 36.1), ('2015', 36.5), ('2022', 38.0), ('2023', 57.0), ('2024', 92.4), ('2025', 96.6)]

def s_flip(ctx, t, D):
    background(ctx)
    eyebrow(ctx, 'Part renouvelable de la production d\'électricité', X0, 200, t, 0.3)
    text(ctx, 'Le mix bascule.', X0, 285, 76, 'display', 800, C['text'], appear(t, .5, .8), reveal=appear(t, .5, .9))
    para(ctx, 'Pendant quinze ans, la part renouvelable plafonne autour d\'un tiers. Avec les conversions, elle dépasse 96 % en trois ans.',
         X0, 350, t, 1.3, 32, 1400, color=C['muted'])
    gx, gb, gh, cw, gap = 200, 930, 470, 170, 90
    top = gb - gh
    la = appear(t, 1.0, .8)
    line(ctx, gx - 30, top, gx + 6 * cw + 5 * gap + 20, top, C['faint'], la, 1.5, [8, 8])
    text(ctx, '100 %', gx + 6 * cw + 5 * gap + 30, top + 8, 22, 'mono', 500, C['faint'], la)
    line(ctx, gx - 30, gb + .5, gx + 6 * cw + 5 * gap + 20, gb + .5, C['faint'], la, 1.5)
    for i, (yr, v) in enumerate(ENR):
        x = gx + i * (cw + gap)
        t0 = 2.0 + i * 1.25 + (1.0 if i >= 3 else 0)
        p = eio(prog(t, t0, 1.2))
        h = gh * v / 100 * p
        col = C['hydro'] if i < 3 else mix(C['hydro'], C['bagasse'], 0.55)
        rrect(ctx, x, gb - h, cw, h, 6) if h > 1 else None
        if h > 1:
            fill(ctx, col, 0.55 if i < 3 else 1)
        a = appear(t, t0 + 0.5, .5)
        text(ctx, fmt(v * p, 0 if v == int(v) else 1) + ' %', x + cw / 2, gb - h - 18, 44, 'display', 700,
             C['text'], appear(t, t0, .4), 'c')
        text(ctx, yr, x + cw / 2, gb + 46, 30, 'mono', 600, C['muted'], appear(t, t0 - .3, .5), 'c')
    source(ctx, 'Sources : INSEE (2008) · Connaissance des Énergies (2015) · EDF SEI, bilans prévisionnels (2022-2023) · '
                'Question écrite AN n°15241 (2024) · Leader Réunion, mars 2026 (2025)', t, y=H - 40)

# ───────────────────────── S7 · Renouvelable, oui. Local, pas encore.
def s_local(ctx, t, D):
    background(ctx)
    eyebrow(ctx, '2025 · d\'où vient l\'électricité ?', X0, 200, t, 0.3)
    text(ctx, 'Renouvelable, oui.', X0, 285, 70, 'display', 800, C['text'], appear(t, .5, .8), reveal=appear(t, .5, .9))
    text(ctx, 'Local, pas encore.', X0, 365, 70, 'display', 800, C['pellets'], appear(t, 1.0, .8), reveal=appear(t, 1.0, .9))
    counts = [('pv', 11), ('hydro', 8), ('bagasse', 6), ('eolien', 1), ('biogaz', 1), ('pellets', 69), ('tac', 4)]
    waffle(ctx, 1190, 215, 54, 8, counts, t, 1.6, 3.0)
    v1 = 26.6 * eio(prog(t, 4.8, 1.2))
    a1 = appear(t, 4.6, .6)
    text(ctx, fmt(v1) + ' %', X0, 520, 104, 'display', 800, C['bagasse'], a1)
    para(ctx, 'de production vraiment locale : soleil, eau, bagasse, vent, biogaz.', X0, 575, t, 5.2, 32, 900)
    a2 = appear(t, 8.0, .6)
    text(ctx, '≈ 70 %', X0, 730, 104, 'display', 800, C['pellets'], a2)
    para(ctx, 'de biomasse importée : huile de colza venue d\'Europe, granulés de bois.', X0, 785, t, 8.4, 32, 900)
    para(ctx, 'EDF parle d\'un mix renouvelable ; ses critiques, d\'une dépendance déplacée du fioul vers d\'autres importations.',
         X0, 890, t, 12.0, 28, 940, color=C['muted'])
    la = appear(t, 4.0, .8)
    leg = [('pv', 'Solaire'), ('hydro', 'Hydraulique'), ('bagasse', 'Bagasse'), ('eolien', 'Éolien'),
           ('biogaz', 'Biogaz'), ('pellets', 'Biomasse importée'), ('tac', 'Fossile (turbines)')]
    for i, (k, lab) in enumerate(leg):
        cx = 1190 + (i % 3) * 205
        cy = 870 + (i // 3) * 40
        if i == 6:
            cx = 1190 + 2 * 205
        rrect(ctx, cx, cy - 16, 18, 18, 3); fill(ctx, C[k], la)
        text(ctx, lab, cx + 28, cy, 21, 'body', 500, C['muted'], la)
    source(ctx, 'Source : Leader Réunion, 23 mars 2026, d\'après le bilan électrique 2025 · 1 carré = 1 %, valeurs arrondies', t, y=H - 40)

# ───────────────────────── S8 · Une journée réelle (open data EDF)
def load_day():
    rows = list(csv.DictReader(open(HERE / 'prod-electricite-temps-reel-974.csv', encoding='utf-8-sig')))
    rows.sort(key=lambda r: r['Date'])
    out = []
    for r in rows:
        d = r['Date']
        if not ('2026-03-07T12:25' <= d[:16] <= '2026-03-08T10:55') or d[:16] == '2026-03-08T01:05':
            continue
        hh, mm = int(d[11:13]), int(d[14:16])
        day = 0 if d[8:10] == '07' else 1
        minutes = day * 1440 + hh * 60 + mm
        g = lambda k: max(0.0, float(r[k]))
        out.append((minutes, [g('Diesel'), g('Charbon'), g('Bioénergies'), g('Hydraulique'), g('Eolien'),
                              g('Photovoltaique'), g('Turbines_combustion')]))
    return out

DAY = load_day()
BANDS = [('colza', 'Huile de colza · Port-Est'), ('pellets', 'Biomasse · granulés, bagasse'),
         ('biogaz', 'Bioénergies'), ('hydro', 'Hydraulique'), ('eolien', 'Éolien'), ('pv', 'Solaire'),
         ('tac', 'Turbines à combustion')]
CALLOUTS = [
    (16 * 60, 'Fin d\'après-midi : le soleil baisse, le solaire recule.'),
    (19 * 60, 'Pointe du soir, 413 MW : les barrages montent à 91 MW pour suivre.'),
    (26 * 60, 'La nuit : biomasse et huile de colza portent le réseau.'),
    (31 * 60 + 30, 'Le jour revient : le solaire reprend sa place.'),
]

def s_day(ctx, t, D):
    background(ctx)
    eyebrow(ctx, 'Comment ça marche · une journée réelle, 7-8 mars 2026', X0, 150, t, 0.3)
    text(ctx, 'Le réseau, heure par heure.', X0, 225, 64, 'display', 800, C['text'], appear(t, .5, .8), reveal=appear(t, .5, .9))
    x0, x1, yb, yt, ymax = 210, 1430, 930, 380, 450
    m0, m1 = DAY[0][0], DAY[-1][0]
    X = lambda m: x0 + (m - m0) / (m1 - m0) * (x1 - x0)
    Y = lambda v: yb - v / ymax * (yb - yt)
    la = appear(t, 0.8, .8)
    for v in (0, 100, 200, 300, 400):
        line(ctx, x0, Y(v) + .5, x1, Y(v) + .5, C['grid'], la, 1)
        text(ctx, f'{v}', x0 - 18, Y(v) + 8, 20, 'mono', 400, C['faint'], la, 'r')
    text(ctx, 'MW', x0 - 18, yt - 26, 20, 'mono', 500, C['faint'], la, 'r')
    for hh in (14, 18, 22, 26, 30, 34):
        m = hh * 60
        if m0 <= m <= m1:
            text(ctx, f'{hh % 24:02d} h', X(m), yb + 40, 22, 'mono', 500, C['muted'], la, 'c')
            line(ctx, X(m), yb, X(m), yb + 10, C['faint'], la, 1.5)
    cp = eio(prog(t, 1.6, 13.0))
    cur_m = m0 + cp * (m1 - m0)
    cx = X(cur_m)
    # bandes empilées, découpées au curseur
    ctx.save()
    ctx.rectangle(x0, 0, cx - x0, H)
    ctx.clip()
    base = [0.0] * len(DAY)
    for bi, (key, _) in enumerate(BANDS):
        tops = [base[i] + DAY[i][1][bi] for i in range(len(DAY))]
        ctx.move_to(X(DAY[0][0]), Y(base[0]))
        for i in range(len(DAY)):
            ctx.line_to(X(DAY[i][0]), Y(tops[i]))
        for i in range(len(DAY) - 1, -1, -1):
            ctx.line_to(X(DAY[i][0]), Y(base[i]))
        ctx.close_path()
        fill(ctx, C[key], 0.92)
        base = tops
    ctx.move_to(X(DAY[0][0]), Y(base[0]))
    for i in range(len(DAY)):
        ctx.line_to(X(DAY[i][0]), Y(base[i]))
    ctx.set_source_rgba(*hx(C['text'], 0.9)); ctx.set_line_width(2); ctx.stroke()
    ctx.restore()
    if 0 < cp < 1:
        line(ctx, cx, yt - 10, cx, yb, C['text'], 0.7, 1.5)
        # valeur du total au curseur
        j = min(range(len(DAY)), key=lambda i: abs(DAY[i][0] - cur_m))
        tot = sum(DAY[j][1])
        hh = (DAY[j][0] // 60) % 24
        mm = DAY[j][0] % 60
        text(ctx, f'{hh:02d}:{mm:02d}  {tot:.0f} MW', cx + 12, yt - 4, 22, 'mono', 600, C['text'], 0.9)
    # légende
    for i, (key, lab) in enumerate(reversed(BANDS)):
        yy = 420 + i * 58
        rrect(ctx, 1480, yy - 18, 20, 20, 4); fill(ctx, C[key], la)
        text(ctx, lab, 1512, yy, 23, 'body', 500, C['text'] if key != 'tac' else C['muted'], la)
    # légendes contextuelles synchronisées avec le curseur
    cy = 300
    shown = None
    for i, (m, s) in enumerate(CALLOUTS):
        nxt = CALLOUTS[i + 1][0] if i + 1 < len(CALLOUTS) else 10 ** 9
        if m <= cur_m < nxt and cp < 1:
            shown = (i, m, s)
    if shown:
        i, m, s = shown
        fa = clamp((cur_m - m) / 60)
        text(ctx, s, X0, cy, 32, 'body', 600, C['lava'], fa)
    fin = appear(t, 15.2, .8)
    if fin > 0:
        text(ctx, 'Solaire et éolien n\'apportent pas d\'inertie au réseau : au-delà d\'un seuil, la fréquence devient', X0, cy - 12, 28, 'body', 500, C['text'], fin)
        text(ctx, 'difficile à tenir. Centrales pilotables, barrages et batteries assurent l\'équilibre.', X0, cy + 26, 28, 'body', 500, C['text'], appear(t, 15.5, .8))
    source(ctx, 'Données : EDF Réunion open data, production par filière, valeurs estimées · stockage (±5 MW) non représenté · une valeur isolée écartée (01:05)', t, y=H - 40)

# ───────────────────────── S9 · Cyclones
def cyclone(ctx, cx, cy, r, ang, a):
    for k in range(4):
        base = ang + k * math.pi / 2
        ctx.new_path()
        for j in range(60):
            u = j / 59
            rr = r * (0.12 + 0.88 * u)
            th = base - u * 2.6
            x, y = cx + rr * math.cos(th), cy + rr * math.sin(th)
            ctx.line_to(x, y)
        ctx.set_source_rgba(*hx(C['text'], a * 0.45))
        ctx.set_line_width(10)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.stroke()
    ctx.arc(cx, cy, r * 0.09, 0, 2 * math.pi)
    fill(ctx, C['bg'], a)

def s_cyclone(ctx, t, D):
    background(ctx)
    isl = Island(1330, 560, 1000)
    isl.draw(ctx, appear(t, 0, .6))
    cxp = lerp(2150, 1560, eio(prog(t, 0.5, 6.5)))
    cyp = lerp(330, 470, eio(prog(t, 0.5, 6.5)))
    cyclone(ctx, cxp, cyp, 330, t * 1.4, appear(t, 0.3, 1.0))
    lon, lat, name = SITES['riviere_est']
    x, y = isl.xy(lon, lat)
    hit = prog(t, 5.0, 0.6)
    col = mix(C['hydro'], C['lava'], hit)
    marker(ctx, x, y, col, appear(t, .5, .5), 12, pulse=((t * 1.2) % 1) if hit > 0 else None)
    text(ctx, name, x - 22, y + 50, 24, 'body', 600, C['text'], appear(t, .8, .5), 'r')
    eyebrow(ctx, 'Fragilités', X0, 250, t, 0.3)
    text(ctx, 'Le climat met', X0, 340, 72, 'display', 800, C['text'], appear(t, .5, .8), reveal=appear(t, .5, .9))
    text(ctx, 'le réseau à l\'épreuve.', X0, 420, 72, 'display', 800, C['text'], appear(t, .8, .8), reveal=appear(t, .8, .9))
    text(ctx, 'JANV. 2024', X0, 520, 24, 'mono', 700, C['lava'], appear(t, 1.8, .6), spacing=2)
    para(ctx, 'Cyclone Belal.', X0, 560, t, 1.9, 32, 640)
    text(ctx, '28 FÉVR. 2025', X0, 640, 24, 'mono', 700, C['lava'], appear(t, 3.2, .6), spacing=2)
    y = para(ctx, 'Cyclone Garance : 21 pylônes à très haute tension détruits, la prise d\'eau qui alimente Rivière de l\'Est arrachée.',
             X0, 680, t, 3.3, 32, 640)
    para(ctx, 'En 2025, l\'hydraulique ne fournit plus que 7,7 % de l\'électricité.', X0, y + 24, t, 6.2, 32, 640, wght=600, color=C['hydro'])
    source(ctx, 'Sources : EDF Réunion · Leader Réunion, mars 2026 · EDF SEI, Bilan prévisionnel 2024', t)

# ───────────────────────── S10 · Horizon 2040
STATS = [
    ('Consommation d\'électricité', '+40 à +50 %', 'd\'ici 2040 : population, véhicules électriques', (100, 150), 150),
    ('Pointe de consommation', '498 → 799 MW', '2023 → 2040 (737 à 799 MW selon le scénario)', (498, 799), 800),
    ('Solaire installé', '210 → 980 MWc', '2024 → 2040 (730 à 980 MWc selon le scénario)', (210, 980), 1000),
    ('Puissance pilotable à trouver', 'jusqu\'à 480 MW', 'en 2040, notamment après la fin du contrat de Port-Est', (0, 480), 500),
]

def s_2040(ctx, t, D):
    background(ctx)
    eyebrow(ctx, 'Horizon 2040 · scénarios du gestionnaire de réseau', X0, 200, t, 0.3)
    text(ctx, 'Demain : plus de besoins.', X0, 285, 72, 'display', 800, C['text'], appear(t, .5, .8), reveal=appear(t, .5, .9))
    for i, (lab, big, sub, (v0, v1), vmax) in enumerate(STATS):
        bx = X0 + (i % 2) * 860
        by = 380 + (i // 2) * 300
        t0 = 1.6 + i * 2.3
        a = appear(t, t0, .7)
        text(ctx, lab.upper(), bx, by + 20, 21, 'mono', 600, C['muted'], a, spacing=2, reveal=a)
        text(ctx, big, bx, by + 110, 78, 'display', 800, C['lava'] if i == 3 else C['text'], a)
        para(ctx, sub, bx, by + 158, t, t0 + 0.3, 26, 760, color=C['muted'])
        # jauge : valeur de départ (pleine) puis extension animée
        bw = 740
        yb = by + 200
        rrect(ctx, bx, yb, bw, 12, 6); fill(ctx, C['grid'], a)
        w0 = bw * v0 / vmax
        if w0 > 0:
            rrect(ctx, bx, yb, w0 * a, 12, 6); fill(ctx, C['faint'], 1)
        g = eio(prog(t, t0 + 0.6, 1.4))
        w1 = bw * v1 / vmax
        if g > 0 and w1 > w0:
            rrect(ctx, bx + w0, yb, (w1 - w0) * g, 12, 6); fill(ctx, C['lava'] if i == 3 else C['hydro'], 1)
    source(ctx, 'Source : EDF SEI, Bilan prévisionnel de l\'équilibre offre-demande, La Réunion 2024 (horizon 2040, scénarios Azur et Emeraude)', t, y=H - 40)

# ───────────────────────── S11 · Les chantiers
def icon(ctx, kind, x, y, a):
    ctx.save()
    ctx.set_line_width(3.5)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_source_rgba(*hx(C['lava'], a))
    if kind == 'store':  # vague + flèche montante (pompage)
        ctx.move_to(x, y + 30)
        for k in range(0, 61, 3):
            ctx.line_to(x + k, y + 30 + 6 * math.sin(k / 6))
        ctx.stroke()
        ctx.move_to(x + 30, y + 18); ctx.line_to(x + 30, y - 18); ctx.stroke()
        ctx.move_to(x + 18, y - 6); ctx.line_to(x + 30, y - 18); ctx.line_to(x + 42, y - 6); ctx.stroke()
    elif kind == 'local':  # île + point
        ctx.arc(x + 30, y + 6, 26, 0, 2 * math.pi); ctx.stroke()
        ctx.arc(x + 30, y + 6, 8, 0, 2 * math.pi); ctx.fill()
    else:  # prise / voiture : éclair
        ctx.move_to(x + 36, y - 22); ctx.line_to(x + 18, y + 10); ctx.line_to(x + 34, y + 10)
        ctx.line_to(x + 24, y + 38); ctx.line_to(x + 46, y + 2); ctx.line_to(x + 30, y + 2); ctx.close_path(); ctx.stroke()
    ctx.restore()

CARDS = [
    ('store', 'Stocker', 'Projet Tanika : une station de pompage en eau de mer de 50 MW à Saint-Denis, en concertation depuis 2026.'),
    ('local', 'Produire sur l\'île', 'La loi vise l\'autonomie énergétique en 2030. En 2025, 7 kWh sur 10 viennent encore de biomasse importée.'),
    ('elec', 'Électrifier', 'Les transports représentent 63 % de l\'énergie finale de l\'île, et roulent presque tous aux carburants fossiles.'),
]

def s_next(ctx, t, D):
    background(ctx)
    eyebrow(ctx, 'Les chantiers ouverts', X0, 200, t, 0.3)
    text(ctx, 'Trois questions pour la suite.', X0, 285, 72, 'display', 800, C['text'], appear(t, .5, .8), reveal=appear(t, .5, .9))
    cw, gap = 520, 70
    for i, (ic, title, body) in enumerate(CARDS):
        x = X0 + i * (cw + gap)
        y = 380
        t0 = 1.6 + i * 2.4
        a = appear(t, t0, .8)
        rrect(ctx, x, y + (1 - a) * 30, cw, 430, 14)
        fill(ctx, C['bg2'], a)
        rrect(ctx, x, y + (1 - a) * 30, cw, 430, 14)
        ctx.set_source_rgba(*hx(C['grid'], a)); ctx.set_line_width(2); ctx.stroke()
        icon(ctx, ic, x + 40, y + 70 + (1 - a) * 30, a)
        text(ctx, title, x + 40, y + 170 + (1 - a) * 30, 40, 'display', 700, C['text'], a)
        para(ctx, body, x + 40, y + 230, t, t0 + 0.4, 28, cw - 80, color=C['muted'])
    para(ctx, 'La programmation pluriannuelle de l\'énergie de La Réunion est en cours de révision.',
         X0, 900, t, 9.2, 30, 1600, wght=500)
    source(ctx, 'Sources : EDF Réunion, lettre « EDF & moi » juil.-déc. 2026 (Tanika) · Question écrite AN n°15241 · Région Réunion (PPE)', t, y=H - 40)

# ───────────────────────── S12 · Fin
def s_end(ctx, t, D):
    background(ctx)
    isl = Island(W / 2, 560, 1200)
    ctx.save()
    isl.draw(ctx, 0.35 * appear(t, 0, 1.0))
    ctx.restore()
    p1, p2 = appear(t, 0.6, 1.0), appear(t, 2.4, 1.0)
    text(ctx, 'Renouvelable : presque fait.', W / 2, 500, 84, 'display', 800, C['text'], p1, 'c')
    text(ctx, 'Autonome : le prochain défi.', W / 2, 610, 84, 'display', 800, C['lava'], p2, 'c')
    text(ctx, 'LE COURANT DE L\'ÎLE', W / 2, 760, 24, 'mono', 600, C['muted'], appear(t, 4.4, 1.0), 'c', spacing=4)

# ───────────────────────── S13 · Sources
SOURCES = [
    'Région Réunion — PRERURE, mode de production 1981-2000',
    'INSEE — Tableau économique de La Réunion 2010',
    'Connaissance des Énergies — mix électrique 2015 ; centrales du Gol et de Rivière de l\'Est',
    'EDF SEI — Bilans prévisionnels La Réunion 2023 et 2024',
    'Assemblée nationale — question écrite n°15241, 19 mai 2026',
    'Leader Réunion — « La production d\'électricité est restée stable en 2025 », 23 mars 2026',
    'EDF Réunion — open data, production par filière en temps réel',
    'EDF Réunion — lettre « EDF & moi », juillet-décembre 2026 (projet Tanika)',
    'Région Réunion — déclaration d\'intention de révision de la PPE, 9 juin 2026',
]

def s_sources(ctx, t, D):
    background(ctx)
    eyebrow(ctx, 'Sources', X0, 200, t, 0.2)
    for i, s in enumerate(SOURCES):
        a = appear(t, 0.5 + i * 0.12, .6)
        text(ctx, s, X0, 290 + i * 62, 28, 'body', 400, C['text'], a)
    text(ctx, 'Chiffres arrondis. Les données temps réel EDF sont des valeurs estimées.', X0, 290 + len(SOURCES) * 62 + 40,
         24, 'mono', 400, C['faint'], appear(t, 1.8, .8))

SCENES = [
    (7, s_title), (10, s_zni), (10, s_1981), (15, s_growth), (10, s_2015), (15, s_turn), (14, s_flip),
    (18, s_local), (24, s_day), (11, s_cyclone), (18, s_2040), (14, s_next), (8, s_end), (8, s_sources),
]
