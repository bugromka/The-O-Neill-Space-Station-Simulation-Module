# -*- coding: utf-8 -*-
"""
ММОСО'Н — генератор иллюстраций к документу (редакция 7.0).
Все числовые значения взяты из MMOSON_v6.docx и приложения А.
Автор: Бугаенко Роман Сергеевич, НИК.
"""
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Wedge, FancyArrowPatch, Polygon, Ellipse
from matplotlib.lines import Line2D

plt.rcParams.update({
    'font.family': 'DejaVu Serif',
    'font.size': 9,
    'axes.titlesize': 10.5,
    'axes.labelsize': 9.5,
    'axes.edgecolor': '#333333',
    'axes.linewidth': 0.8,
    'figure.dpi': 200,
    'savefig.dpi': 200,
    'savefig.bbox': 'tight',
    'savefig.facecolor': 'white',
})

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fig')
os.makedirs(OUT, exist_ok=True)

# Палитра: сдержанная, печатается в оттенках серого без потери смысла
C_STEEL = '#3d5a80'
C_ACC = '#bb4430'
C_OK = '#4a7c59'
C_WARN = '#c9992c'
C_GREY = '#8d99ae'
C_LIGHT = '#e0e5ec'
ZONE_COLORS = ['#2a9d5c', '#8bbf3f', '#c9a227', '#7fb8d4']

R = 5000.0
OMEGA = 0.04429
L = 40.0


def save(fig, name):
    p = os.path.join(OUT, name)
    fig.savefig(p)
    plt.close(fig)
    print('  ', name)
    return p


# ─────────────────────────────────────────────────────────────
# Рис. 1. Общая компоновка станции
# ─────────────────────────────────────────────────────────────
def fig01():
    fig = plt.figure(figsize=(7.8, 4.6))
    ax = fig.add_axes([0.010, 0.030, 0.610, 0.940])
    lg = fig.add_axes([0.630, 0.030, 0.365, 0.940]); lg.axis('off')

    H = 10.0
    TOP, BOT = 15.5, 0.0

    def cyl(y0):
        # корпус
        ax.add_patch(Rectangle((0, y0), 40, H, fc='#dfe7ef', ec=C_STEEL, lw=1.2))
        ax.add_patch(Wedge((0, y0 + H / 2), H / 2, 90, 270, fc='#cbd7e3',
                           ec=C_STEEL, lw=1.2))
        ax.add_patch(Wedge((40, y0 + H / 2), H / 2, 270, 90, fc='#cbd7e3',
                           ec=C_STEEL, lw=1.2))
        # климатические полосы — тонкой лентой по жилой поверхности
        bounds = [0, 10, 22, 32, 40]
        for i in range(4):
            for yy in (y0 + 0.10, y0 + H - 0.52):
                ax.add_patch(Rectangle((bounds[i], yy), bounds[i + 1] - bounds[i],
                                       0.42, fc=ZONE_COLORS[i], ec='none', alpha=.9))
        # осевая балка: истинный диаметр 8 м при Ø цилиндра 10 км неразличим,
        # поэтому показана тонкой условной линией
        ax.plot([-4.2, 44.2], [y0 + H / 2, y0 + H / 2], color=C_WARN, lw=0.9,
                solid_capstyle='butt', zorder=5)

    cyl(TOP); cyl(BOT)
    at, ab = TOP + H / 2, BOT + H / 2

    # неподвижная ферменная рама по осям
    for xa in (-4.2, 44.2):
        ax.plot([xa, xa], [ab, at], color=C_GREY, lw=1.8, zorder=4)
        for k in range(7):
            y1 = ab + k * (at - ab) / 7
            y2 = y1 + (at - ab) / 7
            ax.plot([xa - 1.1, xa + 1.1], [y1, y2], color=C_GREY, lw=0.55, zorder=3)
            ax.plot([xa + 1.1, xa - 1.1], [y1, y2], color=C_GREY, lw=0.55, zorder=3)
        ax.plot([xa - 1.1, xa - 1.1], [ab, at], color=C_GREY, lw=0.7, zorder=3)
        ax.plot([xa + 1.1, xa + 1.1], [ab, at], color=C_GREY, lw=0.7, zorder=3)
        for yy in (at, ab):
            ax.add_patch(Circle((xa, yy), 0.62, fc='white', ec=C_ACC, lw=1.4, zorder=6))

    # радиаторные панели: закреплены на выносных пилонах от ферменной рамы,
    # в плоскости рамы между цилиндрами (п. 4.4)
    for xa in (-4.2, 44.2):
        sgn = -1 if xa < 0 else 1
        for yc in (ab + (at - ab) * 0.22, ab + (at - ab) * 0.50,
                   ab + (at - ab) * 0.78):
            # пилон от пояса рамы к панели
            ax.plot([xa + sgn * 1.1, xa + sgn * 2.3], [yc, yc],
                    color=C_GREY, lw=0.9, zorder=3)
            # сама панель — вдоль рамы, ребром к цилиндрам
            ax.add_patch(Rectangle((xa + sgn * 2.3, yc - 1.35), sgn * 0.45, 2.7,
                                   fc='#b9c4cf', ec='#7d8b99', lw=0.6, zorder=3))
            for k in range(1, 4):
                yl = yc - 1.35 + k * 2.7 / 4
                ax.plot([xa + sgn * 2.3, xa + sgn * 2.75], [yl, yl],
                        color='#8f9daa', lw=0.4, zorder=4)

    # встречное вращение
    ax.annotate('', xy=(9.5, TOP + H + 1.1), xytext=(4.0, TOP + H + 1.1),
                arrowprops=dict(arrowstyle='-|>', color=C_STEEL, lw=1.3,
                                connectionstyle='arc3,rad=-0.45'))
    ax.annotate('', xy=(4.0, BOT - 1.1), xytext=(9.5, BOT - 1.1),
                arrowprops=dict(arrowstyle='-|>', color=C_STEEL, lw=1.3,
                                connectionstyle='arc3,rad=-0.45'))
    # к Солнцу
    ax.annotate('', xy=(2.5, TOP + H + 4.0), xytext=(10.5, TOP + H + 4.0),
                arrowprops=dict(arrowstyle='-|>', color=C_WARN, lw=1.6))
    ax.text(11.4, TOP + H + 4.0, 'к Солнцу', ha='left', va='center',
            fontsize=8.0, color='#8a6a1a')

    # размеры
    ax.annotate('', xy=(0, BOT - 3.6), xytext=(40, BOT - 3.6),
                arrowprops=dict(arrowstyle='<->', color='#333', lw=0.8))
    ax.text(20, BOT - 4.7, 'цилиндрическая часть 40 км', ha='center', fontsize=8.0,
            bbox=dict(fc='white', ec='none', pad=1.2))
    ax.annotate('', xy=(-4.2, BOT - 6.4), xytext=(44.2, BOT - 6.4),
                arrowprops=dict(arrowstyle='<->', color='#333', lw=0.8))
    ax.text(20, BOT - 7.5, 'полная длина 49 км (полусферы по 4,5 км)',
            ha='center', fontsize=8.0, bbox=dict(fc='white', ec='none', pad=1.2))
    ax.annotate('', xy=(-8.6, BOT), xytext=(-8.6, BOT + H),
                arrowprops=dict(arrowstyle='<->', color='#333', lw=0.8))
    ax.text(-9.5, BOT + H / 2, 'Ø 10 км', rotation=90, ha='center',
            va='center', fontsize=8.0)

    # номерные выноски
    marks = [('1', (-4.2, at), (-14.5, at + 5.6)),
             ('2', (45.3, (at + ab) / 2), (50.5, (at + ab) / 2 + 3.2)),
             ('3', (22.0, at), (22.0, at + 5.4)),
             ('4', (30.0, BOT + 0.31), (34.5, BOT - 2.4)),
             ('5', (47.0, ab + (at - ab) * 0.22), (52.0, ab - 2.2))]
    for num, xy, xyt in marks:
        ax.annotate(num, xy=xy, xytext=xyt, fontsize=7.6, weight='bold',
                    color='white', ha='center', va='center',
                    bbox=dict(boxstyle='circle,pad=0.26', fc=C_STEEL, ec='none'),
                    arrowprops=dict(arrowstyle='->', lw=0.85, color='#777',
                                    connectionstyle='arc3,rad=0.16'))

    ax.set_xlim(-18, 56); ax.set_ylim(BOT - 10.0, TOP + H + 6.5)
    ax.set_aspect('equal'); ax.axis('off')

    lg.text(0.0, 1.0, 'Компоновка станции: два встречно вращающихся цилиндра',
            fontsize=9.0, weight='bold', va='top', transform=lg.transAxes)
    lg.text(0.0, 0.930, 'ω = 0,0443 рад/с · 0,423 об/мин · период 141,9 с',
            fontsize=7.4, va='top', color='#555', transform=lg.transAxes)

    rows = [('1', C_STEEL, 'Подшипниковый узел',
             'граница вращающегося цилиндра\nи неподвижной рамы'),
            ('2', C_STEEL, 'Неподвижная ферменная рама',
             'соединяет только оси вращения;\nнесёт причалы, склады, реакторы'),
            ('3', C_STEEL, 'Осевая светотепловая балка',
             'показана условной линией: диаметр 8 м\nпри Ø цилиндра 10 км неразличим'),
            ('4', C_STEEL, 'Жилая поверхность',
             'климатические зоны, 1,000 g'),
            ('5', C_STEEL, 'Радиаторные панели',
             'вынесены на раму, 1 477 км²')]
    yy = 0.845
    for m, c, t1, t2 in rows:
        lg.text(0.028, yy - 0.024, m, fontsize=7.4, weight='bold', color='white',
                ha='center', va='center', transform=lg.transAxes,
                bbox=dict(boxstyle='circle,pad=0.26', fc=c, ec='none'))
        lg.text(0.098, yy, t1, fontsize=8.0, va='top', transform=lg.transAxes)
        lg.text(0.098, yy - 0.062, t2, fontsize=7.2, va='top', color='#555',
                linespacing=1.4, transform=lg.transAxes)
        yy -= 0.132
    yy -= 0.010

    lg.text(0.0, yy, 'Климатические зоны, км от переднего торца',
            fontsize=8.0, weight='bold', va='top', transform=lg.transAxes)
    yy -= 0.058
    zn = ['тропическая 0–10', 'субтропическая 10–22',
          'умеренная 22–32', 'холодная 32–40']
    for i, n in enumerate(zn):
        col = i % 2
        row = i // 2
        xx = 0.020 + col * 0.500
        yc = yy - row * 0.058
        lg.add_patch(Rectangle((xx, yc - 0.036), 0.030, 0.030,
                               fc=ZONE_COLORS[i], ec='none',
                               transform=lg.transAxes, clip_on=False))
        lg.text(xx + 0.048, yc - 0.006, n, fontsize=7.3, va='center',
                transform=lg.transAxes)
    yy -= 0.135

    lg.text(0.0, yy, 'Боковые поверхности цилиндров между собой\n'
            'не связаны: они вращаются, и жёсткое соединение\n'
            'по ним невозможно. Связь только по осям.',
            fontsize=7.3, va='top', color=C_ACC, weight='bold',
            linespacing=1.5, transform=lg.transAxes)
    return save(fig, 'fig01_layout.png')


# ─────────────────────────────────────────────────────────────
# Рис. 2. Поперечное сечение и конструкционный пакет
# ─────────────────────────────────────────────────────────────
def fig02():
    fig = plt.figure(figsize=(7.6, 3.9))
    ax = fig.add_axes([0.010, 0.040, 0.335, 0.905])
    ax2 = fig.add_axes([0.385, 0.115, 0.135, 0.790])
    lg = fig.add_axes([0.535, 0.040, 0.460, 0.905]); lg.axis('off')

    # ── сечение цилиндра ──
    ax.add_patch(Circle((0, 0), 1.00, fc='#dfe7ef', ec=C_STEEL, lw=1.3))
    ax.add_patch(Circle((0, 0), 0.982, fc='#f2f5f8', ec='none'))
    ax.add_patch(Wedge((0, 0), 0.982, 0, 360, width=0.016,
                       fc='#7a6a52', ec='none'))
    ax.add_patch(Circle((0, 0), 0.014, fc=C_WARN, ec='none'))
    ax.plot([0, 0], [0, 0.982], color='#555', lw=0.8, ls='--')
    ax.text(0.035, 0.49, 'R = 5 000 м', rotation=90, fontsize=7.6, va='center')

    # сектор увеличения
    th = np.linspace(np.deg2rad(52), np.deg2rad(68), 40)
    ax.plot(np.cos(th), np.sin(th), color=C_ACC, lw=2.2, zorder=6)
    ax.annotate('', xy=(1.62, 0.62), xytext=(0.62, 0.79),
                arrowprops=dict(arrowstyle='->', lw=0.9, color=C_ACC,
                                connectionstyle='arc3,rad=-0.25'))
    for m, xy, xyt in [('1', (0.0, 0.0), (-0.62, -0.30)),
                       ('2', (0.70, -0.70), (0.86, -1.18))]:
        ax.annotate(m, xy=xy, xytext=xyt, fontsize=7.4, weight='bold',
                    color='white', ha='center', va='center',
                    bbox=dict(boxstyle='circle,pad=0.26', fc=C_STEEL, ec='none'),
                    arrowprops=dict(arrowstyle='->', lw=0.85, color='#777',
                                    connectionstyle='arc3,rad=0.18'))
    ax.set_xlim(-1.30, 1.75); ax.set_ylim(-1.35, 1.20)
    ax.set_aspect('equal'); ax.axis('off')

    # ── пакет обшивки: врезка с увеличением ──
    layers = [('Гермооболочка, нерж. сталь', 0.05, '#9aa7b5', '0,608'),
              ('Силовой пояс, 18Ni(300)', 0.85, C_STEEL, '10,343'),
              ('Теплоизоляция, коммуникации', 0.10, '#c7b299', '0,078'),
              ('Радиационная защита,\nреголит + боросиликат', 1.00, '#7d6b58', '2,325'),
              ('Грунт растительный', 1.50, '#6b5636', '4,060')]
    y = 0
    for i, (name, t, c, m) in enumerate(layers):
        ax2.add_patch(Rectangle((0, y), 1, t, fc=c, ec='white', lw=1.1))
        if t >= 0.5:
            ax2.text(0.5, y + t / 2, str(i + 3), ha='center', va='center',
                     fontsize=7.6, weight='bold', color='white')
        else:
            # тонкие слои: номер выносится вбок стрелкой
            ax2.annotate(str(i + 3), xy=(1.0, y + t / 2), xytext=(1.62, y + t / 2),
                         fontsize=7.2, weight='bold', color='white',
                         ha='center', va='center',
                         bbox=dict(boxstyle='circle,pad=0.22', fc=c, ec='#999',
                                   lw=0.4),
                         arrowprops=dict(arrowstyle='-', lw=0.7, color='#999'))
        y += t
    ax2.annotate('', xy=(-0.34, 0), xytext=(-0.34, 2.0),
                 arrowprops=dict(arrowstyle='<->', color='#333', lw=0.9))
    ax2.text(-0.62, 1.0, 'пакет 2,00 м', rotation=90, va='center',
             ha='center', fontsize=7.4)
    ax2.annotate('', xy=(2.16, 2.0), xytext=(2.16, 3.5),
                 arrowprops=dict(arrowstyle='<->', color='#333', lw=0.9))
    ax2.text(2.44, 2.75, 'грунт 1,50 м', rotation=90, va='center',
             ha='center', fontsize=7.4)
    ax2.text(0.5, -0.22, 'наружу\n(космос)', ha='center', va='top',
             fontsize=7.0, color='#555')
    ax2.text(0.5, 3.66, 'внутрь\n(атмосфера)', ha='center', va='bottom',
             fontsize=7.0, color='#555')
    ax2.set_xlim(-0.85, 2.75); ax2.set_ylim(-0.95, 4.35)
    ax2.axis('off')

    # ── легенда ──
    lg.text(0.0, 1.0, 'Поперечное сечение и пакет обшивки', fontsize=9.5,
            weight='bold', va='top', transform=lg.transAxes)
    lg.text(0.0, 0.930, 'Толщина пакета 2 м при радиусе 5 000 м: в масштабе\n'
            'сечения слои неразличимы, поэтому показаны врезкой',
            fontsize=7.2, va='top', color='#555', linespacing=1.4,
            transform=lg.transAxes)

    rows = [('1', C_WARN, 'Осевая светотепловая балка', 'Ø 8 м, показана условно'),
            ('2', '#7a6a52', 'Жилая поверхность', '1,000 g · 221,5 м/с')]
    yy = 0.815
    for m, c, t1, t2 in rows:
        lg.text(0.028, yy - 0.030, m, fontsize=7.4, weight='bold', color='white',
                ha='center', va='center', transform=lg.transAxes,
                bbox=dict(boxstyle='circle,pad=0.26', fc=C_STEEL, ec='none'))
        lg.text(0.098, yy, t1, fontsize=8.0, va='top', transform=lg.transAxes)
        lg.text(0.098, yy - 0.072, t2, fontsize=7.3, va='top', color='#555',
                transform=lg.transAxes)
        yy -= 0.148
    yy -= 0.020

    lg.text(0.0, yy, 'Слои врезки, снаружи внутрь', fontsize=8.4,
            weight='bold', va='top', transform=lg.transAxes)
    yy -= 0.072
    for i, (name, t, c, m) in enumerate(layers):
        lg.add_patch(Rectangle((0.010, yy - 0.052), 0.026, 0.056, fc=c,
                               ec='#999', lw=0.4,
                               transform=lg.transAxes, clip_on=False))
        lg.text(0.070, yy, f'{i + 3} — ' + name.replace('\n', ' '),
                fontsize=7.7, va='top', transform=lg.transAxes)
        lg.text(0.070, yy - 0.070, f'{t:.2f} м · {m} млрд т'.replace('.', ','),
                fontsize=7.2, va='top', color='#555', transform=lg.transAxes)
        yy -= 0.140
    return save(fig, 'fig02_section.png')


# ─────────────────────────────────────────────────────────────
# Рис. 3. Тяжесть и линейная скорость по радиусу
# ─────────────────────────────────────────────────────────────
def fig03():
    r = np.linspace(0, R, 400)
    g = OMEGA ** 2 * r / 9.81
    fig, ax = plt.subplots(figsize=(6.6, 3.5))
    ax.plot(r / 1000, g, color=C_STEEL, lw=2.2)
    ax.fill_between(r / 1000, 0, g, color=C_STEEL, alpha=.08)
    ax.set_xlabel('расстояние от оси, км')
    ax.set_ylabel('местная тяжесть, доли g')
    ax.grid(alpha=.3, ls=':')
    ax.set_xlim(0, 5); ax.set_ylim(0, 1.05)

    # вторая шкала — та же прямая, выраженная в линейной скорости
    axb = ax.twinx()
    axb.set_ylim(0, 1.05 * OMEGA * R)
    axb.set_ylabel('линейная скорость, м/с')
    axb.grid(False)

    ax.text(0.15, 0.55, 'тяжесть и окружная скорость\nрастут строго пропорционально\n'
                        'радиусу: a = ω²r,  v = ωr',
            fontsize=7.8, color=C_STEEL, va='center', linespacing=1.5)

    for rr, lbl, xt, yt in [(5000, '1,000 g · 221,5 м/с', 3.35, 0.86),
                            (2500, '0,500 g · 110,7 м/с', 3.95, 0.44),
                            (1000, '0,200 g · 44,3 м/с', 2.55, 0.20),
                            (100, '0,020 g · 4,4 м/с', 1.05, 0.09)]:
        gg = OMEGA ** 2 * rr / 9.81
        ax.plot([rr / 1000], [gg], 'o', color=C_ACC, ms=5.5, zorder=5)
        ax.annotate(lbl, xy=(rr / 1000, gg), xytext=(xt, yt), fontsize=7.8,
                    ha='center', va='center',
                    bbox=dict(fc='white', ec='#ccc', lw=0.6,
                              boxstyle='round,pad=0.28'),
                    arrowprops=dict(arrowstyle='->', lw=0.8, color='#888',
                                    connectionstyle='arc3,rad=0.15'))

    ax.axhspan(0, 0.02, color=C_OK, alpha=.15)
    ax.text(2.45, 0.038, 'зона возможной стыковки: r < 100 м, v < 4,4 м/с',
            fontsize=7.8, color=C_OK)
    return save(fig, 'fig03_gravity.png')


# ─────────────────────────────────────────────────────────────
# Рис. 4. Климатическое зонирование
# ─────────────────────────────────────────────────────────────
def fig04():
    fig = plt.figure(figsize=(8.4, 4.6))
    ax = fig.add_axes([0.085, 0.125, 0.400, 0.830])
    lg = fig.add_axes([0.525, 0.045, 0.465, 0.910]); lg.axis('off')

    zones = [('Тропическая', 0, 10, 28, 35, '70–85 %'),
             ('Субтропическая', 10, 22, 15, 28, '60–70 %'),
             ('Умеренная', 22, 32, 0, 15, '55–65 %'),
             ('Холодная', 32, 40, -15, -5, '40–50 %')]
    light = [220, 170, 120, 60]
    role = ['теплолюбивые культуры, рис, батат, бананы',
            'зерновые, соя, масличные, сады, зелень из арктики',
            'пшеница, картофель, ячмень, овощи, грибы из арктики',
            'только морозостойкие многолетники, теплиц нет']
    for i, (n, a, b, t0, t1, hum) in enumerate(zones):
        ax.add_patch(Rectangle((a, t0), b - a, t1 - t0, fc=ZONE_COLORS[i],
                               ec='white', lw=1.2, alpha=.9))
        ax.text((a + b) / 2, (t0 + t1) / 2, str(i + 1), ha='center', va='center',
                fontsize=8.6, weight='bold', zorder=6, color=ZONE_COLORS[i],
                bbox=dict(boxstyle='circle,pad=0.28', fc='white',
                          ec=ZONE_COLORS[i], lw=1.0))
    xs = [0, 10, 22, 32, 40]
    mids = [(xs[i] + xs[i + 1]) / 2 for i in range(4)]
    temps = [31.5, 21.5, 7.5, -10]
    ax.plot(mids, temps, 'o--', color='#2b2b2b', lw=1.1, ms=4, zorder=4, alpha=.55)
    for x in xs[1:-1]:
        ax.axvline(x, color='#555', ls='--', lw=0.8)
        ax.plot([x], [40.5], 'v', color='#555', ms=4, clip_on=False)
    ax.axhline(0, color='#666', lw=0.8, ls=':')
    ax.set_xlim(0, 40); ax.set_ylim(-22, 42)
    ax.set_xlabel('расстояние от переднего торца, км', fontsize=8.3)
    ax.set_ylabel('температура, °C', fontsize=8.3)
    ax.tick_params(labelsize=8)
    ax.grid(axis='y', alpha=.25, ls=':')

    lg.text(0.0, 1.0, 'Климатические зоны цилиндра', fontsize=9.5, weight='bold',
            va='top', transform=lg.transAxes)
    yy = 0.880
    for i, (n, a, b, t0, t1, hum) in enumerate(zones):
        lg.add_patch(Rectangle((0.005, yy - 0.080), 0.028, 0.085,
                               fc=ZONE_COLORS[i], ec='none',
                               transform=lg.transAxes, clip_on=False))
        lg.text(0.058, yy, f'{i + 1} — {n}, {a}–{b} км', fontsize=8.0, va='top',
                transform=lg.transAxes)
        lg.text(0.058, yy - 0.087, f'{t0:+d}\u2009…\u2009{t1:+d} °C · влажность {hum} · '
                f'свет {light[i]} Вт/м²',
                fontsize=7.3, va='top', color='#555', transform=lg.transAxes)
        lg.text(0.058, yy - 0.150, role[i], fontsize=7.0, va='top',
                color='#777', transform=lg.transAxes)
        yy -= 0.185
    yy -= 0.075
    lg.plot([0.008, 0.046], [yy + 0.038, yy + 0.038], 'o--', color='#2b2b2b',
            lw=1.1, ms=3.4, alpha=.55, transform=lg.transAxes, clip_on=False)
    lg.text(0.058, yy + 0.068, 'Средняя температура зоны', fontsize=8.0,
            va='top', transform=lg.transAxes)
    lg.text(0.058, yy - 0.010, 'На границах зон — теплоизолирующие перегородки\n'
            '(отмечены штрихом). Теплицы и гидропоника из холодной\n'
            'зоны выведены полностью: 14,8 км² переданы в тёплые\n'
            'зоны, экономия 4,15 ГВт на станцию (п. Б.12)',
            fontsize=7.1, va='top', color='#555', linespacing=1.4,
            transform=lg.transAxes)
    return save(fig, 'fig04_climate.png')


# ─────────────────────────────────────────────────────────────
# Рис. 5. Барометрический профиль во вращающейся системе
# ─────────────────────────────────────────────────────────────
def fig05():
    M, Rg, T = 0.02896, 8.314, 293.15
    r = np.linspace(0, R, 400)
    ratio = np.exp(-M * OMEGA ** 2 * (R ** 2 - r ** 2) / (2 * Rg * T))
    p = 101.325 * ratio
    fig, ax = plt.subplots(figsize=(6.4, 3.4))
    ax.plot(p, r / 1000, color=C_STEEL, lw=2.0)
    ax.fill_betweenx(r / 1000, 0, p, color=C_STEEL, alpha=.10)
    ax.set_xlabel('давление, кПа')
    ax.set_ylabel('расстояние от оси, км')
    ax.set_xlim(70, 105); ax.set_ylim(0, 5)
    ax.grid(alpha=.3, ls=':')
    for rr, txt, xt, yt in [(5000, '101,3 кПа — уровень\nжилой поверхности', 86.0, 4.35),
                            (0, '74,7 кПа на оси —\nкак 2 450 м над у. м.', 87.0, 0.60)]:
        pv = 101.325 * np.exp(-M * OMEGA ** 2 * (R ** 2 - rr ** 2) / (2 * Rg * T))
        ax.plot([pv], [rr / 1000], 'o', color=C_ACC, ms=6, zorder=5)
        ax.annotate(txt, xy=(pv, rr / 1000), xytext=(xt, yt), fontsize=7.8,
                    ha='center', va='center',
                    bbox=dict(fc='white', ec='#ccc', lw=0.6,
                              boxstyle='round,pad=0.28'),
                    arrowprops=dict(arrowstyle='->', lw=0.8, color='#888',
                                    connectionstyle='arc3,rad=0.15'))
    ax.axhspan(0, 0.1, color=C_WARN, alpha=.2)
    ax.text(103.5, 2.55, 'приосевая зона:\nработы только\nдистанционно\nуправляемыми\nмеханизмами',
            fontsize=7.0, color='#8a6a1a', ha='right', va='center')
    return save(fig, 'fig05_pressure.png')


# ─────────────────────────────────────────────────────────────
# Рис. 6. Применимость марок стали
# ─────────────────────────────────────────────────────────────
def fig06():
    marks = ['Ст3', '09Г2С', '30ХГСА', '18Ni(250)', '18Ni(300)', '18Ni(350)']
    lim = [400, 500, 1100, 1700, 2000, 2400]
    allow = [267, 333, 733, 1133, 1333, 1600]
    rest = [-118, -52, 348, 748, 948, 1215]
    x = np.arange(len(marks))
    fig, ax = plt.subplots(figsize=(6.8, 3.6))
    ax.bar(x - 0.21, lim, 0.42, color=C_LIGHT, ec=C_STEEL, lw=0.8, label='предел прочности')
    ax.bar(x + 0.21, allow, 0.42, color=C_STEEL, label='допускаемое σ при SF = 1,5')
    ax.axhline(385, color=C_ACC, lw=1.6, ls='--')
    ax.text(2.55, 250, 'порог 385 МПа — напряжение от собственного веса оболочки',
            fontsize=7.6, color=C_ACC, ha='center',
            bbox=dict(fc='white', ec='none', pad=1.6))
    for i, v in enumerate(rest):
        yy = allow[i] + 60 if v > 0 else lim[i] + 60
        ax.text(x[i], yy, f'{v:+d}'.replace('-', '−'), ha='center',
                fontsize=7.5, color=C_OK if v > 0 else C_ACC, weight='bold',
                bbox=dict(fc='white', ec='none', pad=1.0))
    ax.text(5.45, 2560, 'подписи над столбцами — остаток прочности на полезную нагрузку, МПа',
            fontsize=7.2, color='#555', ha='right')
    ax.set_xticks(x); ax.set_xticklabels(marks, fontsize=8.5)
    ax.set_ylabel('напряжение, МПа'); ax.set_ylim(0, 2700)
    ax.grid(axis='y', alpha=.3, ls=':')
    ax.legend(fontsize=8, frameon=False, loc='upper left', bbox_to_anchor=(0.0, 0.95))
    return save(fig, 'fig06_steel.png')


# ─────────────────────────────────────────────────────────────
# Рис. 7. Состав нагрузки и напряжений
# ─────────────────────────────────────────────────────────────
def fig07():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(8.0, 3.6),
                                 gridspec_kw={'width_ratios': [1.45, 1], 'wspace': 0.50})
    # состав по табл. 4.3 с учётом собственного веса пояса (п. Б.16)
    lbl = ['Атмосферное давление', 'Собственный вес пояса 0,85 м',
           'Грунт, 1,5 м', 'Радиационная защита, 1,0 м',
           'Застройка, инфраструктура', 'Вода: водоёмы, почва, оборотная']
    val = [101.3, 65.4, 28.0, 14.7, 4.9, 3.7]
    cols = ['#9fb8d0', C_STEEL, '#8a6a4a', '#7d6b58', '#b0b7bf', '#5b8fa8']
    Q = sum(val)
    y = np.arange(len(lbl))[::-1]
    a1.barh(y, val, 0.62, color=cols)
    for i2, v in enumerate(val):
        a1.text(v + 2.5, y[i2], f'{v} кПа · {v / Q * 100:.0f} %'.replace('.', ','),
                va='center', fontsize=7.6)
    a1.set_yticks(y); a1.set_yticklabels(lbl, fontsize=7.4)
    a1.set_xlabel('нагрузка на силовой пояс, кПа', fontsize=8.3)
    a1.set_xlim(0, 145)
    a1.grid(axis='x', alpha=.3, ls=':')
    a1.set_title(f'Состав расчётной нагрузки\nq = {Q:.1f} кПа'.replace('.', ','),
                 fontsize=9.5)

    sig_ext, sig_own = 923., 385.
    sig = sig_ext + sig_own
    a2.bar([0], [sig_ext], 0.42, color=C_STEEL,
           label=f'от внешней нагрузки — {sig_ext:.0f} МПа ({sig_ext/sig*100:.0f} %)')
    a2.bar([0], [sig_own], 0.42, bottom=[sig_ext], color=C_GREY,
           label=f'от собственного веса — {sig_own:.0f} МПа ({sig_own/sig*100:.0f} %)')
    a2.axhline(2000, color=C_ACC, lw=1.5, ls='--')
    a2.text(0.0, 2050, 'предел прочности 2 000 МПа', fontsize=7.6, color=C_ACC,
            ha='center')
    a2.axhline(1333, color='#c98a00', lw=1.2, ls=':')
    a2.text(-0.40, 1245, 'предел текучести 1 333 МПа', fontsize=7.0,
            color='#c98a00', ha='left', va='top',
            bbox=dict(fc='white', ec='none', pad=1.0))
    a2.annotate('', xy=(0.32, sig), xytext=(0.32, 2000),
                arrowprops=dict(arrowstyle='<->', color='#333', lw=0.9))
    a2.text(0.37, (sig + 2000) / 2, 'запас\n1,53', fontsize=7.8, va='center')
    a2.text(0, sig + 60, 'σ = 1 308 МПа', ha='center', fontsize=8.5,
            weight='bold', va='bottom',
            bbox=dict(fc='white', ec='none', pad=1.2))
    a2.set_xlim(-0.42, 0.62); a2.set_ylim(0, 2300)
    a2.set_xticks([]); a2.set_ylabel('кольцевое напряжение, МПа', fontsize=8.3)
    a2.grid(axis='y', alpha=.3, ls=':')
    a2.legend(fontsize=7.2, frameon=False, loc='upper center',
              bbox_to_anchor=(0.42, -0.04))
    a2.set_title('Напряжение в силовом поясе\nt = 0,85 м', fontsize=9.5)

    return save(fig, 'fig07_load.png')


# ─────────────────────────────────────────────────────────────
# Рис. 8. Массовый баланс
# ─────────────────────────────────────────────────────────────
def fig08():
    items = [('Конструкционный пакет с набором', 26.85, C_STEEL),
             ('Внутренний грунт', 8.13, '#8a6a4a'),
             ('Атмосфера', 7.55, '#6f8fae'),
             ('Ферменная рама и узлы', 3.00, C_GREY),
             ('Вода: водоёмы, почва, оборотная', 1.17, '#5b8fa8')]
    fig, ax = plt.subplots(figsize=(6.8, 2.9))
    left = 0
    for n, v, c in items:
        ax.barh([0], [v], left=left, color=c, ec='white', lw=1.0)
        lab = f'{v:.2f}'.replace('.', ',')
        if v >= 3.0:
            ax.text(left + v / 2, 0, lab, ha='center', va='center',
                    fontsize=8, color='white', weight='bold')
        else:
            ax.annotate(lab, xy=(left + v / 2, -0.30), xytext=(left + v / 2, -0.68),
                        ha='center', va='top', fontsize=7.6, color='#333',
                        bbox=dict(fc='white', ec='none', pad=1.0),
                        arrowprops=dict(arrowstyle='-', lw=0.7, color='#666'))
        left += v
    ax.set_xlim(0, 47.5); ax.set_ylim(-1.05, 0.95)
    ax.set_yticks([])
    ax.set_xlabel('масса, млрд т')
    ax.text(46.70, 0.48, 'ИТОГО 46,70 млрд т', ha='right', fontsize=9, weight='bold')
    ax.legend([Rectangle((0, 0), 1, 1, fc=c) for _, _, c in items],
              [f'{n} — {v:.2f} млрд т ({v / 46.70 * 100:.0f} %)'.replace('.', ',')
               for n, v, c in items],
              loc='upper center', bbox_to_anchor=(0.5, -0.30), ncol=2,
              frameon=False, fontsize=7.8)
    ax.grid(axis='x', alpha=.3, ls=':')
    return save(fig, 'fig08_mass.png')


# ─────────────────────────────────────────────────────────────
# Рис. 9. Тепловой баланс: площадь радиаторов
# ─────────────────────────────────────────────────────────────
def fig09():
    T = np.linspace(15, 90, 300)
    q = 0.95 * 5.67e-8 * ((T + 273.15) ** 4 - 4 ** 4)
    area = 677e9 / q / 1e6

    fig = plt.figure(figsize=(7.6, 3.6))
    ax = fig.add_axes([0.105, 0.145, 0.455, 0.815])
    lg = fig.add_axes([0.585, 0.105, 0.405, 0.855]); lg.axis('off')

    ax.plot(T, area, color=C_STEEL, lw=2.0, zorder=4)
    ax.axhline(1477, color=C_OK, lw=1.5, ls='--')
    ax.axhline(477, color=C_ACC, lw=1.2, ls=':')
    ax.axvline(60, color='#555', lw=0.8, ls='--')

    pts = [('1', 25, 1594, C_ACC), ('2', 60, 1022, C_STEEL), ('3', 80, 809, C_STEEL)]
    for m, t, a, c in pts:
        ax.plot([t], [a], 'o', color=c, ms=6, zorder=5)
        ax.text(t + 2.6, a + 95, m, fontsize=7.8, weight='bold', color='white',
                ha='center', va='center', zorder=6,
                bbox=dict(boxstyle='circle,pad=0.26', fc=c, ec='none'))
    ax.text(70, 1560, 'А', fontsize=7.8, weight='bold', color='white',
            ha='center', va='center',
            bbox=dict(boxstyle='circle,pad=0.26', fc=C_OK, ec='none'))
    ax.text(70, 560, 'Б', fontsize=7.8, weight='bold', color='white',
            ha='center', va='center',
            bbox=dict(boxstyle='circle,pad=0.26', fc=C_ACC, ec='none'))

    ax.set_xlabel('температура радиатора, °C', fontsize=8.5)
    ax.set_ylabel('площадь радиаторов, км²', fontsize=8.5)
    ax.set_xlim(15, 92); ax.set_ylim(0, 2100)
    ax.tick_params(labelsize=8)
    ax.grid(alpha=.3, ls=':')

    lg.text(0.0, 1.0, 'Сброс 677 ГВт: потребная площадь', fontsize=9.5,
            weight='bold', va='top', transform=lg.transAxes)
    lg.plot([0.01, 0.075], [0.885, 0.885], color=C_STEEL, lw=2.0,
            transform=lg.transAxes, clip_on=False)
    lg.text(0.105, 0.905, 'потребная площадь радиатора', fontsize=8.0,
            va='top', transform=lg.transAxes)
    lg.text(0.105, 0.825, 'растёт при снижении температуры\nсброса как обратная'
            ' четвёртая степень', fontsize=7.3, va='top', color='#555',
            transform=lg.transAxes)

    rows = [('1', C_ACC, '25 °C — 1 594 км²', 'больше располагаемой, режим не проходит'),
            ('2', C_STEEL, '60 °C — 1 022 км²', 'принятая температура, запас 1,45'),
            ('3', C_STEEL, '80 °C — 809 км²', 'запас больше, но растут потери в насосах'),
            ('А', C_OK, 'Располагаемая площадь 1 477 км²', 'редакция 3.0, таблица 4.3'),
            ('Б', C_ACC, 'Площадь редакции 2.0 — 477 км²', 'недостаточна, отвергнута')]
    yy = 0.700
    for m, c, title, note in rows:
        lg.text(0.030, yy - 0.028, m, fontsize=7.6, weight='bold', color='white',
                ha='center', va='center', transform=lg.transAxes,
                bbox=dict(boxstyle='circle,pad=0.26', fc=c, ec='none'))
        lg.text(0.105, yy, title, fontsize=8.0, va='top', transform=lg.transAxes)
        lg.text(0.105, yy - 0.077, note, fontsize=7.3, va='top', color='#555',
                transform=lg.transAxes)
        yy -= 0.163
    return save(fig, 'fig09_thermal.png')


# ─────────────────────────────────────────────────────────────
# Рис. 10. Энергобаланс станции
# ─────────────────────────────────────────────────────────────
def fig10():
    fig = plt.figure(figsize=(7.6, 5.4))

    ax = fig.add_axes([0.075, 0.610, 0.310, 0.335])
    lg = fig.add_axes([0.410, 0.590, 0.580, 0.355]); lg.axis('off')

    lbl = ['Осевые светотепловые балки', 'Тепловые насосы сброса тепла',
           'Удержание станции в точке L1', 'Резерв и потери передачи',
           'Жизнеобеспечение, насосы', 'Быт, транспорт, промышленность']
    val = [503, 96, 63, 33, 20, 6]
    cols = [C_WARN, '#5b8fa8', C_ACC, C_GREY, C_OK, '#9b6b9e']
    y = np.arange(len(lbl))[::-1]
    ax.barh(y, val, 0.66, color=cols)
    for i in range(len(lbl)):
        ax.text(-32, y[i], str(i + 1), va='center', ha='center', fontsize=7.4,
                weight='bold', color=C_STEEL)
    ax.set_yticks([]); ax.set_ylim(-0.7, len(lbl) - 0.3)
    ax.set_xlabel('электрическая мощность, ГВт', fontsize=8.3)
    ax.set_xlim(0, 560); ax.set_xticks([0, 200, 400])
    ax.tick_params(axis='x', labelsize=8)
    ax.grid(axis='x', alpha=.3, ls=':')
    for sp in ('top', 'right', 'left'):
        ax.spines[sp].set_visible(False)

    lg.text(0.0, 1.0, 'Потребление электроэнергии: всего 721 ГВт',
            fontsize=9.5, weight='bold', va='top', transform=lg.transAxes)
    yy = 0.855
    for i, (n, v, c) in enumerate(zip(lbl, val, cols)):
        lg.add_patch(Rectangle((0.005, yy - 0.085), 0.026, 0.090, fc=c, ec='none',
                               transform=lg.transAxes, clip_on=False))
        lg.text(0.052, yy, f'{i + 1} — {n}', fontsize=8.0, va='top',
                transform=lg.transAxes)
        pct = (f'{v / 721.4 * 100:.2f}' if v < 10 else f'{v / 721.4 * 100:.0f}')
        lg.text(0.660, yy, f'{v} ГВт · ' + pct.replace('.', ',') + ' %',
                fontsize=7.5, va='top', color='#555', transform=lg.transAxes)
        yy -= 0.143

    ax2 = fig.add_axes([0.075, 0.095, 0.310, 0.375])
    lg2 = fig.add_axes([0.410, 0.070, 0.580, 0.400]); lg2.axis('off')

    zname = ['Тропическая', 'Субтропическая', 'Умеренная', 'Холодная']
    zkm = ['0–10 км', '10–22 км', '22–32 км', '32–40 км']
    flux = [220, 170, 120, 60]
    powr = [69.1, 64.1, 37.7, 15.1]
    x = np.arange(4)
    ax2.bar(x, flux, 0.58, color=ZONE_COLORS)
    for i, f in enumerate(flux):
        ax2.text(i, f / 2, str(i + 1), ha='center', va='center', fontsize=8.4,
                 weight='bold', color='white' if i < 3 else '#1e3a4c')
    ax2.set_xticks(x)
    ax2.set_xticklabels(['1', '2', '3', '4'], fontsize=9, weight='bold')
    ax2.set_xlabel('климатическая зона', fontsize=8.3)
    ax2.set_ylabel('световой поток, Вт/м²', fontsize=8.3)
    ax2.set_ylim(0, 250); ax2.tick_params(axis='y', labelsize=8)
    ax2.grid(axis='y', alpha=.3, ls=':')

    lg2.text(0.0, 1.0, 'Световой режим по зонам: 186 ГВт на цилиндр',
             fontsize=9.5, weight='bold', va='top', transform=lg2.transAxes)
    yy = 0.845
    for i in range(4):
        lg2.add_patch(Rectangle((0.005, yy - 0.080), 0.026, 0.085,
                                fc=ZONE_COLORS[i], ec='none',
                                transform=lg2.transAxes, clip_on=False))
        lg2.text(0.052, yy, f'{i + 1} — {zname[i]}, {zkm[i]}', fontsize=8.0,
                 va='top', transform=lg2.transAxes)
        lg2.text(0.660, yy, f'{flux[i]} Вт/м² · {powr[i]} ГВт'.replace('.', ','),
                 fontsize=7.5, va='top', color='#555', transform=lg2.transAxes)
        yy -= 0.163
    lg2.text(0.052, yy + 0.010, 'Отсчёт ведётся от переднего торца цилиндра',
             fontsize=7.4, va='top', color=C_STEEL, weight='bold',
             transform=lg2.transAxes)
    return save(fig, 'fig10_energy.png')


# ─────────────────────────────────────────────────────────────
# Рис. 11. Скорости и стыковка
# ─────────────────────────────────────────────────────────────
def fig11():
    fig = plt.figure(figsize=(7.6, 3.6))
    ax = fig.add_axes([0.110, 0.150, 0.390, 0.800])
    lg = fig.add_axes([0.535, 0.100, 0.455, 0.850]); lg.axis('off')

    rr = np.array([5000, 2500, 1000, 100, 10])
    v = OMEGA * rr
    names = ['Жилая поверхность, r = 5 000 м', 'r = 2 500 м', 'r = 1 000 м',
             'r = 100 м', 'Причальное кольцо, r = 10 м']
    notes = ['стыковка невозможна', 'стыковка невозможна', 'стыковка невозможна',
             'технически возможна', 'скорость пешехода']
    cols = [C_ACC, C_ACC, C_ACC, C_WARN, C_OK]
    x = np.arange(5)
    ax.bar(x, v, 0.58, color=cols)
    ax.set_yscale('log')
    for i, val in enumerate(v):
        ax.text(i, val * 1.45, str(i + 1), ha='center', fontsize=8.4,
                weight='bold', color=C_STEEL)
    ax.set_xticks(x); ax.set_xticklabels([str(i + 1) for i in range(5)],
                                         fontsize=9, weight='bold')
    ax.set_xlabel('точка на радиусе', fontsize=8.3)
    ax.set_ylabel('линейная скорость, м/с', fontsize=8.3)
    ax.set_ylim(0.2, 1600)
    ax.tick_params(axis='y', labelsize=8)
    ax.grid(axis='y', alpha=.3, ls=':', which='both')

    lg.text(0.0, 1.0, 'Окружная скорость и возможность стыковки',
            fontsize=9.5, weight='bold', va='top', transform=lg.transAxes)
    yy = 0.855
    for i in range(5):
        lg.add_patch(Rectangle((0.005, yy - 0.078), 0.026, 0.082, fc=cols[i],
                               ec='none', transform=lg.transAxes, clip_on=False))
        lg.text(0.052, yy, f'{i + 1} — {names[i]}', fontsize=8.0, va='top',
                transform=lg.transAxes)
        lg.text(0.052, yy - 0.085, f'{v[i]:.2f}'.replace('.', ',') +
                f' м/с · {v[i] * 3.6:.0f} км/ч · {notes[i]}', fontsize=7.3,
                va='top', color='#555', transform=lg.transAxes)
        yy -= 0.172
    lg.text(0.052, yy + 0.030, 'Корабль причаливает к неподвижной раме, '
            'а не\nк вращающемуся корпусу: разность скоростей нулевая',
            fontsize=7.3, va='top', color=C_STEEL, weight='bold',
            transform=lg.transAxes)
    return save(fig, 'fig11_docking.png')


# ─────────────────────────────────────────────────────────────
# Рис. 12. Кориолис по способам перемещения
# ─────────────────────────────────────────────────────────────
def fig12():
    fig = plt.figure(figsize=(7.6, 4.0))
    ax = fig.add_axes([0.115, 0.150, 0.395, 0.800])
    lg = fig.add_axes([0.545, 0.075, 0.445, 0.880]); lg.axis('off')

    names = ['Прямая шахта, 5 мин', 'Прямая шахта, 10 мин',
             'Наклонная шахта, 17,8 мин', 'Фуникулёр, 30 мин',
             'Фуникулёр, 40 мин']
    notes = ['карданный подвес обязателен',
             'карданный подвес обязателен',
             'принятое решение: наклон постоянен',
             'спецустройства не требуются',
             'спецустройства не требуются']
    g = [0.301, 0.151, 0.015, 0.025, 0.019]
    cols = [C_ACC, C_ACC, C_STEEL, C_OK, C_OK]
    x = np.arange(5)
    ax.bar(x, g, 0.58, color=cols)
    ax.set_yscale('log')
    for i, v in enumerate(g):
        ax.text(i, v * 1.22, str(i + 1), ha='center', fontsize=8.2,
                weight='bold', color=C_STEEL)
    ax.axhline(0.05, color='#555', ls='--', lw=1.0)
    ax.set_xticks(x); ax.set_xticklabels([str(i + 1) for i in range(5)],
                                         fontsize=9, weight='bold')
    ax.set_xlabel('вариант перехода «ось — обод»', fontsize=8.3)
    ax.set_ylabel('ускорение Кориолиса, доли g', fontsize=8.3)
    ax.set_ylim(0.006, 0.95)
    ax.tick_params(axis='y', labelsize=8)
    ax.grid(axis='y', alpha=.3, ls=':', which='both')

    lg.text(0.0, 1.0, 'Боковое ускорение при переходе «ось — обод»',
            fontsize=9.5, weight='bold', va='top', transform=lg.transAxes)
    yy = 0.855
    for i in range(5):
        lg.add_patch(Rectangle((0.005, yy - 0.078), 0.026, 0.082, fc=cols[i],
                               ec='none', transform=lg.transAxes, clip_on=False))
        lg.text(0.052, yy, f'{i + 1} — {names[i]}', fontsize=8.0, va='top',
                transform=lg.transAxes)
        lg.text(0.052, yy - 0.083, f'{g[i]:.3f} g'.replace('.', ',') +
                f' · {notes[i]}', fontsize=7.3, va='top', color='#555',
                transform=lg.transAxes)
        yy -= 0.163
    yy -= 0.055
    lg.plot([0.008, 0.042], [yy + 0.045, yy + 0.045], color='#555', ls='--',
            lw=1.0, transform=lg.transAxes, clip_on=False)
    lg.text(0.052, yy + 0.075, 'Порог заметности 0,050 g', fontsize=8.0,
            va='top', transform=lg.transAxes)
    lg.text(0.052, yy - 0.005, 'Принятая наклонная шахта даёт 0,015 g — '
            'втрое\nниже порога и в десять раз меньше прямого лифта',
            fontsize=7.3, va='top', color=C_STEEL, transform=lg.transAxes)
    return save(fig, 'fig12_coriolis.png')


# ─────────────────────────────────────────────────────────────
# Рис. 13. Работа подъёма и отклонение вертикали
# ─────────────────────────────────────────────────────────────
def fig13():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.6, 3.4),
                                 gridspec_kw={'wspace': 0.62})
    seg = ['5→4', '4→3', '3→2', '2→1', '1→0']
    work = [8827, 6866, 4904, 2942, 981]
    share = [36.0, 28.0, 20.0, 12.0, 4.0]
    x = np.arange(5)
    a1.bar(x, work, 0.55, color=C_STEEL)
    for i, (w, s) in enumerate(zip(work, share)):
        a1.text(i, w + 260, f'{s:.0f} %', ha='center', fontsize=8, weight='bold')
    cum = np.cumsum(work)
    ab = a1.twinx()
    ab.plot(x, cum, 'o-', color=C_ACC, lw=1.6, ms=4.5)
    ab.set_ylabel('нарастающим итогом, Дж/кг', color=C_ACC, fontsize=8.5)
    ab.tick_params(axis='y', labelcolor=C_ACC, labelsize=8)
    ab.set_ylim(0, 27000)
    ab.text(4.15, 21500, '24 520 Дж/кг\n≈ 2 499 м при 1 g', fontsize=7.3,
            ha='right', va='top', color=C_ACC)
    a1.set_xticks(x); a1.set_xticklabels(seg, fontsize=8.5)
    a1.set_xlabel('участок пути, км от оси')
    a1.set_ylabel('работа, Дж/кг')
    a1.set_ylim(0, 10500)
    a1.grid(axis='y', alpha=.3, ls=':')
    a1.set_title('Работа подъёма по участкам', fontsize=9.5)
    a1.text(0.02, 0.97, 'энергия не зависит от способа подъёма',
            transform=a1.transAxes, fontsize=6.9, color='#666', va='top')

    r = np.linspace(5000, 100, 300)
    dev_straight = np.degrees(np.arctan2(2 * OMEGA * 16.7, OMEGA ** 2 * r))
    a2.plot(r / 1000, dev_straight, color=C_ACC, lw=2.0,
            label='прямая шахта, 16,7 м/с')
    a2.plot(r / 1000, np.full_like(r, 10.0), color=C_STEEL, lw=2.0,
            label='наклонная шахта, θ = const')
    a2.fill_between(r / 1000, 10.0, dev_straight, color=C_ACC, alpha=.10)
    a2.invert_xaxis()
    a2.set_xlabel('расстояние от оси, км')
    a2.set_ylabel('наклон кажущейся вертикали, град')
    a2.grid(alpha=.3, ls=':')
    a2.set_ylim(0, 90)
    a2.set_yticks([0, 15, 30, 45, 60, 75, 90])
    a2.annotate('82,4°', xy=(0.1, 82.4), xytext=(0.62, 78.0), fontsize=7.8,
                color=C_ACC, bbox=dict(fc='white', ec='none', pad=1.0))
    a2.annotate('8,6°', xy=(5.0, 8.6), xytext=(4.85, 17.5), fontsize=7.8,
                color=C_ACC, bbox=dict(fc='white', ec='none', pad=1.0))
    a2.text(2.6, 3.0, 'наклон постоянен — подвес не нужен', fontsize=7.2,
            color=C_STEEL, ha='center', bbox=dict(fc='white', ec='none', pad=1.2))
    a2.legend(fontsize=7.4, frameon=False, loc='upper left')
    a2.set_title('Наклон вертикали: прямая шахта и наклонная', fontsize=9.5)
    return save(fig, 'fig13_climb.png')


# ─────────────────────────────────────────────────────────────
# Рис. 14. Падение внутри цилиндра
# ─────────────────────────────────────────────────────────────
def fig14():
    fig = plt.figure(figsize=(7.6, 4.2))
    ax = fig.add_axes([0.015, 0.135, 0.320, 0.820])
    a2 = fig.add_axes([0.420, 0.195, 0.205, 0.755])
    lg = fig.add_axes([0.665, 0.055, 0.330, 0.900]); lg.axis('off')

    ax.add_patch(Circle((0, 0), 1, fc='#f4f7fa', ec=C_STEEL, lw=1.6))

    # точки срыва на своих радиусах: 2 500 м и 1 000 м от оси при R = 5 000 м
    for rad, mark in ((0.50, '1'), (0.20, '2')):
        T = np.linspace(0, 1.15, 300)
        xi = T * 0.9
        yi = np.full_like(T, rad)
        ang = -T * 0.95
        xr = xi * np.cos(ang) - yi * np.sin(ang)
        yr = xi * np.sin(ang) + yi * np.cos(ang)
        m = xr ** 2 + yr ** 2 <= 1.0
        ax.plot(xr[m], yr[m], color=C_ACC, lw=1.6, alpha=.9)
        ax.plot([0], [rad], 'o', color=C_ACC, ms=6, zorder=5)
        ax.text(-0.13, rad, mark, fontsize=7.6, weight='bold', color='white',
                ha='center', va='center', zorder=6,
                bbox=dict(boxstyle='circle,pad=0.24', fc=C_ACC, ec='none'))
        # место соударения
        xi_e, yi_e = xr[m][-1], yr[m][-1]
        ax.plot([xi_e], [yi_e], marker='X', color=C_ACC, ms=7, zorder=5)

    # приосевая зона, из которой тело поверхности не достигает
    ax.add_patch(Circle((0, 0), 0.02, fc=C_OK, ec='none'))
    ax.add_patch(Circle((0, 0), 0.14, fc='none', ec=C_OK, lw=1.2, ls=':'))
    ax.text(0.0, -0.25, '3', fontsize=7.6, weight='bold', color='white',
            ha='center', va='center', zorder=6,
            bbox=dict(boxstyle='circle,pad=0.24', fc=C_OK, ec='none'))

    # вращение поверхности: синяя стрелка, буква В прямо под ней
    arc = np.linspace(-1.30, -0.52, 60)
    ax.plot(1.055 * np.cos(arc), 1.055 * np.sin(arc), color=C_STEEL, lw=1.6)
    ax.annotate('', xy=(1.055 * np.cos(-0.52), 1.055 * np.sin(-0.52)),
                xytext=(1.055 * np.cos(-0.60), 1.055 * np.sin(-0.60)),
                arrowprops=dict(arrowstyle='-|>', color=C_STEEL, lw=1.6))
    ax.text(0.42, -1.14, 'В', fontsize=7.6, weight='bold', color='white',
            ha='center', va='center',
            bbox=dict(boxstyle='circle,pad=0.24', fc=C_STEEL, ec='none'))

    ax.set_xlim(-1.25, 1.35); ax.set_ylim(-1.25, 1.20)
    ax.set_aspect('equal'); ax.axis('off')

    vel = [192, 217, 0]
    x = np.arange(3)
    a2.bar(x, vel, 0.55, color=[C_ACC, C_ACC, C_OK])
    for i, v in enumerate(vel):
        if v:
            a2.text(i, v / 2, str(i + 1), ha='center', va='center', fontsize=8.4,
                    weight='bold', color='white')
        else:
            a2.text(i, 10, '3', ha='center', va='bottom', fontsize=8.4,
                    weight='bold', color=C_OK)
    a2.set_xticks(x); a2.set_xticklabels(['1', '2', '3'], fontsize=9, weight='bold')
    a2.set_xlabel('место срыва', fontsize=8.3)
    a2.set_ylabel('скорость соударения, м/с', fontsize=8.3)
    a2.set_ylim(0, 260); a2.tick_params(axis='y', labelsize=8)
    a2.grid(axis='y', alpha=.3, ls=':')

    lg.text(0.0, 1.0, 'Срыв с высоты в поле вращения', fontsize=9.5,
            weight='bold', va='top', transform=lg.transAxes)
    yy = 0.880
    rows = [('1', C_ACC, 'Срыв с r = 2 500 м',
             '192 м/с · 691 км/ч · падение 39 с'),
            ('2', C_ACC, 'Срыв с r = 1 000 м',
             '217 м/с · 781 км/ч · падение 111 с'),
            ('3', C_OK, 'Срыв при r < 100 м',
             'поверхности не достигает'),
            ('В', C_STEEL, 'Вращение поверхности',
             '221,5 м/с у обода')]
    for m_, c, t1, t2 in rows:
        lg.text(0.030, yy - 0.026, m_, fontsize=7.6, weight='bold', color='white',
                ha='center', va='center', transform=lg.transAxes,
                bbox=dict(boxstyle='circle,pad=0.26', fc=c, ec='none'))
        lg.text(0.105, yy, t1, fontsize=8.0, va='top', transform=lg.transAxes)
        lg.text(0.105, yy - 0.072, t2, fontsize=7.3, va='top', color='#555',
                transform=lg.transAxes)
        yy -= 0.148
    yy -= 0.058
    lg.plot([0.020, 0.044], [yy + 0.038, yy + 0.038], color=C_ACC, lw=1.6,
            transform=lg.transAxes, clip_on=False)
    lg.text(0.105, yy + 0.070, 'Траектория в системе цилиндра', fontsize=8.0,
            va='top', transform=lg.transAxes)
    lg.text(0.105, yy - 0.002, 'В инерциальной системе это прямая; знаком ×\n'
            'отмечено место соударения с поверхностью',
            fontsize=7.3, va='top', color='#555', transform=lg.transAxes)
    yy -= 0.135
    lg.text(0.010, yy, 'Удар возникает за счёт разности\n'
            'скоростей, а не радиального падения.\n'
            'Принятая наклонная шахта закрыта\n'
            'по всей длине — срыв в ней исключён.',
            fontsize=7.2, va='top', color=C_STEEL, weight='bold',
            linespacing=1.45, transform=lg.transAxes)
    return save(fig, 'fig14_fall.png')


# ─────────────────────────────────────────────────────────────
# Рис. 15. Схема транспортного узла ось — обод
# ─────────────────────────────────────────────────────────────
def fig15():
    """Маршрут «причал — жилая поверхность» в обход раскалённой ОСБ."""
    fig = plt.figure(figsize=(7.8, 5.0))
    ax = fig.add_axes([0.02, 0.05, 0.50, 0.92])
    lg = fig.add_axes([0.545, 0.02, 0.455, 0.96]); lg.axis('off')

    # Продольный разрез торцевой части. X — вдоль оси станции (0 — вершина
    # торца, вправо — вглубь цилиндра), Y — расстояние от оси.
    A, Rr = 4.5, 5.0            # полуоси торцевого купола, км

    th = np.linspace(0, np.pi / 2, 240)
    dome_x, dome_y = A * (1 - np.cos(th)), Rr * np.sin(th)   # выпуклость влево

    # внутренний объём с лёгким градиентом освещения от оси
    ax.fill_between(np.concatenate([dome_x, [9.5, 9.5]]),
                    np.concatenate([dome_y, [Rr, -Rr]]),
                    np.concatenate([-dome_y, [-Rr, -Rr]]),
                    color='#eef2f6', zorder=0)
    for k in range(14):
        f = k / 13.0
        ax.add_patch(Rectangle((0.55, -Rr + f * Rr), 8.95, 0.02 + Rr * 0.075,
                               fc='#fff8e6', alpha=0.055, ec='none', zorder=0))

    # ── толща конструкции торцевого купола: показана как пакет ──
    for dl, col in ((0.00, '#9aa7b5'), (0.10, C_STEEL), (0.26, '#7d6b58')):
        ax.plot(A * (1 - np.cos(th)) - dl * 0.9, (Rr + dl) * np.sin(th),
                color=col, lw=1.5, zorder=2)
        ax.plot(A * (1 - np.cos(th)) - dl * 0.9, -(Rr + dl) * np.sin(th),
                color=col, lw=1.5, zorder=2)
    for dl, col in ((0.00, '#9aa7b5'), (0.10, C_STEEL), (0.26, '#7d6b58')):
        ax.plot([A - dl * 0.9, 9.5], [Rr + dl, Rr + dl], color=col, lw=1.5, zorder=2)
        ax.plot([A - dl * 0.9, 9.5], [-Rr - dl, -Rr - dl], color=col, lw=1.5, zorder=2)

    # грунт жилой поверхности с неровным профилем рельефа
    xg = np.linspace(A, 9.5, 260)
    relief = 0.10 + 0.055 * np.sin(xg * 2.7) + 0.030 * np.sin(xg * 6.1 + 1.2)
    ax.fill_between(xg, Rr - relief, Rr, color='#6b5636', ec='none', zorder=3)
    ax.fill_between(xg, -Rr, -Rr + relief, color='#6b5636', ec='none', zorder=3)
    ax.fill_between(xg, Rr - relief - 0.045, Rr - relief,
                    color=ZONE_COLORS[0], ec='none', zorder=3)
    ax.fill_between(xg, -Rr + relief, -Rr + relief + 0.045,
                    color=ZONE_COLORS[0], ec='none', zorder=3)

    # ── ОСБ и распределение потока (спад обратно пропорционально r) ──
    x0 = 0.55
    for rad, al in ((2.50, .05), (1.55, .08), (1.00, .13), (0.50, .20),
                    (0.22, .30)):
        ax.add_patch(Rectangle((x0, -rad), 9.5 - x0, 2 * rad,
                               fc=C_ACC, alpha=al, ec='none', zorder=1))
    ax.add_patch(Rectangle((x0, -0.055), 9.5 - x0, 0.11,
                           fc='#ffd75e', ec='#c98a10', lw=0.7, zorder=2))
    # опорные фермы балки к торцу
    for yy in (0.9, -0.9):
        ax.plot([x0 + 0.15, x0 + 0.15], [0, yy], color='#c9a227', lw=0.6,
                alpha=.7, zorder=2)

    # гермопереборка торца
    ax.plot([x0, x0], [-2.55, 2.55], color=C_STEEL, lw=2.4, zorder=3)
    for yy in np.linspace(-2.45, 2.45, 16):
        ax.plot([x0 - 0.10, x0], [yy, yy], color=C_STEEL, lw=0.5, alpha=.6, zorder=3)

    # ── причал на неподвижной раме (слева, вне вращения) ──
    ax.add_patch(Rectangle((-2.75, -0.62), 1.45, 1.24, fc='#f7f9fb', ec=C_STEEL,
                           lw=1.2, zorder=4))
    for k in range(3):
        ax.add_patch(Rectangle((-2.62 + k * 0.42, -0.46), 0.26, 0.92,
                               fc='#dbe4ec', ec='#9aa7b5', lw=0.5, zorder=5))
    # ферма рамы
    ax.plot([-2.75, -1.30], [0.62, 0.62], color=C_GREY, lw=1.0, zorder=4)
    ax.plot([-2.75, -1.30], [-0.62, -0.62], color=C_GREY, lw=1.0, zorder=4)
    for k in range(4):
        xx1 = -2.75 + k * 0.3625
        ax.plot([xx1, xx1 + 0.3625], [0.62, -0.62], color=C_GREY, lw=0.45, zorder=4)
        ax.plot([xx1, xx1 + 0.3625], [-0.62, 0.62], color=C_GREY, lw=0.45, zorder=4)
    ax.plot([-1.30, -0.66], [0, 0], color=C_GREY, lw=1.8, zorder=4)
    # подшипниковый узел
    ax.add_patch(Circle((-0.52, 0), 0.20, fc='white', ec=C_ACC, lw=1.5, zorder=6))
    ax.add_patch(Circle((-0.52, 0), 0.085, fc=C_ACC, ec='none', zorder=7))

    # причаливший корабль
    ax.add_patch(Polygon([[-4.30, 0.30], [-3.55, 0.30], [-3.30, 0.13],
                          [-3.30, -0.13], [-3.55, -0.30], [-4.30, -0.30]],
                         fc='#cbd7e3', ec=C_STEEL, lw=0.9, zorder=4))
    ax.add_patch(Rectangle((-4.62, -0.16), 0.32, 0.32, fc='#9aa7b5',
                           ec=C_STEEL, lw=0.7, zorder=4))
    ax.plot([-3.30, -2.75], [0, 0], color=C_GREY, lw=1.2, zorder=4)

    # ── шахта в толще купола ──
    ths = np.linspace(0.030, np.pi / 2 - 0.004, 300)
    sx = A * (1 - np.cos(ths)) + 0.26
    sy = (Rr - 0.13) * np.sin(ths)
    for sgn in (1, -1):
        ax.plot(sx, sgn * sy, color='white', lw=4.4, solid_capstyle='round',
                zorder=7)
        ax.plot(sx, sgn * sy, color=C_OK, lw=2.8, solid_capstyle='round',
                zorder=8)
    # кабины на маршруте
    for f in (0.22, 0.52, 0.82):
        i = int(f * len(ths))
        dx, dy = sx[i] - sx[i - 6], sy[i] - sy[i - 6]
        angd = np.degrees(np.arctan2(dy, dx))
        ax.add_patch(Rectangle((sx[i] - 0.10, sy[i] - 0.055), 0.20, 0.11,
                               angle=angd, rotation_point='center',
                               fc='white', ec=C_OK, lw=1.0, zorder=9))
    ax.plot([-0.36, 0.26], [0, sy[0]], color=C_OK, lw=2.2, zorder=8)

    ax.set_xlim(-5.1, 10.2); ax.set_ylim(-7.6, 7.9)
    ax.set_aspect('equal'); ax.axis('off')

    # выноски — номерами, расшифровка в перечне обозначений справа
    marks = [
        ('1', (-3.60, 0.00), (-3.30, 2.05)),
        ('2', (-0.50, 0.00), (-1.55, 3.35)),
        ('3', (0.55, 1.55), (0.05, 4.60)),
        ('4', (sx[150], sy[150]), (3.05, 6.35)),
        ('5', (7.20, 0.10), (7.35, 2.30)),
        ('6', (8.40, 4.80), (9.35, 2.95)),
        ('7', (3.40, -1.15), (1.60, -4.15)),
    ]
    for num, xy, xyt in marks:
        ax.annotate(num, xy=xy, xytext=xyt, fontsize=8.2, weight='bold',
                    color='white', ha='center', va='center',
                    bbox=dict(boxstyle='circle,pad=0.28', fc=C_STEEL, ec='none'),
                    arrowprops=dict(arrowstyle='->', lw=0.9, color='#666',
                                    connectionstyle='arc3,rad=0.14'))

    rows = [
        (C_OK, 'Наклонная шахта в толще торцевого купола',
         ['17,8 мин · от причала r = 150 м до обода r = 5 000 м',
          'две шахты, обе в переднем торце; длина трассы 7 429 м',
          'наклон кажущейся вертикали постоянен — 10°,',
          'карданный подвес не требуется',
          'проходит внутри конструкции, минуя объём с ОСБ']),
        (C_ACC, 'Осевая светотепловая балка (ОСБ)',
         ['наружная труба Ø8 м, оболочка охлаждается до 25 °C',
          'сквозь неё идёт 186 ГВт: у самой трубы 185 кВт/м²,',
          'в 136 раз ярче солнца — опасна не жаром металла,',
          'а плотностью светового потока']),
        (C_GREY, 'Причал на неподвижной раме',
         ['стыковка при нулевой скорости, вне вращения',
          'подшипниковый узел передаёт людей на вращение']),
    ]
    y = 0.985
    for c, title, lines in rows:
        lg.add_patch(Rectangle((0.012, y - 0.042), 0.030, 0.030, fc=c, ec='none',
                               transform=lg.transAxes, clip_on=False))
        lg.text(0.066, y, title, fontsize=8.0, weight='bold', va='top',
                transform=lg.transAxes)
        yy = y - 0.062
        for ln in lines:
            lg.text(0.066, yy, ln, fontsize=7.1, va='top', color='#333',
                    transform=lg.transAxes)
            yy -= 0.049
        y = yy - 0.040

    lg.text(0.012, y, 'Обозначения на разрезе', fontsize=8.0, weight='bold',
            va='top', transform=lg.transAxes)
    y -= 0.058
    legend_items = [
        '1 — корабль причаливает к неподвижной раме',
        '2 — подшипниковый узел: переход на вращение',
        '3 — гермопереборка отделяет причал от объёма с ОСБ',
        '4 — шахта проложена в толще торцевого купола',
        '5 — осевая светотепловая балка',
        '6 — жилая поверхность, 1,000 g',
        '7 — приосевая зона r < 2 500 м, закрыта для людей',
    ]
    for it in legend_items:
        lg.text(0.030, y, it, fontsize=7.1, va='top', color='#333',
                transform=lg.transAxes)
        y -= 0.047
    y -= 0.010
    lg.text(0.066, y + 0.012,
            'Приосевой объём радиусом до 2 500 м закрыт для людей:\n'
            'поток от ОСБ там превышает 300 Вт/м², а ближе 500 м —\n'
            '1 500 Вт/м². Обслуживание балки ведут дистанционно\n'
            'управляемые механизмы. Свободный полёт у оси отменён.',
            fontsize=7.0, va='top', color=C_ACC, transform=lg.transAxes,
            linespacing=1.55)
    return save(fig, 'fig15_transport.png')


# ─────────────────────────────────────────────────────────────
# Рис. 16. Ресурсная обеспеченность
# ─────────────────────────────────────────────────────────────
def fig16():
    fig = plt.figure(figsize=(7.6, 3.5))
    ax = fig.add_axes([0.075, 0.155, 0.360, 0.795])
    lg = fig.add_axes([0.470, 0.100, 0.520, 0.850]); lg.axis('off')

    names = ['Сталь 18Ni(300), силовой пояс', 'Грунт растительный',
             'Летучие (N₂, O₂)', 'Реголит, боросиликат', 'Вода',
             'Сталь нержавеющая, гермооболочка']
    notes = ['определяющий ресурс: 94 % металла астероида (6178) 1986 DA',
             'переработка реголита, обеспечено',
             'требует отдельной программы добычи',
             'дроблёный реголит, обеспечено',
             'требует отдельной программы добычи',
             'обеспечено']
    need = [20.83, 8.13, 7.55, 4.65, 1.17, 1.22]
    stat = ['опр', 'ок', 'прог', 'ок', 'прог', 'ок']
    cmap = {'опр': C_ACC, 'ок': C_OK, 'прог': C_WARN}
    cols = [cmap[t] for t in stat]
    y = np.arange(len(names))[::-1]
    ax.barh(y, need, 0.66, color=cols)
    for i in range(len(names)):
        ax.text(-1.15, y[i], str(i + 1), va='center', ha='center', fontsize=7.6,
                weight='bold', color=C_STEEL)
    ax.set_yticks([]); ax.set_ylim(-0.7, len(names) - 0.3)
    ax.set_xlabel('потребность, млрд т', fontsize=8.3)
    ax.set_xlim(0, 23); ax.set_xticks([0, 5, 10, 15, 20])
    ax.tick_params(axis='x', labelsize=8)
    ax.grid(axis='x', alpha=.3, ls=':')
    for sp in ('top', 'right', 'left'):
        ax.spines[sp].set_visible(False)

    lg.text(0.0, 1.0, 'Потребность в материалах, всего 43,55 млрд т',
            fontsize=9.5, weight='bold', va='top', transform=lg.transAxes)
    yy = 0.865
    for i in range(len(names)):
        lg.add_patch(Rectangle((0.004, yy - 0.070), 0.022, 0.074, fc=cols[i],
                               ec='none', transform=lg.transAxes, clip_on=False))
        lg.text(0.044, yy, f'{i + 1} — {names[i]}', fontsize=7.9, va='top',
                transform=lg.transAxes)
        lg.text(0.044, yy - 0.078, f'{need[i]:.2f}'.replace('.', ',') +
                f' млрд т · {notes[i]}', fontsize=7.1, va='top', color='#555',
                transform=lg.transAxes)
        yy -= 0.150
    return save(fig, 'fig16_resources.png')


# ─────────────────────────────────────────────────────────────
# Рис. 17. Продовольственный баланс
# ─────────────────────────────────────────────────────────────
def fig17():
    fig = plt.figure(figsize=(7.6, 6.2))

    # ── верх: энергетический баланс, подписи вынесены в легенду ──
    ax = fig.add_axes([0.105, 0.640, 0.290, 0.300])
    lg = fig.add_axes([0.415, 0.615, 0.575, 0.325]); lg.axis('off')

    marks = ['А', 'Б', 'В']
    names = ['Потребность 1 млн человек',
             'С резервом ×1,5',
             'Производство (нетто)']
    notes = ['2 800 ккал в сутки на человека',
             'страховой коэффициент',
             'запас над потребностью ×1,83']
    kcal = [1.022, 1.533, 1.870]
    cols = [C_GREY, C_WARN, C_OK]

    ax.bar(range(3), kcal, 0.52, color=cols)
    for i, v in enumerate(kcal):
        ax.text(i, v / 2, marks[i], ha='center', va='center', fontsize=10,
                weight='bold', color='white')
    ax.set_xticks(range(3)); ax.set_xticklabels(marks, fontsize=9.5, weight='bold')
    ax.set_xlim(-0.62, 2.72)
    ax.set_ylabel('энергия, трлн ккал/год', fontsize=8.2, labelpad=2)
    ax.set_ylim(0, 2.15)
    ax.set_yticks([0, 0.5, 1.0, 1.5, 2.0])
    ax.set_yticklabels(['0', '0,5', '1,0', '1,5', '2,0'], fontsize=8)
    ax.grid(axis='y', alpha=.3, ls=':')

    lg.text(0.0, 1.0, 'Энергетический баланс питания', fontsize=9.5,
            weight='bold', va='top', transform=lg.transAxes)
    yy = 0.80
    for m, n, nt, v, c in zip(marks, names, notes, kcal, cols):
        lg.add_patch(Rectangle((0.005, yy - 0.075), 0.030, 0.105, fc=c, ec='none',
                               transform=lg.transAxes, clip_on=False))
        lg.text(0.058, yy, f'{m} — {n}', fontsize=8.2, va='top',
                transform=lg.transAxes)
        lg.text(0.058, yy - 0.115, f'{v:.3f}'.replace('.', ',') +
                f' трлн ккал/год · {nt}', fontsize=7.4, va='top', color='#555',
                transform=lg.transAxes)
        yy -= 0.285

    # ── низ: вклад культур, легенда с номерами ──
    ax2 = fig.add_axes([0.105, 0.080, 0.290, 0.450])
    lg2 = fig.add_axes([0.415, 0.055, 0.575, 0.495]); lg2.axis('off')

    # состав и числа — таблица 5.5, все 14 позиций
    crops = ['Кукуруза', 'Рис', 'Картофель', 'Пшеница', 'Масличные',
             'Батат, таро, маниок, ямс', 'Овощи', 'Грибы', 'Ячмень',
             'Фрукты и ягоды', 'Прочие бобовые', 'Водоросли',
             'Соя', 'Зелень и пряности']
    area = [150, 120, 100, 50, 50, 46, 80, 30, 20, 60, 36, 30, 10, 25]
    kc = [657, 432, 308, 170, 150, 124, 80, 75, 70, 60, 38, 21, 16, 15]
    n = len(crops)
    y = np.arange(n)[::-1]
    shades = [plt.cm.Greens(0.80 - 0.042 * i) for i in range(n)]

    ax2.barh(y, kc, 0.72, color=shades)
    for i in range(n):
        ax2.text(-30, y[i], str(i + 1), va='center', ha='center', fontsize=7.0,
                 weight='bold', color=C_STEEL)
    ax2.set_yticks([]); ax2.set_ylim(-0.7, n - 0.3)
    ax2.set_xlabel('энергетический выход, млрд ккал/год', fontsize=8.5)
    ax2.set_xlim(0, 700)
    ax2.set_xticks([0, 200, 400, 600])
    ax2.tick_params(axis='x', labelsize=8)
    ax2.grid(axis='x', alpha=.3, ls=':')
    for sp in ('top', 'right', 'left'):
        ax2.spines[sp].set_visible(False)

    lg2.text(0.0, 1.0, 'Вклад культур: энергия и посевная площадь',
             fontsize=9.5, weight='bold', va='top', transform=lg2.transAxes)
    yy = 0.900
    for i in range(n):
        lg2.add_patch(Rectangle((0.005, yy - 0.040), 0.026, 0.042, fc=shades[i],
                                ec='none', transform=lg2.transAxes, clip_on=False))
        lg2.text(0.050, yy, f'{i + 1} — {crops[i]}', fontsize=7.5, va='top',
                 transform=lg2.transAxes)
        lg2.text(0.575, yy, f'{kc[i]} млрд ккал · {area[i]} км²', fontsize=7.1,
                 va='top', color='#555', transform=lg2.transAxes)
        yy -= 0.0625
    lg2.text(0.050, yy - 0.012, 'Итого 2 216 млрд ккал на 807 км² посевов '
             '(таблица 5.5)', fontsize=7.4, va='top', weight='bold',
             color=C_STEEL, transform=lg2.transAxes)

    return save(fig, 'fig17_food.png')


# ─────────────────────────────────────────────────────────────
# Рис. 18. Землепользование
# ─────────────────────────────────────────────────────────────
def fig18():
    """Землепользование: баланс площадей двух цилиндров."""
    fig = plt.figure(figsize=(7.6, 3.4))
    ax = fig.add_axes([0.075, 0.150, 0.360, 0.800])
    lg = fig.add_axes([0.470, 0.070, 0.520, 0.880]); lg.axis('off')

    lbl = ['Посевные площади', 'Свободный резерв',
           'Резерв аварийных культур', 'Рыбные бассейны']
    notes = ['14 культур, таблица 5.5; нетто 1,870 трлн ккал',
             'в том числе 29,6 км² приняли культуры из арктики',
             'вводится при потере урожая, не засевается',
             'насыпной способ, глубина до 3 м, п. Б.11']
    val = [807, 536, 150, 15]
    cols = [C_OK, C_LIGHT, C_WARN, '#5b8fa8']
    y = np.arange(len(val))[::-1]
    ax.barh(y, val, 0.62, color=cols, ec='#999', lw=0.5)
    for i2 in range(len(val)):
        ax.text(-42, y[i2], str(i2 + 1), va='center', ha='center', fontsize=7.6,
                weight='bold', color=C_STEEL)
    ax.set_yticks([]); ax.set_ylim(-0.7, len(val) - 0.3)
    ax.set_xlim(0, 900)
    ax.set_xlabel('площадь, км²', fontsize=8.3)
    ax.tick_params(axis='x', labelsize=8)
    ax.grid(axis='x', alpha=.3, ls=':')
    for sp in ('top', 'right', 'left'):
        ax.spines[sp].set_visible(False)

    lg.text(0.0, 1.0, 'Землепользование двух цилиндров, сельхозугодья 1 508 км²',
            fontsize=9.5, weight='bold', va='top', transform=lg.transAxes)
    yy = 0.845
    for i2 in range(len(val)):
        lg.add_patch(Rectangle((0.006, yy - 0.070), 0.024, 0.074, fc=cols[i2],
                               ec='#999', lw=0.4,
                               transform=lg.transAxes, clip_on=False))
        lg.text(0.052, yy, f'{i2 + 1} — {lbl[i2]}', fontsize=8.0, va='top',
                transform=lg.transAxes)
        lg.text(0.052, yy - 0.080,
                f'{val[i2]} км² · {val[i2] / 1508 * 100:.0f} %'.replace('.', ',')
                + f' · {notes[i2]}', fontsize=7.0, va='top', color='#555',
                transform=lg.transAxes)
        yy -= 0.165
    lg.text(0.0, yy - 0.010, 'Сельхозугодья составляют 49 % полной площади '
            '3 100,2 км²;\nостальное — застройка, дороги, водоёмы 150 км² '
            'глубиной 1,2 м\nи склоны. Теплиц в холодной зоне нет (п. Б.12)',
            fontsize=7.2, va='top', color=C_STEEL, linespacing=1.45,
            transform=lg.transAxes)
    return save(fig, 'fig18_land.png')



# ─────────────────────────────────────────────────────────────
# Рис. 19. Эпидемическая устойчивость и секционирование
# ─────────────────────────────────────────────────────────────
def fig19():
    fig = plt.figure(figsize=(7.6, 3.7))
    ax = fig.add_axes([0.088, 0.150, 0.360, 0.800])
    lg = fig.add_axes([0.490, 0.075, 0.505, 0.875]); lg.axis('off')

    R0 = np.linspace(1.02, 14, 400)
    z = np.full_like(R0, 0.5)
    for _ in range(400):
        z = 1 - np.exp(-R0 * z)
    ax.plot(R0, z * 100, color=C_ACC, lw=2.0, zorder=4)
    ax.plot(R0, (1 - 1 / R0) * 100, color=C_OK, lw=2.0, ls='--', zorder=4)

    pts = [('1', 1.5), ('2', 2.5), ('3', 5.0), ('4', 12.0)]
    for m, r0 in pts:
        zz = 0.5
        for _ in range(400):
            zz = 1 - np.exp(-r0 * zz)
        ax.plot([r0], [zz * 100], 'o', color=C_ACC, ms=5.5, zorder=6)
        dx, dy = (0.85, -9) if r0 >= 4 else (-0.75, 8)
        ax.text(r0 + dx, zz * 100 + dy, m, fontsize=7.4, weight='bold',
                color='white', ha='center', va='center', zorder=7,
                bbox=dict(boxstyle='circle,pad=0.24', fc=C_STEEL, ec='none'))

    ax.set_xlabel('базовое репродуктивное число $R_0$', fontsize=8.3)
    ax.set_ylabel('доля населения, %', fontsize=8.3)
    ax.set_xlim(1, 14.5); ax.set_ylim(0, 104)
    ax.tick_params(labelsize=8)
    ax.grid(alpha=.3, ls=':')

    lg.text(0.0, 1.0, 'Эпидемия в замкнутой популяции 1 000 000 человек',
            fontsize=9.3, weight='bold', va='top', transform=lg.transAxes)
    lg.plot([0.010, 0.052], [0.906, 0.906], color=C_ACC, lw=2.0,
            transform=lg.transAxes, clip_on=False)
    lg.text(0.078, 0.930, 'Переболеет без противодействия', fontsize=8.0,
            va='top', transform=lg.transAxes)
    lg.plot([0.010, 0.052], [0.836, 0.836], color=C_OK, lw=2.0, ls='--',
            transform=lg.transAxes, clip_on=False)
    lg.text(0.078, 0.860, 'Порог коллективного иммунитета', fontsize=8.0,
            va='top', transform=lg.transAxes)

    rows = [('1', '$R_0$ = 1,5 — сезонный грипп', '58 % · 291 тыс. чел.'),
            ('2', '$R_0$ = 2,5 — грипп 1918 года', '89 % · 446 тыс. чел.'),
            ('3', '$R_0$ = 5,0 — оспа, краснуха', '99 % · 497 тыс. чел.'),
            ('4', '$R_0$ = 12 — корь', '100 % · 1 млн чел.')]
    yy = 0.755
    for m, t1, t2 in rows:
        lg.text(0.028, yy - 0.026, m, fontsize=7.4, weight='bold', color='white',
                ha='center', va='center', transform=lg.transAxes,
                bbox=dict(boxstyle='circle,pad=0.24', fc=C_STEEL, ec='none'))
        lg.text(0.078, yy, t1, fontsize=8.0, va='top', transform=lg.transAxes)
        lg.text(0.640, yy, t2, fontsize=7.4, va='top', color='#555',
                transform=lg.transAxes)
        yy -= 0.098
    yy -= 0.030

    lg.text(0.0, yy, 'Секционирование как мера', fontsize=8.6, weight='bold',
            va='top', transform=lg.transAxes)
    yy -= 0.072
    for k, note in ((1, 'вспышка охватывает всю станцию'), (4, 'по климатическим зонам'),
                    (10, 'по округам'), (40, 'по кварталам')):
        lg.add_patch(Rectangle((0.012, yy - 0.048), 0.024, 0.052,
                               fc=C_OK if k >= 10 else C_WARN, ec='none',
                               transform=lg.transAxes, clip_on=False))
        lg.text(0.078, yy, ('единый объём — 1 млн человек в очаге' if k == 1
                else f'{k} секций — не более {1000000 // k // 1000} тыс. человек в очаге'),
                fontsize=7.8, va='top', transform=lg.transAxes)
        lg.text(0.078, yy - 0.062, note, fontsize=7.2, va='top', color='#666',
                transform=lg.transAxes)
        yy -= 0.118
    return save(fig, 'fig19_epidemic.png')


# ─────────────────────────────────────────────────────────────
# Рис. 20. Собственные частоты станции и порог слуха
# ─────────────────────────────────────────────────────────────
def fig20():
    fig = plt.figure(figsize=(7.6, 3.4))
    ax = fig.add_axes([0.088, 0.190, 0.380, 0.740])
    lg = fig.add_axes([0.510, 0.085, 0.485, 0.855]); lg.axis('off')

    modes = [('1', 0.00429, C_STEEL), ('2', 0.00857, C_STEEL),
             ('3', 0.01286, C_STEEL), ('4', 0.0171, '#5b8fa8'),
             ('5', 0.1607, C_WARN)]
    # частоты 1-4 лежат очень близко: метки разводятся по высоте выносками
    tops = [1.00, 0.80, 0.60, 0.40, 1.00]
    labx = [0.0016, 0.0042, 0.0115, 0.045, 0.1607]
    for i, (m, f, c) in enumerate(modes):
        ax.plot([f, f], [0, tops[i]], color=c, lw=2.4)
        ax.annotate(m, xy=(f, tops[i]), xytext=(labx[i], tops[i] + 0.16),
                    fontsize=7.4, weight='bold', color='white',
                    ha='center', va='center',
                    bbox=dict(boxstyle='circle,pad=0.24', fc=c, ec='none'),
                    arrowprops=dict(arrowstyle='-', lw=0.7, color='#999'))

    ax.axvspan(20, 20000, color=C_OK, alpha=.16)
    ax.axvline(20, color=C_OK, lw=1.4, ls='--')
    ax.set_xscale('log')
    ax.set_xlim(1e-3, 3e4); ax.set_ylim(0, 1.32)
    ax.set_yticks([])
    ax.set_xlabel('частота, Гц (логарифмическая шкала)', fontsize=8.3)
    ax.tick_params(axis='x', labelsize=8)
    ax.grid(axis='x', alpha=.3, ls=':', which='both')
    for sp in ('top', 'right', 'left'):
        ax.spines[sp].set_visible(False)

    lg.text(0.0, 1.0, 'Собственные частоты станции', fontsize=9.3,
            weight='bold', va='top', transform=lg.transAxes)
    rows = [('1', C_STEEL, 'Продольная мода объёма, 1-я',
             '0,0043 Гц · период 233 с'),
            ('2', C_STEEL, 'Продольная мода, 2-я', '0,0086 Гц · период 117 с'),
            ('3', C_STEEL, 'Продольная мода, 3-я', '0,0129 Гц · период 78 с'),
            ('4', '#5b8fa8', 'Поперечная мода объёма', '0,0171 Гц · период 58 с'),
            ('5', C_WARN, 'Кольцевая мода стальной оболочки',
             '0,161 Гц · период 6,2 с')]
    yy = 0.855
    for m, c, t1, t2 in rows:
        lg.text(0.028, yy - 0.026, m, fontsize=7.4, weight='bold', color='white',
                ha='center', va='center', transform=lg.transAxes,
                bbox=dict(boxstyle='circle,pad=0.24', fc=c, ec='none'))
        lg.text(0.078, yy, t1, fontsize=8.0, va='top', transform=lg.transAxes)
        lg.text(0.078, yy - 0.070, t2, fontsize=7.3, va='top', color='#555',
                transform=lg.transAxes)
        yy -= 0.148
    lg.add_patch(Rectangle((0.012, yy - 0.030), 0.024, 0.048, fc=C_OK,
                           alpha=.35, ec=C_OK, lw=1.0,
                           transform=lg.transAxes, clip_on=False))
    lg.text(0.078, yy + 0.020, 'Полоса слышимого звука, 20 Гц — 20 кГц',
            fontsize=8.0, va='top', transform=lg.transAxes)
    lg.text(0.078, yy - 0.050, 'Все собственные частоты станции лежат в области\n'
            'инфразвука: ухом они не слышны, но способны\n'
            'раскачивать конструкции и вызывать недомогание',
            fontsize=7.3, va='top', color=C_STEEL, weight='bold',
            linespacing=1.45, transform=lg.transAxes)
    return save(fig, 'fig20_acoustics.png')



# ─────────────────────────────────────────────────────────────
# Рис. 21. Программа добычи летучих: источники и объёмы сырья
# ─────────────────────────────────────────────────────────────
def fig21():
    fig = plt.figure(figsize=(7.6, 4.0))
    ax = fig.add_axes([0.085, 0.155, 0.345, 0.760])
    lg = fig.add_axes([0.470, 0.055, 0.525, 0.895]); lg.axis('off')

    names = ['Кислород\nиз реголита', 'Вода\nиз C-хондритов',
             'Азот\nиз C-хондритов', 'Азот\nиз кометных льдов']
    raw = [3.94, 5.85, 3674.0, 551.0]
    cols = [C_OK, C_WARN, C_ACC, C_WARN]
    x = np.arange(4)
    ax.bar(x, raw, 0.58, color=cols)
    ax.set_yscale('log')
    for i, v in enumerate(raw):
        ax.text(i, v * 1.45, str(i + 1), ha='center', fontsize=8.4,
                weight='bold', color=C_STEEL)
    ax.axhline(46.70, color=C_STEEL, lw=1.3, ls='--')
    ax.text(-0.42, 59, 'масса всей станции 46,70', fontsize=6.8, color=C_STEEL,
            ha='left', va='bottom')

    ax.set_xticks(x); ax.set_xticklabels([str(i + 1) for i in range(4)],
                                         fontsize=9, weight='bold')
    ax.set_xlabel('вариант источника', fontsize=8.3)
    ax.set_ylabel('потребное сырьё, млрд т', fontsize=8.3)
    ax.set_ylim(1, 2e4)
    ax.tick_params(axis='y', labelsize=8)
    ax.grid(axis='y', alpha=.3, ls=':', which='both')

    lg.text(0.0, 1.0, 'Программа добычи летучих: сколько сырья надо переработать',
            fontsize=9.0, weight='bold', va='top', transform=lg.transAxes)
    rows = [('1', C_OK, 'Кислород 1,69 млрд т — из реголита',
             '3,94 млрд т сырья · получается попутно при\n'
             'добыче радзащиты и грунта, отдельной программы нет'),
            ('2', C_WARN, 'Вода 1,17 млрд т — из хондритов CI',
             '5,85 млрд т сырья · достижимо, один объект\n'
             'класса Цереры или несколько малых'),
            ('3', C_ACC, 'Азот 5,51 млрд т — из хондритов',
             '3 674 млрд т сырья · в 79 раз больше массы\n'
             'станции. Путь непроходим'),
            ('4', C_WARN, 'Азот 5,51 млрд т — из кометных льдов',
             '551 млрд т сырья · ядро Ø 1,2 км или 55 комет\n'
             'типа 67P. Тяжело, но мыслимо')]
    yy = 0.865
    for m, c, t1, t2 in rows:
        lg.add_patch(Rectangle((0.008, yy - 0.060), 0.024, 0.064, fc=c, ec='none',
                               transform=lg.transAxes, clip_on=False))
        lg.text(0.062, yy, f'{m} — ' + t1[t1.index(' ') + 1:] if False else
                f'{m} — {t1}', fontsize=7.9, va='top', transform=lg.transAxes)
        lg.text(0.062, yy - 0.072, t2, fontsize=7.2, va='top', color='#555',
                linespacing=1.45, transform=lg.transAxes)
        yy -= 0.196
    lg.text(0.0, yy + 0.030, 'Решение: снизить потребность, а не только добывать',
            fontsize=8.4, weight='bold', va='top', transform=lg.transAxes)
    lg.text(0.062, yy - 0.040, 'Давление 70 кПа при доле кислорода 30 % даёт\n'
            'массу атмосферы 5,26 млрд т вместо 7,55 (−30 %)\n'
            'и азота 3,53 вместо 5,51 млрд т (−36 %)',
            fontsize=7.2, va='top', color=C_STEEL, linespacing=1.45,
            transform=lg.transAxes)
    return save(fig, 'fig21_volatiles.png')



# ─────────────────────────────────────────────────────────────
# Рис. 22. Орбиты ресурсных тел в плоскости эклиптики
# ─────────────────────────────────────────────────────────────
def fig22():
    """Орбиты строятся по реальным элементам (эпоха 2023-2025, JPL SBDB)."""
    fig = plt.figure(figsize=(7.8, 4.9))
    ax = fig.add_axes([0.015, 0.035, 0.505, 0.930])
    lg = fig.add_axes([0.540, 0.025, 0.455, 0.945]); lg.axis('off')

    def orbit(a, e, om_deg, n=600):
        """Проекция орбиты на плоскость эклиптики: r(θ) с поворотом на ω."""
        nu = np.linspace(0, 2 * np.pi, n)
        r = a * (1 - e ** 2) / (1 + e * np.cos(nu))
        th = nu + np.radians(om_deg)
        return r * np.cos(th), r * np.sin(th)

    # планеты — фон
    planets = [('Земля', 1.000, 0.0167, 102.9, '#4a7fb5'),
               ('Марс', 1.524, 0.0934, 286.5, '#a8563a'),
               ('Юпитер', 5.204, 0.0489, 273.9, '#8a7a5a')]
    for name, a, e, om, c in planets:
        x, y = orbit(a, e, om)
        ax.plot(x, y, color=c, lw=1.0, ls='--', alpha=.75, zorder=2)

    # пояс астероидов
    ring = Wedge((0, 0), 3.3, 0, 360, width=1.1, fc='#d8dee5',
                 ec='none', alpha=.40, zorder=0)
    ax.add_patch(ring)

    # ресурсные тела
    targets = [('1', '(6178) 1986 DA', 2.8216, 0.5818, 127.36, C_ACC),
               ('2', '(1) Ceres', 2.7660, 0.0785, 73.6, C_OK),
               ('3', '(24) Themis', 3.1490, 0.1165, 108.06, '#5b8fa8'),
               ('4', '(10) Hygiea', 3.1415, 0.1125, 312.32, '#9b6b9e'),
               ('5', '67P/Чурюмова — Герасименко', 3.4620, 0.6410, 12.8, C_WARN)]
    for m, name, a, e, om, c in targets:
        x, y = orbit(a, e, om)
        ax.plot(x, y, color=c, lw=1.9, zorder=4)
        # тело в перигелии
        xp, yp = orbit(a, e, om, 2)[0][0], orbit(a, e, om, 2)[1][0]
        ax.plot([xp], [yp], 'o', color=c, ms=6, zorder=6)
        ax.text(xp * 1.16, yp * 1.16, m, fontsize=7.4, weight='bold',
                color='white', ha='center', va='center', zorder=7,
                bbox=dict(boxstyle='circle,pad=0.24', fc=c, ec='none'))

    # Солнце и станция
    ax.plot([0], [0], 'o', color='#f0b429', ms=11, zorder=8)
    ax.add_patch(Circle((0, 0), 0.30, fc='#f0b429', alpha=.18, ec='none', zorder=1))
    ax.text(0, -0.42, 'Солнце', fontsize=7.2, ha='center', color='#8a6a1a')
    # станция в точке L1 системы Солнце - Земля
    ax.plot([0.99], [0], 's', color=C_STEEL, ms=6, zorder=8)
    ax.annotate('станция, точка L1', xy=(0.99, 0), xytext=(3.05, -1.05),
                fontsize=7.2, color=C_STEEL, ha='left', va='center',
                bbox=dict(fc='white', ec='none', pad=1.2),
                arrowprops=dict(arrowstyle='->', lw=0.8, color=C_STEEL,
                                connectionstyle='arc3,rad=-0.18'))

    for rr in (1, 2, 3, 4, 5):
        ax.add_patch(Circle((0, 0), rr, fc='none', ec='#c8cfd6', lw=0.5,
                            ls=':', zorder=1))
    # шкала расстояний — отдельным лучом влево, вне орбит
    for rr in (1, 2, 3, 4, 5):
        ax.plot([-rr, -rr], [-5.05, -4.85], color='#8a94a0', lw=0.7)
        ax.text(-rr, -5.42, str(rr), fontsize=6.4, color='#8a94a0',
                ha='center', va='center')
    ax.plot([-5, -1], [-4.95, -4.95], color='#8a94a0', lw=0.7)
    ax.text(-3.0, -4.62, 'расстояние от Солнца, а.е.', fontsize=6.6,
            color='#8a94a0', ha='center', va='bottom')

    ax.set_xlim(-6.1, 6.1); ax.set_ylim(-5.6, 5.6)
    ax.set_aspect('equal'); ax.axis('off')

    lg.text(0.0, 1.0, 'Ресурсные тела: орбиты в плоскости эклиптики',
            fontsize=9.3, weight='bold', va='top', transform=lg.transAxes)
    lg.text(0.0, 0.945, 'Элементы орбит по базе малых тел JPL. Точкой отмечен '
            'перигелий', fontsize=7.0, va='top', color='#555',
            transform=lg.transAxes)

    rows = [('1', C_ACC, '(6178) 1986 DA — металл',
             'M-тип · a = 2,82 а.е. · e = 0,582 · i = 4,3°\n'
             'перигелий 1,18, афелий 4,46 а.е. · период 4,7 года\n'
             'сталь и никель: 94 % потребности проекта'),
            ('2', C_OK, '(1) Церера — вода',
             'C-тип · a = 2,77 а.е. · e = 0,079 · i = 10,6°\n'
             'период 4,6 года · водяной лёд в коре\n'
             'ближайший крупный источник воды'),
            ('3', '#5b8fa8', '(24) Themis — вода и органика',
             'C/B-тип · a = 3,15 а.е. · e = 0,117 · i = 0,7°\n'
             'иней водяного льда на поверхности\n'
             'семейство Themis: тысячи тел того же состава'),
            ('4', '#9b6b9e', '(10) Hygiea — гидросиликаты',
             'C-тип · a = 3,14 а.е. · e = 0,113 · i = 3,8°\n'
             'аммонийные силикаты: источник азота\n'
             'крупнейшее тело C-класса внешнего пояса'),
            ('5', C_WARN, '67P/Чурюмова — Герасименко — льды',
             'комета · a = 3,46 а.е. · e = 0,641 · i = 7,0°\n'
             'перигелий 1,24, афелий 5,68 а.е.\n'
             'аммиак и азот во льду: 1 % массы ядра')]
    yy = 0.828
    for m, c, t1, t2 in rows:
        lg.text(0.026, yy - 0.024, m, fontsize=7.4, weight='bold', color='white',
                ha='center', va='center', transform=lg.transAxes,
                bbox=dict(boxstyle='circle,pad=0.24', fc=c, ec='none'))
        lg.text(0.078, yy, t1, fontsize=7.9, va='top', transform=lg.transAxes)
        lg.text(0.078, yy - 0.058, t2, fontsize=7.0, va='top', color='#555',
                linespacing=1.42, transform=lg.transAxes)
        yy -= 0.163
    yy -= 0.030
    lg.text(0.0, 0.898, 'Штриховые окружности — орбиты Земли, Марса и Юпитера',
            fontsize=7.0, va='top', color='#8a7a5a', transform=lg.transAxes)
    return save(fig, 'fig22_asteroids.png')



# ─────────────────────────────────────────────────────────────
# Рис. 23. Карантинный контур: четыре потока на входе
# ─────────────────────────────────────────────────────────────
def fig23():
    fig = plt.figure(figsize=(7.8, 4.3))
    ax = fig.add_axes([0.010, 0.045, 0.505, 0.910])
    lg = fig.add_axes([0.535, 0.030, 0.460, 0.940]); lg.axis('off')

    # три зоны: космос -> карантин -> станция
    ax.add_patch(Rectangle((0.0, 0.0), 2.6, 8.4, fc='#eceff2', ec='#b8c2cc',
                           lw=1.0, zorder=1))
    ax.add_patch(Rectangle((2.6, 0.0), 3.6, 8.4, fc='#fdf3e3', ec=C_WARN,
                           lw=1.4, zorder=1))
    ax.add_patch(Rectangle((6.2, 0.0), 2.6, 8.4, fc='#eaf3ec', ec=C_OK,
                           lw=1.4, zorder=1))
    ax.text(1.3, 8.66, 'ВНЕШНЯЯ\nСТОРОНА', fontsize=7.2, weight='bold',
            ha='center', va='bottom', color='#63707d', linespacing=1.35)
    ax.text(4.4, 8.66, 'КАРАНТИННЫЙ КОНТУР', fontsize=7.2, weight='bold',
            ha='center', va='bottom', color='#a6791b')
    ax.text(7.5, 8.66, 'ЖИЛОЙ\nОБЪЁМ', fontsize=7.2, weight='bold',
            ha='center', va='bottom', color='#3f7350', linespacing=1.35)

    # гермопереборки на границах
    for xx in (2.6, 6.2):
        ax.plot([xx, xx], [0, 8.4], color=C_STEEL, lw=2.4, zorder=4)

    # четыре потока
    lanes = [(7.15, '1', 'Люди', C_ACC),
             (5.05, '2', 'Живое', C_OK),
             (2.95, '3', 'Грузы', '#5b8fa8'),
             (0.95, '4', 'Воздух\nи вода', '#9b6b9e')]
    for y, m, name, c in lanes:
        ax.annotate('', xy=(6.15, y), xytext=(0.35, y),
                    arrowprops=dict(arrowstyle='-|>', lw=1.5, color=c,
                                    shrinkA=0, shrinkB=0), zorder=5)
        ax.text(0.30, y + 0.62, name, fontsize=7.4, ha='left', va='center',
                color=c, weight='bold', linespacing=1.35)
        ax.text(6.62, y, m, fontsize=7.6, weight='bold', color='white',
                ha='center', va='center', zorder=7,
                bbox=dict(boxstyle='circle,pad=0.26', fc=c, ec='none'))
        # ступени обработки внутри контура
        for k, xx in enumerate((3.25, 4.35, 5.45)):
            ax.add_patch(Rectangle((xx - 0.36, y - 0.42), 0.72, 0.84,
                                   fc='white', ec=c, lw=1.0, zorder=6))
            ax.text(xx, y, 'I II III'.split()[k], fontsize=6.6, ha='center',
                    va='center', color=c, zorder=7)

    ax.set_xlim(-0.15, 8.95); ax.set_ylim(-0.35, 10.25)
    ax.axis('off')

    lg.text(0.0, 1.0, 'Карантинный контур: три ступени для каждого потока',
            fontsize=9.2, weight='bold', va='top', transform=lg.transAxes)
    lg.text(0.0, 0.940, 'Ступени I, II, III проходятся последовательно; переход '
            'на\nследующую — только по отрицательному результату проверки',
            fontsize=7.0, va='top', color='#555', linespacing=1.45,
            transform=lg.transAxes)

    rows = [('1', C_ACC, 'Люди — выдержка 40 суток',
             'I обследование и посев · II изоляция на срок\n'
             'инкубации · III допуск по анализам, не по времени'),
            ('2', C_OK, 'Живое: семена, биота, насекомые',
             'I проверка партии · II выращивание в изоляторе\n'
             'до первого урожая · III выпуск в биосферу'),
            ('3', '#5b8fa8', 'Грузы и оборудование',
             'I вскрытие в вакууме · II гамма-облучение 25 кГр\n'
             'или прогрев 200 °C · III контрольный посев'),
            ('4', '#9b6b9e', 'Воздух и вода шлюза',
             'I сброс воздуха шлюза в вакуум · II фильтрация\n'
             'и ультрафиолет · III контроль перед подачей')]
    yy = 0.808
    for m, c, t1, t2 in rows:
        lg.text(0.026, yy - 0.026, m, fontsize=7.4, weight='bold', color='white',
                ha='center', va='center', transform=lg.transAxes,
                bbox=dict(boxstyle='circle,pad=0.24', fc=c, ec='none'))
        lg.text(0.078, yy, t1, fontsize=8.0, va='top', transform=lg.transAxes)
        lg.text(0.078, yy - 0.062, t2, fontsize=7.2, va='top', color='#555',
                linespacing=1.45, transform=lg.transAxes)
        yy -= 0.170
    lg.text(0.0, yy + 0.020, 'Пропускная способность и срок заселения',
            fontsize=8.4, weight='bold', va='top', transform=lg.transAxes)
    lg.text(0.030, yy - 0.048, 'Размер изолятора N = R·Q. Заселение 1 млн '
            'человек\nза 10 лет: поток R = 100 000 чел/год (274 в сутки),\n'
            'выдержка Q = 40 сут — N = 10 951 место, 9,13 цикла в год.\n'
            'Транспорт даёт 32 400 чел/сут — запас 118 крат.',
            fontsize=7.2, va='top', color=C_STEEL, weight='bold',
            linespacing=1.45, transform=lg.transAxes)
    return save(fig, 'fig23_quarantine.png')


if __name__ == '__main__':
    print('Генерация иллюстраций ММОСО\'Н:')
    for f in [fig01, fig02, fig03, fig04, fig05, fig06, fig07, fig08, fig09,
              fig10, fig11, fig12, fig13, fig14, fig15, fig16, fig17, fig18,
              fig19, fig20, fig21, fig22, fig23]:
        f()
    print('Готово. Каталог:', OUT)


def fig24():
    """Выбор размера панели: конкуренция двух ограничений."""
    import numpy as np
    fig, ax = plt.subplots(figsize=(9.2, 5.6))
    a = np.linspace(10, 120, 400)
    R, t, rho = 5000., 0.85, 7900.
    S = 2*np.pi*R*40000.

    n = S/(a*(a*2.0))
    weld = (2*(a+a*2.0))*n/2/1e6                 # тыс. км
    mass = a*(a*2.0)*t*rho/1000                  # т
    sag  = R*(1-np.cos((a/R)/2))*1000            # мм

    ax.plot(a, weld, lw=2.6, color='#1f4e79')
    ax.set_xlim(10, 120); ax.set_ylim(0, 215)
    ax.set_xlabel('ширина панели a, м  (длина b = 2a)')
    ax.set_ylabel('длина сварных швов, тыс. км', color='#1f4e79')
    ax.tick_params(axis='y', labelcolor='#1f4e79')
    ax.grid(alpha=.3)

    ax2 = ax.twinx()
    ax2.plot(a, mass/1000, lw=2.6, color='#2a7')
    ax2.set_ylim(0, 145)
    ax2.set_ylabel('масса панели, тыс. т', color='#1a6')
    ax2.tick_params(axis='y', labelcolor='#1a6')

    ax.axvspan(40, 60, color='#ffd', alpha=.9, zorder=0)
    ax.axvline(50, color='#333', lw=1.6, ls='--', zorder=5)
    ax.text(50, 196, 'принято 50 x 100 м', ha='center', va='bottom',
            fontsize=10.5, fontweight='bold')

    ax.plot([50], [37.7], marker='o', ms=10, color='#1f4e79', zorder=6)
    ax2.plot([50], [33.575], marker='o', ms=10, color='#2a7', zorder=6)

    rows = [
        ('#1f4e79', '1 — сварные швы', ['убывают с ростом панели',
                                        'при 50 м — 37,7 тыс. км',
                                        'против 94,2 при 20 м']),
        ('#2a7',    '2 — масса панели', ['растёт как квадрат',
                                         'при 50 м — 33 575 т',
                                         'кривизна 62 мм']),
    ]
    y = 0.95
    for c, h, ss in rows:
        ax.plot([1.14], [y], marker='o', ms=10, color=c,
                transform=ax.transAxes, clip_on=False)
        ax.text(1.18, y, h, transform=ax.transAxes, fontsize=10.5,
                va='center', fontweight='bold')
        for k, s in enumerate(ss):
            ax.text(1.18, y-0.065-k*0.052, s, transform=ax.transAxes,
                    fontsize=9.2, va='center', color='#555')
        y -= 0.30
    ax.text(1.14, y+0.02, 'Окно 40–60 м', transform=ax.transAxes,
            fontsize=10.5, va='center', fontweight='bold')
    for k, s in enumerate(['швы сокращены в 2,5 раза',
                           'кривизна технологична',
                           'заполнение формы 17 мин',
                           '251 тыс. панелей на цилиндр']):
        ax.text(1.14, y-0.045-k*0.052, '· '+s, transform=ax.transAxes,
                fontsize=9.2, va='center', color='#555')

    fig.subplots_adjust(left=0.085, right=0.565, top=0.94, bottom=0.11)
    fig.savefig(os.path.join(OUT, 'fig24_panel_choice.png'), dpi=150)
    plt.close(fig)
