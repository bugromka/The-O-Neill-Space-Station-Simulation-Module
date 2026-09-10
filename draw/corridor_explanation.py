# -*- coding: utf-8 -*-
"""ММОСО'Н — внешний вид и отдельные внутренние разрезы транспортных коридоров.

Лист 1 намеренно без cutaway: только наружная компоновка.
Листы 2–4 — отдельные инженерные разрезы, объясняющие путь перемещения.
"""
import math
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Rectangle, Circle, Ellipse, Arc, FancyArrowPatch, Polygon
from matplotlib.lines import Line2D
from eskd import Sheet, S_MAIN, S_THIN, C

BLUE = '#145b92'
BLUE_LIGHT = '#dcecf7'
RED = '#b41f1f'
RED_LIGHT = '#f3d8d4'
METAL = '#b7b7b7'
DARK = '#3a3a3a'
GREY = '#777777'
ORANGE = '#985700'
GREEN = '#28613d'
INNER = '#f4f1e8'


def L(A, x1, y1, x2, y2, kind='main', color=C, lw=None, z=3):
    styles = {'main': (S_MAIN, '-'), 'thin': (S_THIN, '-'),
              'axis': (S_THIN, (0, (10, 3, 2, 3))),
              'hidden': (S_THIN, (0, (5, 3)))}
    w, ls = styles[kind]
    A.add_line(Line2D([x1, x2], [y1, y2], color=color, lw=lw or w,
                      ls=ls, zorder=z))


def T(A, x, y, value, size=7, ha='left', va='center', color=C,
      weight=None, style=None, z=20):
    A.text(x, y, value, fontsize=size, ha=ha, va=va, color=color,
           fontweight=weight, fontstyle=style, linespacing=1.22, zorder=z)


def ARR(A, x1, y1, x2, y2, color=BLUE, lw=1.15, ms=8, z=15):
    A.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle='-|>',
                                mutation_scale=ms, linewidth=lw,
                                color=color, zorder=z))


def title(s, h, sub):
    A = s.ax
    T(A, 30, 405, h, size=10, weight='bold')
    T(A, 30, 394, sub, size=6.7, style='italic')
    L(A, 30, 387, 565, 387, 'thin', color=GREY)


def section_marker(A, x, y, letter, tx, ty):
    L(A, x, y, tx, ty, 'thin')
    A.add_patch(Circle((tx, ty), 4, fc='white', ec=C, lw=S_THIN, zorder=25))
    T(A, tx, ty, letter, size=6, ha='center', weight='bold', z=26)


def callout(s, x, y, tx, ty, n, label, side='right', size=6.0):
    A = s.ax
    L(A, x, y, tx, ty, 'thin')
    A.add_patch(Circle((tx, ty), 4, fc='white', ec=C, lw=S_THIN, zorder=25))
    T(A, tx, ty, n, size=5.8, ha='center', weight='bold', z=26)
    T(A, tx+7 if side == 'right' else tx-7, ty, label, size=size,
      ha='left' if side == 'right' else 'right', z=25)


def channel(A, x1, x2, y, label=None, color=BLUE):
    L(A, x1, y-3.5, x2, y-3.5, 'main', color=color, lw=1.45, z=10)
    L(A, x1, y+3.5, x2, y+3.5, 'main', color=color, lw=1.45, z=10)
    ARR(A, x1+7, y, x2-6, y, color, .9, 7, 12)
    if label:
        T(A, (x1+x2)/2, y+10, label, size=5.5, ha='center', color=color, weight='bold')


def hatch_rect(s, x1, y1, x2, y2, step=2.5):
    s.hatch(x1, y1, x2, y2, step=step)


def sheet1_exterior():
    s = Sheet('A2', title='Станция.\nНаружный вид', material='Сталь 18Ni(300)',
              scale='см. виды', number='ММОСО.00.900 ВО', mass='46,70 млрд т',
              sheet_no='1', sheets='4', lit='П', date='10.09.2026')
    A = s.ax
    title(s, 'ЛИСТ 1. НАРУЖНЫЙ ВИД — БЕЗ РАЗРЕЗА И БЕЗ ПОКАЗА ИНТЕРЬЕРА',
          'Ортографическая внешняя компоновка. Внутренние трассы приведены только на листах 2–4.')
    # Two smooth external shells. No interior lines, no transparent surfaces.
    x0, x1 = 175, 460
    ys = (287, 181)
    r = 25
    for i, cy in enumerate(ys, 1):
        A.add_patch(Rectangle((x0, cy-r), x1-x0, 2*r, fc='#d0d0d0', ec=C, lw=S_MAIN))
        A.add_patch(Arc((x0, cy), 2*r, 2*r, theta1=90, theta2=270, ec=C, lw=S_MAIN))
        A.add_patch(Arc((x1, cy), 2*r, 2*r, theta1=-90, theta2=90, ec=C, lw=S_MAIN))
        T(A, (x0+x1)/2, cy, f'ГЛАДКАЯ ОБОЛОЧКА ЦИЛИНДРА {i}', size=6.7, ha='center', weight='bold')
        # thin construction axes only, no interior/route lines
        L(A, x0-9, cy, x1+9, cy, 'axis', color=GREY)
    # front and rear fixed frames, external equipment only on them
    for cy in ys:
        A.add_patch(Rectangle((112, cy-34), 14, 68, fc=DARK, ec=C, lw=S_MAIN))
        A.add_patch(Rectangle((515, cy-34), 14, 68, fc=DARK, ec=C, lw=S_MAIN))
        # front docking deck and two metal corridors (outside view only)
        A.add_patch(Rectangle((63, cy-18), 35, 36, fc=METAL, ec=C, lw=S_THIN))
        L(A, 98, cy-10, 112, cy-10, 'main', color=METAL, lw=2)
        L(A, 98, cy+10, 112, cy+10, 'main', color=METAL, lw=2)
        # rear solar wings (blue) and radiators (red)
        for yy in (cy+35, cy-35):
            A.add_patch(Rectangle((540, yy-5), 10, 10, fc=RED_LIGHT, ec=RED, lw=S_THIN))
        A.add_patch(Rectangle((495, cy+19), 9, 22, fc=BLUE_LIGHT, ec=BLUE, lw=S_THIN))
        A.add_patch(Rectangle((495, cy-41), 9, 22, fc=BLUE_LIGHT, ec=BLUE, lw=S_THIN))
        for xx in (497, 500):
            L(A, xx, cy+20, xx, cy+40, 'thin', color=BLUE)
            L(A, xx, cy-40, xx, cy-20, 'thin', color=BLUE)
    # three rear antennas, visible from outside
    for i, yy in enumerate((287+34, 234, 181-34), 1):
        L(A, 529, yy, 566, yy+10, 'thin')
        A.add_patch(Ellipse((572, yy+12), 16, 7, fill=False, ec=C, lw=S_THIN))
        T(A, 572, yy+24, f'А{i}', size=5.3, ha='center')
    T(A, 119, 338, 'ПЕРЕДНЯЯ НЕПОДВИЖНАЯ РАМА', size=6.5, ha='center', weight='bold')
    T(A, 522, 338, 'ЗАДНЯЯ НЕПОДВИЖНАЯ РАМА', size=6.5, ha='center', weight='bold')
    # clear gap annotation
    T(A, 316, 237, '11 000 СВОБОДНОГО ЗАЗОРА\nвнешних связей между оболочками нет', size=6.4, ha='center', color=GREY, weight='bold')
    s.dim_v(ys[1]+r, ys[0]-r, 476, '11 000', ext_from=x1)
    s.dim_v(ys[1], ys[0], 494, '21 000 оси', ext_from=x1)
    s.dim_h(x0, x1, 137, '40 000 цилиндрическая часть', ext_from=ys[1]-r)
    s.dim_h(112, 529, 354, '49 000 общая длина', ext_from=ys[0]+r)
    # external legend, no route lines on this sheet
    T(A, 42, 112, 'НАРУЖНЫЕ ЭЛЕМЕНТЫ', size=7.4, weight='bold')
    A.add_patch(Rectangle((45, 91), 12, 9, fc=METAL, ec=C, lw=S_THIN)); T(A, 64, 95, 'рама / причал / внешняя дека', size=6.0)
    A.add_patch(Rectangle((45, 76), 12, 9, fc=RED_LIGHT, ec=RED, lw=S_THIN)); T(A, 64, 80, 'красный — только радиатор', size=6.0, color=RED)
    A.add_patch(Rectangle((45, 61), 12, 9, fc=BLUE_LIGHT, ec=BLUE, lw=S_THIN)); T(A, 64, 65, 'синий — солнечное крыло', size=6.0, color=BLUE)
    s.note(260, 108,
           'На этом листе намеренно нет cutaway, прозрачности и внутреннего оборудования.\n'
           'Он отвечает только на вопрос: что видно снаружи и где находятся неподвижные рамы.\n'
           'Как человек или груз проходит внутрь — листы 2–4.', size=6.3)
    return s


def sheet2_longitudinal_section():
    s = Sheet('A2', title='Цилиндр.\nПродольный разрез транспортной трассы', material='Сталь 18Ni(300)',
              scale='схема / узлы увеличены', number='ММОСО.01.900 СБ', mass='—',
              sheet_no='2', sheets='4', lit='П', date='10.09.2026')
    A = s.ax
    title(s, 'ЛИСТ 2. ПРОДОЛЬНЫЙ РАЗРЕЗ — КАК ПРОХОДИТ ТРАНСПОРТНЫЙ КОРИДОР',
          'Один цилиндр показан в разрезе. Два независимых канала A и B сохраняются раздельными от причала до жилой поверхности.')
    # coordinate layout
    y = 250
    dock_x = 48
    fixed_x = 128
    seal_x = 198
    hub_x = 320
    surface_x = 403
    body_end = 535
    r = 78
    # open sectional shell: upper external contour and lower internal contour
    A.add_patch(Arc((body_end, y), 2*r, 2*r, theta1=-90, theta2=90, ec=C, lw=S_MAIN))
    L(A, hub_x, y+r, body_end, y+r, 'main')
    L(A, hub_x, y-r, body_end, y-r, 'main')
    # inner residential surfaces
    L(A, hub_x+8, y+r-12, body_end-5, y+r-12, 'thin', color=GREY)
    L(A, hub_x+8, y-r+12, body_end-5, y-r+12, 'thin', color=GREY)
    T(A, 447, y+55, 'внутренний объём цилиндра', size=6.5, ha='center', color=GREY)
    T(A, 447, y-55, 'жилая поверхность', size=6.5, ha='center', color=GREY)
    # front dome / sectioned shell
    A.add_patch(Arc((hub_x, y), 2*r, 2*r, theta1=90, theta2=270, ec=C, lw=S_MAIN))
    A.add_patch(Arc((hub_x, y), 2*(r-8), 2*(r-8), theta1=90, theta2=270, ec=C, lw=S_THIN))
    for ang in range(100, 261, 12):
        a = math.radians(ang)
        L(A, hub_x+(r-2)*math.cos(a), y+(r-2)*math.sin(a),
          hub_x+(r-8)*math.cos(a), y+(r-8)*math.sin(a), 'thin')
    # fixed front docking frame and two exterior corridors
    A.add_patch(Rectangle((fixed_x-8, y-52), 16, 104, fc=DARK, ec=C, lw=S_MAIN))
    A.add_patch(Rectangle((dock_x, y-24), 35, 48, fill=False, ec=C, lw=S_MAIN))
    T(A, dock_x+17, y, 'П', size=14, ha='center', weight='bold')
    T(A, fixed_x, y+64, 'ФИКСИРОВАННАЯ\nРАМА', size=6.1, ha='center', weight='bold')
    T(A, dock_x+17, y-35, 'причал', size=6.0, ha='center')
    # stationary part A/B corridors, separate
    for off, lab in ((11, 'A'), (-11, 'B')):
        channel(A, dock_x+35, fixed_x-12, y+off, lab)
        A.add_patch(Rectangle((fixed_x+5, y+off-8), 28, 16, fc=BLUE_LIGHT, ec=BLUE, lw=S_THIN))
        T(A, fixed_x+19, y+off, 'Ш/К', size=5.7, ha='center', color=BLUE, weight='bold')
    T(A, 91, y-45, '2 независимых\nканала', size=5.8, ha='center', color=BLUE)
    # station/rotor boundary
    L(A, seal_x, y-r-22, seal_x, y+r+22, 'axis', color=ORANGE)
    T(A, seal_x, y+r+31, 'граница: статор / ротор', size=6.0, ha='center', color=ORANGE, weight='bold')
    T(A, seal_x, y-r-34, 'внешняя рама не вращается', size=5.6, ha='center', color=ORANGE)
    # dual-channel rotating hermetic transfer
    A.add_patch(Rectangle((seal_x-8, y-31), 16, 62, fc=RED_LIGHT, ec=ORANGE, lw=S_MAIN))
    for off in (-11, 11):
        channel(A, seal_x-25, seal_x+25, y+off, None)
    T(A, seal_x, y+47, 'двухканальный\nгермопереход', size=5.7, ha='center', color=ORANGE)
    # hollow shaft with two separate lanes
    for off, lab in ((11, 'A'), (-11, 'B')):
        channel(A, seal_x+25, hub_x-13, y+off, lab)
    A.add_patch(Circle((hub_x, y), 14, fill=False, ec=C, lw=S_MAIN))
    A.add_patch(Circle((hub_x, y), 8, fill=False, ec=C, lw=S_THIN))
    T(A, 255, y+24, 'полый осевой вал\nA и B не сливаются', size=6.0, ha='center', color=BLUE, weight='bold')
    ARR(A, 255, y+11, 300, y+11, BLUE, .9, 7)
    ARR(A, 255, y-11, 300, y-11, BLUE, .9, 7)
    # distribution hub and two independent inclined shafts
    for off, sign, lab in ((11, 1, 'A'), (-11, -1, 'B')):
        x2, y2 = hub_x+64, y+sign*57
        dx, dy = x2-hub_x, y2-(y+off)
        norm = math.hypot(dx, dy)
        nx, ny = -dy/norm*3.0, dx/norm*3.0
        L(A, hub_x+nx, y+off+ny, x2+nx, y2+ny, 'main', color=BLUE, lw=1.6)
        L(A, hub_x-nx, y+off-ny, x2-nx, y2-ny, 'main', color=BLUE, lw=1.6)
        ARR(A, hub_x+dx*.35, y+off+dy*.35, hub_x+dx*.70, y+off+dy*.70, BLUE, .9, 7)
        A.add_patch(Circle((x2, y2), 4, fill=False, ec=BLUE, lw=S_THIN))
        T(A, x2+30, y2, f'ШAХТА {lab}\nгермодвери', size=5.7, color=BLUE, weight='bold')
    # actual living surface landing points
    T(A, surface_x, y+87, 'вестибюль на жилой поверхности A', size=5.8, ha='center', color=BLUE)
    T(A, surface_x, y-87, 'вестибюль на жилой поверхности B', size=5.8, ha='center', color=BLUE)
    # rotation arrow and dimensions
    ARR(A, 365, y+r+12, 425, y+r+12, GREEN, 1.1, 9)
    T(A, 395, y+r+22, 'ω цилиндра', size=6.0, ha='center', color=GREEN, weight='bold')
    s.dim_h(hub_x, body_end, y+r+26, 'цилиндрическая часть 40 000', ext_from=y+r)
    s.dim_h(dock_x, body_end, y-r-28, 'общая длина 49 000', ext_from=y-r)
    s.dim_v(y-r, y+r, 554, 'Ø10 000', ext_from=body_end)
    # numbered route list below the section
    T(A, 42, 111, 'Что физически происходит с пассажиром/грузом', size=7.6, weight='bold')
    steps = [
        ('1', 'Причал', 'неподвижный'), ('2', 'Шлюз + карантин', 'давление/санконтроль'),
        ('3', 'Гермопереход', 'A и B переходят на ротор'), ('4', 'Полый вал', 'две отдельные линии'),
        ('5', 'Распределительный узел', 'A/B расходятся'), ('6', 'Шахта', 'две наклонные трассы'),
        ('7', 'Вестибюль', 'выход на жилую поверхность')]
    x = 45
    for i, (n, a, b) in enumerate(steps):
        w = 60
        A.add_patch(Rectangle((x, 77), w, 22, fc=BLUE_LIGHT, ec=BLUE, lw=S_THIN))
        A.add_patch(Circle((x+7, 92), 3.5, fc='white', ec=BLUE, lw=S_THIN))
        T(A, x+7, 92, n, size=4.8, ha='center', color=BLUE, weight='bold')
        T(A, x+w/2, 88, a, size=5.2, ha='center', color=BLUE, weight='bold')
        T(A, x+w/2, 81, b, size=4.8, ha='center', color=BLUE)
        if i < len(steps)-1:
            ARR(A, x+w+2, 88, x+w+9, 88, BLUE, .8, 6)
        x += w+10
    T(A, 42, 65, 'Ключевое: каналы A и B не пересекаются и не открываются в вакуум. Только гермопереход является вращающимся интерфейсом.', size=6.1, color=BLUE, weight='bold')
    return s


def sheet3_views():
    s = Sheet('A2', title='Транспортные коридоры.\nПлан и поперечные разрезы', material='Сталь 18Ni(300)',
              scale='см. виды', number='ММОСО.01.910 СБ', mass='—',
              sheet_no='3', sheets='4', lit='П', date='10.09.2026')
    A = s.ax
    title(s, 'ЛИСТ 3. КАК КОРИДОРЫ ВЫГЛЯДЯТ В ПЛАНЕ И В ПОПЕРЕЧНОМ РАЗРЕЗЕ',
          'Разные виды показывают, что фиксированная рама, вращающийся вал и шахты являются последовательными, а не одной общей камерой.')
    # Left: front frame plan, two cylinders and four channels.
    cx, cy = 120, 245
    top, bot = cy+64, cy-64
    T(A, cx, 346, 'Вид со стороны причала', size=7.7, ha='center', weight='bold')
    T(A, cx, 336, 'передняя рама и два цилиндра', size=5.9, ha='center', style='italic')
    L(A, cx, bot-48, cx, top+48, 'main')
    for yy in (top, bot):
        A.add_patch(Circle((cx, yy), 40, fill=False, ec=C, lw=S_MAIN))
        A.add_patch(Circle((cx, yy), 8, fill=False, ec=C, lw=S_MAIN))
        for off in (-15,15):
            channel(A, cx+45, cx+112, yy+off, None)
            T(A, cx+78, yy+off+9, 'A' if off > 0 else 'B', size=5.5, ha='center', color=BLUE, weight='bold')
    T(A, 46, cy, 'зазор\n11 000\nпустой', size=6.2, ha='center', color=GREY, weight='bold')
    L(A, 63, bot+40, 63, top-40, 'axis', color=GREY)
    s.dim_v(bot+40, top-40, 205, '11 000', ext_from=cx+40)
    s.dim_v(bot, top, 222, '21 000', ext_from=cx+40)
    T(A, cx, cy-105, 'Для каждого цилиндра: A и B — отдельные коридоры.', size=6.0, ha='center', color=BLUE)
    # Center top: axial shaft cross-section, two conduits.
    sx, sy = 330, 276
    T(A, sx, 346, 'Сечение полого осевого вала', size=7.7, ha='center', weight='bold')
    T(A, sx, 336, 'вид поперёк оси вращения', size=5.9, ha='center', style='italic')
    A.add_patch(Circle((sx, sy), 52, fill=False, ec=C, lw=S_MAIN))
    A.add_patch(Circle((sx, sy), 43, fill=False, ec=C, lw=S_THIN))
    A.add_patch(Circle((sx, sy), 9, fill=False, ec=C, lw=S_THIN))
    for yy, lab in ((sy+19,'A'), (sy-19,'B')):
        A.add_patch(Rectangle((sx-25, yy-6), 50, 12, fc=BLUE_LIGHT, ec=BLUE, lw=S_THIN))
        T(A, sx, yy, f'КАНАЛ {lab}', size=5.3, ha='center', color=BLUE, weight='bold')
    T(A, sx, sy-72, 'две герметичные линии\nвнутри одного вращающегося вала', size=5.8, ha='center', color=BLUE)
    T(A, sx+63, sy, 'размеры сечения\nназначаются отдельным\nрасчётом прочности', size=5.4, color=GREY)
    # Center bottom: rotating seal cross-section.
    zx, zy = 330, 151
    T(A, zx, 224, 'Сечение вращающегося гермоперехода', size=7.5, ha='center', weight='bold')
    A.add_patch(Rectangle((zx-52, zy-34), 104, 68, fill=False, ec=C, lw=S_MAIN))
    A.add_patch(Rectangle((zx-40, zy-24), 80, 48, fill=False, ec=ORANGE, lw=S_MAIN))
    for yy, lab in ((zy+12,'A'), (zy-12,'B')):
        A.add_patch(Rectangle((zx-31, yy-5), 62, 10, fc=BLUE_LIGHT, ec=BLUE, lw=S_THIN))
        T(A, zx, yy, f'канал {lab}', size=5.3, ha='center', color=BLUE, weight='bold')
    L(A, zx, zy-50, zx, zy+50, 'axis', color=ORANGE)
    T(A, zx+68, zy+14, 'статор', size=5.7, color=ORANGE)
    T(A, zx+68, zy-14, 'ротор', size=5.7, color=ORANGE)
    ARR(A, zx-82, zy+45, zx-55, zy+45, BLUE, .9, 7)
    ARR(A, zx+55, zy-45, zx+82, zy-45, BLUE, .9, 7)
    T(A, zx, zy-59, 'A/B не смешиваются при вращении', size=5.8, ha='center', color=BLUE, weight='bold')
    # Right: front hemisphere transverse section.
    hx, hy = 485, 245
    T(A, hx, 346, 'Сечение передней полусферы', size=7.7, ha='center', weight='bold')
    T(A, hx, 336, 'вид изнутри вращающегося цилиндра', size=5.9, ha='center', style='italic')
    A.add_patch(Circle((hx, hy), 70, fill=False, ec=C, lw=S_MAIN))
    A.add_patch(Circle((hx, hy), 62, fill=False, ec=C, lw=S_THIN))
    L(A, hx-83, hy, hx+83, hy, 'axis', color=GREY)
    L(A, hx, hy-83, hx, hy+83, 'axis', color=GREY)
    A.add_patch(Circle((hx, hy), 8, fill=False, ec=C, lw=S_MAIN))
    for ang, lab in ((38,'A'),(-38,'B')):
        a=math.radians(ang)
        x1,y1=hx+10*math.cos(a),hy+10*math.sin(a)
        x2,y2=hx+55*math.cos(a),hy+55*math.sin(a)
        L(A,x1,y1,x2,y2,'main',color=BLUE,lw=2)
        ARR(A,x1+10*math.cos(a),y1+10*math.sin(a),x2-4*math.cos(a),y2-4*math.sin(a),BLUE,.9,7)
        T(A,x2+12*math.cos(a),y2+12*math.sin(a),f'ШAХТА {lab}',size=5.5,color=BLUE,weight='bold',ha='center')
    T(A, hx, hy-87, 'центр распределения из полого вала', size=5.7, ha='center')
    s.dim_v(hy-70, hy+70, 402, 'Ø10 000', ext_from=hx-70)
    # bottom route logic as clean numbered table
    s.table(42, 112,
            ['Участок', 'Состояние', 'Что происходит', 'Вращение'],
            [['I. Причал → шлюзы', 'статор', 'стыковка, карантин, давление', 'не вращается'],
             ['II. Гермопереход', 'граница', 'две герметичные линии переходят на ротор', 'уплотнение вращается'],
             ['III. Полый вал', 'ротор', 'A/B идут параллельно внутри вала', 'вращается вместе с цилиндром'],
             ['IV. Шахты', 'ротор', 'A и B расходятся к двум вестибюлям', 'вращаются вместе с цилиндром'],
             ['V. Поверхность', 'ротор', 'выход в жилой объём', 'вращается вместе с цилиндром']],
            [42, 50, 100, 40], rh=6.0, size=5.8, head_size=6.0,
            title='ЛОГИКА ТРАССЫ', align=['left','left','left','center'])
    return s


def sheet4_inside():
    s = Sheet('A2', title='Внутренний маршрут.\nФункциональная последовательность', material='—',
              scale='схема', number='ММОСО.01.920 СБ', mass='—',
              sheet_no='4', sheets='4', lit='П', date='10.09.2026')
    A = s.ax
    title(s, 'ЛИСТ 4. ВНУТРЕННИЙ МАРШРУТ — ЧТО ВИДИТ ПАССАЖИР И КАК РАБОТАЮТ ОТСЕКИ',
          'Схема не заменяет расчёт герметичности; она показывает последовательность пространств и границ давления.')
    # Long exploded functional route, separated into zones.
    y = 245
    zones = [
        (40, 76, 'ПРИЧАЛ', 'неподвижный\nвакуумный интерфейс'),
        (125, 78, 'ШЛЮЗ 1', 'входная\nгермодверь'),
        (225, 78, 'КАРАНТИН', 'контроль\nи изоляция'),
        (325, 88, 'ГЕРМОПЕРЕХОД', 'статор → ротор\nдвухканальный'),
        (435, 82, 'ПОЛЫЙ ВАЛ', 'A / B\nпараллельно'),
    ]
    for x,w,head,sub in zones:
        A.add_patch(Rectangle((x, y-30), w, 60, fill=False, ec=C, lw=S_MAIN))
        A.add_patch(Rectangle((x+8, y-18), w-16, 36, fc=BLUE_LIGHT, ec=BLUE, lw=S_THIN))
        T(A, x+w/2, y+9, head, size=6.4, ha='center', color=BLUE, weight='bold')
        T(A, x+w/2, y-7, sub, size=5.5, ha='center', color=BLUE)
        if x != zones[0][0]:
            pass
    for x1,x2 in ((116,125),(203,225),(313,325),(413,435)):
        channel(A, x1, x2, y, None)
    # split into shafts and vestibules on the right
    hubx = 545
    A.add_patch(Circle((hubx, y), 18, fill=False, ec=C, lw=S_MAIN))
    T(A, hubx, y-29, 'распределительный узел', size=5.6, ha='center')
    for sign, lab in ((1,'A'),(-1,'B')):
        y2 = y+sign*64
        L(A, hubx+13, y+sign*5, 570, y2, 'main', color=BLUE, lw=1.8)
        L(A, hubx+18, y+sign*5, 575, y2, 'main', color=BLUE, lw=1.8)
        ARR(A, hubx+20, y+sign*12, 560, y2-sign*9, BLUE, .9, 7)
        A.add_patch(Rectangle((566, y2-11), 25, 22, fc=BLUE_LIGHT, ec=BLUE, lw=S_THIN))
        T(A, 578, y2, f'ВЕСТИБЮЛЬ {lab}', size=4.9, ha='center', color=BLUE, weight='bold')
    T(A, 545, y+91, 'две наклонные шахты', size=6.0, ha='center', color=BLUE, weight='bold')
    # pressure boundaries below each zone
    for x,w,head,sub in zones:
        L(A, x+4, y-36, x+4, y-51, 'thin', color=ORANGE)
        T(A, x+4, y-60, 'гермодверь', size=4.9, ha='center', color=ORANGE)
    # physical labels and a person/vehicle scale marker
    A.add_patch(Circle((59, y+2), 3, fc=C, ec=C)); L(A, 59, y-1, 59, y-12, 'thin'); L(A, 59, y-7, 54, y-16, 'thin'); L(A, 59, y-7, 64, y-16, 'thin')
    T(A, 59, y-25, 'человек / грузовой модуль', size=5.2, ha='center')
    # fixed/rotating boundary and direction
    L(A, 320, y-50, 320, y+50, 'axis', color=ORANGE)
    T(A, 320, y+69, 'граница неподвижного и вращающегося участка', size=6.0, ha='center', color=ORANGE, weight='bold')
    ARR(A, 401, y+51, 455, y+51, GREEN, 1.0, 8)
    T(A, 428, y+62, 'вращение ротора', size=5.7, ha='center', color=GREEN)
    # below: door logic and failure isolation
    T(A, 44, 130, 'Герметизация и аварийная логика', size=7.7, weight='bold')
    boxes = [
        (50, 'ДВЕРЬ 1', 'закрыта до\nвыравнивания давления'),
        (155, 'ДВЕРЬ 2', 'карантинный\nконтур'),
        (260, 'ДВЕРЬ 3', 'вращающееся\nуплотнение'),
        (365, 'ДВЕРЬ 4', 'валовая\nсекция'),
        (470, 'ДВЕРЬ 5', 'вестибюль\nцилиндра'),
    ]
    for x,hd,sub in boxes:
        A.add_patch(Rectangle((x, 89), 80, 28, fill=False, ec=ORANGE, lw=S_THIN))
        T(A, x+40, 108, hd, size=5.7, ha='center', color=ORANGE, weight='bold')
        T(A, x+40, 97, sub, size=5.1, ha='center')
    for x in (130,235,340,445):
        ARR(A, x, 103, x+20, 103, ORANGE, .8, 6)
    s.note(44, 76,
           'Если любой участок закрывается, соседние двери образуют герметичный отсек.\n'
           'Канал A и канал B имеют независимые двери и могут работать раздельно.\n'
           'При остановке вращения пассажирский переход остаётся герметичным; причальная\n'
           'рама не вращается и не передаёт момент на транспортный модуль.', size=6.2)
    return s


SHEETS = (sheet1_exterior, sheet2_longitudinal_section, sheet3_views, sheet4_inside)


def build(pdf_name='MMOSON_exterior_and_corridors.pdf'):
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    pdf_path = os.path.join(root, pdf_name)
    pngs = []
    with PdfPages(pdf_path) as pdf:
        for i, fn in enumerate(SHEETS, 1):
            s = fn()
            png = os.path.join(root, f'MMOSON_corridors_{i:02d}.png')
            s.fig.savefig(png, dpi=220, facecolor='white')
            pdf.savefig(s.fig)
            plt.close(s.fig)
            pngs.append(png)
        info = pdf.infodict()
        info['Title'] = 'ММОСО\'Н. Наружный вид и внутренние разрезы транспортных коридоров'
        info['Author'] = 'Бугаенко Р. С., НИК'
        info['Subject'] = 'Внешняя компоновка, внутренний маршрут, рамы, вал и шахты'
    return pdf_path, pngs


if __name__ == '__main__':
    p, imgs = build()
    print(p)
    for i in imgs:
        print(i)
