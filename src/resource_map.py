# -*- coding: utf-8 -*-
"""Карта ресурсных тел программы ММОСО'Н — отдельный крупноформатный лист.

Строится по реальным элементам орбит (JPL SBDB). В отличие от рисунка 22,
входящего в документ, здесь:
  * формат A3-альбом (420 x 297 мм), 300 dpi — один читаемый печатный лист;
  * звёздное поле и реалистичная светотень тел;
  * пояс астероидов — облако точек с распределением по большой полуоси;
  * орбиты с учётом наклонения;
  * ресурсные тела отмечены номерами, а их параметры вынесены в крупную правую легенду;
  * таблица потребности проекта рассчитана на A3 без мелкого постерного текста.

Запуск:  python3 resource_map.py
Выход:   ../resource_map.png  (и ../resource_map.pdf)
"""
import os
import math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Ellipse, Polygon, Rectangle, FancyArrow
from matplotlib.lines import Line2D
from matplotlib.collections import LineCollection
import matplotlib.patheffects as pe

matplotlib.rcParams.update({
    'font.family': 'DejaVu Sans',
    'savefig.dpi': 300,
})

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ── палитра «ночного неба» ──────────────────────────────────────────────
BG      = '#070b14'      # фон космоса
BG_LG   = '#0d1422'      # фон панелей
FG      = '#e8edf5'      # основной текст
FG_DIM  = '#8b97ab'      # вторичный текст
GRID    = '#1c2740'      # сетка
SUN     = '#ffd257'
C_METAL = '#e2643c'      # 1986 DA — металл
C_WATER = '#4fa8d8'      # вода
C_ORG   = '#5fb98a'      # органика
C_NITRO = '#a878c8'      # азот
C_COMET = '#e8c860'      # комета
C_EARTH = '#5b8fd6'
C_MARS  = '#c1704a'
C_JUP   = '#c9a878'
C_ST    = '#7fd4e8'      # станция

AU = 1.0


# ── орбитальная механика ────────────────────────────────────────────────
def orbit_xy(a, e, om_deg, i_deg=0.0, n=1400):
    """Проекция эллиптической орбиты на плоскость эклиптики.

    a  — большая полуось, а.е.;  e — эксцентриситет;
    om_deg — долгота перигелия (ω + Ω), градусы;
    i_deg  — наклонение: проекция сжимает орбиту поперёк линии узлов.
    """
    nu = np.linspace(0, 2 * np.pi, n)
    r = a * (1 - e ** 2) / (1 + e * np.cos(nu))
    th = nu + math.radians(om_deg)
    x, y = r * np.cos(th), r * np.sin(th)
    if i_deg:
        # поворот в плоскость узлов, сжатие на cos i, поворот обратно
        s = math.radians(om_deg)
        xr = x * math.cos(-s) - y * math.sin(-s)
        yr = x * math.sin(-s) + y * math.cos(-s)
        yr *= math.cos(math.radians(i_deg))
        x = xr * math.cos(s) - yr * math.sin(s)
        y = xr * math.sin(s) + yr * math.cos(s)
    return x, y


def perihelion_xy(a, e, om_deg, i_deg=0.0):
    x, y = orbit_xy(a, e, om_deg, i_deg, n=3)
    return x[0], y[0]


def point_at(a, e, om_deg, nu_deg, i_deg=0.0):
    """Положение тела при истинной аномалии nu."""
    nu = math.radians(nu_deg)
    r = a * (1 - e ** 2) / (1 + e * math.cos(nu))
    th = nu + math.radians(om_deg)
    x, y = r * math.cos(th), r * math.sin(th)
    if i_deg:
        s = math.radians(om_deg)
        xr = x * math.cos(-s) - y * math.sin(-s)
        yr = x * math.sin(-s) + y * math.cos(-s)
        yr *= math.cos(math.radians(i_deg))
        x = xr * math.cos(s) - yr * math.sin(s)
        y = xr * math.sin(s) + yr * math.cos(s)
    return x, y


# ── ТЕЛА ────────────────────────────────────────────────────────────────
# (метка, имя, a, e, долгота перигелия, i, диаметр км, цвет, роль)
TARGETS = [
    ('1', '(6178) 1986 DA', 2.8216, 0.5818, 127.36, 4.31, 3.0,
     C_METAL, 'металл'),
    ('2', '(1) Церера', 2.7660, 0.0785, 73.60, 10.59, 939.4,
     C_WATER, 'вода'),
    ('3', '(24) Themis', 3.1490, 0.1165, 108.06, 0.74, 198.0,
     C_ORG, 'вода, органика'),
    ('4', '(10) Hygiea', 3.1415, 0.1125, 312.32, 3.83, 434.0,
     C_NITRO, 'азот'),
    ('5', '67P/Чурюмова — Герасименко', 3.4620, 0.6410, 12.80, 7.04, 4.1,
     C_COMET, 'льды, аммиак'),
]

# (имя, a, e, долгота перигелия, i, цвет, радиус значка, истинная аномалия)
PLANETS = [
    ('Земля',   1.0000, 0.0167, 102.9, 0.00, C_EARTH, 0.085,  25),
    ('Марс',    1.5237, 0.0934, 286.5, 1.85, C_MARS,  0.070, 250),
    ('Юпитер',  5.2038, 0.0489, 273.9, 1.30, C_JUP,   0.150,  38),
]

# Между Марсом и Юпитером планет нет — там лежит главный пояс астероидов.
# Пояс и есть «промежуточное звено» ряда Земля → Юпитер.


def draw_starfield(ax, xlim, ylim, n=1400, seed=7):
    """Звёздное поле: степенное распределение яркости, лёгкий цветовой разброс."""
    rng = np.random.default_rng(seed)
    x = rng.uniform(xlim[0], xlim[1], n)
    y = rng.uniform(ylim[0], ylim[1], n)
    mag = rng.power(0.35, n)                 # много слабых, мало ярких
    size = 0.15 + mag ** 3 * 7.0
    alpha = 0.20 + mag * 0.70
    tint = rng.uniform(0, 1, n)
    cols = []
    for t in tint:
        if t < 0.70:
            cols.append('#ffffff')
        elif t < 0.86:
            cols.append('#cfe0ff')           # горячие
        else:
            cols.append('#ffe2c0')           # холодные
    ax.scatter(x, y, s=size, c=cols, alpha=alpha, lw=0, zorder=0)
    # несколько ярких звёзд с дифракционными лучами
    for _ in range(9):
        sx = rng.uniform(xlim[0], xlim[1])
        sy = rng.uniform(ylim[0], ylim[1])
        if math.hypot(sx, sy) < 1.4:
            continue
        r = rng.uniform(0.10, 0.19)
        ax.plot([sx - r, sx + r], [sy, sy], color='white', lw=0.45,
                alpha=0.5, zorder=1, solid_capstyle='round')
        ax.plot([sx, sx], [sy - r, sy + r], color='white', lw=0.45,
                alpha=0.5, zorder=1, solid_capstyle='round')
        ax.scatter([sx], [sy], s=9, c='white', alpha=0.85, lw=0, zorder=1)


def draw_belt(ax, n=9000, seed=3):
    """Главный пояс: облако точек с щелями Кирквуда и наклонением."""
    rng = np.random.default_rng(seed)
    # распределение по большой полуоси: основная масса 2,1-3,3 а.е.
    a = rng.normal(2.70, 0.36, n)
    a = a[(a > 2.02) & (a < 3.55)]
    # щели Кирквуда — резонансы с Юпитером
    for gap, width in ((2.502, 0.018), (2.825, 0.016),
                       (2.958, 0.014), (3.279, 0.020)):
        keep = np.abs(a - gap) > rng.exponential(width, a.size)
        a = a[keep]
    m = a.size
    e = np.abs(rng.normal(0.0, 0.095, m))
    nu = rng.uniform(0, 2 * np.pi, m)
    om = rng.uniform(0, 2 * np.pi, m)
    inc = np.abs(rng.normal(0.0, math.radians(9.0), m))
    r = a * (1 - e ** 2) / (1 + e * np.cos(nu))
    th = nu + om
    x = r * np.cos(th)
    y = r * np.sin(th) * np.cos(inc)         # проекция наклонения
    size = rng.uniform(0.12, 1.15, m)
    alpha = rng.uniform(0.18, 0.62, m)
    ax.scatter(x, y, s=size, c='#b6c8de', alpha=alpha, lw=0, zorder=2)

    # группа троянцев Юпитера — L4 и L5
    for lead in (+1, -1):
        k = 420
        ang = math.radians(273.9) + lead * math.radians(60)
        aa = rng.normal(5.20, 0.16, k)
        th2 = ang + rng.normal(0, math.radians(13), k)
        rr = aa
        ax.scatter(rr * np.cos(th2), rr * np.sin(th2) * 0.985,
                   s=rng.uniform(0.15, 1.0, k), c='#9db2cd',
                   alpha=0.42, lw=0, zorder=2)


def shaded_body(ax, x, y, R, color, sun_dir=None, zorder=10, glow=True):
    """Тело со светотенью: освещённый лимб к Солнцу, терминатор, ободок."""
    if sun_dir is None:
        d = math.hypot(x, y)
        sun_dir = (-x / d, -y / d) if d > 1e-9 else (-1.0, 0.0)
    if glow:
        for k, aa in ((2.6, 0.05), (1.9, 0.08), (1.45, 0.13)):
            ax.add_patch(Circle((x, y), R * k, fc=color, ec='none',
                                alpha=aa, zorder=zorder - 1))
    # полный диск — теневая сторона
    ax.add_patch(Circle((x, y), R, fc=_dark(color, 0.42), ec='none',
                        zorder=zorder))
    # освещённый серп: полукруг, смещённый к Солнцу
    ang = math.degrees(math.atan2(sun_dir[1], sun_dir[0]))
    wedge = Ellipse((x + sun_dir[0] * R * 0.20, y + sun_dir[1] * R * 0.20),
                    R * 1.72, R * 1.94, angle=ang,
                    fc=color, ec='none', zorder=zorder + 1)
    wedge.set_clip_path(Circle((x, y), R,
                               transform=ax.transData))
    ax.add_patch(wedge)
    # блик
    ax.add_patch(Circle((x + sun_dir[0] * R * 0.34,
                         y + sun_dir[1] * R * 0.34), R * 0.30,
                        fc=_light(color, 0.55), ec='none', alpha=0.75,
                        zorder=zorder + 2))
    # ободок
    ax.add_patch(Circle((x, y), R, fc='none', ec=_light(color, 0.35),
                        lw=0.6, alpha=0.85, zorder=zorder + 3))


def _dark(hexc, f):
    r, g, b = _rgb(hexc)
    return '#%02x%02x%02x' % (int(r * f), int(g * f), int(b * f))


def _light(hexc, f):
    r, g, b = _rgb(hexc)
    return '#%02x%02x%02x' % (int(r + (255 - r) * f),
                              int(g + (255 - g) * f),
                              int(b + (255 - b) * f))


def _rgb(hexc):
    hexc = hexc.lstrip('#')
    return tuple(int(hexc[i:i + 2], 16) for i in (0, 2, 4))


def fade_orbit(ax, x, y, color, lw=1.5, zorder=5, n_seg=180):
    """Орбита с переменной прозрачностью: ярче у перигелия."""
    pts = np.array([x, y]).T.reshape(-1, 1, 2)
    segs = np.concatenate([pts[:-1], pts[1:]], axis=1)
    r = np.hypot(x, y)[:-1]
    a = 1.0 - (r - r.min()) / (r.max() - r.min() + 1e-9) * 0.62
    lc = LineCollection(segs, colors=[color] * len(segs), linewidths=lw,
                        alpha=None, zorder=zorder, capstyle='round')
    lc.set_alpha(list(np.clip(a, 0.22, 1.0)))
    ax.add_collection(lc)


def build():
    """Собирает карту в формате A3, альбомная ориентация.

    Компоновка специально рассчитана на один печатный лист A3:
    крупное поле орбит слева, короткая читаемая легенда и таблица
    ресурсов справа. Мелкие пояснительные абзацы A1-версии удалены.
    """
    # A3 landscape: 420 x 297 mm. Text sizes below are chosen for a printed page,
    # not for a zoomed-in A1 poster.
    fig = plt.figure(figsize=(420 / 25.4, 297 / 25.4), facecolor=BG)

    # ── Орбитальная карта ─────────────────────────────────────────────
    ax = fig.add_axes([0.035, 0.155, 0.585, 0.745])
    ax.set_facecolor(BG)
    xlim, ylim = (-5.82, 5.82), (-5.20, 5.20)
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect('equal')
    ax.axis('off')

    draw_starfield(ax, xlim, ylim, n=1100, seed=7)
    draw_belt(ax, n=6000, seed=3)

    # Масштабные кольца в а.е.
    for rr in range(1, 6):
        ax.add_patch(Circle((0, 0), rr, fc='none', ec=GRID, lw=0.55,
                            ls=(0, (2, 4)), zorder=3))
        ax.text(rr * 0.7071 + 0.035, -rr * 0.7071 - 0.04, f'{rr} а.е.',
                fontsize=6.4, color='#4a5878', ha='left', va='top', zorder=3)

    # Планетные орбиты и планеты.
    for name, a, e, om, i, c, Rm, nu0 in PLANETS:
        x, y = orbit_xy(a, e, om, i)
        ax.plot(x, y, color=c, lw=1.45, alpha=0.90, zorder=4)
        ax.plot(x, y, color=c, lw=4.0, alpha=0.08, zorder=3)
        px, py = point_at(a, e, om, nu0, i)
        shaded_body(ax, px, py, Rm, c, zorder=12)
        ax.text(px, py - Rm - 0.17, name, fontsize=7.3, color=c,
                ha='center', va='top', weight='bold',
                path_effects=[pe.withStroke(linewidth=2.0, foreground=BG)])

    # Солнце.
    for k, aa in ((5.8, 0.028), (3.8, 0.05), (2.4, 0.10), (1.5, 0.20)):
        ax.add_patch(Circle((0, 0), 0.105 * k, fc=SUN, ec='none',
                            alpha=aa, zorder=6))
    ax.add_patch(Circle((0, 0), 0.105, fc='#fff3c4', ec='none', zorder=8))
    ax.add_patch(Circle((0, 0), 0.082, fc='#ffffff', ec='none', zorder=9))
    ax.text(0, -0.25, 'Солнце', fontsize=7.2, color=SUN, ha='center',
            va='top', weight='bold',
            path_effects=[pe.withStroke(linewidth=2.0, foreground=BG)])

    # Орбиты ресурсных тел и точки перигелия/афелия.
    # Текущие положения самих тел намеренно не наносятся: карта показывает
    # типовые орбитальные параметры, а диаметры вынесены в правую легенду.
    for m, name, a, e, om, i, dkm, c, role in TARGETS:
        x, y = orbit_xy(a, e, om, i)
        ax.plot(x, y, color=c, lw=1.55, alpha=0.88, zorder=7)
        px, py = perihelion_xy(a, e, om, i)
        ax.plot([px], [py], marker='o', ms=6.3, color=c, zorder=13,
                markeredgecolor='white', markeredgewidth=0.9)
        qx, qy = point_at(a, e, om, 180, i)
        ax.plot([qx], [qy], marker='x', ms=6.0, mew=1.45, color=c,
                zorder=13, alpha=0.95)

    # Станция в точке L1.
    ex, ey = point_at(1.0, 0.0167, 102.9, 25, 0.0)
    d = math.hypot(ex, ey)
    sx, sy = ex * (1 - 0.010 / d), ey * (1 - 0.010 / d)
    ax.plot([sx], [sy], marker='s', ms=5.5, color=C_ST, zorder=17,
            markeredgecolor='white', markeredgewidth=0.55)
    ax.annotate('станция ММОСО′Н\nL1: 1,5 млн км от Земли',
                xy=(sx, sy), xytext=(2.18, 2.18), fontsize=7.0,
                color=C_ST, ha='left', va='center', weight='bold',
                path_effects=[pe.withStroke(linewidth=2.0, foreground=BG)],
                arrowprops=dict(arrowstyle='-', lw=0.75, color=C_ST,
                                alpha=0.8, connectionstyle='arc3,rad=-0.20'))

    ax.text(-3.25, 1.63, 'ГЛАВНЫЙ ПОЯС АСТЕРОИДОВ', fontsize=7.0,
            color='#7f8fa8', rotation=-30, ha='center', style='italic',
            path_effects=[pe.withStroke(linewidth=2.0, foreground=BG)])
    ax.text(-4.62, -2.78, 'троянцы\nЮпитера', fontsize=6.5,
            color='#7f8fa8', ha='center', style='italic',
            path_effects=[pe.withStroke(linewidth=1.8, foreground=BG)])
    ax.text(-5.72, 5.06, 'ОРБИТАЛЬНАЯ КАРТА РЕСУРСНЫХ ТЕЛ', fontsize=11.5,
            color=FG, weight='bold', ha='left', va='top')

    # Компактная легенда в левом верхнем секторе.
    kx, ky, kw, kh = -5.68, 4.66, 3.35, 0.78
    ax.add_patch(Rectangle((kx, ky - kh), kw, kh, fc='#0b1120', ec=GRID,
                           lw=0.75, alpha=0.94, zorder=20))
    ax.text(kx + 0.13, ky - 0.17, 'ОБОЗНАЧЕНИЯ', fontsize=7.3,
            color=FG, weight='bold', va='center', zorder=21)
    rows = [(ky - 0.39, 'o', 'перигелий'),
            (ky - 0.61, 'x', 'афелий')]
    for yy, mark, label in rows:
        if mark == 'o':
            ax.plot([kx + 0.22], [yy], marker='o', ms=6, color=FG_DIM,
                    markeredgecolor='white', markeredgewidth=0.8, zorder=21)
        elif mark == 'x':
            ax.plot([kx + 0.22], [yy], marker='x', ms=6, mew=1.4,
                    color=FG_DIM, zorder=21)
        ax.text(kx + 0.40, yy, label, fontsize=6.6, color=FG_DIM,
                va='center', zorder=21)

    # ── Правая колонка: крупная легенда и компактная таблица ─────────
    lg = fig.add_axes([0.645, 0.155, 0.322, 0.745])
    lg.set_facecolor(BG)
    lg.set_xlim(0, 1); lg.set_ylim(0, 1); lg.axis('off')
    lg.text(0, 1.0, 'РЕСУРСНАЯ БАЗА ПРОГРАММЫ', fontsize=13.2,
            weight='bold', color=FG, va='top')
    lg.text(0, 0.956, 'Пять источников · расстояния в а.е. · диаметры тел условны на карте',
            fontsize=7.3, color=FG_DIM, va='top')
    lg.plot([0, 1], [0.930, 0.930], color=GRID, lw=0.9)

    y = 0.905
    info = [
        (C_METAL, '1', '(6178) 1986 DA', 'диаметр Ø 3,0 км · a 2,8216 · e 0,5818 · металл', 'определяющий ресурс стали'),
        (C_WATER, '2', '(1) Церера', 'диаметр Ø 939 км · a 2,7660 · e 0,0785 · вода', 'крупнейший близкий источник воды'),
        (C_ORG, '3', '(24) Themis', 'диаметр Ø 198 км · a 3,1490 · вода и органика', 'водяной лёд и органические вещества'),
        (C_NITRO, '4', '(10) Hygiea', 'диаметр Ø 434 км · a 3,1415 · e 0,1125 · азот', 'буферный газ атмосферы'),
        (C_COMET, '5', '67P/Чурюмова — Герасименко', 'диаметр Ø 4,1 км · a 3,4620 · льды и аммиак', 'дальний кометный источник летучих'),
    ]
    for c, m, name, line1, line2 in info:
        lg.add_patch(Circle((0.022, y - 0.013), 0.014, fc=c, ec='none',
                            transform=lg.transAxes, clip_on=False))
        lg.text(0.022, y - 0.013, m, fontsize=7.0, weight='bold', color=BG,
                ha='center', va='center', transform=lg.transAxes)
        lg.text(0.060, y, name, fontsize=8.2, weight='bold', color=FG, va='top')
        lg.text(0.060, y - 0.025, line1, fontsize=7.0, color=c, va='top')
        lg.text(0.060, y - 0.046, line2, fontsize=6.8, color=FG_DIM, va='top')
        y -= 0.112

    lg.plot([0, 1], [y + 0.018, y + 0.018], color=GRID, lw=0.9)
    y -= 0.008
    lg.text(0, y, 'ПОТРЕБНОСТЬ ПРОЕКТА, млрд т', fontsize=8.7,
            weight='bold', color=FG, va='top')
    y -= 0.034
    tbl = [
        ('Сталь 18Ni(300), пояс', '20,83', C_METAL),
        ('Гермооболочка', '1,22', C_METAL),
        ('Сталь с набором', '22,05', C_METAL),
        ('Сырьё с потерями 25 %', '29,40', C_METAL),
        ('Реголит и боросиликат', '4,65', C_METAL),
        ('Грунт растительный', '8,13', C_ORG),
        ('Азот', '5,51', C_NITRO),
        ('Кислород', '2,04', C_WATER),
        ('Вода', '1,17', C_WATER),
    ]
    for i, (nm, val, c) in enumerate(tbl):
        if i % 2 == 0:
            lg.add_patch(Rectangle((0, y - 0.014), 1, 0.019, fc=BG_LG,
                                   ec='none', transform=lg.transAxes, zorder=0))
        lg.add_patch(Rectangle((0, y - 0.012), 0.008, 0.013, fc=c,
                               ec='none', transform=lg.transAxes, zorder=1))
        lg.text(0.024, y, nm, fontsize=7.0, color=FG_DIM, va='top', zorder=2)
        lg.text(1.0, y, val, fontsize=7.0, color=FG, va='top', ha='right',
                weight='bold', zorder=2)
        y -= 0.024
    y -= 0.004
    lg.text(0, y, '1986 DA покрывает около 94 % потребности в стали.\n'
                  'Остальные источники обеспечивают воду, грунт и летучие.',
            fontsize=6.9, color=FG, va='top', linespacing=1.45)

    ax.text(-5.70, -4.86, 'Диаметры тел приведены в легенде справа; размеры на орбитальной схеме условны.',
            fontsize=6.4, color=FG_DIM, ha='left', va='center')

    # Подвал.
    ft = fig.add_axes([0, 0, 1, 1]); ft.set_xlim(0, 1); ft.set_ylim(0, 1)
    ft.axis('off'); ft.patch.set_alpha(0)
    ft.plot([0.035, 0.977], [0.035, 0.035], color=GRID, lw=0.8)
    ft.text(0.035, 0.019, 'ММОСО′Н · личный проект · ресурсная карта · формат A3, альбом',
            fontsize=6.4, color=FG_DIM, va='center')
    ft.text(0.977, 0.019, 'Бугаенко Р. С., НИК · 07.09.2026 · JPL Small-Body Database',
            fontsize=6.4, color=FG_DIM, va='center', ha='right')

    png = os.path.join(HERE, 'resource_map.png')
    pdf = os.path.join(HERE, 'resource_map.pdf')
    fig.savefig(png, facecolor=BG, dpi=300)
    fig.savefig(pdf, facecolor=BG)
    plt.close(fig)
    return png, pdf


if __name__ == '__main__':
    for p in build():
        print(p)
