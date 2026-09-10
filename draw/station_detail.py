# -*- coding: utf-8 -*-
"""ММОСО'Н — подробный технический лист узлов станции.

Это именно чертёжный лист ЕСКД, а не художественная визуализация:
продольный сборочный вид, передняя рама, подшипниковый узел,
цилиндр с транспортными шахтами и задняя рама.
"""
import math
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Arc, Ellipse, Polygon, FancyBboxPatch, FancyArrowPatch
from matplotlib.lines import Line2D
from matplotlib.backends.backend_pdf import PdfPages

from eskd import Sheet, S_MAIN, S_THIN, C

BLUE = '#145a91'          # транспортные пути
BLUE_LIGHT = '#d8e8f4'
RED = '#b51f1f'           # только радиаторы
RED_LIGHT = '#f1d6d1'
STEEL = '#bdbdbd'
STEEL_DARK = '#777777'
GRAPH = '#333333'
GREEN = '#2b6e40'
ORANGE = '#a45b00'
PALE = '#f4f4f4'


def L(A, x1, y1, x2, y2, kind='main', color=C, lw=None, ls=None, z=3):
    styles = {'main': (S_MAIN, '-'), 'thin': (S_THIN, '-'),
              'axis': (S_THIN, (0, (10, 3, 2, 3))),
              'hidden': (S_THIN, (0, (5, 3)))}
    w, default_ls = styles[kind]
    A.add_line(Line2D([x1, x2], [y1, y2], color=color, lw=lw or w,
                      ls=ls or default_ls, zorder=z))


def T(A, x, y, text, size=7, ha='left', va='center', weight=None,
      color=C, style=None, z=20):
    A.text(x, y, text, fontsize=size, ha=ha, va=va, fontweight=weight,
           color=color, fontstyle=style, zorder=z, linespacing=1.25)


def arrow(A, x1, y1, x2, y2, color=BLUE, lw=1.2, z=12, ms=8):
    A.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle='-|>',
                                mutation_scale=ms, linewidth=lw,
                                color=color, zorder=z))


def hatch_box(s, x1, y1, x2, y2, step=3.0, color=C):
    """Плотная штриховка прямоугольника без заливки соседних зон."""
    s.hatch(x1, y1, x2, y2, step=step)


def route_box(A, x, y, w, h, label, number=None):
    A.add_patch(Rectangle((x, y), w, h, fc=BLUE_LIGHT, ec=BLUE,
                          lw=S_THIN, zorder=5))
    T(A, x+w/2, y+h/2, label, size=5.8, ha='center', color=BLUE,
      weight='bold', z=7)
    if number is not None:
        A.add_patch(Circle((x+4, y+h-4), 3, fc='white', ec=BLUE,
                           lw=S_THIN, zorder=8))
        T(A, x+4, y+h-4, str(number), size=5.2, ha='center', color=BLUE,
          weight='bold', z=9)


def station_detail_sheet():
    s = Sheet('A1', title='Передняя и задняя рамы.\nПодшипниковый узел и транспортная трасса',
              material='Сталь 18Ni(300)', scale='см. виды',
              number='ММОСО.01.800 СБ', mass='см. спецификацию',
              sheet_no='8', sheets='8', lit='П', date='10.09.2026')
    A = s.ax

    # Заголовок поля — оставляем чистый инженерный лист, без декоративного фона.
    T(A, 34, 572, 'ММОСО\'Н — ЛИСТ 8. УЗЛЫ СТАНЦИИ И ТРАНСПОРТНАЯ ТРАССА',
      size=11, weight='bold')
    T(A, 34, 563, 'Главный вид — продольный разрез одного цилиндра; остальные виды — увеличенные узлы. '
      'Второй цилиндр геометрически независим и имеет аналогичный комплект узлов.', size=6.8)
    L(A, 34, 556, 806, 556, 'thin', color='#777777')

    # =====================================================================
    # А. ПРОДОЛЬНЫЙ СБОРОЧНЫЙ ВИД ОДНОГО ЦИЛИНДРА
    # =====================================================================
    ax, ay0 = 55, 365
    aw, ah = 750, 175
    T(A, ax, ay0+ah-10, 'А. ПРОДОЛЬНЫЙ СБОРОЧНЫЙ ВИД — ЦИЛИНДР, РАМЫ И ТРАССА ДОСТУПА',
      size=8.4, weight='bold')
    T(A, ax, ay0+ah-20, 'условный масштаб по длине; размерные значения — натуральные',
      size=6.2, style='italic')

    # Геометрия вида. Цилиндр: передний торец x=250, задний x=620.
    shell_x0, shell_x1 = 230, 615
    cy = 420
    r = 34
    # передняя и задняя оболочки (гладкая внешняя линия; секция оболочки заштрихована)
    A.add_patch(Rectangle((shell_x0, cy-r), shell_x1-shell_x0, 2*r,
                          fill=False, ec=C, lw=S_MAIN, zorder=2))
    A.add_patch(Arc((shell_x0, cy), 2*r, 2*r, theta1=90, theta2=270,
                    ec=C, lw=S_MAIN, zorder=2))
    A.add_patch(Arc((shell_x1, cy), 2*r, 2*r, theta1=-90, theta2=90,
                    ec=C, lw=S_MAIN, zorder=2))
    # внутренняя жилая поверхность и силовой пакет
    L(A, shell_x0+5, cy-r+5, shell_x1-5, cy-r+5, 'thin')
    L(A, shell_x0+5, cy+r-5, shell_x1-5, cy+r-5, 'thin')
    L(A, shell_x0+7, cy-r+9, shell_x0+7, cy+r-9, 'hidden', color='#555555')
    L(A, shell_x1-7, cy-r+9, shell_x1-7, cy+r-9, 'hidden', color='#555555')
    T(A, 420, cy+16, 'гладкая силовая оболочка Ø10 000', size=6.8, ha='center')
    T(A, 420, cy-17, 'жилая поверхность / внутренний объём', size=6.3, ha='center', color='#555555')
    # Штриховка только торцевого сечения оболочки
    A.add_patch(Rectangle((shell_x0, cy-r), 8, 2*r, fc=PALE, ec=C, lw=S_THIN, zorder=4))
    hatch_box(s, shell_x0+1, cy-r+1, shell_x0+7, cy+r-1, step=2.2)
    A.add_patch(Rectangle((shell_x1-8, cy-r), 8, 2*r, fc=PALE, ec=C, lw=S_THIN, zorder=4))
    hatch_box(s, shell_x1-7, cy-r+1, shell_x1-1, cy+r-1, step=2.2)

    # Передняя неподвижная рама: причал + шлюзы + подшипниковый/гермопереходный узел.
    fx = 84
    A.add_patch(Rectangle((fx-9, cy-52), 18, 104, fc=GRAPH, ec=C, lw=S_MAIN, zorder=4))
    T(A, fx, cy+57, 'ПЕРЕДНЯЯ', size=6.2, ha='center', weight='bold')
    T(A, fx, cy+49, 'НЕПОДВИЖНАЯ РАМА', size=5.5, ha='center')
    # причальный модуль снаружи
    A.add_patch(Rectangle((42, cy-18), 30, 36, fc='white', ec=C, lw=S_MAIN, zorder=5))
    T(A, 57, cy, 'П', size=11, ha='center', weight='bold')
    L(A, 72, cy, fx-9, cy, 'main')
    T(A, 57, cy-25, 'неподвижный\nпричал', size=5.8, ha='center')
    # две независимые трассы — два параллельных шлюзовых канала
    for off, n in [(11, 1), (-11, 2)]:
        route_box(A, 92, cy+off-5, 27, 10, 'Ш/К', n)
        route_box(A, 123, cy+off-5, 27, 10, 'ГП', None)
        L(A, 72, cy+off, 92, cy+off, 'thin', color=BLUE, lw=1.4)
        L(A, 119, cy+off, 123, cy+off, 'thin', color=BLUE, lw=1.4)
        # вращающийся гермопереход и полый вал
        L(A, 150, cy+off, 190, cy+off, 'main', color=BLUE, lw=2.2)
        arrow(A, 165, cy+off, 185, cy+off, BLUE, 1.0, ms=7)
    T(A, 105, cy-42, 'Ш/К — шлюзы и карантин', size=5.6, ha='center', color=BLUE)
    T(A, 136, cy-51, 'ГП — вращающийся\nгермопереход', size=5.6, ha='center', color=BLUE)
    T(A, 183, cy-42, 'полый осевой вал', size=5.8, ha='center', color=BLUE)
    # Bearing at front end, shown as ring around shaft.
    A.add_patch(Circle((205, cy), 13, fc='white', ec=C, lw=S_MAIN, zorder=5))
    A.add_patch(Circle((205, cy), 8, fc='none', ec=C, lw=S_THIN, zorder=6))
    T(A, 205, cy+19, 'активная\nрадиально-осевая опора', size=5.5, ha='center')
    # Two inclined shafts in front hemisphere
    for off in (-10, 10):
        L(A, 218, cy+off, 248, cy+off*2.15, 'main', color=BLUE, lw=2.0)
        arrow(A, 225, cy+off, 242, cy+off*1.9, BLUE, 1.0, ms=7)
    T(A, 252, cy+48, '2 наклонные транспортные шахты\nв передней полусфере', size=5.7,
      ha='center', color=BLUE)
    T(A, 252, cy-49, 'маршрут пассажира / груза\nзаканчивается на жилой поверхности', size=5.5,
      ha='center', color=BLUE)
    # Rear bearing and fixed rear frame. Passenger paths do not cross here.
    rx = 650
    A.add_patch(Circle((shell_x1, cy), 7, fc='white', ec=C, lw=S_MAIN, zorder=5))
    L(A, shell_x1, cy, rx-10, cy, 'main')
    A.add_patch(Rectangle((rx-9, cy-52), 18, 104, fc=GRAPH, ec=C, lw=S_MAIN, zorder=4))
    T(A, rx, cy+57, 'ЗАДНЯЯ', size=6.2, ha='center', weight='bold')
    T(A, rx, cy+49, 'НЕПОДВИЖНАЯ РАМА', size=5.5, ha='center')
    # motor-generator pod on rear frame
    A.add_patch(Ellipse((rx+22, cy), 25, 20, fc='white', ec=C, lw=S_MAIN, zorder=5))
    T(A, rx+22, cy, 'МГ', size=6.6, ha='center', weight='bold')
    A.add_patch(Rectangle((rx+35, cy-4), 28, 8, fc='white', ec=C, lw=S_THIN, zorder=5))
    T(A, rx+49, cy-12, 'тяговый модуль', size=5.5, ha='center')
    # 3 antennas, compact radiators, limited blue solar wings
    for i, yy in enumerate((cy+29, cy, cy-29), start=1):
        L(A, rx, yy, rx+34, yy+8, 'thin')
        A.add_patch(Ellipse((rx+38, yy+9), 10, 5, fc='white', ec=C, lw=S_THIN))
        T(A, rx+38, yy+17, f'А{i}', size=5.1, ha='center')
    for yy in (cy+38, cy-38):
        A.add_patch(Rectangle((rx-27, yy-5), 9, 10, fc=RED_LIGHT, ec=RED, lw=S_THIN))
    for yy in (cy+24, cy-24):
        A.add_patch(Rectangle((rx+10, yy-9), 8, 18, fc=BLUE_LIGHT, ec=BLUE, lw=S_THIN))
        for xx in (rx+12, rx+15): L(A, xx, yy-8, xx, yy+8, 'thin', color=BLUE)
    # no rear passenger path, service route only
    L(A, shell_x1+7, cy-18, rx-10, cy-18, 'hidden', color='#555555')
    T(A, rx+18, cy-31, 'транспортный пассажирский путь\nсюда не продолжается', size=5.5,
      ha='center', color='#555555')

    # Main view dimensions and explanatory notes
    s.dim_h(shell_x0, shell_x1, cy-r-18, '40 000', ext_from=cy-r)
    s.dim_h(42, rx+9, cy+r+17, '49 000', ext_from=cy+r)
    s.dim_v(cy-r, cy+r, shell_x0-18, 'Ø10 000', ext_from=shell_x0)
    s.dim_h(42, 72, cy-65, 'причал', ext_from=cy-18)
    T(A, 410, ay0+9, 'Синие линии — герметичная транспортная трасса. Чёрные линии — конструкция. '
      'Красные элементы — только радиаторы.', size=6.4)

    # =====================================================================
    # Б. ПЕРЕДНЯЯ РАМА — ФРОНТАЛЬНЫЙ ВИД
    # =====================================================================
    bx, by = 128, 173
    T(A, bx, 295, 'Б. ПЕРЕДНЯЯ НЕПОДВИЖНАЯ РАМА — ВИД СО СТОРОНЫ ПРИЧАЛА',
      size=8.2, weight='bold')
    T(A, bx, 285, 'два цилиндра независимы; в каждом — два отдельных коридора доступа', size=6.0)
    # frame plane around two cylinder endcaps
    fx2 = bx+30
    top_y, bot_y = by+44, by-44
    L(A, fx2, bot_y-31, fx2, top_y+31, 'main')
    L(A, fx2+6, bot_y-31, fx2+6, top_y+31, 'thin')
    for yy, lab in ((top_y, 'ЦИЛИНДР 1'), (bot_y, 'ЦИЛИНДР 2')):
        A.add_patch(Circle((fx2, yy), 27, fill=False, ec=C, lw=S_MAIN))
        A.add_patch(Circle((fx2, yy), 6, fill=False, ec=C, lw=S_THIN))
        A.add_patch(Circle((fx2, yy), 2.5, fc='white', ec=C, lw=S_THIN))
        # two corridors per cylinder, separate from bearing
        for off in (-10, 10):
            route_box(A, fx2+32, yy+off-3.5, 29, 7, 'Ш/К→ВАЛ')
            arrow(A, fx2+10, yy+off, fx2+31, yy+off, BLUE, 1.0, ms=6)
        # front frame radiators/panels
        A.add_patch(Rectangle((fx2-39, yy+15), 7, 18, fc=RED_LIGHT, ec=RED, lw=S_THIN))
        A.add_patch(Rectangle((fx2+13, yy-30), 7, 18, fc=RED_LIGHT, ec=RED, lw=S_THIN))
        A.add_patch(Rectangle((fx2-54, yy-8), 8, 17, fc=BLUE_LIGHT, ec=BLUE, lw=S_THIN))
        for xx in (fx2-52, fx2-49): L(A, xx, yy-7, xx, yy+7, 'thin', color=BLUE)
        T(A, fx2-2, yy-32, lab, size=5.8, ha='center', weight='bold')
    # open gap between cylinders, no bridge/equipment
    L(A, bx-9, bot_y+27, bx-9, top_y-27, 'axis', color='#777777')
    T(A, bx-4, by, 'свободный зазор\n11 км между оболочками', size=5.8, ha='right', color='#555555')
    s.dim_v(bot_y+27, top_y-27, bx+120, '21 000 между осями', ext_from=fx2+27)
    T(A, bx+30, by-83, 'Рама неподвижна. Подшипник в центре каждого торцевого узла. '
      'Оборудование не закреплено на цилиндрической оболочке.', size=5.8, ha='center')

    # =====================================================================
    # В. ПОДШИПНИКОВЫЙ УЗЕЛ — ОСЕВОЙ РАЗРЕЗ
    # =====================================================================
    cx, cy2 = 382, 183
    T(A, cx, 295, 'В. ПОДШИПНИКОВЫЙ УЗЕЛ — ОСЕВОЙ РАЗРЕЗ', size=8.2, weight='bold')
    T(A, cx, 285, 'вращающийся ротор справа; статор, питание и ловитель закреплены на раме', size=6.0)
    # frame / stator housing
    A.add_patch(Rectangle((cx-95, cy2-39), 35, 78, fc=PALE, ec=C, lw=S_MAIN))
    hatch_box(s, cx-94, cy2-38, cx-61, cy2+38, step=3)
    T(A, cx-78, cy2+49, 'неподвижная рама', size=5.8, ha='center')
    # motor-generator
    A.add_patch(Ellipse((cx-36, cy2), 25, 52, fc='white', ec=C, lw=S_MAIN))
    T(A, cx-36, cy2, 'МГ', size=7, ha='center', weight='bold')
    # bearing housing and active magnetic pads
    A.add_patch(Rectangle((cx-8, cy2-45), 32, 90, fc='white', ec=C, lw=S_MAIN))
    for yy in (cy2-22, cy2+22):
        A.add_patch(Rectangle((cx-4, yy-5), 24, 10, fc=BLUE_LIGHT, ec=BLUE, lw=S_THIN))
        T(A, cx+8, yy, 'АМП', size=4.8, ha='center', color=BLUE, weight='bold')
    # radial-axial bearing ring
    A.add_patch(Circle((cx+37, cy2), 28, fill=False, ec=C, lw=S_MAIN))
    A.add_patch(Circle((cx+37, cy2), 20, fill=False, ec=C, lw=S_THIN))
    # rotating seal and hollow shaft
    A.add_patch(Rectangle((cx+55, cy2-29), 12, 58, fc=RED_LIGHT, ec=ORANGE, lw=S_MAIN))
    T(A, cx+61, cy2+39, 'вращающийся\nгермопереход', size=5.3, ha='center', color=ORANGE)
    L(A, cx+67, cy2, cx+157, cy2, 'main', color=BLUE, lw=5)
    L(A, cx+67, cy2, cx+157, cy2, 'thin', color=C, lw=1.2)
    # hollow core
    L(A, cx+75, cy2, cx+150, cy2, 'thin', color=BLUE, lw=1.0)
    T(A, cx+111, cy2+16, 'полый осевой вал', size=5.8, ha='center', color=BLUE)
    # emergency catcher
    A.add_patch(Rectangle((cx+22, cy2-53), 40, 5, fc='white', ec=C, lw=S_THIN))
    A.add_patch(Rectangle((cx+22, cy2+48), 40, 5, fc='white', ec=C, lw=S_THIN))
    T(A, cx+42, cy2-61, 'резервный механический ловитель', size=5.2, ha='center')
    # power bus and path arrows
    L(A, cx-78, cy2-45, cx-78, cy2-67, 'main', color=ORANGE, lw=1.3)
    L(A, cx-78, cy2-67, cx+8, cy2-67, 'main', color=ORANGE, lw=1.3)
    T(A, cx-35, cy2-76, 'реакторная шина / 2 ГВт на узлы вращения', size=5.3, ha='center', color=ORANGE)
    arrow(A, cx+75, cy2+7, cx+112, cy2+7, BLUE, 1.0, ms=7)
    s.dim_h(cx-8, cx+24, cy2-88, '400', ext_from=cy2-45)
    s.dim_h(cx+67, cx+157, cy2+65, '9 000', ext_from=cy2)
    T(A, cx+173, cy2+8, 'к шахтам\nцилиндра', size=5.7, color=BLUE)

    # =====================================================================
    # Г. ЦИЛИНДР — ПОПЕРЕЧНЫЙ РАЗРЕЗ И ДВЕ НАКЛОННЫЕ ШАХТЫ
    # =====================================================================
    dx, dy = 570, 183
    T(A, dx, 295, 'Г. ЦИЛИНДР — ПОПЕРЕЧНЫЙ РАЗРЕЗ', size=8.2, weight='bold')
    T(A, dx, 285, 'передняя полусфера; трасса от осевого вала к жилой поверхности', size=6.0)
    A.add_patch(Circle((dx, dy), 58, fill=False, ec=C, lw=S_MAIN))
    A.add_patch(Circle((dx, dy), 51, fill=False, ec=C, lw=S_THIN))
    # shell hatch wedge at top
    A.add_patch(Arc((dx, dy), 116, 116, theta1=20, theta2=160, ec=C, lw=S_MAIN))
    # central hollow axial shaft
    A.add_patch(Circle((dx, dy), 7, fill=False, ec=C, lw=S_MAIN))
    T(A, dx, dy-14, 'полый вал', size=5.7, ha='center', color=BLUE)
    # two inclined shafts and arrival at living surface
    for ang in (48, 132):
        a = math.radians(ang)
        x0 = dx + 8*math.cos(a); y0 = dy + 8*math.sin(a)
        x1 = dx + 44*math.cos(a); y1 = dy + 44*math.sin(a)
        L(A, x0, y0, x1, y1, 'main', color=BLUE, lw=2.2)
        L(A, x0, y0, x1, y1, 'thin', color=C, lw=.8)
        arrow(A, x0+8*math.cos(a), y0+8*math.sin(a), x1-3*math.cos(a), y1-3*math.sin(a), BLUE, 1.0, ms=7)
        A.add_patch(Circle((x1, y1), 3.5, fc='white', ec=BLUE, lw=S_THIN))
    T(A, dx, dy+72, 'две отдельные шахты', size=6, ha='center', color=BLUE, weight='bold')
    T(A, dx, dy+64, 'в передней полусфере', size=5.7, ha='center', color=BLUE)
    T(A, dx, dy-74, 'жилые поверхности / станции прибытия', size=5.5, ha='center', color=BLUE)
    s.dim_v(dy-58, dy+58, dx-72, 'Ø10 000', ext_from=dx-58)
    s.dim_h(dx, dx+58, dy-70, 'R = 5 000', ext_from=dy-58)
    # path legend inside view
    L(A, dx+22, dy-34, dx+42, dy-34, 'main', color=BLUE, lw=2)
    T(A, dx+46, dy-34, 'герметичная трасса', size=5.4, color=BLUE)
    # shell material notation
    T(A, dx+70, dy+22, 'оболочка /\nпакет защиты', size=5.3, color=C)
    L(A, dx+51, dy+28, dx+70, dy+25, 'thin')

    # =====================================================================
    # Д. ЗАДНЯЯ РАМА — ВИД СЗАДИ
    # =====================================================================
    ex, ey = 748, 183
    T(A, ex, 295, 'Д. ЗАДНЯЯ НЕПОДВИЖНАЯ РАМА — ВИД СЗАДИ', size=8.2, weight='bold')
    T(A, ex, 285, 'ровно три антенны; компактные радиаторы; ограниченные солнечные крылья', size=6.0)
    # two bearing/cylinder nodes, vertical arrangement
    for yy in (ey+43, ey-43):
        A.add_patch(Circle((ex, yy), 25, fill=False, ec=C, lw=S_MAIN))
        A.add_patch(Circle((ex, yy), 6, fill=False, ec=C, lw=S_THIN))
        # mechanical catcher and motor-generator
        A.add_patch(Ellipse((ex+37, yy), 18, 12, fc='white', ec=C, lw=S_THIN))
        T(A, ex+37, yy, 'МГ', size=5.2, ha='center', weight='bold')
        # two compact radiators only
        A.add_patch(Rectangle((ex-42, yy+12), 7, 16, fc=RED_LIGHT, ec=RED, lw=S_THIN))
        A.add_patch(Rectangle((ex-42, yy-28), 7, 16, fc=RED_LIGHT, ec=RED, lw=S_THIN))
        # one solar wing each side, blue
        A.add_patch(Rectangle((ex+14, yy+13), 8, 19, fc=BLUE_LIGHT, ec=BLUE, lw=S_THIN))
        A.add_patch(Rectangle((ex+14, yy-32), 8, 19, fc=BLUE_LIGHT, ec=BLUE, lw=S_THIN))
        for xx in (ex+16, ex+19):
            L(A, xx, yy+14, xx, yy+31, 'thin', color=BLUE)
            L(A, xx, yy-31, xx, yy-14, 'thin', color=BLUE)
    # fixed rear frame plane
    L(A, ex, ey-76, ex, ey+76, 'main')
    L(A, ex+5, ey-76, ex+5, ey+76, 'thin')
    # exactly three antennas
    for i, yy in enumerate((ey+68, ey, ey-68), start=1):
        L(A, ex-4, yy, ex-37, yy+12, 'thin')
        A.add_patch(Ellipse((ex-43, yy+14), 13, 6, fill=False, ec=C, lw=S_THIN))
        T(A, ex-43, yy+23, f'А{i}', size=5.1, ha='center')
    # reactor bus and propulsion arrows
    L(A, ex+47, ey-10, ex+47, ey-80, 'main', color=ORANGE, lw=1.2)
    T(A, ex+47, ey-88, 'реакторная\nшина', size=5.3, ha='center', color=ORANGE)
    arrow(A, ex+58, ey-43, ex+84, ey-43, ORANGE, 1.0, ms=7)
    T(A, ex+89, ey-43, 'тяга', size=5.5, color=ORANGE)
    T(A, ex, ey-107, 'Пассажирские трассы сюда не проходят: задняя рама — привод, питание и связь.',
      size=5.7, ha='center')

    # =====================================================================
    # СПЕЦИФИКАЦИЯ И ТЕХНИЧЕСКИЕ ТРЕБОВАНИЯ
    # =====================================================================
    s.spec_table(34, 66, [
        ['1', 'Передняя неподвижная рама', '1', 'ММОСО.01.810'],
        ['2', 'Причальный модуль с шлюзами/карантином', '2', 'на цилиндр'],
        ['3', 'Вращающийся гермопереход', '2', 'на цилиндр'],
        ['4', 'Полый осевой вал', '1', 'L = 9 000'],
        ['5', 'Активный магнитный подшипник', '2', 'на цилиндр'],
        ['6', 'Мотор-генератор', '2', 'на цилиндр'],
        ['7', 'Наклонная транспортная шахта', '2', 'на цилиндр'],
        ['8', 'Задняя неподвижная рама', '1', 'ММОСО.01.820'],
        ['9', 'Антенна направленная', '3', 'ровно три'],
        ['10', 'Радиаторная панель', 'огр.', 'красная маркировка'],
    ], widths=(10, 76, 18, 30), rh=5.4, size=5.7,
      title='СПЕЦИФИКАЦИЯ УЗЛОВ')

    s.note(190, 119,
           'ТЕХНИЧЕСКИЕ ТРЕБОВАНИЯ\n'
           '1. Передняя и задняя рамы неподвижны относительно инерциального пространства.\n'
           '2. Цилиндр вращается на активных магнитных радиально-осевых опорах;\n'
           '   резервный механический ловитель включается только при аварийном режиме.\n'
           '3. В каждом цилиндре два независимых герметичных коридора.\n'
           '4. Каноническая трасса: причал → шлюзы/карантин → вращающийся гермопереход\n'
           '   → полый осевой вал → две наклонные шахты передней полусферы → жилая поверхность.\n'
           '5. Полый вал и гермопереход не являются продольной связью между цилиндрами.\n'
           '6. Межцилиндровый свободный зазор 11 000; в нём нет балок, тоннелей, кабелей\n'
           '   или оборудования. Геометрия станции: межосевое расстояние 21 000.\n'
           '7. Внешнее оборудование размещать только на торцевых неподвижных рамах.\n'
           '8. Цветовая легенда: красный — только радиаторы; синий — солнечные панели\n'
           '   и транспортные трассы; серебристый/графитовый — рамы и силовые узлы.\n'
           '9. Квота узлов вращения, приводов и силовой электроники — 2 ГВт; питание\n'
           '   от реакторной шины на неподвижной раме.\n'
           '10. Схема не масштабна по отдельным узлам; размеры и расчётные значения — в MMOSON_v7.docx.',
           size=5.65)

    # small line legend
    L(A, 555, 114, 578, 114, 'main')
    T(A, 582, 114, 'конструкция', size=5.8)
    L(A, 625, 114, 648, 114, 'main', color=BLUE, lw=2)
    T(A, 652, 114, 'герметичный транспортный путь', size=5.8, color=BLUE)
    A.add_patch(Rectangle((730, 111), 8, 7, fc=RED_LIGHT, ec=RED, lw=S_THIN))
    T(A, 742, 114, 'радиатор', size=5.8, color=RED)

    return s


def build(out_pdf='MMOSON_station_detail.pdf'):
    s = station_detail_sheet()
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    pdf_path = os.path.join(root, out_pdf)
    png_path = os.path.join(root, 'MMOSON_station_detail.png')
    s.fig.savefig(png_path, dpi=220, facecolor='white')
    with PdfPages(pdf_path) as pdf:
        pdf.savefig(s.fig)
        info = pdf.infodict()
        info['Title'] = 'ММОСО\'Н. Передняя и задняя рамы, подшипниковый узел и транспортная трасса'
        info['Author'] = 'Бугаенко Р. С., НИК'
        info['Subject'] = 'Подробный технический чертёж узлов станции'
    plt.close(s.fig)
    return pdf_path, png_path


if __name__ == '__main__':
    print(*build())
