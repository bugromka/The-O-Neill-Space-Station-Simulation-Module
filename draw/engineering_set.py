# -*- coding: utf-8 -*-
"""ММОСО'Н — раздельный комплект инженерных чертежей.

Каждый узел вынесен на отдельный лист A2, чтобы размерные линии,
выноски и транспортные трассы не перекрывали друг друга.
"""
import math
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Rectangle, Circle, Ellipse, Arc, Polygon, FancyArrowPatch
from matplotlib.lines import Line2D

from eskd import Sheet, S_MAIN, S_THIN, C

BLUE = '#135b92'       # транспортная трасса
BLUE_LIGHT = '#d9e9f4'
RED = '#b51e1e'        # только радиаторы
RED_LIGHT = '#f3d9d5'
STEEL = '#b8b8b8'
DARK = '#3d3d3d'
ORANGE = '#9a5700'     # силовая шина / тяга
GREEN = '#27633a'
GREY = '#777777'


def line(A, x1, y1, x2, y2, kind='main', color=C, lw=None, z=3):
    styles = {'main': (S_MAIN, '-'), 'thin': (S_THIN, '-'),
              'axis': (S_THIN, (0, (10, 3, 2, 3))),
              'hidden': (S_THIN, (0, (5, 3)))}
    w, ls = styles[kind]
    A.add_line(Line2D([x1, x2], [y1, y2], color=color, lw=lw or w,
                      ls=ls, zorder=z))


def text(A, x, y, value, size=7, ha='left', va='center', color=C,
         weight=None, style=None, z=20):
    A.text(x, y, value, fontsize=size, ha=ha, va=va, color=color,
           fontweight=weight, fontstyle=style, linespacing=1.22, zorder=z)


def arrow(A, x1, y1, x2, y2, color=BLUE, lw=1.1, ms=8, z=15):
    A.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle='-|>',
                                mutation_scale=ms, linewidth=lw,
                                color=color, zorder=z))


def hatch_rect(s, x1, y1, x2, y2, step=2.5):
    s.hatch(x1, y1, x2, y2, step=step)


def callout(s, x, y, tx, ty, number, label, side='left', size=6.2):
    """Номер позиции в кружке с отдельной выноской."""
    A = s.ax
    line(A, x, y, tx, ty, 'thin')
    A.add_patch(Circle((tx, ty), 4.0, fc='white', ec=C, lw=S_THIN, zorder=25))
    text(A, tx, ty, str(number), size=5.8, ha='center', weight='bold', z=26)
    if side == 'left':
        text(A, tx-7, ty, label, size=size, ha='right', z=25)
    else:
        text(A, tx+7, ty, label, size=size, ha='left', z=25)


def route_channel(A, x1, x2, y, label=None, box=None):
    """Один герметичный транспортный канал: две стенки и стрелка."""
    line(A, x1, y-3.5, x2, y-3.5, 'main', color=BLUE, lw=1.5, z=10)
    line(A, x1, y+3.5, x2, y+3.5, 'main', color=BLUE, lw=1.5, z=10)
    arrow(A, x1+7, y, x2-7, y, BLUE, .9, 7, 12)
    if box:
        bx, bw, name = box
        A.add_patch(Rectangle((bx, y-8), bw, 16, fc=BLUE_LIGHT,
                              ec=BLUE, lw=S_THIN, zorder=11))
        text(A, bx+bw/2, y, name, size=5.3, ha='center', color=BLUE,
             weight='bold', z=13)
    if label:
        text(A, (x1+x2)/2, y+10, label, size=5.4, ha='center', color=BLUE)


def title(s, heading, subtitle):
    A = s.ax
    text(A, 30, 405, heading, size=10, weight='bold')
    text(A, 30, 394, subtitle, size=6.7, style='italic')
    line(A, 30, 387, 565, 387, 'thin', color='#777777')


def sheet1_assembly():
    s = Sheet('A2', title='Станция.\nСборочный вид и кинематическая трасса',
              material='Сталь 18Ni(300)', scale='см. виды',
              number='ММОСО.00.800 ВО', mass='46,70 млрд т',
              sheet_no='1', sheets='5', lit='П', date='10.09.2026')
    A = s.ax
    title(s, 'ЛИСТ 1. СБОРOЧНЫЙ ВИД СТАНЦИИ И ТРАНСПОРТНАЯ ТРАССА',
          'Два цилиндра показаны раздельно. Внешние узлы находятся только на неподвижных торцевых рамах.')

    # Two independent longitudinal views.
    x0, x1 = 170, 455
    ys = (292, 190)
    r = 24
    front_x, rear_x = 105, 520
    for idx, cy in enumerate(ys, start=1):
        # smooth cylindrical envelope with front/rear domes
        A.add_patch(Rectangle((x0, cy-r), x1-x0, 2*r, fill=False,
                              ec=C, lw=S_MAIN, zorder=3))
        A.add_patch(Arc((x0, cy), 2*r, 2*r, theta1=90, theta2=270,
                        ec=C, lw=S_MAIN, zorder=3))
        A.add_patch(Arc((x1, cy), 2*r, 2*r, theta1=-90, theta2=90,
                        ec=C, lw=S_MAIN, zorder=3))
        line(A, x0+5, cy-r+5, x1-5, cy-r+5, 'thin', color=GREY)
        line(A, x0+5, cy+r-5, x1-5, cy+r-5, 'thin', color=GREY)
        text(A, (x0+x1)/2, cy, f'ЦИЛИНДР {idx}', size=6.2, ha='center', weight='bold')
        # front and rear bearing centers
        for xx in (x0, x1):
            A.add_patch(Circle((xx, cy), 6, fill=False, ec=C, lw=S_MAIN))
            A.add_patch(Circle((xx, cy), 2, fill=False, ec=C, lw=S_THIN))
        # route starts at front frame and terminates in front hemisphere
        for off in (-8, 8):
            route_channel(A, front_x+12, x0-10, cy+off,
                          box=(front_x+24, 28, 'Ш/К'))
            line(A, x0-10, cy+off, x0+5, cy+off*1.65, 'main', color=BLUE, lw=1.5)
            arrow(A, x0-4, cy+off, x0+3, cy+off*1.48, BLUE, .9, 7)
        # labels sit in dedicated space above/below each cylinder
        text(A, 294, cy+r+10, 'гладкая оболочка · L цилиндрической части = 40 000',
             size=5.7, ha='center')
        text(A, 294, cy-r-11, 'две независимые пассажирские/грузовые трассы',
             size=5.4, ha='center', color=BLUE)

    # Fixed front and rear frames drawn as planes, not a longitudinal truss.
    for cy in ys:
        A.add_patch(Rectangle((front_x-7, cy-34), 14, 68, fc=DARK, ec=C, lw=S_MAIN))
        A.add_patch(Rectangle((rear_x-7, cy-34), 14, 68, fc=DARK, ec=C, lw=S_MAIN))
    text(A, front_x, 333, 'ПЕРЕДНЯЯ\nНЕПОДВИЖНАЯ РАМА', size=6.0, ha='center', weight='bold')
    text(A, rear_x, 333, 'ЗАДНЯЯ\nНЕПОДВИЖНАЯ РАМА', size=6.0, ha='center', weight='bold')
    # show empty inter-cylinder gap with dimension, no connecting line
    text(A, 305, 241, 'СВОБОДНЫЙ ЗАЗОР 11 000\nнет балок, тоннелей, кабелей или оборудования',
         size=6.3, ha='center', color=GREY, weight='bold')
    s.dim_v(ys[1]+r, ys[0]-r, 470, '11 000', ext_from=455)
    s.dim_v(ys[1], ys[0], 492, '21 000 оси', ext_from=455)
    s.dim_h(x0, x1, 145, '40 000', ext_from=ys[1]-r)
    s.dim_h(front_x, rear_x, 355, '49 000 общая длина', ext_from=ys[0]+r)

    # enlarged transport chain at the bottom, spaced like a process diagram
    text(A, 44, 118, 'Кинематическая последовательность для каждого цилиндра', size=7.5, weight='bold')
    chain = [('1', 'ПРИЧАЛ'), ('2', 'ШЛЮЗЫ /\nКАРАНТИН'), ('3', 'ВРАЩАЮЩИЙСЯ\nГЕРМОПЕРЕХОД'),
             ('4', 'ПОЛЫЙ\nОСЕВОЙ ВАЛ'), ('5', '2 НАКЛОННЫЕ\nШАХТЫ'), ('6', 'ЖИЛАЯ\nПОВЕРХНОСТЬ')]
    xx = 55
    widths = [56, 68, 84, 66, 76, 72]
    for i, (n, lab) in enumerate(chain):
        w = widths[i]
        A.add_patch(Rectangle((xx, 82), w, 25, fc=BLUE_LIGHT, ec=BLUE, lw=S_THIN))
        A.add_patch(Circle((xx+7, 100), 4, fc='white', ec=BLUE, lw=S_THIN))
        text(A, xx+7, 100, n, size=5, ha='center', color=BLUE, weight='bold')
        text(A, xx+w/2, 94.5, lab, size=5.7, ha='center', color=BLUE, weight='bold')
        if i < len(chain)-1:
            arrow(A, xx+w+3, 94.5, xx+w+widths[i+1]-3, 94.5, BLUE, .9, 7)
        xx += w + 13
    text(A, 44, 70, 'Трасса герметична по всей длине; задняя рама не является пассажирским входом.',
         size=6.2, color=BLUE)
    return s


def sheet2_front_frame():
    s = Sheet('A2', title='Передняя рама.\nПричальный и шлюзовой узел',
              material='Сталь 18Ni(300)', scale='см. виды',
              number='ММОСО.01.810 СБ', mass='см. спецификацию',
              sheet_no='2', sheets='5', lit='П', date='10.09.2026')
    A = s.ax
    title(s, 'ЛИСТ 2. ПЕРЕДНЯЯ НЕПОДВИЖНАЯ РАМА И ДВА ВХОДНЫХ КОРИДОРА',
          'Главный вид — со стороны причала. Справа вынесен один коридор в увеличенном разрезе.')

    # Main front view, left field.
    cx, cy = 160, 245
    top_y, bot_y = cy+66, cy-66
    # frame plane and two endcaps
    line(A, cx, bot_y-48, cx, top_y+48, 'main')
    line(A, cx+7, bot_y-48, cx+7, top_y+48, 'thin')
    for i, yy in enumerate((top_y, bot_y), start=1):
        A.add_patch(Circle((cx, yy), 42, fill=False, ec=C, lw=S_MAIN))
        A.add_patch(Circle((cx, yy), 9, fill=False, ec=C, lw=S_MAIN))
        A.add_patch(Circle((cx, yy), 3.2, fill=False, ec=C, lw=S_THIN))
        text(A, cx, yy-55, f'ЦИЛИНДР {i}', size=6.5, ha='center', weight='bold')
        # two separate corridors leaving frame toward right
        for off in (-16, 16):
            route_channel(A, cx+48, cx+135, yy+off, box=(cx+69, 43, 'ШЛЮЗ / КАРАНТИН'))
            line(A, cx+48, yy+off, cx+42, yy+off, 'thin', color=BLUE, lw=1.2)
        # radiator and solar wing symbols on the fixed frame
        A.add_patch(Rectangle((cx-60, yy+22), 9, 22, fc=RED_LIGHT, ec=RED, lw=S_THIN))
        A.add_patch(Rectangle((cx+20, yy-44), 9, 22, fc=RED_LIGHT, ec=RED, lw=S_THIN))
        A.add_patch(Rectangle((cx-74, yy-8), 9, 22, fc=BLUE_LIGHT, ec=BLUE, lw=S_THIN))
        for xx in (cx-72, cx-69): line(A, xx, yy-7, xx, yy+13, 'thin', color=BLUE)
    # no equipment in gap
    text(A, 64, cy, 'ПУСТОЙ\nЗАЗОР\n11 000', size=6.2, ha='center', color=GREY, weight='bold')
    line(A, 84, bot_y+42, 84, top_y-42, 'axis', color=GREY)
    s.dim_v(bot_y+42, top_y-42, 235, '11 000 светлый', ext_from=cx+42)
    s.dim_v(bot_y, top_y, 255, '21 000 между осями', ext_from=cx+42)
    s.dim_h(cx, cx+42, bot_y-72, 'R = 5 000', ext_from=bot_y-42)
    callout(s, cx+9, top_y, 38, top_y+42, 1, 'ось и активный\nмагнитный подшипник', side='left')
    callout(s, cx+42, top_y+16, 285, top_y+50, 2, 'два коридора\nдоступа', side='right')
    callout(s, cx, bot_y-42, 36, bot_y-68, 3, 'плоскость\nнеподвижной рамы', side='left')

    # Enlarged side section of one route on right.
    x = 300
    text(A, x+125, 337, 'Увеличенный продольный разрез одного коридора', size=7.5, ha='center', weight='bold')
    text(A, x+125, 326, 'не в масштабе; стрелки показывают движение от причала к цилиндру', size=5.9, ha='center', style='italic')
    y = 245
    # fixed dock
    A.add_patch(Rectangle((x, y-23), 27, 46, fill=False, ec=C, lw=S_MAIN))
    text(A, x+13.5, y, 'П', size=11, ha='center', weight='bold')
    # airlock modules
    route_channel(A, x+35, x+77, y, box=(x+37, 25, 'ШЛЮЗ'))
    route_channel(A, x+84, x+126, y, box=(x+86, 34, 'КАРАНТИН'))
    # rotating seal
    A.add_patch(Rectangle((x+134, y-28), 10, 56, fc=RED_LIGHT, ec=ORANGE, lw=S_MAIN))
    text(A, x+139, y+40, 'вращающийся\nгермопереход', size=5.1, ha='center', color=ORANGE)
    arrow(A, x+126, y, x+132, y, BLUE, .8, 6)
    # hollow shaft and entry to front hemisphere
    route_channel(A, x+150, x+210, y, box=None)
    text(A, x+180, y+13, 'полый вал', size=5.7, ha='center', color=BLUE)
    A.add_patch(Circle((x+226, y), 20, fill=False, ec=C, lw=S_MAIN))
    text(A, x+226, y+31, 'опора', size=5.5, ha='center')
    for off in (-8, 8):
        line(A, x+230, y+off, x+255, y+off*2.3, 'main', color=BLUE, lw=1.6)
        arrow(A, x+235, y+off, x+251, y+off*2.0, BLUE, .8, 6)
    text(A, x+260, y+37, '2 наклонные шахты\nк жилой поверхности', size=5.3, ha='center', color=BLUE)
    text(A, x+260, y-37, 'гермодвери\nсекционный контур', size=5.3, ha='center')
    line(A, x, y-60, x+250, y-60, 'thin', color=GREY)
    text(A, x+125, y-72, 'Путь доступа герметичен на всём протяжении', size=6.1, ha='center', color=BLUE, weight='bold')
    # notes in dedicated right lower block
    s.note(x, 118,
           'СОСТАВ УЗЛА\n'
           '1. Неподвижная рама воспринимает статические и тяговые нагрузки.\n'
           '2. На каждый цилиндр предусмотрены два независимых коридора.\n'
           '3. Шлюзы и карантин расположены до вращающегося гермоперехода.\n'
           '4. Вращающийся переход передаёт герметичность от статора к ротору.\n'
           '5. В межцилиндровом зазоре отсутствуют переходы и коммуникации.', size=6.1)
    s.spec_table(34, 70, [
        ['1', 'Передняя неподвижная рама', '1', 'статор'],
        ['2', 'Причальный модуль', '2', 'на цилиндр'],
        ['3', 'Шлюзовая камера', '2', 'на коридор'],
        ['4', 'Карантинная камера', '2', 'на коридор'],
        ['5', 'Вращающийся гермопереход', '2', 'на цилиндр'],
        ['6', 'Коридор доступа', '4', '2 на цилиндр'],
    ], widths=(10, 72, 18, 32), rh=5.4, size=5.8, title='СПЕЦИФИКАЦИЯ')
    return s


def sheet3_bearing():
    s = Sheet('A2', title='Подшипниковый узел.\nОсевая опора и гермопереход',
              material='Сталь 18Ni(300) / YBCO', scale='см. виды',
              number='ММОСО.01.830 СБ', mass='—', sheet_no='3', sheets='5',
              lit='П', date='10.09.2026')
    A = s.ax
    title(s, 'ЛИСТ 3. ПОДШИПНИКОВЫЙ УЗЕЛ — ОСЕВОЙ РАЗРЕЗ И СХЕМА НАГРУЗОК',
          'Статор закреплён на неподвижной раме; ротор, вал и цилиндр вращаются независимо.')
    y = 245
    # components from left to right, with generous spacing
    # fixed frame
    A.add_patch(Rectangle((50, y-58), 42, 116, fc='#eeeeee', ec=C, lw=S_MAIN))
    hatch_rect(s, 52, y-56, 90, y+56, step=3)
    text(A, 71, y+70, 'рама', size=6.7, ha='center', weight='bold')
    # motor generator
    A.add_patch(Ellipse((130, y), 44, 72, fill=False, ec=C, lw=S_MAIN))
    text(A, 130, y, 'МГ', size=10, ha='center', weight='bold')
    text(A, 130, y-48, 'мотор-генератор\nраскрутка / торможение', size=5.8, ha='center')
    # magnetic housing with radial and axial pads
    A.add_patch(Rectangle((170, y-68), 64, 136, fill=False, ec=C, lw=S_MAIN))
    for yy in (y-32, y+32):
        A.add_patch(Rectangle((178, yy-8), 30, 16, fc=BLUE_LIGHT, ec=BLUE, lw=S_THIN))
        text(A, 193, yy, 'АМП', size=5.2, ha='center', color=BLUE, weight='bold')
    A.add_patch(Rectangle((205, y-55), 20, 10, fc=BLUE_LIGHT, ec=BLUE, lw=S_THIN))
    A.add_patch(Rectangle((205, y+45), 20, 10, fc=BLUE_LIGHT, ec=BLUE, lw=S_THIN))
    text(A, 202, y+82, 'активные магнитные\nрадиально-осевые опоры', size=6.0, ha='center', color=BLUE)
    # catcher
    line(A, 164, y-76, 246, y-76, 'main')
    line(A, 164, y+76, 246, y+76, 'main')
    text(A, 205, y-90, 'резервный механический ловитель', size=5.9, ha='center')
    # rotating ring and seal
    A.add_patch(Circle((270, y), 39, fill=False, ec=C, lw=S_MAIN))
    A.add_patch(Circle((270, y), 27, fill=False, ec=C, lw=S_THIN))
    text(A, 270, y+53, 'вращающийся ротор', size=6.3, ha='center', weight='bold')
    A.add_patch(Rectangle((302, y-42), 18, 84, fc=RED_LIGHT, ec=ORANGE, lw=S_MAIN))
    text(A, 311, y+58, 'гермопереход', size=6.0, ha='center', color=ORANGE)
    # hollow axial shaft
    line(A, 320, y-9, 500, y-9, 'main', color=BLUE, lw=2.0)
    line(A, 320, y+9, 500, y+9, 'main', color=BLUE, lw=2.0)
    line(A, 320, y, 500, y, 'thin', color=C, lw=.9)
    arrow(A, 355, y, 410, y, BLUE, 1.0, 8)
    text(A, 410, y+22, 'полый осевой вал L = 9 000', size=6.5, ha='center', color=BLUE)
    # load directions and power
    arrow(A, 126, y+101, 126, y+77, ORANGE, 1.0, 8)
    text(A, 126, y+111, 'реакторная шина', size=6.0, ha='center', color=ORANGE)
    arrow(A, 130, y-112, 170, y-112, ORANGE, 1.0, 8)
    text(A, 186, y-112, 'управление АМП', size=5.9, color=ORANGE)
    arrow(A, 450, y-45, 500, y-45, GREEN, 1.0, 8)
    text(A, 475, y-58, 'тяга / момент через вал', size=5.8, ha='center', color=GREEN)
    # dimensions and callouts
    s.dim_h(170, 234, y-100, '400 корпус опоры', ext_from=y-68)
    s.dim_h(320, 500, y+78, '9 000', ext_from=y+9)
    s.dim_v(y-68, y+68, 158, 'узел 1 600', ext_from=170)
    callout(s, 190, y+32, 245, y+112, 1, 'магнитный\nрадиальный контур', side='right')
    callout(s, 216, y+51, 250, y+145, 2, 'магнитный\nосевой контур', side='right')
    callout(s, 311, y+42, 346, y+125, 3, 'вращающееся\nгермоуплотнение', side='right')
    callout(s, 430, y+9, 448, y+143, 4, 'внутренний\nпроход людей/груза', side='right')

    # Separate load/logic diagram at bottom, no overlap with main section.
    text(A, 42, 137, 'Принцип работы узла', size=7.6, weight='bold')
    blocks = [(52, 'рама /\nстатор'), (142, 'МГ'), (218, 'АМП'), (294, 'ротор'), (370, 'вал'), (446, 'цилиндр')]
    for i, (xx, lab) in enumerate(blocks):
        A.add_patch(Rectangle((xx, 96), 56, 25, fill=False, ec=C, lw=S_THIN))
        text(A, xx+28, 108.5, lab, size=5.9, ha='center')
        if i < len(blocks)-1:
            arrow(A, xx+59, 108.5, blocks[i+1][0]-3, 108.5, BLUE, .9, 7)
    text(A, 52, 82, 'Путь энергии: реакторная шина → статор АМП / МГ.\nПуть момента: МГ → ротор → цапфа → цилиндр.', size=6.0)
    s.note(300, 124,
           'РАСЧЁТНЫЕ ДАННЫЕ\n'
           '• активные магнитные подшипники: 4 торцевых узла станции;\n'
           '• предварительная квота узлов вращения и силовой электроники: 2 ГВт;\n'
           '• статор и силовая электроника размещены на неподвижных рамах;\n'
           '• при отказе магнитного контура нагрузку принимает механический ловитель;\n'
           '• гермопереход не передаёт вращение на причальную раму;\n'
           '• транспортная трасса проходит внутри полого вала, не через зазор между цилиндрами.', size=6.1)
    s.spec_table(34, 69, [
        ['1', 'Корпус активной магнитной опоры', '2', 'на цилиндр'],
        ['2', 'Мотор-генератор', '1', 'на узел'],
        ['3', 'Роторное гермоуплотнение', '1', 'на канал'],
        ['4', 'Полый осевой вал', '1', 'L = 9 000'],
        ['5', 'Механический ловитель', '2', 'верх/низ'],
    ], widths=(10, 80, 18, 28), rh=5.4, size=5.8, title='СПЕЦИФИКАЦИЯ')
    return s


def sheet4_cylinder():
    s = Sheet('A2', title='Цилиндр.\nПередняя полусфера и транспортные шахты',
              material='Сталь 18Ni(300)', scale='см. виды',
              number='ММОСО.01.840 СБ', mass='—', sheet_no='4', sheets='5',
              lit='П', date='10.09.2026')
    A = s.ax
    title(s, 'ЛИСТ 4. ЦИЛИНДР — ПРОДОЛЬНЫЙ РАЗРЕЗ ПЕРЕДНЕЙ ПОЛУСФЕРЫ',
          'Показана инженерная трасса от полого осевого вала к двум наклонным шахтам и жилой поверхности.')

    # longitudinal section: left axis, dome, cylindrical part right
    ax, cy = 110, 245
    dome_r = 92
    body_x = 202
    body_end = 415
    # outer/inner shell contours
    A.add_patch(Arc((body_x, cy), 2*dome_r, 2*dome_r, theta1=90, theta2=270,
                    ec=C, lw=S_MAIN))
    line(A, body_x, cy-dome_r, body_end, cy-dome_r, 'main')
    line(A, body_x, cy+dome_r, body_end, cy+dome_r, 'main')
    # The view stops at the cylindrical body; the rear dome is intentionally omitted.
    # This keeps the front-hemisphere section separate from the transverse inset.
    # shell thickness at front dome in section
    A.add_patch(Arc((body_x, cy), 2*(dome_r-7), 2*(dome_r-7), theta1=90, theta2=270,
                    ec=C, lw=S_THIN))
    # local hatch between arcs, limited to left quadrant
    for ang in range(95, 266, 10):
        a = math.radians(ang)
        x1 = body_x + (dome_r-2)*math.cos(a)
        y1 = cy + (dome_r-2)*math.sin(a)
        x2 = body_x + (dome_r-7)*math.cos(a)
        y2 = cy + (dome_r-7)*math.sin(a)
        line(A, x1, y1, x2, y2, 'thin')
    # axial hollow shaft from left
    line(A, ax, cy-8, body_x, cy-8, 'main', color=BLUE, lw=2)
    line(A, ax, cy+8, body_x, cy+8, 'main', color=BLUE, lw=2)
    arrow(A, ax+10, cy, body_x-12, cy, BLUE, 1.0, 8)
    text(A, 150, cy+19, 'полый осевой вал', size=6.4, ha='center', color=BLUE)
    # bulkhead and hub
    A.add_patch(Circle((body_x, cy), 11, fill=False, ec=C, lw=S_MAIN))
    text(A, body_x, cy-19, 'узел распределения', size=5.8, ha='center')
    # two inclined shafts, separated vertically
    shaft_ends = []
    for sign in (-1, 1):
        x_start, y_start = body_x+9, cy+sign*9
        x_end, y_end = body_x+68, cy+sign*58
        # channel pair
        dx = x_end-x_start; dy = y_end-y_start
        norm = math.hypot(dx,dy)
        nx, ny = -dy/norm*3, dx/norm*3
        line(A, x_start+nx, y_start+ny, x_end+nx, y_end+ny, 'main', color=BLUE, lw=1.8)
        line(A, x_start-nx, y_start-ny, x_end-nx, y_end-ny, 'main', color=BLUE, lw=1.8)
        arrow(A, x_start+dx*.35, y_start+dy*.35, x_start+dx*.7, y_start+dy*.7, BLUE, .9, 7)
        A.add_patch(Circle((x_end, y_end), 4, fill=False, ec=BLUE, lw=S_THIN))
        shaft_ends.append((x_end, y_end))
    text(A, 286, cy+78, 'ШАХТА 1', size=6.0, color=BLUE, weight='bold')
    text(A, 286, cy-78, 'ШАХТА 2', size=6.0, color=BLUE, weight='bold')
    text(A, 280, cy+66, 'гермодвери + тормозной шлюз', size=5.6, color=BLUE)
    text(A, 280, cy-66, 'гермодвери + тормозной шлюз', size=5.6, color=BLUE)
    # living surface: internal thin line and station endpoint
    line(A, body_x+78, cy-dome_r+10, body_end-8, cy-dome_r+10, 'thin', color=GREY)
    line(A, body_x+78, cy+dome_r-10, body_end-8, cy+dome_r-10, 'thin', color=GREY)
    text(A, 404, cy-71, 'жилая поверхность', size=6.2, ha='center', color=BLUE)
    text(A, 404, cy+71, 'внутренний объём', size=6.2, ha='center', color=GREY)
    # Dimensions
    s.dim_v(cy-dome_r, cy+dome_r, 65, 'Ø10 000', ext_from=body_x)
    s.dim_h(body_x, body_x+68, cy-112, '5 000 до обода', ext_from=cy-dome_r)
    s.dim_h(body_x, body_end, cy+dome_r+23, 'цилиндрическая часть 40 000', ext_from=cy+dome_r)
    callout(s, body_x, cy+dome_r-3, 42, 346, 1, 'силовая оболочка\nи защитный пакет', side='left')
    callout(s, body_x+52, cy+48, 365, 354, 2, 'наклонная\nшахта 1', side='right')
    callout(s, body_x+52, cy-48, 365, 135, 3, 'наклонная\nшахта 2', side='right')

    # transverse section as separate right view
    cx, cy2 = 495, 210
    text(A, cx, 340, 'Поперечный разрез цилиндра', size=7.7, ha='center', weight='bold')
    text(A, cx, 330, 'вид со стороны передней полусферы', size=5.9, ha='center', style='italic')
    A.add_patch(Circle((cx, cy2), 60, fill=False, ec=C, lw=S_MAIN))
    A.add_patch(Circle((cx, cy2), 53, fill=False, ec=C, lw=S_THIN))
    line(A, cx-70, cy2, cx+70, cy2, 'axis', color=GREY)
    line(A, cx, cy2-70, cx, cy2+70, 'axis', color=GREY)
    A.add_patch(Circle((cx, cy2), 7, fill=False, ec=C, lw=S_MAIN))
    for sign in (-1,1):
        ang = math.radians(38*sign)
        x0 = cx + 9*math.cos(ang); y0 = cy2 + 9*math.sin(ang)
        x1 = cx + 47*math.cos(ang); y1 = cy2 + 47*math.sin(ang)
        line(A, x0, y0, x1, y1, 'main', color=BLUE, lw=2)
        arrow(A, x0+8*math.cos(ang), y0+8*math.sin(ang), x1-4*math.cos(ang), y1-4*math.sin(ang), BLUE, .9, 7)
    text(A, cx, cy2+82, 'две независимые шахты', size=6.0, ha='center', color=BLUE, weight='bold')
    text(A, cx, cy2-83, 'ось / полый вал', size=5.9, ha='center')
    s.dim_v(cy2-60, cy2+60, cx-76, 'Ø10 000', ext_from=cx-60)
    # lower notes, free from views
    s.note(42, 114,
           'ПРИНЦИП ТРАССЫ\n'
           '1. Обе шахты начинаются после вращающегося гермоперехода и полого вала.\n'
           '2. Шахты расположены в передней полусфере и не проходят через жилой объём\n'
           '   цилиндрической части до выхода на поверхность.\n'
           '3. Каждая шахта имеет секционные гермодвери, тормозной участок и аварийную\n'
           '   остановку; отказ одной шахты не закрывает вторую.\n'
           '4. Внутри межцилиндрового зазора шахт нет.', size=6.2)
    s.spec_table(330, 70, [
        ['1', 'Полый осевой вал', '1', 'на цилиндр'],
        ['2', 'Шахта наклонная', '2', 'раздельные'],
        ['3', 'Гермодверь секционная', 'по трассе', 'аварийная'],
        ['4', 'Выход на жилую поверхность', '2', 'на цилиндр'],
    ], widths=(10, 82, 22, 24), rh=5.4, size=5.8, title='СПЕЦИФИКАЦИЯ')
    return s


def sheet5_rear_frame():
    s = Sheet('A2', title='Задняя рама.\nПривод, питание и связь',
              material='Сталь 18Ni(300)', scale='см. виды',
              number='ММОСО.01.820 СБ', mass='см. спецификацию',
              sheet_no='5', sheets='5', lit='П', date='10.09.2026')
    A = s.ax
    title(s, 'ЛИСТ 5. ЗАДНЯЯ НЕПОДВИЖНАЯ РАМА — ПРИВОД, ПИТАНИЕ И СВЯЗЬ',
          'Пассажирская транспортная трасса заканчивается в передней раме; задняя рама обслуживает вращение и управление.')
    cx, cy = 160, 240
    top_y, bot_y = cy+64, cy-64
    # frame plane and bearing centers
    line(A, cx, bot_y-50, cx, top_y+50, 'main')
    line(A, cx+7, bot_y-50, cx+7, top_y+50, 'thin')
    for i, yy in enumerate((top_y, bot_y), start=1):
        A.add_patch(Circle((cx, yy), 40, fill=False, ec=C, lw=S_MAIN))
        A.add_patch(Circle((cx, yy), 9, fill=False, ec=C, lw=S_MAIN))
        A.add_patch(Circle((cx, yy), 3, fill=False, ec=C, lw=S_THIN))
        text(A, cx, yy-53, f'ЦИЛИНДР {i}\nподшипниковый центр', size=6.0, ha='center')
        # compact radiators and limited blue wings
        for sy in (yy+24, yy-24):
            A.add_patch(Rectangle((cx-60, sy-5), 10, 10, fc=RED_LIGHT, ec=RED, lw=S_THIN))
            text(A, cx-67, sy, 'Р', size=5.1, ha='right', color=RED, weight='bold')
        A.add_patch(Rectangle((cx+20, yy+18), 10, 20, fc=BLUE_LIGHT, ec=BLUE, lw=S_THIN))
        A.add_patch(Rectangle((cx+20, yy-38), 10, 20, fc=BLUE_LIGHT, ec=BLUE, lw=S_THIN))
        for xx in (cx+22, cx+26):
            line(A, xx, yy+19, xx, yy+37, 'thin', color=BLUE)
            line(A, xx, yy-37, xx, yy-19, 'thin', color=BLUE)
        # motor generator and mechanical catcher
        A.add_patch(Ellipse((cx+57, yy), 25, 16, fill=False, ec=C, lw=S_MAIN))
        text(A, cx+57, yy, 'МГ', size=6.4, ha='center', weight='bold')
        line(A, cx+8, yy+18, cx+42, yy+18, 'hidden', color=GREY)
        line(A, cx+8, yy-18, cx+42, yy-18, 'hidden', color=GREY)
    text(A, cx, 333, 'ФИКСИРОВАННАЯ ЗАДНЯЯ РАМА', size=7.2, ha='center', weight='bold')
    # Exactly three antennas, clearly spaced and numbered.
    for i, yy in enumerate((cy+105, cy+64, cy+23), start=1):
        line(A, cx-7, yy-6, cx-58, yy+10, 'thin')
        A.add_patch(Ellipse((cx-66, yy+12), 18, 8, fill=False, ec=C, lw=S_THIN))
        text(A, cx-66, yy+26, f'АНТЕННА {i}', size=5.7, ha='center')
    # labels and power/propulsion module on right
    x = 340
    text(A, x+90, 337, 'Состав задней рамы', size=7.8, ha='center', weight='bold')
    equipment = [
        ('А', 'реакторная шина', ORANGE),
        ('Б', 'контроллеры магнитных опор', BLUE),
        ('В', 'два мотор-генератора', C),
        ('Г', 'две тяговые установки', GREEN),
        ('Д', 'три направленные антенны', C),
    ]
    yy = 292
    for letter, label, col in equipment:
        A.add_patch(Rectangle((x, yy-10), 24, 20, fill=False, ec=C, lw=S_THIN))
        text(A, x+12, yy, letter, size=7, ha='center', weight='bold', color=col)
        text(A, x+32, yy, label, size=6.4, color=col)
        yy -= 28
    # power flow and thrust diagram — separate upper block, not over the specification
    text(A, x+95, 156, 'СИЛОВАЯ СХЕМА', size=7.5, ha='center', weight='bold')
    A.add_patch(Rectangle((x+20, 132), 150, 18, fill=False, ec=ORANGE, lw=S_MAIN))
    text(A, x+95, 141, 'РЕАКТОРНАЯ ШИНА', size=5.8, ha='center', color=ORANGE, weight='bold')
    for bx, lab in ((x+20, 'АМП 1'), (x+72, 'МГ 1'), (x+124, 'АМП 2'), (x+176, 'МГ 2')):
        A.add_patch(Rectangle((bx, 102), 38, 18, fill=False, ec=C, lw=S_THIN))
        arrow(A, bx+19, 132, bx+19, 121, ORANGE, .8, 7)
        text(A, bx+19, 111, lab, size=5.2, ha='center')
    # propulsion arrows
    arrow(A, x+95, 252, x+145, 252, GREEN, 1.2, 8)
    arrow(A, x+95, 188, x+145, 188, GREEN, 1.2, 8)
    text(A, x+170, 252, 'тяга +ω', size=6.0, color=GREEN)
    text(A, x+170, 188, 'тяга −ω', size=6.0, color=GREEN)
    text(A, x+120, 166, 'цилиндры вращаются встречно', size=5.9, ha='center', color=GREEN)
    # no passenger path callout
    line(A, 244, 240, 310, 240, 'hidden', color=GREY)
    text(A, 277, 249, 'пассажирской трассы нет', size=5.8, ha='center', color=GREY)
    # dimensions and notes
    s.dim_v(bot_y+40, top_y-40, 246, '21 000 между осями', ext_from=cx+40)
    s.dim_v(bot_y+40, top_y-40, 266, '11 000 светлый зазор', ext_from=cx+40)
    callout(s, cx-60, top_y+24, 43, 347, 1, 'красные панели —\nтолько радиаторы', side='left')
    callout(s, cx+25, top_y+34, 308, 350, 2, 'синие панели —\nсолнечные крылья', side='right')
    callout(s, cx-66, cy+105+12, 43, 304, 3, 'ровно 3 антенны', side='left')
    s.note(42, 117,
           'ТЕХНИЧЕСКИЕ ТРЕБОВАНИЯ\n'
           '1. Задняя рама неподвижна; мотор-генераторы воздействуют на ротор через опоры.\n'
           '2. Реакторная шина и контроллеры магнитных опор размещены на раме.\n'
           '3. Радиаторы компактные и красные; солнечные крылья синие; причальные\n'
           '   и силовые элементы металлические/графитовые.\n'
           '4. На задней раме установлены ровно три направленные антенны.\n'
           '5. Пассажирский маршрут через заднюю раму не проходит.', size=6.2)
    s.spec_table(320, 61, [
        ['1', 'Задняя неподвижная рама', '1', 'статор'],
        ['2', 'Мотор-генератор', '2', 'по цилиндрам'],
        ['3', 'Тяговая установка', '2', 'встречное вращение'],
        ['4', 'Антенна направленная', '3', 'ровно три'],
        ['5', 'Радиаторная панель', 'огр.', 'красная'],
        ['6', 'Солнечное крыло', 'огр.', 'синее'],
    ], widths=(10, 80, 18, 28), rh=5.4, size=5.8, title='СПЕЦИФИКАЦИЯ')
    return s


SHEETS = (sheet1_assembly, sheet2_front_frame, sheet3_bearing,
          sheet4_cylinder, sheet5_rear_frame)


def build(pdf_name='MMOSON_engineering_set.pdf'):
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    pdf_path = os.path.join(root, pdf_name)
    png_paths = []
    with PdfPages(pdf_path) as pdf:
        for i, fn in enumerate(SHEETS, start=1):
            s = fn()
            png = os.path.join(root, f'MMOSON_engineering_{i:02d}.png')
            s.fig.savefig(png, dpi=220, facecolor='white')
            pdf.savefig(s.fig)
            plt.close(s.fig)
            png_paths.append(png)
        info = pdf.infodict()
        info['Title'] = 'ММОСО\'Н. Раздельный комплект инженерных чертежей станции'
        info['Author'] = 'Бугаенко Р. С., НИК'
        info['Subject'] = 'Рамы, подшипниковые узлы, цилиндры и транспортные трассы'
    return pdf_path, png_paths


if __name__ == '__main__':
    result = build()
    print(result[0])
    for path in result[1]:
        print(path)
