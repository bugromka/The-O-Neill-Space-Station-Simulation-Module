# -*- coding: utf-8 -*-
"""Чертёжный модуль по ЕСКД: лист A3, рамка, основная надпись (школьная форма
по образцу 145 x 22 мм), типы линий, размеры со стрелками, штриховка, разрезы.
Все построения ведутся в миллиметрах листа."""
import os, math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Circle, Arc, Rectangle
from matplotlib.lines import Line2D

matplotlib.rcParams.update({
    'font.family': 'DejaVu Sans',
    'savefig.dpi': 200,
    'savefig.facecolor': 'white',
})

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')
os.makedirs(OUT, exist_ok=True)

# Толщины по ГОСТ 2.303: основная s = 0.6 мм
S_MAIN = 1.4     # сплошная толстая основная
S_THIN = 0.5     # сплошная тонкая (размерные, выносные, штриховка)
S_AXIS = 0.6     # штрихпунктирная осевая
S_HID  = 0.7     # штриховая невидимого контура

C = '#000000'

FORMATS = {'A4': (210, 297), 'A3': (420, 297), 'A2': (594, 420), 'A1': (841, 594)}


class Sheet:
    """Лист чертежа с рамкой и основной надписью."""

    LAST = None

    def __init__(self, fmt='A3', title='', material='', scale='1:1',
                 number='', author='Бугаенко Р. С.', checker='НИК',
                 date='07.09.2026', org='ММОСО’Н — личный проект',
                 mass='—', sheet_no='1', sheets='1', lit=('У', '', ''),
                 approver=''):
        self.W, self.H = FORMATS[fmt]
        self.fig = plt.figure(figsize=(self.W/25.4, self.H/25.4))
        self.ax = self.fig.add_axes([0, 0, 1, 1])
        self.ax.set_xlim(0, self.W); self.ax.set_ylim(0, self.H)
        self.ax.set_aspect('equal'); self.ax.axis('off')
        self._frame()
        self._stamp(title, material, scale, number, author, checker, date,
                    org, mass=mass, sheet_no=sheet_no, sheets=sheets,
                    lit=lit, developer=author, normcontrol=checker,
                    approver=approver)

    # ── рамка листа: слева 20 мм, прочие 5 мм (ГОСТ 2.301) ──
    def _frame(self):
        self.ax.add_patch(Rectangle((0, 0), self.W, self.H, fill=False,
                                    lw=S_THIN, ec='#888'))
        self.ax.add_patch(Rectangle((20, 5), self.W-25, self.H-10,
                                    fill=False, lw=S_MAIN, ec=C))
        self.x0, self.y0 = 20, 5
        self.x1, self.y1 = self.W-5, self.H-5

    # ── основная надпись по ГОСТ 2.104, форма 1 (185 x 55 мм) ──
    def _stamp(self, title, material, scale, number, author, checker, date,
               org, mass='—', sheet_no='1', sheets='1', lit=('У', '', ''),
               developer='Бугаенко Р. С.', normcontrol='НИК', approver=''):
        """Основная надпись по ГОСТ 2.104-2006, форма 1.

        Сетка строится от левого нижнего угла штампа (x, y) в мм.
        По горизонтали слева направо: 7 + 10 + 23 + 15 + 10 = 65 мм
        (графы 14..18: Изм., Лист, № докум., Подп., Дата),
        далее 120 мм — блок наименования, литеры, массы, масштаба.
        По вертикали снизу вверх: 5 x 5 мм (строки должностей) = 25,
        затем 15 мм (шапка «Изм./Лист/...»), итого 40, сверху 15 мм.
        """
        W, H = 185., 55.
        x, y = self.x1 - W, self.y0
        A = self.ax

        def ln(x1, y1, x2, y2, lw=S_THIN):
            A.add_line(Line2D([x1, x2], [y1, y2], lw=lw, color=C, zorder=30))

        def tx(xx, yy, s, size=6.4, weight='normal', style='normal',
               ha='center'):
            A.text(xx, yy, s, ha=ha, va='center', fontsize=size,
                   fontweight=weight, fontstyle=style, color=C, zorder=31)

        # фон, чтобы графика не просвечивала сквозь штамп
        A.add_patch(Rectangle((x, y), W, H, fc='white', ec='none', zorder=29))
        A.add_patch(Rectangle((x, y), W, H, fill=False, lw=S_MAIN, ec=C,
                              zorder=32))

        # ── вертикальные границы левого блока (графы 14..18) ──
        cx = [0., 8., 18., 43., 55., 65.]
        for k, dx in enumerate(cx[1:-1], start=1):
            ln(x + dx, y, x + dx, y + 40)
        ln(x + 65, y, x + 65, y + H, S_MAIN)          # граница блоков

        # ── горизонтали левого блока: 5 строк по 5 мм ──
        for k in range(1, 5):
            ln(x, y + k * 5, x + 65, y + k * 5)
        ln(x, y + 25, x + 65, y + 25, S_MAIN)         # над строками должностей
        ln(x, y + 40, x + 65, y + 40, S_MAIN)         # верх левого блока

        # шапка граф изменений (одна строка 15 мм, подписи по центру)
        for lbl, dx in (('Изм.', 4.0), ('Лист', 13.0), ('№ докум.', 30.5),
                        ('Подп.', 49.0), ('Дата', 60.0)):
            tx(x + dx, y + 32.5, lbl, 5.8)

        # строки должностей (снизу вверх)
        posts = [('Разраб.', developer), ('Пров.', checker),
                 ('Т.контр.', ''), ('Н.контр.', normcontrol),
                 ('Утв.', approver)]
        for k, (p, v) in enumerate(posts):
            yy = y + 22.5 - k * 5
            tx(x + 4.0, yy, p, 5.4)
            if v:
                tx(x + 30.5, yy, v, 6.0)
                tx(x + 60.0, yy, date, 5.0)

        # ── ПРАВЫЙ БЛОК ──
        RX = x + 65.
        RW = W - 65.                                   # 120 мм
        # горизонтали: y+15 (лист/листов), y+25 (лит/масса/масштаб), y+40
        ln(RX, y + 15, x + W, y + 15, S_MAIN)
        ln(RX, y + 25, x + W, y + 25, S_MAIN)
        ln(RX, y + 40, x + W, y + 40, S_MAIN)

        # графа 2 — обозначение документа (верхняя полоса 15 мм)
        tx(RX + RW / 2, y + 47.5, number, 12.0, 'bold')

        # графа 1 — наименование изделия (полоса 25..40)
        _l = [t for t in title.split('\n') if t.strip()]
        if len(_l) == 1:
            tx(RX + RW / 2, y + 32.5, _l[0], 10.0, 'bold')
        else:
            for k, t in enumerate(_l[:2]):
                tx(RX + RW / 2, y + 36.5 - k * 6.0, t,
                   9.0 if k == 0 else 7.8, 'bold' if k == 0 else 'normal')

        # полоса 15..25: литера (3 клетки по 5) | масса 25 | масштаб 30
        LIT_W, MASS_W = 15., 25.
        for k in range(1, 3):
            ln(RX + k * 5, y + 15, RX + k * 5, y + 25)
        ln(RX + LIT_W, y + 15, RX + LIT_W, y + 25, S_MAIN)
        ln(RX + LIT_W + MASS_W, y + 15, RX + LIT_W + MASS_W, y + 25, S_MAIN)
        ln(RX + LIT_W + MASS_W + 30, y + 15,
           RX + LIT_W + MASS_W + 30, y + 25, S_MAIN)
        # заголовки граф — мелко, над строкой значений
        tx(RX + LIT_W / 2, y + 26.9, 'Лит.', 5.4)
        tx(RX + LIT_W + MASS_W / 2, y + 26.9, 'Масса', 5.4)
        tx(RX + LIT_W + MASS_W + 15, y + 26.9, 'Масштаб', 5.4)
        for k, s_ in enumerate(list(lit)[:3]):
            tx(RX + 2.5 + k * 5, y + 20, s_, 6.4)
        tx(RX + LIT_W + MASS_W / 2, y + 20, mass, 6.4)
        tx(RX + LIT_W + MASS_W + 15, y + 20, scale, 8.0, 'bold')

        # полоса 0..15: лист | листов | организация
        SH = RX + LIT_W + MASS_W + 30                  # = RX + 70
        ln(SH, y, SH, y + 15, S_MAIN)
        ln(RX + 35, y, RX + 35, y + 15)
        tx(RX + 17.5, y + 7.5, f'Лист  {sheet_no}', 6.6)
        tx(RX + 52.5, y + 7.5, f'Листов  {sheets}', 6.6)
        tx((SH + x + W) / 2, y + 9.5, org, 7.6, 'bold', 'italic')
        tx((SH + x + W) / 2, y + 4.0, material, 6.4, 'normal', 'italic')

        self.stamp_box = (x, y, W, H)

    # ── линии ──
    def line(self, x1, y1, x2, y2, kind='main'):
        st = {'main': (S_MAIN, '-'), 'thin': (S_THIN, '-'),
              'axis': (S_AXIS, (0, (12, 3, 2, 3))), 'hidden': (S_HID, (0, (6, 3)))}[kind]
        self.ax.add_line(Line2D([x1, x2], [y1, y2], lw=st[0], ls=st[1], color=C,
                                solid_capstyle='round'))

    def poly(self, pts, kind='main', close=False, fc='none'):
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        if close:
            xs.append(pts[0][0]); ys.append(pts[0][1])
        st = {'main': (S_MAIN, '-'), 'thin': (S_THIN, '-'),
              'axis': (S_AXIS, (0, (12, 3, 2, 3))), 'hidden': (S_HID, (0, (6, 3)))}[kind]
        if fc != 'none':
            self.ax.add_patch(Polygon(list(zip(xs, ys)), fc=fc, ec='none', zorder=0))
        self.ax.add_line(Line2D(xs, ys, lw=st[0], ls=st[1], color=C))

    def circle(self, cx, cy, r, kind='main'):
        st = {'main': S_MAIN, 'thin': S_THIN, 'axis': S_AXIS, 'hidden': S_HID}[kind]
        ls = {'main': '-', 'thin': '-', 'axis': (0, (12, 3, 2, 3)),
              'hidden': (0, (6, 3))}[kind]
        self.ax.add_patch(Circle((cx, cy), r, fill=False, lw=st, ls=ls, ec=C))

    def centerlines(self, cx, cy, r):
        e = r*0.15+3
        self.line(cx-r-e, cy, cx+r+e, cy, 'axis')
        self.line(cx, cy-r-e, cx, cy+r+e, 'axis')

    def hatch(self, x1, y1, x2, y2, step=2.5, ang=45):
        """Штриховка прямоугольной области под 45°, ГОСТ 2.306."""
        import numpy as np
        t = math.tan(math.radians(ang))
        w, h = x2-x1, y2-y1
        c = -w*t
        while c <= h + w*t:
            xa, ya = x1, y1+c
            xb, yb = x2, y1+c+w*t
            pts = []
            for (xx, yy) in ((xa, ya), (xb, yb)):
                pts.append((xx, yy))
            # обрезка по прямоугольнику
            seg = _clip((xa, ya), (xb, yb), x1, y1, x2, y2)
            if seg:
                self.ax.add_line(Line2D([seg[0][0], seg[1][0]],
                                        [seg[0][1], seg[1][1]],
                                        lw=0.35, color=C, zorder=6))
            c += step

    # ── размеры ──
    def dim_h(self, x1, x2, y, text=None, ext_from=None, off=0, tick=1.6):
        """Горизонтальный размер со стрелками."""
        A = self.ax
        if ext_from is not None:
            for xx in (x1, x2):
                self.line(xx, ext_from, xx, y+(1.5 if y > ext_from else -1.5), 'thin')
        A.annotate('', xy=(x1, y), xytext=(x2, y),
                   arrowprops=dict(arrowstyle='<|-|>,head_width=0.13,head_length=0.5',
                                   lw=S_THIN, color=C, shrinkA=0, shrinkB=0))
        s = text if text is not None else f'{abs(x2-x1):.0f}'
        A.text((x1+x2)/2, y+1.1, s, ha='center', va='bottom', fontsize=7.5, color=C)

    def dim_v(self, y1, y2, x, text=None, ext_from=None):
        A = self.ax
        if ext_from is not None:
            for yy in (y1, y2):
                self.line(ext_from, yy, x+(1.5 if x > ext_from else -1.5), yy, 'thin')
        A.annotate('', xy=(x, y1), xytext=(x, y2),
                   arrowprops=dict(arrowstyle='<|-|>,head_width=0.13,head_length=0.5',
                                   lw=S_THIN, color=C, shrinkA=0, shrinkB=0))
        s = text if text is not None else f'{abs(y2-y1):.0f}'
        A.text(x-1.2, (y1+y2)/2, s, ha='center', va='center', fontsize=7.5,
               rotation=90, color=C)

    def leader(self, x, y, tx, ty, text, size=7.5, ha='left'):
        """Выноска-полка."""
        self.ax.annotate('', xy=(x, y), xytext=(tx, ty),
                         arrowprops=dict(arrowstyle='-', lw=S_THIN, color=C))
        self.ax.plot([x], [y], marker='o', ms=1.8, color=C)
        self.ax.text(tx, ty+0.8, text, fontsize=size, ha=ha, va='bottom', color=C)

    def note(self, x, y, text, size=7.5, ha='left', weight='normal'):
        self.ax.text(x, y, text, fontsize=size, ha=ha, va='top', color=C,
                     fontweight=weight, linespacing=1.5)


    # ── номер позиции в кружке на выноске (ГОСТ 2.109) ──
    def mark(self, x, y, n, dx=0, dy=0, r=3.0, size=7):
        self.ax.plot([x], [y], marker='o', ms=2.0, color=C, zorder=9)
        self.line(x, y, x+dx, y+dy, 'thin')
        self.ax.add_patch(Circle((x+dx, y+dy), r, fc='white', ec=C,
                                 lw=S_THIN, zorder=10))
        self.ax.text(x+dx, y+dy, str(n), fontsize=size, ha='center',
                     va='center', zorder=11, fontweight='bold')

    # ── обозначение выносного элемента: окружность + буква ──
    def detail_ref(self, x, y, r, letter, ang=45, gap=2.5):
        self.ax.add_patch(Circle((x, y), r, fill=False, lw=S_THIN, ec=C,
                                 ls=(0, (6, 3))))
        a = math.radians(ang)
        xa, ya = x+r*math.cos(a), y+r*math.sin(a)
        xb, yb = x+(r+gap)*math.cos(a), y+(r+gap)*math.sin(a)
        self.line(xa, ya, xb, yb, 'thin')
        self.ax.text(xb+0.6*math.cos(a), yb+0.6*math.sin(a), letter,
                     fontsize=9, fontweight='bold', color=C,
                     ha='left' if math.cos(a) >= 0 else 'right',
                     va='bottom' if math.sin(a) >= 0 else 'top')

    def view_title(self, x, y, text, size=10):
        self.ax.text(x, y, text, fontsize=size, ha='center', va='bottom',
                     fontweight='bold', color=C)

    # ── таблица параметров ──
    def table(self, x, y, cols, rows, widths, rh=5.0, size=6.4,
              head_size=6.6, title=None, align=None, zebra=True):
        """Таблица: (x, y) — левый ВЕРХНИЙ угол. widths — мм по столбцам."""
        A = self.ax
        W = sum(widths)
        n = len(rows)
        if title:
            A.text(x, y+1.6, title, fontsize=7.6, fontweight='bold',
                   ha='left', va='bottom', color=C)
        top = y
        bot = y-rh*(n+1)
        if zebra:
            for i in range(n):
                if i % 2:
                    A.add_patch(Rectangle((x, top-rh*(i+2)), W, rh,
                                          fc='#f2f2f2', ec='none', zorder=0))
        A.add_patch(Rectangle((x, top-rh), W, rh, fc='#e2e2e2', ec='none',
                              zorder=0))
        A.add_patch(Rectangle((x, bot), W, top-bot, fill=False, lw=S_MAIN,
                              ec=C, zorder=3))
        A.plot([x, x+W], [top-rh, top-rh], color=C, lw=S_MAIN, zorder=3)
        for i in range(1, n+1):
            A.plot([x, x+W], [top-rh*(i+1)]*2, color=C, lw=S_THIN, zorder=3)
        cx = x
        for w in widths[:-1]:
            cx += w
            A.plot([cx, cx], [bot, top], color=C, lw=S_THIN, zorder=3)
        al = align or (['left']+['center']*(len(cols)-1))
        def put(vals, yy, sz, wt):
            cc = x
            for v, w, a in zip(vals, widths, al):
                if a == 'left':
                    tx, ha = cc+1.4, 'left'
                elif a == 'right':
                    tx, ha = cc+w-1.4, 'right'
                else:
                    tx, ha = cc+w/2, 'center'
                A.text(tx, yy, str(v), fontsize=sz, ha=ha, va='center',
                       color=C, fontweight=wt, zorder=4)
                cc += w
        put(cols, top-rh/2, head_size, 'bold')
        for i, r in enumerate(rows):
            put(r, top-rh*(i+1)-rh/2, size, 'normal')
        return bot

    # ── диаметр / радиус ──
    def dim_r(self, cx, cy, r, ang, text, size=7.2):
        a = math.radians(ang)
        xa, ya = cx+r*math.cos(a), cy+r*math.sin(a)
        self.ax.annotate('', xy=(xa, ya), xytext=(cx, cy),
                         arrowprops=dict(arrowstyle='-|>,head_width=0.13,'
                                         'head_length=0.5', lw=S_THIN,
                                         color=C, shrinkA=0, shrinkB=0))
        self.ax.text(cx+r*0.55*math.cos(a), cy+r*0.55*math.sin(a)+1.0, text,
                     fontsize=size, ha='center', va='bottom', color=C,
                     bbox=dict(fc='white', ec='none', pad=0.6))

    # ── обозначение сварного шва ──
    def weld(self, x, y, tx, ty, text, size=6.4):
        self.ax.annotate('', xy=(x, y), xytext=(tx, ty),
                         arrowprops=dict(arrowstyle='-|>,head_width=0.10,'
                                         'head_length=0.4', lw=S_THIN,
                                         color=C, shrinkA=0, shrinkB=0))
        sgn = 1 if tx >= x else -1
        self.ax.plot([tx, tx+sgn*13], [ty, ty], color=C, lw=S_THIN)
        self.ax.text(tx+sgn*0.8, ty+0.7, text, fontsize=size, color=C,
                     ha='left' if sgn > 0 else 'right', va='bottom')

    # ── линия обрыва (сплошная тонкая с изломом) ──
    def breakline(self, x, y1, y2, amp=1.6, n=7):
        import numpy as np
        ys = np.linspace(y1, y2, n*2+1)
        xs = [x+(amp if i % 2 else -amp)*(0 if i in (0, len(ys)-1) else 1)
              for i in range(len(ys))]
        self.ax.add_line(Line2D(xs, ys, lw=S_THIN, color=C))


    # ── обозначение секущей плоскости по ГОСТ 2.305 ──
    def section_mark(self, x, y, letter, direction='down', length=9,
                     arrow=7, size=11):
        """Разомкнутая линия со стрелкой и буквой. direction — куда смотрит.

        Штрихи разомкнутой линии наносятся вне контура изображения,
        стрелки указывают направление взгляда, буква ставится
        с внешней стороны стрелки.
        """
        A = self.ax
        s_ = 1 if direction in ('down', 'right') else -1
        if direction in ('down', 'up'):
            A.add_line(Line2D([x, x], [y, y - s_ * length], lw=2.0, color=C,
                              solid_capstyle='butt', zorder=12))
            xa, ya = x, y - s_ * (length - 1.5)
            A.annotate('', xy=(xa + arrow, ya), xytext=(xa, ya),
                       arrowprops=dict(arrowstyle='-|>,head_width=0.20,'
                                       'head_length=0.7', lw=1.5, color=C),
                       zorder=12)
            A.text(xa + arrow + 3.0, ya, letter, fontsize=size,
                   fontweight='bold', ha='center', va='center', zorder=12)
        else:
            A.add_line(Line2D([x, x + s_ * length], [y, y], lw=2.0, color=C,
                              solid_capstyle='butt', zorder=12))
            xa, ya = x + s_ * (length - 1.5), y
            A.annotate('', xy=(xa, ya - arrow), xytext=(xa, ya),
                       arrowprops=dict(arrowstyle='-|>,head_width=0.20,'
                                       'head_length=0.7', lw=1.5, color=C),
                       zorder=12)
            A.text(xa, ya - arrow - 3.0, letter, fontsize=size,
                   fontweight='bold', ha='center', va='center', zorder=12)

    # ── ось проекционной связи (тонкая штрихпунктирная) ──
    def link(self, x1, y1, x2, y2):
        self.ax.add_line(Line2D([x1, x2], [y1, y2], lw=0.35, color='#9a9a9a',
                                ls=(0, (10, 4)), zorder=1))

    # ── штриховка произвольного многоугольника (ГОСТ 2.306) ──
    def hatch_poly(self, pts, step=2.2, ang=45, lw=0.35, color=None):
        import numpy as np
        from matplotlib.path import Path
        pth = Path(pts)
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        x1, x2, y1, y2 = min(xs), max(xs), min(ys), max(ys)
        t = math.tan(math.radians(ang))
        c = y1 - (x2 - x1) * t
        col = color or C
        while c <= y2 + (x2 - x1) * t:
            a = (x1, x1 * 0 + c + (x1 - x1) * t)
            p0 = (x1, c + (x1 - x1) * t)
            p1 = (x2, c + (x2 - x1) * t)
            # разбиваем отрезок и оставляем куски внутри контура
            n = 220
            inside = []
            for k in range(n + 1):
                u = k / n
                px = p0[0] + (p1[0] - p0[0]) * u
                py = p0[1] + (p1[1] - p0[1]) * u
                inside.append(pth.contains_point((px, py)))
            k = 0
            while k <= n:
                if inside[k]:
                    j = k
                    while j <= n and inside[j]:
                        j += 1
                    u0, u1 = k / n, (j - 1) / n
                    if u1 > u0:
                        self.ax.add_line(Line2D(
                            [p0[0] + (p1[0] - p0[0]) * u0,
                             p0[0] + (p1[0] - p0[0]) * u1],
                            [p0[1] + (p1[1] - p0[1]) * u0,
                             p0[1] + (p1[1] - p0[1]) * u1],
                            lw=lw, color=col, zorder=2))
                    k = j
                else:
                    k += 1
            c += step

    # ── таблица составных частей (спецификация на поле чертежа) ──
    def spec_table(self, x, y, rows, widths=(10, 78, 14, 26), rh=6.0,
                   size=6.6, title='Таблица составных частей'):
        """Строится СНИЗУ ВВЕРХ, как спецификация: (x, y) — низ таблицы."""
        A = self.ax
        W = sum(widths)
        n = len(rows)
        head = ['Поз.', 'Наименование', 'Кол.', 'Примечание']
        A.add_patch(Rectangle((x, y), W, rh * (n + 1), fill=False,
                              lw=S_MAIN, ec=C, zorder=6))
        for k in range(1, n + 1):
            A.plot([x, x + W], [y + k * rh] * 2, color=C,
                   lw=S_THIN if k < n + 1 else S_MAIN, zorder=6)
        A.plot([x, x + W], [y + n * rh] * 2, color=C, lw=S_MAIN, zorder=6)
        cx = x
        for w in widths[:-1]:
            cx += w
            A.plot([cx, cx], [y, y + rh * (n + 1)], color=C, lw=S_THIN,
                   zorder=6)
        def put(vals, yy, wt='normal', sz=None):
            cc = x
            for v, w, al in zip(vals, widths, ('center', 'left', 'center',
                                               'left')):
                if al == 'left':
                    A.text(cc + 1.6, yy, str(v), fontsize=sz or size,
                           ha='left', va='center', color=C, fontweight=wt,
                           zorder=7)
                else:
                    A.text(cc + w / 2, yy, str(v), fontsize=sz or size,
                           ha='center', va='center', color=C, fontweight=wt,
                           zorder=7)
                cc += w
        put(head, y + n * rh + rh / 2, 'bold', size)
        for k, r in enumerate(reversed(rows)):
            put(r, y + k * rh + rh / 2)
        if title:
            A.text(x, y + rh * (n + 1) + 2.0, title, fontsize=7.4,
                   fontweight='bold', ha='left', va='bottom', color=C)
        return y + rh * (n + 1)

    def save(self, name, keep=False):
        p = os.path.join(OUT, name)
        self.fig.savefig(p, dpi=200)
        if keep:
            Sheet.LAST = self.fig
        else:
            plt.close(self.fig)
        return p


def _clip(p, q, xmin, ymin, xmax, ymax):
    """Обрезка отрезка прямоугольником (алгоритм Лианга — Барски)."""
    x1, y1 = p; x2, y2 = q
    dx, dy = x2-x1, y2-y1
    t0, t1 = 0.0, 1.0
    for pp, qq in ((-dx, x1-xmin), (dx, xmax-x1), (-dy, y1-ymin), (dy, ymax-y1)):
        if pp == 0:
            if qq < 0: return None
            continue
        r = qq/pp
        if pp < 0:
            if r > t1: return None
            if r > t0: t0 = r
        else:
            if r < t0: return None
            if r < t1: t1 = r
    return ((x1+t0*dx, y1+t0*dy), (x1+t1*dx, y1+t1*dy))
