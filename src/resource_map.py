# -*- coding: utf-8 -*-
"""Карта ресурсных тел программы ММОСО'Н — отдельный крупноформатный лист.

Строится по реальным элементам орбит (JPL SBDB). В отличие от рисунка 22,
входящего в документ, здесь:
  * формат A1-альбом (841 x 594 мм), 300 dpi — печать и рассматривание вблизи;
  * звёздное поле и реалистичная светотень тел;
  * пояс астероидов — не серое кольцо, а облако из тысяч точек
    с распределением по большой полуоси и щелями Кирквуда;
  * орбиты с учётом наклонения (проекция на эклиптику даёт видимое сжатие);
  * тела показаны в масштабе диаметров с отдельной шкалой;
  * таблица характеристик и таблица потребности проекта.

Запуск:  python3 resource_map.py
Выход:   resource_map.png  (и resource_map.pdf)
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

HERE = os.path.dirname(os.path.abspath(__file__))

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
    # A2 альбом: 594 x 420 мм
    fig = plt.figure(figsize=(841 / 25.4, 594 / 25.4), facecolor=BG)

    # ── ГЛАВНОЕ ПОЛЕ ────────────────────────────────────────────────
    ax = fig.add_axes([0.030, 0.052, 0.605, 0.878])
    ax.set_facecolor(BG)
    LIM = 6.60
    ax.set_xlim(-LIM, LIM)
    ax.set_ylim(-LIM * 420 / 594 * (0.878 / 0.605) * 0.605 / 0.605, LIM)
    ax.set_xlim(-LIM, LIM)
    ax.set_ylim(-5.95, 5.95)
    ax.set_aspect('equal')
    ax.axis('off')

    draw_starfield(ax, (-LIM, LIM), (-5.05, 5.05))
    draw_belt(ax)

    # кольца-масштаб
    for rr in range(1, 7):
        ax.add_patch(Circle((0, 0), rr, fc='none', ec=GRID, lw=0.6,
                            ls=(0, (2, 4)), zorder=3))
        ax.text(rr * 0.7071 + 0.04, -rr * 0.7071 - 0.04, f'{rr}',
                fontsize=7.0, color='#4a5878', ha='left', va='top',
                zorder=3)
    ax.text(6.42, -5.05, 'кольца — расстояние от Солнца, а.е.',
            fontsize=7.4, color='#4a5878', ha='right', style='italic')

    # орбиты планет — сплошные, заметные, с подписью вдоль кривой
    for name, a, e, om, i, c, Rm, nu0 in PLANETS:
        x, y = orbit_xy(a, e, om, i)
        ax.plot(x, y, color=c, lw=1.9, alpha=0.85, zorder=4)
        ax.plot(x, y, color=c, lw=5.5, alpha=0.10, zorder=3)   # мягкое свечение
        # подпись орбиты у левого края кривой
        k = int(len(x) * 0.50)
        ang = math.degrees(math.atan2(y[k + 6] - y[k - 6], x[k + 6] - x[k - 6]))
        if ang > 90:
            ang -= 180
        if ang < -90:
            ang += 180
        ax.text(x[k], y[k], f' орбита {name} ', fontsize=8.0, color=c,
                ha='center', va='center', rotation=ang, alpha=0.95,
                rotation_mode='anchor',
                bbox=dict(fc=BG, ec='none', pad=0.9), zorder=5)
    # планеты — тела
    for name, a, e, om, i, c, R, nu in PLANETS:
        px, py = point_at(a, e, om, nu, i)
        shaded_body(ax, px, py, R, c, zorder=12)
        ax.text(px, py - R - 0.19, name, fontsize=9.2, color=c,
                ha='center', va='top', weight='bold',
                path_effects=[pe.withStroke(linewidth=2.6, foreground=BG)])

    # Солнце
    for k, aa in ((7.0, 0.028), (4.6, 0.05), (3.0, 0.09),
                  (2.0, 0.16), (1.4, 0.28)):
        ax.add_patch(Circle((0, 0), 0.115 * k, fc=SUN, ec='none',
                            alpha=aa, zorder=6))
    ax.add_patch(Circle((0, 0), 0.125, fc='#fff3c4', ec='none', zorder=8))
    ax.add_patch(Circle((0, 0), 0.098, fc='#ffffff', ec='none', zorder=9))
    ax.text(0, -0.30, 'Солнце', fontsize=8.6, color=SUN, ha='center',
            va='top', weight='bold',
            path_effects=[pe.withStroke(linewidth=2.6, foreground=BG)])

    # орбиты и тела ресурсных объектов
    # ВАЖНО: тело показывается НЕ в перигелии, иначе шар накрывает метку
    # перигелия и та становится невидимой. Тело ставится на текущее
    # положение по орбите, перигелий и афелий отмечаются отдельно.
    BODY_NU = {'1': 300, '2': 205, '3': 60, '4': 145, '5': 250}
    for m, name, a, e, om, i, dkm, c, role in TARGETS:
        x, y = orbit_xy(a, e, om, i)
        fade_orbit(ax, x, y, c, lw=2.2, zorder=7)

        # ── метка перигелия: залитый кружок с белым ободком ──
        px, py = perihelion_xy(a, e, om, i)
        ax.plot([px], [py], marker='o', ms=8.5, color=c, zorder=13,
                markeredgecolor='white', markeredgewidth=1.3)
        # ── метка афелия: косой крест ──
        qx, qy = point_at(a, e, om, 180, i)
        ax.plot([qx], [qy], marker='x', ms=8.0, mew=2.0, color=c,
                zorder=13, alpha=0.95)

        # ── само тело в стороне от обеих меток ──
        bx, by = point_at(a, e, om, BODY_NU[m], i)
        R = 0.062 + 0.085 * math.log10(max(dkm, 1.0)) / 3.0
        shaded_body(ax, bx, by, R, c, zorder=14)
        d = math.hypot(bx, by) or 1
        ox, oy = bx / d * (R + 0.34), by / d * (R + 0.34)
        ax.text(bx + ox, by + oy, m, fontsize=10.0, weight='bold',
                color=BG, ha='center', va='center', zorder=16,
                bbox=dict(boxstyle='circle,pad=0.32', fc=c, ec='none'))

    # станция в L1
    ex, ey = point_at(1.0, 0.0167, 102.9, 25, 0.0)
    d = math.hypot(ex, ey)
    sx, sy = ex * (1 - 0.010 / d), ey * (1 - 0.010 / d)
    ax.plot([sx], [sy], marker='s', ms=7.0, color=C_ST, zorder=17,
            markeredgecolor='white', markeredgewidth=0.7)
    ax.annotate('станция ММОСО′Н\nточка L1, 1,5 млн км от Земли',
                xy=(sx, sy), xytext=(2.35, 2.62),
                fontsize=8.4, color=C_ST, ha='left', va='center',
                weight='bold',
                path_effects=[pe.withStroke(linewidth=2.6, foreground=BG)],
                arrowprops=dict(arrowstyle='-', lw=0.9, color=C_ST,
                                alpha=0.8,
                                connectionstyle='arc3,rad=-0.22'))

    # подпись пояса
    ax.text(-3.42, 1.72, 'ГЛАВНЫЙ ПОЯС АСТЕРОИДОВ', fontsize=8.6,
            color='#7f8fa8', rotation=-30, ha='center', style='italic',
            path_effects=[pe.withStroke(linewidth=2.6, foreground=BG)])
    ax.text(-4.72, -2.95, 'троянцы\nЮпитера', fontsize=7.4,
            color='#7f8fa8', ha='center', style='italic',
            path_effects=[pe.withStroke(linewidth=2.4, foreground=BG)])

    ax.text(1.05, -5.62,
            'Плоскость эклиптики, вид с северного полюса мира. '
            'Орбиты показаны с учётом наклонения — отсюда видимое сжатие.',
            fontsize=8.2, color=FG_DIM, va='center', linespacing=1.55)

    # ── КЛЮЧ УСЛОВНЫХ ОБОЗНАЧЕНИЙ (врезка в поле карты) ──────────────
    kx, ky = -LIM + 0.16, 5.82          # левый верхний угол врезки
    kw, kh = 3.60, 1.52
    ax.add_patch(Rectangle((kx, ky - kh), kw, kh, fc='#0b1120', ec=GRID,
                           lw=0.9, alpha=0.92, zorder=20))
    ax.text(kx + 0.13, ky - 0.19, 'УСЛОВНЫЕ ОБОЗНАЧЕНИЯ', fontsize=8.4,
            color=FG, weight='bold', va='center', zorder=21)
    _ky = ky - 0.52
    # перигелий
    ax.plot([kx + 0.29], [_ky], marker='o', ms=9.5, color=FG_DIM, zorder=21,
            markeredgecolor='white', markeredgewidth=1.3)
    ax.text(kx + 0.56, _ky, 'перигелий — ближайшая к Солнцу точка орбиты',
            fontsize=8.0, color=FG_DIM, va='center', zorder=21)
    _ky -= 0.34
    # афелий
    ax.plot([kx + 0.29], [_ky], marker='x', ms=9.0, mew=2.0, color=FG_DIM,
            zorder=21)
    ax.text(kx + 0.56, _ky, 'афелий — наиболее удалённая точка орбиты',
            fontsize=8.0, color=FG_DIM, va='center', zorder=21)
    _ky -= 0.34
    # тело
    shaded_body(ax, kx + 0.29, _ky, 0.115, FG_DIM, sun_dir=(-1, 0.25),
                zorder=21, glow=False)
    ax.text(kx + 0.56, _ky, 'само тело: положение на орбите, размер условен',
            fontsize=8.0, color=FG_DIM, va='center', zorder=24)

    # ── ПРАВАЯ КОЛОНКА ──────────────────────────────────────────────
    lg = fig.add_axes([0.652, 0.052, 0.325, 0.878])
    lg.set_facecolor(BG)
    lg.set_xlim(0, 1)
    lg.set_ylim(0, 1)
    lg.axis('off')

    lg.text(0, 1.0, 'РЕСУРСНАЯ БАЗА ПРОГРАММЫ', fontsize=15.5,
            weight='bold', color=FG, va='top')
    lg.text(0, 0.968, 'Модуль моделирования орбитальной станции О′Нилла',
            fontsize=8.6, color=FG_DIM, va='top')
    lg.plot([0, 1], [0.951, 0.951], color=GRID, lw=1.1)

    y = 0.930
    info = [
        (C_METAL, '1', '(6178) 1986 DA', 'металл — определяющий ресурс',
         ['M-тип · Ø ≈ 3,0 км · масса ≈ 37 млрд т',
          'a = 2,8216 а.е. · e = 0,5818 · i = 4,31°',
          'перигелий 1,18 · афелий 4,46 · период 4,70 года',
          'никель-железо: покрывает 94 % потребности в стали']),
        (C_WATER, '2', '(1) Церера', 'вода — ближайший крупный источник',
         ['C-тип, карликовая планета · Ø 939 км',
          'a = 2,7660 а.е. · e = 0,0785 · i = 10,59°',
          'период 4,60 года · водяной лёд в коре и мантии',
          'запас воды превосходит потребность на порядки']),
        (C_ORG, '3', '(24) Themis', 'вода и органика',
         ['C/B-тип · Ø 198 км · иней водяного льда',
          'a = 3,1490 а.е. · e = 0,1165 · i = 0,74°',
          'на поверхности обнаружены водяной лёд и органика',
          'семейство Themis — тысячи тел того же состава']),
        (C_NITRO, '4', '(10) Hygiea', 'азот — буферный газ атмосферы',
         ['C-тип · Ø 434 км · крупнейшее тело внешнего пояса',
          'a = 3,1415 а.е. · e = 0,1125 · i = 3,83°',
          'гидратированные и аммонийные силикаты',
          'источник 5,51 млрд т азота для атмосферы']),
        (C_COMET, '5', '67P/Чурюмова — Герасименко', 'льды, аммиак',
         ['короткопериодическая комета · Ø ядра 4,1 км',
          'a = 3,4620 а.е. · e = 0,6410 · i = 7,04°',
          'перигелий 1,24 · афелий 5,68 а.е.',
          'аммиак и азот во льду — около 1 % массы ядра']),
    ]
    for c, m, name, role, lines in info:
        lg.add_patch(Circle((0.021, y - 0.011), 0.0155, fc=c, ec='none',
                            transform=lg.transAxes, clip_on=False))
        lg.text(0.021, y - 0.011, m, fontsize=8.2, weight='bold', color=BG,
                ha='center', va='center', transform=lg.transAxes)
        lg.text(0.058, y, name, fontsize=10.2, weight='bold', color=FG,
                va='top')
        lg.text(0.058, y - 0.0225, role, fontsize=8.2, color=c, va='top',
                style='italic')
        yy = y - 0.047
        for ln in lines:
            lg.text(0.058, yy, ln, fontsize=7.7, color=FG_DIM, va='top')
            yy -= 0.0182
        y = yy - 0.0165

    # ── таблица потребности ──
    lg.plot([0, 1], [y + 0.008, y + 0.008], color=GRID, lw=1.1)
    y -= 0.020
    lg.text(0, y, 'ПОТРЕБНОСТЬ ПРОЕКТА, млрд т', fontsize=9.6,
            weight='bold', color=FG, va='top')
    y -= 0.030
    tbl = [
        ('Сталь 18Ni(300), силовой пояс', '20,83', C_METAL),
        ('Сталь нержавеющая, гермооболочка', '1,22', C_METAL),
        ('Сталь всего с силовым набором', '22,05', C_METAL),
        ('Сырьё с потерями 25 %', '29,40', C_METAL),
        ('Реголит и боросиликат', '4,65', C_METAL),
        ('Грунт растительный', '8,13', C_ORG),
        ('Азот атмосферы', '5,51', C_NITRO),
        ('Кислород атмосферы', '2,04', C_WATER),
        ('Вода', '1,17', C_WATER),
    ]
    for i, (nm, val, c) in enumerate(tbl):
        if i % 2 == 0:
            lg.add_patch(Rectangle((0, y - 0.0142), 1, 0.0182, fc=BG_LG,
                                   ec='none', transform=lg.transAxes,
                                   zorder=0))
        lg.add_patch(Rectangle((0, y - 0.0125), 0.006, 0.0135, fc=c,
                               ec='none', transform=lg.transAxes, zorder=1))
        lg.text(0.022, y, nm, fontsize=7.9, color=FG_DIM, va='top', zorder=2)
        lg.text(1.0, y, val, fontsize=7.9, color=FG, va='top', ha='right',
                weight='bold', zorder=2)
        y -= 0.0182
    y -= 0.006
    lg.plot([0, 1], [y + 0.006, y + 0.006], color=GRID, lw=0.8)
    y -= 0.016
    lg.text(0, y, 'Металл астероида (6178) 1986 DA покрывает 94 % '
                  'потребности\nв стали. Это определяющее ограничение '
                  'программы: прочие\nресурсы имеются в избытке '
                  '(приложение Б, п. Б.16).',
            fontsize=7.8, color=FG, va='top', linespacing=1.62)

    # ── ШКАЛА РАЗМЕРОВ ТЕЛ (врезка) ─────────────────────────────────
    sc = fig.add_axes([0.038, 0.062, 0.175, 0.150])
    sc.set_facecolor('#0b1120')
    sc.set_xlim(0, 1)
    sc.set_ylim(0, 0.606)      # w/h оси = 1,65 -> круги остаются кругами
    sc.set_aspect('equal')
    sc.set_xticks([])
    sc.set_yticks([])
    for spine in sc.spines.values():
        spine.set_color(GRID)
        spine.set_linewidth(0.9)
    sc.text(0.045, 0.560, 'ДЕЙСТВИТЕЛЬНЫЕ РАЗМЕРЫ ТЕЛ', fontsize=7.2,
            color=FG, weight='bold', va='top')
    sizes = [('Церера', 939.4, C_WATER), ('Hygiea', 434.0, C_NITRO),
             ('Themis', 198.0, C_ORG), ('67P', 4.1, C_COMET),
             ('1986 DA', 3.0, C_METAL)]
    scale = 0.235 / 939.4          # радиус в долях оси
    xpos = 0.085
    for nm, dkm, c in sizes:
        r = max(dkm * scale / 2, 0.0075)
        sc.add_patch(Circle((xpos + r, 0.275), r, fc=c, ec=_light(c, 0.3),
                            lw=0.5))
        sc.text(xpos + r, 0.275 - r - 0.030, nm, fontsize=6.0, color=FG_DIM,
                ha='center', va='top', rotation=0)
        sc.text(xpos + r, 0.275 + r + 0.018,
                f'{dkm:.0f}'.replace('.', ',') if dkm >= 10 else
                f'{dkm:.1f}'.replace('.', ','),
                fontsize=5.8, color=c, ha='center', va='bottom')
        xpos += 2 * r + 0.052
    sc.text(0.045, 0.038, 'диаметр, км · единый масштаб',
            fontsize=6.0, color='#5a6a85', va='bottom')

    # ── ПОДВАЛ ──────────────────────────────────────────────────────
    ft = fig.add_axes([0, 0, 1, 1])
    ft.set_xlim(0, 1)
    ft.set_ylim(0, 1)
    ft.axis('off')
    ft.patch.set_alpha(0)
    ft.plot([0.030, 0.977], [0.038, 0.038], color=GRID, lw=1.0)
    ft.text(0.030, 0.026,
            'МХ «КРЯК» · ММОСО′Н · проект «Уютные регионы» · '
            'Курское региональное отделение',
            fontsize=7.6, color=FG_DIM, va='center')
    ft.text(0.977, 0.026,
            'Бугаенко Р. С., НИК · 07.09.2026 · элементы орбит: '
            'JPL Small-Body Database',
            fontsize=7.6, color=FG_DIM, va='center', ha='right')

    png = os.path.join(HERE, 'resource_map.png')
    pdf = os.path.join(HERE, 'resource_map.pdf')
    fig.savefig(png, facecolor=BG, dpi=300)
    fig.savefig(pdf, facecolor=BG)
    plt.close(fig)
    return png, pdf


if __name__ == '__main__':
    for p in build():
        print(p)
