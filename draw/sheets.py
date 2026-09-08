# -*- coding: utf-8 -*-
"""Чертежи ММОСО'Н по ЕСКД."""
import math
import os
import matplotlib.pyplot as plt
import numpy as _np
from eskd import Sheet, S_MAIN, S_THIN, C
from matplotlib.patches import Rectangle, Arc, Polygon, Circle
from matplotlib.lines import Line2D


def sheet01():
    """Лист 1. Цилиндр обитаемый. Чертёж общего вида в трёх проекциях.

    Компоновка по ГОСТ 2.305: главный вид (фронтальный разрез) вверху слева,
    вид слева — справа от него в горизонтальной проекционной связи,
    вид сверху — под главным в вертикальной связи. Масштаб единый 1:150 000.
    """
    s = Sheet('A1', title='Цилиндр обитаемый\nЧертёж общего вида',
              material='Сталь 18Ni(300)', scale='1:100 000',
              number='ММОСО.01.000 ВО', mass='21,85 млрд т',
              sheet_no='1', sheets='7')
    A = s.ax
    M = 1 / 100.                       # мм листа на метр натуры
    R = 5000 * M                       # 33,33 мм
    c = 4500 * M                       # 30,00 мм
    Lh = 40000 * M / 2                 # 133,33 мм — полуцилиндр
    GT = 2.6                           # грунт, показан условно (вне масштаба)

    # ── ОСИ КОМПОНОВКИ ──
    xF, yF = 300., 432.                # центр главного вида
    xL = 655.                          # центр вида слева (та же высота yF)
    yT = 268.                          # центр вида сверху (та же ось xF)

    # ═══════════ ГЛАВНЫЙ ВИД: ФРОНТАЛЬНЫЙ РАЗРЕЗ ═══════════
    A.text(xF, yF + R + 62, 'Фронтальный разрез', fontsize=11,
           ha='center', fontweight='bold')

    # наружный контур оболочки
    s.line(xF - Lh, yF + R, xF + Lh, yF + R)
    s.line(xF - Lh, yF - R, xF + Lh, yF - R)
    for e in (-1, 1):
        A.add_patch(Arc((xF + e * Lh, yF), 2 * c, 2 * R,
                        theta1=-90 if e > 0 else 90,
                        theta2=90 if e > 0 else 270, lw=S_MAIN, ec=C))

    # конструкционный пакет в разрезе — штриховка металла
    TP = 1.9                                        # пакет, условно
    for sg in (1, -1):
        y1, y2 = yF + sg * R, yF + sg * (R - TP)
        s.line(xF - Lh, y2, xF + Lh, y2, 'thin')
        s.hatch(xF - Lh, min(y1, y2), xF + Lh, max(y1, y2), step=1.9)
    # грунт — условное обозначение насыпного материала (точки + штрих)
    for sg in (1, -1):
        yg1 = yF + sg * (R - TP)
        yg2 = yF + sg * (R - TP - GT)
        s.line(xF - Lh, yg2, xF + Lh, yg2, 'thin')
        A.add_patch(Rectangle((xF - Lh, min(yg1, yg2)), 2 * Lh, GT,
                              fc='#efe6d6', ec='none', zorder=1))
        rng = _np.random.default_rng(4 + sg)
        A.scatter(rng.uniform(xF - Lh, xF + Lh, 900),
                  rng.uniform(min(yg1, yg2) + 0.15, max(yg1, yg2) - 0.15, 900),
                  s=0.30, c='#6b5a44', zorder=2)

    # осевая световая балка
    hb = 1.5
    A.add_patch(Rectangle((xF - Lh - c * 0.72, yF - hb / 2),
                          2 * (Lh + c * 0.72), hb, fc='#f6efb8', ec=C,
                          lw=S_THIN, zorder=4))
    s.line(xF - Lh - c - 34, yF, xF + Lh + c + 34, yF, 'axis')

    # климатические зоны — границы и обозначения
    zones = [(0, 10, 'I', 'ТРОПИЧЕСКАЯ', '+28…+35 °C', '220 Вт/м²'),
             (10, 22, 'II', 'СУБТРОПИЧЕСКАЯ', '+15…+28 °C', '170 Вт/м²'),
             (22, 32, 'III', 'УМЕРЕННАЯ', '0…+15 °C', '120 Вт/м²'),
             (32, 40, 'IV', 'ХОЛОДНАЯ', '−15…−5 °C', '60 Вт/м²')]
    for z0, z1, rn, nm, tt, wt in zones:
        xa = xF - Lh + z0 * 1000 * M
        xb = xF - Lh + z1 * 1000 * M
        if z1 < 40:
            s.line(xb, yF - R + TP, xb, yF + R - TP, 'thin')
        xm = (xa + xb) / 2
        A.text(xm, yF + R + 15.5, f'{rn}  {nm}', fontsize=7.6, ha='center',
               fontweight='bold')
        A.text(xm, yF + R + 10.5, f'{tt} · {wt}', fontsize=6.8, ha='center')

    # рельеф жилой поверхности (нижняя образующая в разрезе)
    gy = yF - R + TP + GT
    def town(x0, w, n=5):
        for k in range(n):
            xx = x0 + k * w / n
            hh = 2.4 + ((k * 7) % 3) * 0.7
            A.add_patch(Rectangle((xx, gy), w / n * 0.5, hh, fc='#dcdcdc',
                                  ec=C, lw=0.35, zorder=3))
    def trees(x0, w, n=8):
        for k in range(n):
            xx = x0 + k * w / n
            s.line(xx, gy, xx, gy + 0.9, 'thin')
            A.add_patch(Circle((xx, gy + 1.6), 0.85, fc='#cfe3c4', ec=C,
                               lw=0.35, zorder=3))
    def water(x0, w, d=0.8):
        A.add_patch(Rectangle((x0, gy - d), w, d, fc='#c7dff0', ec=C,
                              lw=0.4, zorder=3))
    def field(x0, w):
        for k in range(int(w / 2.0)):
            s.line(x0 + k * 2.0, gy, x0 + k * 2.0 + 1.2, gy + 0.8, 'thin')
    field(xF - Lh + 6, 18);   water(xF - Lh + 27, 11); town(xF - Lh + 41, 15)
    trees(xF - Lh + 60, 16);  field(xF - Lh + 80, 18); water(xF - Lh + 102, 10)
    town(xF - Lh + 115, 13);  trees(xF - Lh + 132, 14); field(xF - Lh + 150, 16)
    water(xF - Lh + 170, 9);  town(xF - Lh + 182, 12); trees(xF - Lh + 198, 13)
    field(xF - Lh + 215, 14)
    for k in range(5):                                   # холодная зона
        A.add_patch(Rectangle((xF - Lh + 234 + k * 6.6, gy), 4.4, 1.4,
                              fc='#eef5f9', ec=C, lw=0.4, zorder=3))

    # ── ДВЕ ТРАНСПОРТНЫЕ ШАХТЫ в толще переднего торца ──
    _t = _np.linspace(math.asin(150. / 5000.), math.pi / 2, 90)
    for sg in (+1, -1):
        xs_ = [xF - Lh - (c - 0.9) * math.cos(t) for t in _t]
        ys_ = [yF + sg * (R - 0.9) * math.sin(t) for t in _t]
        A.add_line(Line2D(xs_, ys_, lw=1.3, ls=(0, (5, 2.5)),
                          color='#1c4f7c', zorder=6))
        A.add_patch(Circle((xF - Lh, yF + sg * (R - TP / 2)), 1.2, fc='white',
                           ec=C, lw=S_MAIN, zorder=7))
    A.add_patch(Rectangle((xF - Lh - c - 1.1, yF - 2.2), 2.2, 4.4, fc='white',
                          ec=C, lw=S_THIN, zorder=7))

    # подшипниковые узлы и причалы
    for e in (-1, 1):
        xb0 = xF + e * (Lh + c)
        A.add_patch(Rectangle((xb0 - 2.2, yF - 4.0), 4.4, 8.0, fc='#dcdcdc',
                              ec=C, lw=S_MAIN, zorder=6))
        s.line(xb0 + e * 2.2, yF, xb0 + e * 13, yF)
        A.add_patch(Rectangle((xb0 + e * 13 - (0 if e > 0 else 6), yF - 3.0),
                              6, 6, fc='white', ec=C, lw=S_MAIN, zorder=6))

    # размеры главного вида
    s.dim_h(xF - Lh, xF + Lh, yF + R + 34, '40 000', ext_from=yF + R + 3)
    s.dim_h(xF - Lh - c, xF + Lh + c, yF + R + 46, '49 000', ext_from=yF + R + 3)
    s.dim_v(yF - R, yF + R, xF - Lh - c - 30, 'Ø10 000', ext_from=xF - Lh - c)
    s.dim_h(xF + Lh, xF + Lh + c, yF - R - 40, '4 500', ext_from=yF - R)
    for z0, z1 in ((0, 10), (10, 22), (22, 32), (32, 40)):
        s.dim_h(xF - Lh + z0 * 1000 * M, xF - Lh + z1 * 1000 * M, yF - R - 20,
                f'{(z1 - z0) * 1000}', ext_from=yF - R - TP - GT - 1)

    # секущие плоскости
    s.section_mark(xF - Lh + 92, yF + R + 6, 'А', 'up')
    s.section_mark(xF - Lh + 92, yF - R - 6, 'А', 'down')
    s.detail_ref(xF + Lh * 0.52, yF + R - TP / 2, 7.0, 'Б', ang=68)
    s.detail_ref(xF - Lh + 27 + 5, gy - 0.4, 6.0, 'В', ang=-115)

    # ═══════════ ВИД СЛЕВА: ПОПЕРЕЧНЫЙ РАЗРЕЗ А–А ═══════════
    A.text(xL, yF + R + 62, 'А–А', fontsize=12, ha='center', fontweight='bold')
    s.circle(xL, yF, R)
    s.circle(xL, yF, R - TP, 'thin')
    # пакет в разрезе — кольцевая штриховка
    _n = 260
    for k in range(_n):
        a0 = 2 * math.pi * k / _n
        s.line(xL + (R - TP) * math.cos(a0), yF + (R - TP) * math.sin(a0),
               xL + R * math.cos(a0), yF + R * math.sin(a0), 'thin')
    s.circle(xL, yF, R - TP - GT, 'thin')
    A.add_patch(Circle((xL, yF), R - TP, fc='#efe6d6', ec='none', zorder=0))
    A.add_patch(Circle((xL, yF), R - TP - GT, fc='white', ec='none', zorder=0))
    s.centerlines(xL, yF, R)
    # граница зоны, закрытой для людей
    s.circle(xL, yF, 2500 * M, 'axis')
    # осевая балка
    A.add_patch(Circle((xL, yF), 1.5, fc='#f6efb8', ec=C, lw=S_MAIN, zorder=5))
    # два устья шахт
    for a0 in (math.radians(90), math.radians(270)):
        xu = xL + (R - TP - GT / 2) * math.cos(a0)
        yu = yF + (R - TP - GT / 2) * math.sin(a0)
        A.add_patch(Circle((xu, yu), 1.3, fc='white', ec=C, lw=S_MAIN,
                           zorder=6))
    # шпангоут — кольцо
    s.circle(xL, yF, R - TP - 0.7, 'thin')
    s.dim_v(yF - R, yF + R, xL - R - 26, 'Ø10 000', ext_from=xL - R)
    s.dim_h(xL, xL + 2500 * M, yF - R - 20, '2 500', ext_from=yF)
    s.detail_ref(xL + (R - TP / 2) * math.cos(math.radians(38)),
                 yF + (R - TP / 2) * math.sin(math.radians(38)), 7.0, 'Г',
                 ang=38)

    # проекционная связь: главный вид ↔ вид слева
    for yy in (yF + R, yF - R):
        s.link(xF + Lh + c + 4, yy, xL - R - 30, yy)

    # ═══════════ ВИД СВЕРХУ ═══════════
    A.text(xF, yT + R + 16, 'Вид сверху', fontsize=11, ha='center',
           fontweight='bold')
    s.line(xF - Lh, yT + R, xF + Lh, yT + R)
    s.line(xF - Lh, yT - R, xF + Lh, yT - R)
    for e in (-1, 1):
        A.add_patch(Arc((xF + e * Lh, yT), 2 * c, 2 * R,
                        theta1=-90 if e > 0 else 90,
                        theta2=90 if e > 0 else 270, lw=S_MAIN, ec=C))
    s.line(xF - Lh - c - 34, yT, xF + Lh + c + 34, yT, 'axis')
    # границы зон в плане
    for z0, z1, rn, nm, tt, wt in zones:
        xb = xF - Lh + z1 * 1000 * M
        if z1 < 40:
            s.line(xb, yT - R, xb, yT + R, 'thin')
        A.text(xF - Lh + (z0 + z1) / 2 * 1000 * M, yT + R * 0.62, rn,
               fontsize=8.5, ha='center', fontweight='bold', color='#666')
    # шахты в плане — в переднем торце
    for sg in (+1, -1):
        xs_ = [xF - Lh - (c - 0.9) * math.cos(t) for t in _t]
        ys_ = [yT + sg * (R - 0.9) * math.sin(t) for t in _t]
        A.add_line(Line2D(xs_, ys_, lw=1.3, ls=(0, (5, 2.5)),
                          color='#1c4f7c', zorder=6))
    # осевая балка в плане — невидимый контур
    s.line(xF - Lh - c * 0.72, yT + 0.8, xF + Lh + c * 0.72, yT + 0.8, 'hidden')
    s.line(xF - Lh - c * 0.72, yT - 0.8, xF + Lh + c * 0.72, yT - 0.8, 'hidden')
    for e in (-1, 1):
        xb0 = xF + e * (Lh + c)
        A.add_patch(Rectangle((xb0 - 2.2, yT - 4.0), 4.4, 8.0, fc='#dcdcdc',
                              ec=C, lw=S_MAIN, zorder=6))
        s.line(xb0 + e * 2.2, yT, xb0 + e * 13, yT)
        A.add_patch(Rectangle((xb0 + e * 13 - (0 if e > 0 else 6), yT - 3.0),
                              6, 6, fc='white', ec=C, lw=S_MAIN, zorder=6))
    s.dim_h(xF - Lh - c, xF + Lh + c, yT - R - 22, '49 000', ext_from=yT - R)

    # вертикальная проекционная связь
    for xx in (xF - Lh - c, xF - Lh, xF + Lh, xF + Lh + c):
        s.link(xx, yF - R - 46, xx, yT + R + 6)

    # ═══════════ ВЫНОСНЫЕ ЭЛЕМЕНТЫ ═══════════
    # Б — пакет обшивки
    bx, by = 690., 300.
    A.text(bx, by + 52, 'Б  (20 : 1)', fontsize=10.5, ha='center',
           fontweight='bold')
    w = 74.
    ytop = by + 36
    layers = [('Радиационная защита,\nреголит + боросиликат', '1 000',
               '#e2e2e2', 17.0),
              ('Теплоизоляция\nэкранно-вакуумная', '100', '#f2f2f2', 3.0),
              ('Силовой пояс,\nсталь 18Ni(300)', '850', '#a8a8a8', 15.0),
              ('Гермооболочка,\nсталь нержавеющая', '50', '#5f5f5f', 2.6)]
    yy = ytop
    for nm, th, col, hh in layers:
        A.add_patch(Rectangle((bx - w / 2, yy - hh), w, hh, fc=col, ec=C,
                              lw=S_MAIN))
        if col == '#a8a8a8':
            s.hatch(bx - w / 2, yy - hh, bx + w / 2, yy, step=2.6)
        A.plot([bx + w / 2, bx + w / 2 + 6], [yy - hh / 2] * 2, lw=S_THIN,
               color=C)
        A.text(bx + w / 2 + 7.5, yy - hh / 2, f'{nm}\n{th} мм', fontsize=6.6,
               va='center')
        yy -= hh
    A.add_patch(Rectangle((bx - w / 2, yy - 14), w, 14, fc='#c8a678', ec=C,
                          lw=S_MAIN))
    A.text(bx, yy - 7, 'ГРУНТ 1 500 мм', fontsize=6.8, ha='center',
           va='center', fontweight='bold')
    s.dim_v(ytop - 37.6, ytop, bx - w / 2 - 12, '2 000', ext_from=bx - w / 2)
    A.text(bx, ytop + 4, 'вакуум', fontsize=7, ha='center', fontstyle='italic')
    A.text(bx, yy - 19, 'обитаемый объём', fontsize=7, ha='center',
           fontstyle='italic')

    # В — устройство водоёма
    vx, vy = 690., 178.
    A.text(vx, vy + 34, 'В  (200 : 1)', fontsize=10.5, ha='center',
           fontweight='bold')
    ww = 118.
    A.add_patch(Rectangle((vx - ww / 2, vy - 9), ww, 9, fc='#a8a8a8', ec=C,
                          lw=S_MAIN))
    s.hatch(vx - ww / 2, vy - 9, vx + ww / 2, vy, step=2.8)
    A.text(vx - ww / 2 + 2.4, vy - 4.5, 'силовой пояс', fontsize=6.0,
           va='center')
    A.add_patch(Rectangle((vx - ww / 2, vy), ww, 19, fc='#c8a678', ec=C,
                          lw=S_THIN))
    A.text(vx - ww / 2 + 2.4, vy + 15.5, 'грунт 1 500', fontsize=6.0,
           va='center')
    A.add_patch(Polygon([(vx - 32, vy + 19), (vx - 24, vy + 3.5),
                         (vx + 24, vy + 3.5), (vx + 32, vy + 19)],
                        closed=True, fc='#c7dff0', ec=C, lw=S_MAIN))
    s.dim_v(vy + 3.5, vy + 19, vx + 42, '1 200', ext_from=vx + 32)
    s.line(vx - 52, vy + 19, vx + 52, vy + 19, 'thin')
    A.text(vx, vy + 21, 'уровень почвы', fontsize=6.2, ha='center')
    A.text(vx, vy - 13, 'дно водоёма выше гермооболочки:\n'
                        'выемка в силовой пояс не допускается',
           fontsize=6.4, ha='center', va='top')

    # Г — сечение шпангоута
    gx, gy2 = 690., 120.
    A.text(gx, gy2 + 34, 'Г  (2 000 : 1)', fontsize=10.5, ha='center',
           fontweight='bold')
    HH, BB, TW, TF = 40., 20., 2.9, 2.9
    x0g, y0g = gx - BB / 2, gy2 - HH / 2
    for ry in (y0g, y0g + HH - TF):
        A.add_patch(Rectangle((x0g, ry), BB, TF, fc='#b9b9b9', ec=C,
                              lw=S_MAIN))
        s.hatch(x0g, ry, x0g + BB, ry + TF, step=1.8)
    A.add_patch(Rectangle((gx - TW / 2, y0g + TF), TW, HH - 2 * TF,
                          fc='#b9b9b9', ec=C, lw=S_MAIN))
    s.hatch(gx - TW / 2, y0g + TF, gx + TW / 2, y0g + HH - TF, step=1.8)
    s.dim_v(y0g, y0g + HH, x0g - 13, '5 000', ext_from=x0g)
    s.dim_h(x0g, x0g + BB, y0g - 10, '2 500', ext_from=y0g)
    s.leader(gx + TW / 2, gy2 + 5, gx + 26, gy2 + 13, 'стенка 40')
    s.leader(x0g + BB * 0.75, y0g + HH - TF / 2, gx + 26, gy2 + 24,
             'полка 40')
    A.text(gx, y0g - 13, 'A = 0,594 м²   I = 2,02 м⁴   W = 0,81 м³\n'
                         'σ = 659 МПа при M = 0,53 ГН·м\n'
                         'шаг 100 000, 400 шт. на цилиндр',
           fontsize=6.4, ha='center', va='top')

    # ═══════════ ТАБЛИЦА СОСТАВНЫХ ЧАСТЕЙ ═══════════
    s.spec_table(46, 92, [
        ['1', 'Пакет конструкционный (элемент Б)', '1', '13,426 млрд т'],
        ['2', 'Грунт растительный, слой 1 500', '1', '4,06 млрд т'],
        ['3', 'Балка светотепловая осевая Ø8 000', '1', 'ММОСО.01.100'],
        ['4', 'Шпангоут 5 000 × 2 500 (элемент Г)', '400', '58,6 млн т'],
        ['5', 'Стрингер', '628', '11,5 млн т'],
        ['6', 'Шахта транспортная наклонная', '2', 'ММОСО.01.200'],
        ['7', 'Узел подшипниковый', '2', 'ММОСО.01.300'],
        ['8', 'Причал', '2', 'ММОСО.01.400'],
        ['9', 'Водоём (элемент В)', '—', '135 км², 0,162 км³'],
    ], widths=(11, 84, 13, 34))

    # ═══════════ ТЕХНИЧЕСКИЕ ТРЕБОВАНИЯ ═══════════
    s.note(200, 92,
           'Технические требования\n'
           '1. Размеры линейные в метрах натуры, толщины слоёв '
           'в миллиметрах.\n'
           '2. Материал силовой оболочки — сталь мартенситностареющая '
           '18Ni(300):\n'
           '    предел прочности 2 000 МПа, предел текучести 1 333 МПа.\n'
           '3. Расчётная нагрузка на силовой пояс 218,0 кПа, в том числе\n'
           '    собственный вес пояса 65,4 кПа. Кольцевое напряжение '
           '1 308 МПа,\n'
           '    запас по пределу прочности 1,53 (п. Б.3, Б.16).\n'
           '4. Частота вращения 0,423 об/мин, тяжесть у обода 1,0 g;\n'
           '    зона r < 2 500 м для пребывания людей закрыта.',
           size=7.0)
    s.note(430, 92,
           ' \n'
           '5. Давление у обода 101,325 кПа, на оси 74,7 кПа — '
           'вращательный\n'
           '    градиент плотности (п. Б.4).\n'
           '6. Шахт транспортных две, обе в толще переднего торца, '
           'устья Ø30 000\n'
           '    (п. Б.17). Заглубление сооружений ограничено толщиной '
           'грунта 1 500.\n'
           '7. Теплицы и гидропоника в холодной зоне не размещаются: '
           '14,8 км²\n'
           '    переданы в зоны II и III, экономия 4,15 ГВт (п. Б.12).\n'
           '8. Сварные швы стыковые с полным проваром, контроль '
           'сплошности 100 %.',
           size=7.0)
    return s.save('01_cylinder_general.png',
                  keep=globals().get('_KEEP', False))


def sheet02():
    """Лист 2. Набор силовой. Сборочный чертёж.

    Шпангоут и стрингеры показаны в трёх видах: поперечное сечение,
    развёртка узла сопряжения и фрагмент в плане. Дублирование сечения А–А
    с листа 1 устранено: там оно дано как проекция общего вида, здесь —
    конструкция набора.
    """
    s = Sheet('A1', title='Набор силовой\nСборочный чертёж',
              material='Сталь 18Ni(300)', scale='1:200',
              number='ММОСО.01.500 СБ', mass='70,1 млн т',
              sheet_no='2', sheets='7')
    A = s.ax

    # ═══════ ВИД 1: ПОПЕРЕЧНОЕ СЕЧЕНИЕ ШПАНГОУТА (главный) ═══════
    xA, yA = 175., 400.
    A.text(xA, yA + 118, 'Шпангоут. Поперечное сечение', fontsize=11,
           ha='center', fontweight='bold')
    HH = 100.                       # 5 000 мм при 1:50 -> условно
    BB = 50.
    TF = 4.0                        # полка 40 мм
    TW = 4.0                        # стенка 40 мм
    x0, y0 = xA - BB / 2, yA - HH / 2
    for ry in (y0, y0 + HH - TF):
        A.add_patch(Rectangle((x0, ry), BB, TF, fc='#c4c4c4', ec=C,
                              lw=S_MAIN, zorder=3))
        s.hatch(x0, ry, x0 + BB, ry + TF, step=2.0)
    A.add_patch(Rectangle((xA - TW / 2, y0 + TF), TW, HH - 2 * TF,
                          fc='#c4c4c4', ec=C, lw=S_MAIN, zorder=3))
    s.hatch(xA - TW / 2, y0 + TF, xA + TW / 2, y0 + HH - TF, step=2.0)
    s.centerlines(xA, yA, HH / 2 + 8)
    s.dim_v(y0, y0 + HH, x0 - 26, '5 000', ext_from=x0)
    s.dim_h(x0, x0 + BB, y0 - 22, '2 500', ext_from=y0)
    s.leader(xA, y0 + HH * 0.62, xA - 58, y0 + HH * 0.86, 'стенка 40')
    s.leader(x0 + BB * 0.78, y0 + HH - TF / 2, xA + 52, y0 + HH + 14, 'полка 40')
    s.weld(xA + TW / 2, yA - 20, xA + 50, yA - 44, 'K = 40, по контуру')
    A.text(xA, y0 - 40,
           'A = 0,594 м²    I = 2,02 м⁴    W = 0,81 м³\n'
           'M = 0,53 ГН·м    σ = 659 МПа    [σ] = 889 МПа\n'
           'запас 1,35 · шаг 100 000 · 400 шт. на цилиндр',
           fontsize=7.2, ha='center', va='top')

    # ═══════ ВИД 2: УЗЕЛ СОПРЯЖЕНИЯ СО СТРИНГЕРОМ (вид слева) ═══════
    xB, yB = 430., 400.
    A.text(xB, yB + 118, 'Узел сопряжения со стрингером', fontsize=11,
           ha='center', fontweight='bold')
    # шпангоут в профиль — узкая полоса
    A.add_patch(Rectangle((xB - 4.0, yB - HH / 2), 8.0, HH, fc='#c4c4c4',
                          ec=C, lw=S_MAIN, zorder=3))
    s.hatch(xB - 4.0, yB - HH / 2, xB + 4.0, yB + HH / 2, step=2.0)
    A.text(xB, yB + HH / 2 + 6, 'шпангоут', fontsize=7, ha='center')
    # обшивка — горизонтальная полоса сверху
    A.add_patch(Rectangle((xB - 90, yB + HH / 2), 180, 8.0, fc='#a8a8a8',
                          ec=C, lw=S_MAIN, zorder=3))
    s.hatch(xB - 90, yB + HH / 2, xB + 90, yB + HH / 2 + 8.0, step=2.2)
    A.text(xB - 78, yB + HH / 2 + 4, 'обшивка 850', fontsize=6.4,
           va='center', zorder=5)
    # стрингеры — тавры, приклёпаны к обшивке
    for k in (-2, -1, 1, 2):
        xs = xB + k * 34
        A.add_patch(Rectangle((xs - 9, yB + HH / 2 - 14), 18, 3.2,
                              fc='#c4c4c4', ec=C, lw=S_MAIN, zorder=3))
        A.add_patch(Rectangle((xs - 1.6, yB + HH / 2 - 14), 3.2, 14,
                              fc='#c4c4c4', ec=C, lw=S_MAIN, zorder=3))
        s.hatch(xs - 9, yB + HH / 2 - 14, xs + 9, yB + HH / 2 - 10.8, step=1.8)
    s.leader(xB + 34, yB + HH / 2 - 14, xB + 74, yB + 12,
             'стрингер 1 200 × 600')
    s.dim_h(xB - 68, xB - 34, yB + HH / 2 - 26, '50 000',
            ext_from=yB + HH / 2 - 14)
    s.weld(xB + 4.0, yB + HH / 2 - 4, xB + 60, yB + HH / 2 - 30,
           'стыковой, полный провар')
    A.text(xB, yB - HH / 2 - 40,
           'Шаг стрингеров 50 000 по образующей\n'
           '628 шт. на цилиндр · 11,5 млн т\n'
           'Назначение: местная устойчивость оболочки',
           fontsize=7.2, ha='center', va='top')


    # ═══════ ВИД 3: ФРАГМЕНТ В ПЛАНЕ (вид сверху) ═══════
    xC, yC = 175., 215.
    A.text(xC, yC + 62, 'Фрагмент набора. План', fontsize=11, ha='center',
           fontweight='bold')
    # шпангоуты — поперечные полосы
    for k in range(3):
        xx = xC - 100 + k * 100
        A.add_patch(Rectangle((xx - 3, yC - 46), 6, 92, fc='#c4c4c4', ec=C,
                              lw=S_MAIN, zorder=3))
    # стрингеры — продольные
    for k in range(-2, 3):
        yy = yC + k * 20
        A.add_line(Line2D([xC - 118, xC + 118], [yy, yy], lw=S_MAIN, color=C,
                          zorder=2))
    s.dim_h(xC - 100, xC, yC - 60, '100 000', ext_from=yC - 46)
    s.dim_v(yC, yC + 20, xC + 128, '50 000', ext_from=xC + 118)
    A.text(xC - 118, yC + 52, 'шпангоуты — шаг 100 000',
           fontsize=6.8, ha='left')
    A.text(xC - 118, yC + 46, 'стрингеры — шаг 50 000',
           fontsize=6.8, ha='left')

    # ═══════ Д — ОКАНТОВКА УСТЬЯ ШАХТЫ ═══════
    xD, yD = 700., 400.
    A.text(xD, yD + 100, 'Окантовка выреза  (1 : 500)', fontsize=10.5, ha='center',
           fontweight='bold')
    A.text(xD, yD + 92, 'окантовка устья шахты Ø30 000', fontsize=7.4,
           ha='center', fontstyle='italic')
    A.add_patch(Rectangle((xD - 88, yD - 62), 176, 124, fc='#dcdcdc', ec=C,
                          lw=S_MAIN, zorder=2))
    s.hatch(xD - 88, yD - 62, xD + 88, yD + 62, step=3.2)
    A.add_patch(Circle((xD, yD), 34, fc='white', ec=C, lw=S_MAIN, zorder=3))
    A.add_patch(Circle((xD, yD), 42, fc='none', ec=C, lw=S_MAIN, zorder=3))
    s.hatch_poly([(xD + 42 * math.cos(a), yD + 42 * math.sin(a))
                  for a in _np.linspace(0, 2 * math.pi, 90)], step=3.0)
    A.add_patch(Circle((xD, yD), 34, fc='white', ec=C, lw=S_MAIN, zorder=4))
    s.centerlines(xD, yD, 50)
    s.dim_h(xD - 34, xD + 34, yD - 76, 'Ø30 000', ext_from=yD - 34)
    s.leader(xD + 38, yD + 22, xD + 66, yD + 56, 'окантовка, S = 37 м²')
    A.text(xD, yD - 88,
           'Погонное усилие пояса 1 096 МН/м прерывается вырезом.\n'
           'Окантовка 27 386 т на вырез; два устья шахт,\n'
           '4 причальных и 8 стыковых вырезов — 0,38 млн т (п. Б.17).',
           fontsize=7.0, ha='center', va='top')

    # ═══════ ТАБЛИЦА СОСТАВНЫХ ЧАСТЕЙ ═══════
    s.spec_table(430, 150, [
        ['1', 'Шпангоут 5 000 × 2 500, стенка 40', '400', '58,6 млн т'],
        ['2', 'Стрингер 1 200 × 600, стенка 40', '628', '11,5 млн т'],
        ['3', 'Окантовка выреза Ø30 000', '14', '0,38 млн т'],
        ['4', 'Обшивка (лист 3)', '251 327', 'ММОСО.01.600'],
    ], widths=(11, 84, 18, 32))

    # ═══════ ТЕХНИЧЕСКИЕ ТРЕБОВАНИЯ ═══════
    s.note(46, 118,
           'Технические требования\n'
           '1. Размеры в миллиметрах натуры.\n'
           '2. Материал — сталь мартенситностареющая 18Ni(300),\n'
           '    предел текучести 1 333 МПа, [σ] = 889 МПа.\n'
           '3. Изгибающий момент на шпангоут M = 0,53 ГН·м,\n'
           '    требуемый момент сопротивления W ≥ 0,60 м³.\n'
           '4. Принято сечение с W = 0,81 м³, запас 1,35.',
           size=7.0)
    s.note(700, 150,
           ' \n'
           '5. Масса набора 70,1 млн т — 0,50 % массы пакета обшивки\n'
           '    и 0,29 % массы станции (п. Б.14).\n'
           '6. В рабочем режиме форму цилиндра удерживает вращение;\n'
           '    назначение набора — местная устойчивость оболочки\n'
           '    вблизи вырезов и монтажная жёсткость (п. 4.9).\n'
           '7. Сварка автоматическая под флюсом, контроль 100 %.',
           size=7.0)
    return s.save('02_cylinder_section.png',
                  keep=globals().get('_KEEP', False))


def sheet03():
    """Лист 3. Панель обшивки 50 х 100 м."""
    s = Sheet('A2', title='Панель обшивки', material='Сталь 18Ni(300)',
              mass='33 575 т', sheet_no='3', sheets='7', lit='П',
              scale='1:1 000', number='ММОСО.01.600')
    A = s.ax
    cx, cy = 200, 300
    L, B = 200., 100.

    def mark(x, y, n, dx=0, dy=0):
        A.plot([x], [y], marker='o', ms=2.0, color=C, zorder=9)
        s.line(x, y, x+dx, y+dy, 'thin')
        A.add_patch(Circle((x+dx, y+dy), 3.2, fc='white', ec=C, lw=S_THIN,
                           zorder=10))
        A.text(x+dx, y+dy, str(n), fontsize=7, ha='center', va='center',
               zorder=11, fontweight='bold')

    # ── ВИД СВЕРХУ ──
    A.text(cx, cy+B/2+34, 'Вид сверху', fontsize=12, ha='center',
           fontweight='bold')
    A.add_patch(Rectangle((cx-L/2, cy-B/2), L, B, fill=False, lw=S_MAIN, ec=C))
    s.line(cx-L/2, cy, cx+L/2, cy, 'axis')
    s.line(cx, cy-B/2, cx, cy+B/2, 'axis')
    # зоны разделки кромок
    for dx in (-1, 1):
        s.line(cx+dx*(L/2-6), cy-B/2, cx+dx*(L/2-6), cy+B/2, 'thin')
    for dy in (-1, 1):
        s.line(cx-L/2, cy+dy*(B/2-6), cx+L/2, cy+dy*(B/2-6), 'thin')
    # рёбра-стрингеры на тыльной стороне (невидимый контур)
    for k in range(1, 5):
        y = cy-B/2 + k*B/5
        s.line(cx-L/2, y, cx+L/2, y, 'hidden')
    for k in range(1, 8):
        x = cx-L/2 + k*L/8
        s.line(x, cy-B/2, x, cy+B/2, 'hidden')
    # ── площадки причаливания буксира (без отверстий в оболочке) ──
    for sx in (-1, 1):
        for sy in (-1, 1):
            px, py = cx+sx*(L/2-16), cy+sy*(B/2-16)
            A.add_patch(Rectangle((px-4.2, py-4.2), 8.4, 8.4, fill=False,
                                  ec=C, lw=S_THIN, ls=(0, (4, 2))))

    s.dim_h(cx-L/2, cx+L/2, cy+B/2+18, '100 000', ext_from=cy+B/2)
    s.dim_v(cy-B/2, cy+B/2, cx-L/2-20, '50 000', ext_from=cx-L/2)
    s.dim_h(cx-L/2, cx-L/2+6, cy-B/2-14, '6 000', ext_from=cy-B/2)
    s.dim_h(cx-L/2+16-4.2, cx-L/2+16+4.2, cy-B/2-26, '4 000',
            ext_from=cy-B/2)

    mark(cx-L/2+3, cy+B/2-20, 1, -24, 16)
    mark(cx+L/8, cy-B/2+B/5, 2, 14, -26)
    mark(cx+L/2-16, cy+B/2-16, 3, 22, 20)

    # ── ВИД СБОКУ ──
    sy = cy-B/2-58
    A.text(cx, sy+26, 'Вид сбоку  (толщина в масштабе 5 : 1)', fontsize=12,
           ha='center', fontweight='bold')
    th = 16.0
    A.add_patch(Rectangle((cx-L/2, sy-th/2), L, th, fc='#cccccc', ec=C,
                          lw=S_MAIN))
    s.hatch(cx-L/2, sy-th/2, cx+L/2, sy+th/2, step=3.4)
    # разделка кромок под сварку (V-образная)
    for sx in (-1, 1):
        x = cx+sx*L/2
        A.add_patch(Polygon([(x, sy-th/2), (x, sy+th/2),
                             (x-sx*7, sy+th/2)], closed=True,
                            fc='white', ec=C, lw=S_THIN))
    s.dim_v(sy-th/2, sy+th/2, cx+L/2+22, '850', ext_from=cx+L/2)
    A.text(cx-L/2+16, sy+th/2+7, 'разделка кромки 30°', fontsize=7)
    A.text(cx, sy-th/2-11, 'кривизна панели: стрелка 62 при хорде 50 000',
           fontsize=7.5, ha='center')

    # ── СХЕМА РАСКРОЯ ──
    rx, ry = 470, 300
    A.text(rx, ry+76, 'Схема раскроя обечайки', fontsize=12, ha='center',
           fontweight='bold')
    cw, ch = 20., 20.
    for jj in range(5):
        off = cw/2 if jj % 2 else 0
        for ii in range(5):
            A.add_patch(Rectangle((rx-50+ii*cw+off-cw/2, ry-50+jj*ch), cw, ch,
                                  fill=False, lw=S_THIN, ec=C))
    A.add_patch(Rectangle((rx-50, ry-50), 100, 100, fill=False, lw=S_MAIN, ec=C))
    A.annotate('', xy=(rx+62, ry-30), xytext=(rx+62, ry+30),
               arrowprops=dict(arrowstyle='-|>,head_width=0.16,head_length=0.6',
                               lw=S_THIN, color=C))
    A.text(rx+65, ry, 'ось цилиндра', fontsize=7.5, rotation=90, va='center')
    A.text(rx, ry-58, 'продольные швы смещены через ряд;\n'
                      'разбежка не менее 5 000', fontsize=7.5,
           ha='center', va='top')

    # ── УЗЕЛ Д: стыковой шов ──
    dx2, dy2 = 470, 150
    A.text(dx2, dy2+40, 'Д  (50 : 1)  стыковой шов панелей', fontsize=11,
           fontweight='bold', ha='center')
    tt = 26.
    for sgn in (-1, 1):
        xa = dx2 + sgn*6
        xb = dx2 + sgn*62
        A.add_patch(Polygon([(xb, dy2-tt/2), (xb, dy2+tt/2),
                             (xa, dy2+tt/2), (xa+sgn*0, dy2-tt/2)],
                            closed=True, fc='#cccccc', ec=C, lw=S_MAIN))
        s.hatch(min(xa, xb), dy2-tt/2, max(xa, xb), dy2+tt/2, step=3.0)
    # металл шва — X-образная разделка
    A.add_patch(Polygon([(dx2-6, dy2+tt/2), (dx2+6, dy2+tt/2),
                         (dx2+1.4, dy2), (dx2+6, dy2-tt/2),
                         (dx2-6, dy2-tt/2), (dx2-1.4, dy2)],
                        closed=True, fc='#8fa8bd', ec=C, lw=S_MAIN))
    s.dim_v(dy2-tt/2, dy2+tt/2, dx2+72, '850', ext_from=dx2+62)
    s.dim_h(dx2-6, dx2+6, dy2-tt/2-13, '6 000', ext_from=dy2-tt/2)
    s.leader(dx2+3, dy2+tt/2-3, dx2+30, dy2+24, 'разделка 30°, притупление 2')
    A.text(dx2, dy2-tt/2-22,
           'шов двусторонний, полный провар;\nконтроль ультразвуковой 100 %',
           fontsize=6.9, ha='center', va='top')

    legend = ['1 — Зона разделки кромок под стыковой шов, 6 000',
              '2 — Рёбра жёсткости тыльной стороны (невидимый контур)',
              '3 — Площадка причаливания буксира 4 000 × 4 000, 4 шт.;',
              '        сквозных отверстий в оболочке не имеет']
    A.text(46, 132, 'Обозначения позиций', fontsize=8.5, fontweight='bold')
    for k, t in enumerate(legend):
        A.text(46, 125 - k*6.4, t, fontsize=7.4, va='top')

    # ── ТАБЛИЦА ПАРАМЕТРОВ ПАНЕЛИ ──
    s.table(46, 100,
            ['Параметр', 'Значение'],
            [['Габарит номинальный', '100 000 × 50 000 мм'],
             ['Толщина силового пояса', '850 мм'],
             ['Кривизна: стрелка при хорде 50 000', '62 мм'],
             ['Объём металла', '4 277 м³'],
             ['Масса панели', '33 575 т'],
             ['Панелей на цилиндр', '251 327 шт.'],
             ['Суммарная длина швов', '37 700 км'],
             ['Материал', 'сталь 18Ni(300)']],
            [58, 44], rh=5.2, title='Параметры панели',
            align=['left', 'right'])

    # ── ТАБЛИЦА ТЕХНОЛОГИИ ──
    s.table(180, 100,
            ['Показатель', 'Значение', 'Примечание'],
            [['Способ получения', 'литьё', 'прокат исключён'],
             ['Предел станов по толщине', '300 мм', 'требуется 850'],
             ['Предел станов по ширине', '5 500 мм', 'требуется 50 000'],
             ['Рекорд стальной отливки (Земля)', '270 т', 'Siempelkamp, 2009'],
             ['Теплота кристаллизации', '8,15 ГДж/м²', 'отвод через подложку'],
             ['Время затвердевания', '≈4 сут', 'перепад ≤50 K'],
             ['Термонапряжение при ΔT = 100 K', '326 МПа', 'трещинообразование'],
             ['Постов литья', '≈136', 'п. 10.5']],
            [56, 26, 40], rh=5.2,
            title='Технологические показатели (гл. 10)',
            align=['left', 'right', 'left'])

    s.note(46, 44,
           'Технические требования\n'
           '1. Размеры в миллиметрах натуры. Масса панели 33 575 т.\n'
           '2. Панель получают литьём в невесомости. Прокат исключён:\n'
           '    предельная толщина листа станов 5 600 мм составляет 300 мм,\n'
           '    требуется 850 мм.\n'
           '3. На один цилиндр 251 327 панелей; суммарная длина швов 37 700 км.\n'
           '4. Расплав подвергают вакуумной дегазации и центробежному\n'
           '    рафинированию: в невесомости включения не всплывают (п. Б.8).',
           size=7.2)
    s.note(300, 44,
           ' \n'
           '5. Охлаждение принудительное через теплообменную подложку;\n'
           '    перепад по сечению не более 50 K. При 100 K термическое\n'
           '    напряжение достигает 326 МПа — образуются трещины.\n'
           '6. Отвод теплоты кристаллизации 8,15 ГДж/м²; расчётное время\n'
           '    затвердевания около 4 суток.\n'
           '7. Кромки разделывают под стыковой шов с полным проваром (узел Д).\n'
           '8. Контроль сплошности 100 %, ультразвуковой.',
           size=7.2)
    return s.save('03_panel.png', keep=globals().get('_KEEP', False))


def sheet04():
    """Лист 4. Общая компоновка станции."""
    s = Sheet('A1', title='Станция. Общая компоновка', material='—',
              mass='46,70 млрд т', sheet_no='4', sheets='7', lit='П',
              scale='1:250 000', number='ММОСО.00.000 ВО')
    A = s.ax
    M = 1/250.
    cx, cy = 250, 430

    def mark(x, y, n, dx=0, dy=0):
        A.plot([x], [y], marker='o', ms=2.0, color=C, zorder=9)
        s.line(x, y, x+dx, y+dy, 'thin')
        A.add_patch(Circle((x+dx, y+dy), 3.2, fc='white', ec=C, lw=S_THIN,
                           zorder=10))
        A.text(x+dx, y+dy, str(n), fontsize=7, ha='center', va='center',
               zorder=11, fontweight='bold')

    Lh = 49000*M/2.       # 98 мм
    R = 5000*M            # 20 мм
    gap = 62
    A.text(cx, cy+gap/2+R+40, 'Главный вид', fontsize=12, ha='center',
           fontweight='bold')

    axes_y = []
    for sgn in (+1, -1):
        ay = cy + sgn*gap/2
        axes_y.append(ay)
        cyl = Lh - R*0.9
        # корпус: цилиндр + сфероидальные торцы
        import numpy as np
        th = np.linspace(-math.pi/2, math.pi/2, 60)
        top = [(cx-cyl, ay+R), (cx+cyl, ay+R)]
        s.line(cx-cyl, ay+R, cx+cyl, ay+R)
        s.line(cx-cyl, ay-R, cx+cyl, ay-R)
        for sx in (-1, 1):
            pts = [(cx+sx*(cyl + (Lh-cyl)*math.cos(t)), ay+R*math.sin(t))
                   for t in np.linspace(-math.pi/2, math.pi/2, 60)]
            s.poly(pts, 'main')
        s.line(cx-Lh-16, ay, cx+Lh+16, ay, 'axis')
        # подшипниковые узлы и цапфы
        for sx in (-1, 1):
            A.add_patch(Rectangle((cx+sx*Lh - (3 if sx > 0 else 0), ay-3.2),
                                  3, 6.4, fc='#bbbbbb', ec=C, lw=S_MAIN))
            A.add_patch(Circle((cx+sx*(Lh+7), ay), 3.4, fc='white', ec=C,
                               lw=S_MAIN))
            s.centerlines(cx+sx*(Lh+7), ay, 3.4)
        # направление вращения
        A.annotate('', xy=(cx+18, ay+R+7), xytext=(cx-18, ay+R+7),
                   arrowprops=dict(arrowstyle='-|>,head_width=0.16,'
                                   'head_length=0.6',
                                   connectionstyle=f'arc3,rad={-0.35*sgn}',
                                   lw=S_THIN, color=C))
        A.text(cx+22, ay+R+9, 'ω', fontsize=9, fontstyle='italic')

    # ── ферменная рама (соединяет только оси) ──
    for sx in (-1, 1):
        x = cx + sx*(Lh+7)
        s.line(x, axes_y[0], x, axes_y[1], 'main')
        for k in range(6):
            y0 = axes_y[1] + k*gap/6
            y1 = axes_y[1] + (k+1)*gap/6
            s.line(x, y0, x+sx*9, (y0+y1)/2, 'thin')
            s.line(x+sx*9, (y0+y1)/2, x, y1, 'thin')
        s.line(x+sx*9, axes_y[1], x+sx*9, axes_y[0], 'thin')

    # ── реакторный блок и радиаторы позади торцов ──
    rxp = cx + Lh + 34
    A.add_patch(Rectangle((rxp, cy-16), 16, 32, fc='#e8e8e8', ec=C, lw=S_MAIN))
    A.text(rxp+8, cy, 'РУ', fontsize=8, ha='center', va='center',
           fontweight='bold')
    for k in range(5):
        yy = cy - 40 + k*20
        s.line(rxp+16, cy, rxp+30, yy, 'thin')
        A.add_patch(Rectangle((rxp+30, yy-3), 34, 6, fc='#f2f2f2', ec=C,
                              lw=S_THIN))
    A.text(rxp+47, cy+52, 'радиаторы\n1 022 км²', fontsize=7.5, ha='center')

    # ── причал ──
    A.add_patch(Rectangle((cx-Lh-30, cy-9), 14, 18, fc='white', ec=C,
                          lw=S_MAIN))
    A.text(cx-Lh-23, cy, 'П', fontsize=8, ha='center', va='center',
           fontweight='bold')
    s.line(cx-Lh-16, cy, cx-Lh-7, cy, 'main')
    s.line(cx-Lh-7, axes_y[0], cx-Lh-7, axes_y[1], 'main')

    mark(cx+Lh+7, axes_y[0], 1, 12, 22)
    mark(cx, axes_y[0]+R, 2, -34, 24)
    mark(rxp+8, cy+16, 3, -14, 34)
    mark(cx+Lh+16, cy+gap/2, 4, 6, 30)
    mark(cx-Lh-23, cy+9, 5, -14, 30)
    mark(rxp+47, cy-40, 6, 0, -26)

    s.dim_h(cx-Lh, cx+Lh, cy-gap/2-R-20, '49 000', ext_from=cy-gap/2-R)

    # ═══════ ВИД С ТОРЦА (проекционная связь по горизонтали) ═══════
    ex, ey = 640., cy
    A.text(ex, cy + gap / 2 + R + 40, 'Вид с торца', fontsize=12,
           ha='center', fontweight='bold')
    for sgn in (1, -1):
        yc = cy + sgn * gap / 2
        A.add_patch(Circle((ex, yc), R, fc='white', ec=C, lw=S_MAIN,
                           zorder=3))
        A.add_patch(Circle((ex, yc), R - 2.0, fc='none', ec=C, lw=S_THIN,
                           zorder=3))
        s.centerlines(ex, yc, R + 10)
        A.add_patch(Circle((ex, yc), 2.6, fc='#dddddd', ec=C, lw=S_THIN,
                           zorder=4))
        A.annotate('', xy=(ex + sgn * R * 0.72, yc + R * 0.72),
                   xytext=(ex - sgn * R * 0.10, yc + R * 1.02),
                   arrowprops=dict(
                       arrowstyle='-|>,head_width=0.15,head_length=0.5',
                       lw=S_THIN, color=C,
                       connectionstyle='arc3,rad=%.2f' % (0.35 * sgn)))
        A.text(ex + sgn * R * 0.86, yc + R * 0.86, 'ω', fontsize=8)
    # ферменная рама между осями
    s.line(ex, cy - gap / 2, ex, cy + gap / 2, 'main')
    for k in range(6):
        y0f = cy - gap / 2 + k * gap / 6
        y1f = cy - gap / 2 + (k + 1) * gap / 6
        s.line(ex - 7, y0f, ex + 7, y1f, 'thin')
        s.line(ex + 7, y0f, ex - 7, y1f, 'thin')
    s.dim_v(cy - gap / 2, cy + gap / 2, ex + R + 26, '13 000',
            ext_from=ex + R)
    s.dim_h(ex - R, ex + R, cy - gap / 2 - R - 20, '10 000',
            ext_from=cy - gap / 2 - R)
    A.text(ex, cy - gap / 2 - R - 34,
           'Цилиндры вращаются встречно;\nсуммарный момент импульса равен нулю',
           fontsize=7.2, ha='center', va='top')
    # проекционная связь главный вид — вид с торца (по осям цилиндров)
    for yy in (cy + gap / 2, cy - gap / 2):
        s.link(cx + Lh + 118, yy, ex - R - 22, yy)

    # ═══════ Е — ПОДШИПНИКОВЫЙ УЗЕЛ ЦАПФЫ ═══════
    hx, hy = 640., 250.
    A.text(hx, hy + 62, 'Е  (1 : 2 000)  подшипниковый узел цапфы',
           fontsize=10.5, ha='center', fontweight='bold')
    # цапфа
    A.add_patch(Rectangle((hx - 78, hy - 9), 78, 18, fc='#cfcfcf', ec=C,
                          lw=S_MAIN, zorder=3))
    s.hatch(hx - 78, hy - 9, hx, hy + 9, step=2.6)
    A.text(hx - 62, hy + 14, 'цапфа торца цилиндра', fontsize=7)
    # обойма подшипника
    A.add_patch(Rectangle((hx - 6, hy - 26), 30, 52, fc='#eaeaea', ec=C,
                          lw=S_MAIN, zorder=2))
    s.hatch(hx - 6, hy - 26, hx + 24, hy + 26, step=3.0, ang=135)
    # тела качения
    for k in (-1, 1):
        A.add_patch(Circle((hx + 9, hy + k * 16), 6.2, fc='white', ec=C,
                           lw=S_MAIN, zorder=5))
        s.centerlines(hx + 9, hy + k * 16, 9)
    # опора на раму
    A.add_patch(Rectangle((hx + 24, hy - 34), 16, 68, fc='#dcdcdc', ec=C,
                          lw=S_MAIN, zorder=2))
    s.hatch(hx + 24, hy - 34, hx + 40, hy + 34, step=3.0)
    A.text(hx + 46, hy, 'ферменная рама\n(неподвижная)', fontsize=7,
           va='center')
    s.centerlines(hx - 40, hy, 0)
    s.line(hx - 84, hy, hx + 46, hy, 'axis')
    s.dim_v(hy - 9, hy + 9, hx - 90, '3 000', ext_from=hx - 78)
    s.leader(hx + 9, hy + 16, hx - 30, hy + 44, 'тела качения')
    A.text(hx, hy - 46,
           'Соединение цилиндров — только по осям через подшипники.\n'
           'Боковые поверхности вращающихся оболочек\n'
           'механически не связаны (п. 4.9).',
           fontsize=7.2, ha='center', va='top')

    s.dim_v(cy-gap/2-R, cy+gap/2+R, cx-Lh-46, '27 000', ext_from=cx-Lh-40)
    s.dim_v(axes_y[1], axes_y[0], cx+Lh+22, '13 000', ext_from=cx+Lh+7)

    legend = ['1 — Подшипниковый узел цапфы, 4 шт.',
              '2 — Цилиндр (лист 1), 2 шт.',
              '3 — Реакторная установка, 4 × 366 ГВт (тепл.)',
              '4 — Ферменная рама, связывает только оси',
              '5 — Причал невращающейся части',
              '6 — Низкотемпературный радиатор, ε = 0,95']
    A.text(46, 190, 'Обозначения позиций', fontsize=8.5, fontweight='bold')
    for k, t in enumerate(legend):
        A.text(46 + (k // 3)*300, 183 - (k % 3)*6.4, t, fontsize=7.4, va='top')

    # ── МАССОВАЯ СВОДКА СТАНЦИИ ──
    s.table(46, 158,
            ['Составляющая', 'Цилиндр', 'Станция', '%'],
            [['Пакет обшивки с силовым набором', '13,426', '26,85', '57'],
             ['Грунт растительный', '4,06', '8,13', '17'],
             ['Атмосфера', '3,77', '7,55', '16'],
             ['Вода', '0,59', '1,17', '3'],
             ['Ферменная рама и узлы', '—', '3,00', '6'],
             ['ИТОГО', '21,85', '46,70', '100']],
            [60, 22, 22, 13], rh=5.2,
            title='Массовая сводка, млрд т (п. Б.16)',
            align=['left', 'right', 'right', 'right'])

    # ── ЭНЕРГОБАЛАНС ──
    s.table(215, 158,
            ['Статья расхода', 'ГВт', '%'],
            [['Осевые светотепловые балки', '503', '69,73'],
             ['Тепловые насосы', '96', '13,31'],
             ['Удержание в точке L1 (п. 11.5)', '63', '8,79'],
             ['Резерв и потери', '33', '4,57'],
             ['Жизнеобеспечение', '20', '2,77'],
             ['Быт, транспорт, промышленность', '6', '0,83'],
             ['ИТОГО электрическая мощность', '721', '100']],
            [62, 18, 18], rh=5.2, title='Энергобаланс станции (п. Б.15)',
            align=['left', 'right', 'right'])

    # ── РЕСУРСЫ ──
    s.table(345, 158,
            ['Материал', 'Потребность', 'Источник'],
            [['Сталь 18Ni(300), пояс', '20,83', '(6178) 1986 DA'],
             ['Сталь нерж., гермооболочка', '1,22', '(6178) 1986 DA'],
             ['Сталь всего с набором', '22,05', '—'],
             ['Сырьё с потерями 25 %', '29,4', '94 % металла 1986 DA'],
             ['Реголит, боросиликат', '4,65', '(6178) 1986 DA'],
             ['Грунт растительный', '8,13', '24 Themis, 10 Hygiea'],
             ['Вода', '1,17', '24 Themis'],
             ['Азот', '5,51', '10 Hygiea']],
            [52, 26, 60], rh=5.2,
            title='Потребность в материалах, млрд т (п. 9, Б.16)',
            align=['left', 'right', 'left'])

    s.note(46, 92,
           'Технические требования\n'
           '1. Цилиндры вращаются встречно с частотой 0,423 об/мин;\n'
           '    суммарный момент импульса равен нулю.\n'
           '2. Соединение цилиндров — только по осям через подшипниковые\n'
           '    узлы. Соединение боковых поверхностей недопустимо.\n'
           '3. Реакторы и высокотемпературные радиаторы вынесены на раму\n'
           '    позади задних торцов, вне обитаемого объёма.\n'
           '4. Масса станции 46,70 млрд т, из них конструкционный пакет\n'
           '    26,85 млрд т, атмосфера 7,55 млрд т (п. Б.16).',
           size=7.2)
    s.note(290, 92,
           ' \n'
           '5. Электрическая мощность 721 ГВт, тепловая 1 603 ГВт.\n'
           '6. Низкотемпературный радиатор: ε = 0,95, температура 60 °C,\n'
           '    удельный поток 662 Вт/м², площадь 1 022 км² при\n'
           '    располагаемых 1 477 км² (запас 1,45).\n'
           '7. Высокотемпературный контур 800 °C: 71,4 кВт/м², 12,4 км².\n'
           '8. Место — точка L1 системы Земля — Солнце. Ось станции\n'
           '    неподвижна в инерциальном пространстве и на Солнце\n'
           '    не ориентируется; освещение реакторное (п. 11.6).\n'
           '9. Расчётное население 1 000 000 человек (п. Б.15).',
           size=7.2)
    return s.save('04_station.png', keep=globals().get('_KEEP', False))


def sheet05():
    """Лист 5. Карантинный контур. Схема."""
    s = Sheet('A2', title='Карантинный контур. Схема',
              mass='—', sheet_no='5', sheets='7', lit='П',
              material='—', scale='Б/М', number='ММОСО.02.000')
    A = s.ax
    x0, y0 = 70, 350
    bw, bh, dx = 92, 26, 116
    rows = [
        ('Люди',   ['Причал', 'Шлюз, санобработка', 'Изолятор 40 сут', 'Шахта']),
        ('Грузы',  ['Причал', 'Вакуум 72 ч', 'Гамма 25 кГр / 200 °C', 'Склад']),
        ('Биомат.',['Причал', 'Документарный контроль', 'Посев, 14 сут', 'Лаборатория']),
        ('Сырьё',  ['Причал', 'Переплавка > 1 500 °C', 'Контроль партии', 'Завод']),
    ]
    for ri, (nm, steps) in enumerate(rows):
        y = y0 - ri*46
        A.text(x0-12, y+bh/2, nm, fontsize=8.5, fontweight='bold',
               ha='right', va='center')
        for si, st in enumerate(steps):
            x = x0 + si*dx
            fc = '#ffffff' if si in (0, 3) else '#ededed'
            A.add_patch(Rectangle((x, y), bw, bh, fc=fc, ec=C, lw=S_MAIN))
            A.text(x+bw/2, y+bh/2, st, fontsize=8, ha='center', va='center', wrap=True)
            if si < 3:
                A.annotate('', xy=(x+dx, y+bh/2), xytext=(x+bw, y+bh/2),
                           arrowprops=dict(arrowstyle='-|>,head_width=0.16,'
                                           'head_length=0.6', lw=S_MAIN, color=C))
    # граница контура
    A.add_patch(Rectangle((x0+dx-11, y0-3*46-10), 2*dx+bw-dx+11, 3*46+bh+20,
                          fill=False, ec=C, lw=S_MAIN, ls=(0, (8, 4))))
    A.text(x0+dx+bw, y0+bh+15, 'ГРАНИЦА КАРАНТИННОГО КОНТУРА',
           fontsize=8.5, fontweight='bold', ha='center')
    A.text(x0+bw/2, y0+bh+9, 'вне контура', fontsize=7.5, ha='center',
           fontstyle='italic')
    A.text(x0+3*dx+bw/2, y0+bh+9, 'внутри станции', fontsize=7.5,
           ha='center', fontstyle='italic')

    # ── ТАБЛИЦА РЕЖИМОВ ОБРАБОТКИ ──
    s.table(70, 168,
            ['Поток', 'Операция', 'Режим', 'Длительность', 'Контроль'],
            [['Люди', 'Шлюз, санобработка', 'душ, смена одежды', '2 ч',
              'осмотр'],
             ['', 'Изолятор', 'бокс на 1–2 чел.', '40 сут',
              'анализы 1 раз в 10 сут'],
             ['Грузы', 'Вакуумирование', '< 1 Па', '72 ч', 'манометрия'],
             ['', 'Гамма-облучение', '25 кГр либо 200 °C', '6 ч',
              'дозиметрия партии'],
             ['Биоматериалы', 'Документарный контроль', 'паспорт штамма', '—',
              'сверка реестра'],
             ['', 'Посев на среды', '37 °C, аэробно и анаэробно', '14 сут',
              'микробиология'],
             ['Сырьё', 'Переплавка', '> 1 500 °C', 'по циклу печи',
              'спектральный анализ'],
             ['', 'Контроль партии', 'проба на 1 000 т', '—', 'сертификат']],
            [24, 46, 48, 28, 46], rh=5.2,
            title='Режимы карантинной обработки',
            align=['left', 'left', 'left', 'center', 'left'])

    # ── ТАБЛИЦА СРОКОВ ИНКУБАЦИИ ──
    s.table(70, 96,
            ['Заболевание', 'Инкубация, сут'],
            [['Гепатит A', '50'],
             ['Брюшной тиф', '30'],
             ['Корь', '21'],
             ['Ветряная оспа', '21'],
             ['Принятый срок карантина', '40']],
            [50, 30], rh=5.2, title='Обоснование срока карантина',
            align=['left', 'right'])

    # ── ПРОПУСКНАЯ СПОСОБНОСТЬ ──
    s.table(180, 96,
            ['Показатель', 'Значение'],
            [['Население станции', '1 000 000 чел.'],
             ['Заданный срок заселения', '10 лет'],
             ['Требуемый поток R', '100 000 чел./год'],
             ['То же в сутки', '274 чел./сут'],
             ['Выдержка Q', '40 сут = 0,1095 года'],
             ['Мест в изоляторе N = R·Q', '10 951'],
             ['Циклов изолятора в год', '9,13'],
             ['Площадь блока (20 м²/чел.)', '21,9 га'],
             ['Транспорт двух цилиндров', '32 400 чел./сут'],
             ['Запас по транспорту', '118 крат']],
            [62, 42], rh=5.2, title='Пропускная способность контура',
            align=['left', 'right'])

    s.note(300, 96,
           'Технические требования\n'
           '1. Контур размещается на неподвижной ферменной раме\n'
           '    между причалом\n'
           '    и устьем шахты и является единственным входом на станцию.\n'
           '2. Карантин людей 40 суток — по наибольшему сроку инкубации\n'
           '    (гепатит A — 50 сут, брюшной тиф — 30, корь — 21).\n'
           '3. Латентные формы (туберкулёз, гепатит B) выявляются анализом,\n'
           '    выдержкой не выявляются.\n'
           '4. Размер изолятора определяется формулой N = R·Q: при потоке\n'
           '    R = 100 000 чел/год и выдержке Q = 40 сут N = 10 951 место.\n'
           '5. Срок заселения станции определяется санитарным\n'
           '    барьером и составляет 10 лет: транспорт\n'
           '    (32 400 чел/сут) избыточен по отношению\n'
           '    к потребности 274 чел/сут в 118 раз.\n'
           '6. Воздух шлюза сбрасывается в вакуум: 100 000 м³ за цикл,\n'
           '    913 000 м³ в год — 0,02 % массы атмосферы цилиндра.\n'
           '7. Реголит и сталь стерильны после переплавки, обработке\n'
           '    не подлежат.',
           size=7.2)
    return s.save('05_quarantine.png', keep=globals().get('_KEEP', False))


def sheet06():
    """Лист 6. Размещение, ориентация и балансировка (глава 11)."""
    s = Sheet('A1', title='Размещение и ориентация станции\nСхема',
              material='—', scale='Б/М', number='ММОСО.00.100',
              mass='—', sheet_no='6', sheets='7', lit='П')
    A = s.ax

    # ═══════ ВИД 1: ТОЧКА L1 И СХЕМА УДЕРЖАНИЯ ═══════
    ex, ey = 205., 440.
    A.text(ex, ey + 118, 'Точка L1 системы Земля — Солнце',
           fontsize=11.5, ha='center', fontweight='bold')
    # линия Солнце — Земля
    s.line(ex - 150, ey, ex + 60, ey, 'axis')
    # Солнце (слева, обрезано рамкой вида)
    A.add_patch(Circle((ex - 158, ey), 20, fc='#f6e3a8', ec=C, lw=S_MAIN,
                       zorder=3))
    A.text(ex - 158, ey, 'Солнце', fontsize=7.0, ha='center', va='center',
           zorder=4)
    # Земля
    A.add_patch(Circle((ex + 42, ey), 10, fc='#c8d8e8', ec=C, lw=S_MAIN,
                       zorder=4))
    A.text(ex + 42, ey - 18, 'Земля', fontsize=7.4, ha='center')
    # точка L1 и станция
    lx = ex + 42 - 26
    A.add_patch(Rectangle((lx - 6, ey - 6), 12, 12, fc='white', ec=C,
                          lw=S_MAIN, zorder=5))
    A.text(lx, ey, 'L1', fontsize=7.2, ha='center', va='center',
           fontweight='bold', zorder=6)
    s.leader(lx, ey + 6, lx - 26, ey + 46, 'станция ММОСО′Н')
    # гало-орбита вокруг L1
    A.add_patch(Arc((lx, ey), 46, 26, theta1=0, theta2=360, lw=S_THIN,
                    ec=C, ls=(0, (4, 2)), zorder=3))
    A.text(lx + 30, ey - 20, 'гало-орбита', fontsize=6.8, ha='left')
    s.dim_h(lx, ex + 42, ey + 34, '1,5 млн км', ext_from=ey + 8)
    # вектор ухода и вектор коррекции
    A.annotate('', xy=(lx - 40, ey - 34), xytext=(lx, ey - 12),
               arrowprops=dict(
                   arrowstyle='-|>,head_width=0.16,head_length=0.6',
                   lw=S_MAIN, color='#c05030'))
    A.text(lx - 44, ey - 40, 'уход: удвоение\nотклонения за 23 сут',
           fontsize=6.8, ha='center', va='top', color='#c05030')
    A.annotate('', xy=(lx + 34, ey - 30), xytext=(lx + 6, ey - 10),
               arrowprops=dict(
                   arrowstyle='-|>,head_width=0.16,head_length=0.6',
                   lw=S_MAIN, color='#2a6ea8'))
    A.text(lx + 40, ey - 36, 'тяга удержания\n2 960 кН непрерывно',
           fontsize=6.8, ha='center', va='top', color='#2a6ea8')
    A.text(ex, ey - 78,
           'Точка L1 коллинеарна и неустойчива, но Солнце в ней\n'
           'не заслоняется Землёй никогда: затмений нет,\n'
           'аккумулирование энергии не требуется.\n'
           'Плата — постоянно работающая установка удержания.',
           fontsize=7.4, ha='center', va='top')

    # ═══════ ВИД 2: ОРИЕНТАЦИЯ ОСИ И ЗЕРКАЛА ═══════
    ox, oy = 520., 430.
    A.text(ox, oy + 120, 'Ориентация оси и энергопитание',
           fontsize=11.5, ha='center', fontweight='bold')
    # станция схематично — два цилиндра, ось горизонтальна и НЕПОДВИЖНА
    for sgn in (1, -1):
        cyy = oy + sgn * 26
        A.add_patch(Rectangle((ox - 52, cyy - 11), 104, 22, fc='white',
                              ec=C, lw=S_MAIN, zorder=3))
        A.add_patch(Rectangle((ox - 48, cyy - 2.2), 96, 4.4, fc='#f0d890',
                              ec=C, lw=S_THIN, zorder=5))
    s.line(ox, oy - 26, ox, oy + 26, 'main')
    A.text(ox - 34, oy + 54, 'ось станции — фиксирована\nв инерциальном пространстве',
           fontsize=7.2, ha='center', va='bottom')
    # реакторная установка на раме — источник света и энергии
    A.add_patch(Rectangle((ox - 116, oy - 24), 30, 48, fc='#e8d0c0', ec=C,
                          lw=S_MAIN, zorder=4))
    A.text(ox - 101, oy, 'РУ', fontsize=8.5, ha='center', va='center',
           fontweight='bold', zorder=5)
    A.text(ox - 101, oy - 30, '4 × 401 ГВт\n(тепловых)', fontsize=6.8,
           ha='center', va='top')
    # шины к осевым балкам обоих цилиндров
    for sgn in (1, -1):
        cyy = oy + sgn * 26
        s.line(ox - 86, oy + sgn * 8, ox - 60, oy + sgn * 8, 'main')
        s.line(ox - 60, oy + sgn * 8, ox - 60, cyy, 'main')
        s.line(ox - 60, cyy, ox - 52, cyy, 'main')
    A.text(ox - 74, oy + 46, 'сверхпроводящие шины YBCO', fontsize=6.8,
           ha='center')
    s.leader(ox + 20, oy + 26, ox - 6, oy + 76,
             'осевая светотепловая балка —\nединственный источник света')

    A.text(ox, oy - 62,
           'Поворот оси станции требует момента 2,41·10¹² Н·м —\n'
           'пара сил 185 МН на плече 13 км, 59,6 млн т рабочего тела\n'
           'в год. Ось не поворачивают. Освещение реакторное, зеркал\n'
           'у станции нет, и световой режим внутри цилиндра\n'
           'от ориентации оси не зависит вовсе (п. 11.6).',
           fontsize=7.4, ha='center', va='top')

    # ═══════ ВИД 3: БАЛАНСИРОВОЧНЫЕ ЦИСТЕРНЫ (сечение) ═══════
    bx, by = 745., 430.
    A.text(bx, by + 120, 'Балансировка. Сечение', fontsize=11.5,
           ha='center', fontweight='bold')
    Rb = 62.
    A.add_patch(Circle((bx, by), Rb, fc='none', ec=C, lw=S_MAIN, zorder=3))
    A.add_patch(Circle((bx, by), Rb - 5, fc='none', ec=C, lw=S_THIN,
                       zorder=3))
    s.centerlines(bx, by, Rb + 12)
    # 12 цистерн по кольцу
    for k in range(12):
        a = math.radians(k * 30 + 15)
        cxx, cyy = bx + (Rb - 11) * math.cos(a), by + (Rb - 11) * math.sin(a)
        A.add_patch(Circle((cxx, cyy), 5.0, fc='#bcd8ee', ec=C, lw=S_THIN,
                           zorder=4))
    # неуравновешенная масса
    A.add_patch(Circle((bx + (Rb - 11) * math.cos(math.radians(75)),
                        by + (Rb - 11) * math.sin(math.radians(75))), 5.0,
                       fc='#e08060', ec=C, lw=S_MAIN, zorder=5))
    s.leader(bx + 18, by + 62, bx + 6, by + 100,
             'сектор с избытком массы')
    A.annotate('', xy=(bx - 34, by - Rb - 12), xytext=(bx + 34, by - Rb - 12),
               arrowprops=dict(
                   arrowstyle='<|-|>,head_width=0.16,head_length=0.5',
                   lw=S_THIN, color=C))
    A.text(bx, by - Rb - 16, 'перекачка воды по кольцу', fontsize=7.0,
           ha='center', va='top')
    A.text(bx, by - Rb - 30,
           'Допуск 1 020 т неуравновешенной массы на ободе\n'
           '(4,7·10⁻⁶ % массы цилиндра) при нагрузке 10 МН на узел.\n'
           'Кольцо цистерн 1,0 млн м³ воды, перекачка по сигналу\n'
           'датчиков вибрации подшипников (п. 11.7).',
           fontsize=7.4, ha='center', va='top')

    # ═══════ ТАБЛИЦА РЕШЕНИЙ ГЛАВЫ 11 ═══════
    s.table(46, 232,
            ['Вопрос', 'Было в ред. 7.0', 'Принято', 'Пункт'],
            [['Место размещения', 'L1 Земля — Солнце', 'L1, решение сохранено', '11.5'],
             ['Удержание', 'ксенон, 10 кг/сут', 'реголит, 8 524 т/сут', '11.5'],
             ['Ориентация оси', 'на Солнце', 'фиксирована; зеркал нет', '11.6'],
             ['Балансировка', 'не рассматривалась', 'цистерны 1,0 млн м³', '11.7'],
             ['Микрометеориты', 'не рассматривались', 'парируются радзащитой', '11.1'],
             ['Отходы', 'не рассматривались', 'полное замыкание цикла', '11.2'],
             ['Умершие', 'не рассматривались', 'кремация, колумбарий', '11.3'],
             ['Население', '1 млн постоянно', 'диапазон 0,6…1,2 млн', '11.4'],
             ['Оборот воды', 'только запас', 'регенерация 98 %', '11.8'],
             ['Стоимость и право', 'не рассматривались', 'энергетич. оценка; право', '13, 15.3']],
            [46, 46, 60, 16], rh=5.4, title='Решения главы 11',
            align=['left', 'left', 'left', 'center'])

    # ═══════ ЧИСЛОВАЯ СВОДКА ═══════
    s.table(340, 232,
            ['Показатель', 'Значение'],
            [['Удаление от Земли', '1,5 млн км'],
             ['Затмений', 'нет'],
             ['Задержка связи с Землёй', '5,0 с в одну сторону'],
             ['Время удвоения отклонения', '23 сут'],
             ['Потребное приращение скорости', '2 м/с в год'],
             ['Тяга непрерывная', '2 960 кН'],
             ['Скорость истечения', '30 км/с (Isp 3 058 с)'],
             ['Мощность потребляемая', '63,4 ГВт = 8,79 %'],
             ['Рабочее тело', 'дроблёный реголит'],
             ['Расход рабочего тела', '3,11 млн т/год = 8 524 т/сут'],
             ['За 100 лет', '311 млн т = 0,67 % массы'],
             ['Момент слежения за Солнцем', '2,41·10¹² Н·м']],
            [62, 46], rh=5.4, title='Размещение: числовая сводка',
            align=['left', 'right'])

    # ═══════ ТЕХНИЧЕСКИЕ ТРЕБОВАНИЯ ═══════
    s.note(46, 118,
           'Технические требования\n'
           '1. Схема без масштаба; расстояния указаны числом.\n'
           '2. Точка размещения — L1 системы Земля — Солнце; точка\n'
           '    неустойчива, удержание непрерывное (п. 11.5).\n'
           '3. Ось станции не поворачивается. Освещение обитаемого\n'
           '    объёма реакторное; зеркал и паруса у станции нет.\n'
           '4. Встречное вращение цилиндров обнуляет момент импульса\n'
           '    станции; внешние моменты парируются тягой на раме.',
           size=7.2)
    s.note(340, 118,
           ' \n'
           '5. Балансировка — непрерывный эксплуатационный процесс,\n'
           '    а не разовая операция монтажа.\n'
           '6. Рабочее тело балансировки — вода из станционного запаса\n'
           '    1,17 млрд т; удержания — дроблёный реголит.\n'
           '7. Затмений в точке L1 нет; аккумулирования энергии\n'
           '    на тёмный период проект не предусматривает.\n'
           '8. Экономическая оценка дана в энергетических единицах\n'
           '    (970 ЭДж, окупаемость 43 года) — п. 15.3; правовое\n'
           '    положение — гл. 13.',
           size=7.2)
    return s.save('06_placement.png',
                  keep=globals().get('_KEEP', False))

def sheet07():
    """Лист 7. Узлы крепления набора и трасса транспортной шахты."""
    s = Sheet('A1', title='Узлы крепления набора.\nТрасса шахты',
              material='Сталь 18Ni(300)', scale='см. виды',
              number='ММОСО.01.700 СБ', mass='—',
              sheet_no='7', sheets='7', lit='П')
    A = s.ax

    # ═══════ УЗЕЛ I: ШПАНГОУТ — СТРИНГЕР (пересечение) ═══════
    ax1, ay1 = 165., 448.
    A.text(ax1, ay1 + 96, 'Узел I  (1 : 50)', fontsize=11,
           ha='center', fontweight='bold')
    A.text(ax1, ay1 + 88, 'пересечение шпангоута и стрингера',
           fontsize=7.4, ha='center', fontstyle='italic')
    # обшивка сверху (в разрезе)
    A.add_patch(Rectangle((ax1 - 100, ay1 + 44), 200, 17, fc='#b8b8b8',
                          ec=C, lw=S_MAIN, zorder=3))
    s.hatch(ax1 - 100, ay1 + 44, ax1 + 100, ay1 + 61, step=3.0)
    A.text(ax1 - 96, ay1 + 52, 'обшивка 850', fontsize=6.6, va='center',
           zorder=7)
    # шпангоут — вертикальная стенка вниз от обшивки
    A.add_patch(Rectangle((ax1 - 4, ay1 - 44), 8, 88, fc='#cfcfcf', ec=C,
                          lw=S_MAIN, zorder=3))
    s.hatch(ax1 - 4, ay1 - 44, ax1 + 4, ay1 + 44, step=2.4)
    # нижняя полка шпангоута
    A.add_patch(Rectangle((ax1 - 25, ay1 - 52), 50, 8, fc='#cfcfcf', ec=C,
                          lw=S_MAIN, zorder=3))
    s.hatch(ax1 - 25, ay1 - 52, ax1 + 25, ay1 - 44, step=2.4)
    A.text(ax1 + 30, ay1 - 48, 'полка шпангоута 2 500 × 40', fontsize=6.8,
           va='center')
    # ВЫРЕЗ в стенке шпангоута для пропуска стрингера
    A.add_patch(Rectangle((ax1 - 4, ay1 + 22), 8, 14, fc='white', ec=C,
                          lw=S_THIN, zorder=5))
    # стрингер проходит сквозь вырез
    for sgn in (-1, 1):
        A.add_patch(Rectangle((ax1 + sgn * 4, ay1 + 24), sgn * 74, 10,
                              fc='#dcdcdc', ec=C, lw=S_MAIN, zorder=4))
    A.add_patch(Rectangle((ax1 - 78, ay1 + 24), 156, 10, fc='#dcdcdc',
                          ec=C, lw=S_MAIN, zorder=4))
    s.hatch(ax1 - 78, ay1 + 24, ax1 + 78, ay1 + 34, step=2.4)
    A.text(ax1 - 74, ay1 + 29, 'стрингер 1 200 × 600', fontsize=6.6,
           va='center', zorder=7)
    # компенсирующая накладка вокруг выреза
    for sgn in (-1, 1):
        A.add_patch(Rectangle((ax1 + sgn * 4, ay1 + 14), sgn * 3.0, 30,
                              fc='#9fb8cc', ec=C, lw=S_MAIN, zorder=6))
    s.leader(ax1 + 7, ay1 + 20, ax1 + 54, ay1 - 6,
             'накладка 30 × 800,\nкомпенсирует вырез')
    # сварные швы
    s.weld(ax1 - 4, ay1 + 44, ax1 - 62, ay1 + 76, 'угловой K = 40')
    s.weld(ax1 + 78, ay1 + 34, ax1 + 62, ay1 + 76, 'по контуру K = 25')
    s.dim_v(ay1 + 22, ay1 + 36, ax1 - 46, '1 400', ext_from=ax1 - 20)
    s.dim_h(ax1 - 4, ax1 + 4, ay1 - 62, '40', ext_from=ay1 - 52)
    A.text(ax1, ay1 - 76,
           'Стрингер непрерывен и проходит сквозь вырез в стенке\n'
           'шпангоута; шпангоут в месте выреза усилен накладками.\n'
           'Разрывать стрингер на шпангоуте не допускается:\n'
           'стык в зоне концентрации напряжений недопустим.',
           fontsize=7.2, ha='center', va='top')

    # ═══════ УЗЕЛ II: ОБШИВКА — НАБОР (крепление панели) ═══════
    ax2, ay2 = 470., 448.
    A.text(ax2, ay2 + 96, 'Узел II  (1 : 20)', fontsize=11,
           ha='center', fontweight='bold')
    A.text(ax2, ay2 + 88, 'примыкание панели обшивки к стрингеру',
           fontsize=7.4, ha='center', fontstyle='italic')
    # две панели встык
    for sgn in (-1, 1):
        A.add_patch(Rectangle((ax2 + sgn * 5, ay2 + 30), sgn * 92, 28,
                              fc='#b8b8b8', ec=C, lw=S_MAIN, zorder=3))
    s.hatch(ax2 - 97, ay2 + 30, ax2 - 5, ay2 + 58, step=3.0)
    s.hatch(ax2 + 5, ay2 + 30, ax2 + 97, ay2 + 58, step=3.0)
    # разделка кромок под сварку — X-образная
    A.add_patch(Polygon([(ax2 - 5, ay2 + 58), (ax2 + 5, ay2 + 58),
                         (ax2 + 1.6, ay2 + 44), (ax2 - 1.6, ay2 + 44)],
                        closed=True, fc='#7fa8c8', ec=C, lw=S_THIN,
                        zorder=4))
    A.add_patch(Polygon([(ax2 - 5, ay2 + 30), (ax2 + 5, ay2 + 30),
                         (ax2 + 1.6, ay2 + 44), (ax2 - 1.6, ay2 + 44)],
                        closed=True, fc='#7fa8c8', ec=C, lw=S_THIN,
                        zorder=4))
    s.leader(ax2, ay2 + 56, ax2 + 44, ay2 + 80,
             'шов X-образный, полный провар,\nконтроль УЗК 100 %')
    # подкладная планка снизу шва
    A.add_patch(Rectangle((ax2 - 22, ay2 + 22), 44, 8, fc='#dcdcdc', ec=C,
                          lw=S_MAIN, zorder=4))
    s.hatch(ax2 - 22, ay2 + 22, ax2 + 22, ay2 + 30, step=2.2)
    s.leader(ax2 - 20, ay2 + 26, ax2 - 66, ay2 + 4,
             'подкладная планка 800,\nостаётся в конструкции')
    # стрингер под стыком — тавр
    A.add_patch(Rectangle((ax2 - 3, ay2 - 34), 6, 56, fc='#cfcfcf', ec=C,
                          lw=S_MAIN, zorder=3))
    A.add_patch(Rectangle((ax2 - 24, ay2 - 42), 48, 8, fc='#cfcfcf', ec=C,
                          lw=S_MAIN, zorder=3))
    s.hatch(ax2 - 3, ay2 - 34, ax2 + 3, ay2 + 22, step=2.2)
    s.hatch(ax2 - 24, ay2 - 42, ax2 + 24, ay2 - 34, step=2.2)
    A.text(ax2 + 30, ay2 - 38, 'стрингер по оси стыка', fontsize=6.8,
           va='center')
    s.weld(ax2 + 3, ay2 + 16, ax2 + 52, ay2 - 12, 'угловой двусторонний')
    s.dim_v(ay2 + 30, ay2 + 58, ax2 + 110, '850', ext_from=ax2 + 97)
    s.dim_h(ax2 - 5, ax2 + 5, ay2 + 70, '6 000', ext_from=ay2 + 58)
    A.text(ax2, ay2 - 58,
           'Стык панелей всегда располагается по оси элемента набора:\n'
           'стрингер служит подкладкой при сварке и воспринимает\n'
           'усилие в случае трещины по шву. Стык на весу запрещён.',
           fontsize=7.2, ha='center', va='top')

    # ═══════ УЗЕЛ III: ТРАССА ШАХТЫ В ТОЛЩЕ КУПОЛА ═══════
    tx, ty = 735., 415.
    A.text(tx, ty + 116, 'Трасса транспортной шахты  (1 : 200 000)',
           fontsize=11, ha='center', fontweight='bold')
    RR = 62.
    CC = 56.
    # контур торцевого купола (четверть сфероида) в разрезе
    th = _np.linspace(0, math.pi/2, 140)
    xo = [tx + RR*math.sin(t) for t in th]
    yo = [ty + CC*math.cos(t) for t in th]
    xi = [tx + (RR-9)*math.sin(t) for t in th]
    yi = [ty + (CC-9)*math.cos(t) for t in th]
    A.add_patch(Polygon(list(zip(xo, yo)) + list(zip(xi[::-1], yi[::-1])),
                        closed=True, fc='#d8d8d8', ec=C, lw=S_MAIN,
                        zorder=3))
    s.hatch_poly(list(zip(xo, yo)) + list(zip(xi[::-1], yi[::-1])),
                 step=3.4)
    # ось и обод
    s.line(tx - 16, ty, tx + RR + 18, ty, 'main')
    s.line(tx, ty - 14, tx, ty + CC + 18, 'axis')
    A.text(tx - 4, ty + CC + 22, 'ось цилиндра', fontsize=7.0, ha='right')
    A.text(tx + RR + 20, ty - 5, 'обод', fontsize=7.0, ha='left')
    # ТРАССА ШАХТЫ — в толще пакета, от оси к ободу
    xs = [tx + (RR-4.5)*math.sin(t) for t in th]
    ys = [ty + (CC-4.5)*math.cos(t) for t in th]
    A.add_line(Line2D(xs, ys, lw=2.0, color='#c04020', zorder=6))
    s.leader(xs[60], ys[60], tx + 52, ty + 80,
             'шахта: трасса 7 429 м\nв толще купола')
    # устья
    A.add_patch(Circle((xs[0], ys[0]), 4.0, fc='white', ec='#c04020',
                       lw=S_MAIN, zorder=7))
    A.add_patch(Circle((xs[-1], ys[-1]), 4.0, fc='white', ec='#c04020',
                       lw=S_MAIN, zorder=7))
    A.text(xs[0] + 7, ys[0] + 5, 'верхнее устье\nу подшипникового узла',
           fontsize=6.8, va='center')
    A.text(xs[-1] - 6, ys[-1] - 14, 'нижнее устье Ø30 000\nв зоне I',
           fontsize=6.8, ha='right', va='center')
    # причал снаружи
    A.add_patch(Rectangle((tx - 30, ty + CC + 4), 18, 12, fc='white',
                          ec=C, lw=S_MAIN, zorder=5))
    A.text(tx - 21, ty + CC + 10, 'П', fontsize=7.4, ha='center',
           va='center', fontweight='bold', zorder=6)
    s.line(tx - 12, ty + CC + 10, xs[0], ys[0], 'main')
    A.text(tx - 40, ty + CC + 10, 'причал\n(неподвижная рама)',
           fontsize=6.8, ha='right', va='center')
    s.dim_v(ty, ty + CC, tx - 30, '4 500', ext_from=tx - 16)
    s.dim_h(tx, tx + RR, ty - 24, '5 000', ext_from=ty)
    A.text(tx, ty - 40,
           'Трасса проложена по меридиану купола в толще пакета\n'
           'и в обитаемый объём не выходит. Длина 7 429 м\n'
           'при длине меридиана 7 466 м; средний уклон 42,3°.\n'
           'Время в пути 17,8 мин, скорость у обода 19,5 м/с,\n'
           'у оси обращается в нуль — торможение самопроизвольное.',
           fontsize=7.2, ha='center', va='top')

    # ═══════ ТАБЛИЦА УЗЛОВ ═══════
    s.spec_table(46, 268, [
        ['1', 'Шпангоут 5 000 × 2 500, стенка 40', '400', 'лист 2'],
        ['2', 'Стрингер 1 200 × 600, стенка 40', '628', 'непрерывный'],
        ['3', 'Накладка компенсирующая 30 × 800', '2 512', 'у каждого выреза'],
        ['4', 'Панель обшивки 850', '251 327', 'лист 3'],
        ['5', 'Планка подкладная 800 × 40', '—', 'по длине швов'],
        ['6', 'Шахта транспортная', '2', 'ММОСО.01.200'],
    ], widths=(11, 78, 20, 34))

    s.note(300, 268,
           'Технические требования\n'
           '1. Размеры в миллиметрах натуры.\n'
           '2. Стрингеры непрерывны по всей длине цилиндра; разрыв\n'
           '    стрингера на шпангоуте не допускается.\n'
           '3. Вырезы в стенках шпангоутов под пропуск стрингеров\n'
           '    компенсируются накладками 30 × 800 с двух сторон.\n'
           '4. Стыки панелей обшивки располагать только по осям\n'
           '    элементов набора; стык на весу не допускается.\n'
           '5. Швы обшивки — X-образная разделка, полный провар,\n'
           '    подкладная планка остаётся в конструкции.\n'
           '6. Контроль сплошности швов ультразвуковой, 100 %.\n'
           '7. Шахта проходит в толще торцевого купола и в обитаемый\n'
           '    объём не выходит; устье в силовом поясе окантовано\n'
           '    (лист 2, узел окантовки).',
           size=7.2)
    return s.save('07_joints.png', keep=globals().get('_KEEP', False))

SHEETS = (sheet01, sheet02, sheet03, sheet04, sheet05, sheet06, sheet07)


def album(name='MMOSON_drawings.pdf'):
    """Собрать все листы в один PDF — альбом чертежей."""
    from matplotlib.backends.backend_pdf import PdfPages
    import eskd
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', name)
    path = os.path.abspath(path)
    with PdfPages(path) as pdf:
        for f in SHEETS:
            f.__globals__['_KEEP'] = True
            f()
            fig = eskd.Sheet.LAST
            pdf.savefig(fig)
            plt.close(fig)
        info = pdf.infodict()
        info['Title'] = 'ММОСО\u2019Н. Альбом чертежей'
        info['Author'] = 'Бугаенко Р. С., НИК'
        info['Subject'] = 'Модуль моделирования орбитальной станции О\u2019Нилла'
    return path


if __name__ == '__main__':
    for f in SHEETS:
        print(f())
    print(album())
