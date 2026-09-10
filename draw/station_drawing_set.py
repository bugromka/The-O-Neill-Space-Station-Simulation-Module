# -*- coding: utf-8 -*-
"""ММОСО'Н — комплект сборочных чертежей станции.

Оформление ориентировано на предоставленный пользователем пример:
ортогональные виды, разрезы, размерные цепи, выноски, спецификация и
основная надпись. Не блок-схема.
"""
import os
import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Rectangle, Circle, Arc, Ellipse
from matplotlib.lines import Line2D

from eskd import Sheet, S_MAIN, S_THIN, C
from front_unit_drawing import (L, T, ARR, hatch, header, bubble, dim_h,
                                sheet1_assembly, sheet2_bearing_and_corridor,
                                sheet3_dome)

BLUE = '#155d92'
BLUE_LIGHT = '#e2eef6'
RED = '#ad1f1f'
RED_LIGHT = '#f4d9d5'
METAL = '#b7b7b7'
DARK = '#3e3e3e'
GREY = '#777777'
ORANGE = '#995a00'


def sheet0_general():
    s = Sheet('A1', title='Станция ММОСО\'Н.\nОбщая сборочная компоновка',
              material='Сталь 18Ni(300)', scale='см. виды',
              number='ММОСО.00.000 ВО', mass='46,70 млрд т',
              sheet_no='1', sheets='5', lit='П', date='10.09.2026')
    A = s.ax
    header(s, 'ЛИСТ 1. СТАНЦИЯ ММОСО\'Н — ОБЩАЯ СБОРНАЯ КОМПОНОВКА',
           'Ортогональные проекции и разрез переднего узла. Размеры инженерно-предварительные; уточняются расчётом и деталировкой.')
    # MAIN: side elevation with two cylinders, frames, axes, no schematic blocks.
    x0, x1 = 185, 700
    ys = (390, 270)
    r = 30
    front, rear = 118, 755
    T(A, 407, 515, 'Главный вид — вид сбоку', size=8.7, ha='center', weight='bold')
    for i, cy in enumerate(ys, 1):
        A.add_patch(Rectangle((x0, cy-r), x1-x0, 2*r, fc='#d0d0d0', ec=C, lw=S_MAIN))
        A.add_patch(Arc((x0, cy), 2*r, 2*r, theta1=90, theta2=270, ec=C, lw=S_MAIN))
        A.add_patch(Arc((x1, cy), 2*r, 2*r, theta1=-90, theta2=90, ec=C, lw=S_MAIN))
        L(A, x0-10, cy, x1+10, cy, 'axis', color=GREY)
        A.add_patch(Circle((x0, cy), 6, fill=False, ec=C, lw=S_MAIN))
        A.add_patch(Circle((x1, cy), 6, fill=False, ec=C, lw=S_MAIN))
        T(A, 442, cy, f'ЦИЛИНДР {i}', size=6.8, ha='center', weight='bold')
        # short trunnions to fixed frames
        L(A, front+7, cy, x0, cy, 'main', color=METAL, lw=3)
        L(A, x1, cy, rear-7, cy, 'main', color=METAL, lw=3)
        # external equipment only at frames
        for yy in (cy+40, cy-40):
            A.add_patch(Rectangle((front-19, yy-5), 10, 10, fc=RED_LIGHT, ec=RED, lw=S_THIN))
            A.add_patch(Rectangle((rear+10, yy-5), 10, 10, fc=RED_LIGHT, ec=RED, lw=S_THIN))
        A.add_patch(Rectangle((front-34, cy+21), 10, 20, fc=BLUE_LIGHT, ec=BLUE, lw=S_THIN))
        A.add_patch(Rectangle((rear+24, cy+21), 10, 20, fc=BLUE_LIGHT, ec=BLUE, lw=S_THIN))
        A.add_patch(Rectangle((front-34, cy-41), 10, 20, fc=BLUE_LIGHT, ec=BLUE, lw=S_THIN))
        A.add_patch(Rectangle((rear+24, cy-41), 10, 20, fc=BLUE_LIGHT, ec=BLUE, lw=S_THIN))
    # frames
    for cy in ys:
        A.add_patch(Rectangle((front-8, cy-43), 16, 86, fc=DARK, ec=C, lw=S_MAIN))
        A.add_patch(Rectangle((rear-8, cy-43), 16, 86, fc=DARK, ec=C, lw=S_MAIN))
    T(A, front, 445, 'передняя\nнеподвижная рама', size=6.3, ha='center', weight='bold')
    T(A, rear, 445, 'задняя\nнеподвижная рама', size=6.3, ha='center', weight='bold')
    T(A, 445, 330, 'свободный межцилиндровый зазор 11 000\nпродольных связей нет', size=6.5, ha='center', color=GREY, weight='bold')
    s.dim_h(front, rear, 468, '49 000 общая длина', ext_from=ys[0]+r)
    s.dim_h(x0, x1, 222, '40 000 цилиндрическая часть', ext_from=ys[1]-r)
    s.dim_v(ys[1]+r, ys[0]-r, 725, '11 000', ext_from=x1)
    s.dim_v(ys[1], ys[0], 743, '21 000 между осями', ext_from=x1)
    # Front end view lower left.
    T(A, 150, 195, 'Вид с переднего торца', size=8.2, ha='center', weight='bold')
    fx, fy = 150, 125
    L(A, fx, fy-47, fx, fy+47, 'main')
    for yy in (fy+28, fy-28):
        A.add_patch(Circle((fx, yy), 22, fill=False, ec=C, lw=S_MAIN))
        A.add_patch(Circle((fx, yy), 5, fill=False, ec=C, lw=S_THIN))
        for off in (-8, 8):
            A.add_patch(Rectangle((fx+27, yy+off-2.5), 29, 5, fill=False, ec=BLUE, lw=S_THIN))
    T(A, 98, fy, '11 000\nсвободный зазор', size=5.8, ha='center', color=GREY, weight='bold')
    s.dim_v(fy-6, fy+6, 212, '21 000 оси', ext_from=fx+22)
    T(A, 247, fy+38, 'два входных коридора\nна каждый цилиндр', size=5.8, color=BLUE, weight='bold')
    # Top view lower right.
    T(A, 490, 195, 'Вид сверху', size=8.2, ha='center', weight='bold')
    ty = 125
    for yy in (ty+28, ty-28):
        A.add_patch(Rectangle((365, yy-22), 250, 44, fill=False, ec=C, lw=S_MAIN))
        A.add_patch(Arc((365, yy), 44, 44, theta1=90, theta2=270, ec=C, lw=S_MAIN))
        A.add_patch(Arc((615, yy), 44, 44, theta1=-90, theta2=90, ec=C, lw=S_MAIN))
        L(A, 365, yy, 615, yy, 'axis', color=GREY)
        # front docking rails and rear frame plane
        L(A, 335, yy-8, 365, yy-8, 'main', color=METAL, lw=2)
        L(A, 335, yy+8, 365, yy+8, 'main', color=METAL, lw=2)
    L(A, 335, ty-55, 335, ty+55, 'main', color=DARK, lw=3)
    L(A, 645, ty-55, 645, ty+55, 'main', color=DARK, lw=3)
    T(A, 490, 70, 'Внешнее оборудование не размещается на гладких оболочках.', size=6.2, ha='center')
    # sectional inset A-A, lower centre.
    T(A, 745, 195, 'Разрез А–А', size=8.2, ha='center', weight='bold')
    A.add_patch(Rectangle((700, 78), 90, 70, fill=False, ec=C, lw=S_MAIN))
    hatch(s, 702, 80, 788, 146, 3)
    A.add_patch(Rectangle((726, 78), 38, 70, fill=False, ec=BLUE, lw=S_MAIN))
    A.add_patch(Circle((745, 113), 11, fill=False, ec=C, lw=S_THIN))
    T(A, 745, 160, 'торцевая рама\nи осевой узел', size=5.9, ha='center', weight='bold')
    # BOM and technical note
    s.spec_table(34, 66, [
        ['1','Цилиндр гладкий','2','R = 5 000'],
        ['2','Передняя неподвижная рама','1','стыковка'],
        ['3','Задняя неподвижная рама','1','привод / связь'],
        ['4','Подшипниковый узел','4','активный магнитный'],
        ['5','Транспортный коридор','4','2 на цилиндр'],
        ['6','Наклонная шахта','4','2 на цилиндр'],
    ], widths=(10,78,18,32), rh=5.2, size=5.7, title='СПЕЦИФИКАЦИЯ СБОРКИ')
    s.note(260, 106,
           'ПРЕДВАРИТЕЛЬНЫЕ ТЕХНИЧЕСКИЕ ТРЕБОВАНИЯ\n'
           '1. Цилиндры независимы и вращаются на собственных узлах.\n'
           '2. Внешние детали расположены на неподвижных торцевых рамах.\n'
           '3. Зазор между оболочками 11 000 полностью пуст.\n'
           '4. Размеры коридоров, фланцев и посадок подшипника уточняются\n'
           '   расчётом прочности, герметичности и пропускной способности.\n'
           '5. Листы 2–4 — деталировка переднего узла и внутренних трасс.', size=6.1)
    return s


def sheet4_rear():
    s = Sheet('A1', title='Задняя рама.\nСборочный чертёж', material='Сталь 18Ni(300)',
              scale='см. виды', number='ММОСО.01.960 СБ', mass='—', sheet_no='5', sheets='5', lit='П', date='10.09.2026')
    A=s.ax
    header(s,'ЛИСТ 5. ЗАДНЯЯ НЕПОДВИЖНАЯ РАМА — ВИДЫ, ПРИВОД И АНТЕННЫ',
          'Предварительная деталировка. Три проекции и сечение узла мотор-генератора.')
    # Main rear frame front view.
    cx,cy=210,355
    T(A,cx,505,'Главный вид — сзади',size=8.8,ha='center',weight='bold')
    L(A,cx,cy-105,cx,cy+105,'main')
    for yy in (cy+60,cy-60):
        A.add_patch(Circle((cx,yy),43,fill=False,ec=C,lw=S_MAIN)); A.add_patch(Circle((cx,yy),9,fill=False,ec=C,lw=S_MAIN))
        A.add_patch(Ellipse((cx+67,yy),32,22,fill=False,ec=C,lw=S_MAIN)); T(A,cx+67,yy,'МГ',size=6.5,ha='center',weight='bold')
        for sy in (yy+28,yy-28): A.add_patch(Rectangle((cx-63,sy-5),10,10,fc=RED_LIGHT,ec=RED,lw=S_THIN))
        A.add_patch(Rectangle((cx+18,yy+20),10,20,fc=BLUE_LIGHT,ec=BLUE,lw=S_THIN)); A.add_patch(Rectangle((cx+18,yy-40),10,20,fc=BLUE_LIGHT,ec=BLUE,lw=S_THIN))
    # exactly three antenna support arms
    for i,yy in enumerate((cy+110,cy+60,cy+10),1):
        L(A,cx-6,yy,cx-58,yy+12,'thin'); A.add_patch(Ellipse((cx-68,yy+14),18,8,fill=False,ec=C,lw=S_THIN)); T(A,cx-68,yy+27,f'А{i}',size=5.6,ha='center')
    T(A,cx,cy-120,'ровно 3 антенны',size=6.2,ha='center',weight='bold')
    s.dim_v(cy-60,cy+60,295,'21 000 оси',ext_from=cx+43)
    s.dim_v(cy-60,cy+60,315,'11 000 зазор',ext_from=cx+43)
    # side elevation right
    T(A,500,505,'Вид сбоку рамы',size=8.8,ha='center',weight='bold')
    L(A,500,260,500,450,'main'); L(A,507,260,507,450,'thin')
    for yy in (355+60,355-60):
        L(A,507,yy,565,yy,'main',color=METAL,lw=3); A.add_patch(Ellipse((592,yy),35,24,fill=False,ec=C,lw=S_MAIN)); T(A,592,yy,'МГ',size=6,ha='center')
    A.add_patch(Rectangle((565,315),8,80,fc=RED_LIGHT,ec=RED,lw=S_THIN)); A.add_patch(Rectangle((530,315),10,80,fc=BLUE_LIGHT,ec=BLUE,lw=S_THIN))
    T(A,500,240,'рамная плоскость\nне вращается',size=6.2,ha='center')
    # top view and thrust section
    T(A,150,195,'Вид сверху',size=8.2,ha='center',weight='bold')
    for yy in (125+28,125-28):
        A.add_patch(Rectangle((45,yy-20),220,40,fill=False,ec=C,lw=S_MAIN)); L(A,45,yy,265,yy,'axis',color=GREY)
    L(A,45,70,45,180,'main'); L(A,265,70,265,180,'main')
    T(A,155,66,'две тяговые линии от МГ к цапфам',size=5.8,ha='center',color=ORANGE)
    T(A,500,195,'Разрез Б–Б: мотор-генератор и цапфа',size=8.2,ha='center',weight='bold')
    A.add_patch(Rectangle((430,80),120,90,fill=False,ec=C,lw=S_MAIN)); hatch(s,432,82,548,168,3)
    A.add_patch(Ellipse((575,125),52,72,fill=False,ec=C,lw=S_MAIN)); T(A,575,125,'МГ',size=9,ha='center',weight='bold')
    A.add_patch(Circle((430,125),20,fill=False,ec=C,lw=S_MAIN)); A.add_patch(Circle((430,125),10,fill=False,ec=C,lw=S_THIN))
    L(A,450,125,548,125,'main',color=ORANGE,lw=2); T(A,490,145,'цапфа / передача момента',size=5.8,ha='center',color=ORANGE)
    bubble(s,430,145,378,205,'1','корпус рамы',side='right'); bubble(s,430,135,378,63,'2','магнитная опора',side='right'); bubble(s,575,145,620,205,'3','мотор-генератор',side='right')
    s.spec_table(34,66,[['1','Задняя рама','1','неподвижная'],['2','Мотор-генератор','2','по цилиндрам'],['3','Тяговая установка','2','встречное вращение'],['4','Антенна','3','ровно три'],['5','Радиатор','огр.','только красный'],['6','Солнечное крыло','огр.','синее']],widths=(10,78,18,32),rh=5.2,size=5.7,title='СПЕЦИФИКАЦИЯ')
    s.note(260,106,'ПРЕДВАРИТЕЛЬНЫЕ ТЕХНИЧЕСКИЕ ТРЕБОВАНИЯ\n1. Задняя рама неподвижна относительно инерциального пространства.\n2. Мотор-генераторы передают момент через цапфы и магнитные опоры.\n3. На раме ровно три направленные антенны.\n4. Пассажирская транспортная трасса через заднюю раму не проходит.\n5. Посадочные диаметры и допуски уточняются после расчёта подшипника.',size=6.1)
    return s


SHEETS=(sheet0_general,sheet1_assembly,sheet2_bearing_and_corridor,sheet3_dome,sheet4_rear)


def build(pdf_name='MMOSON_station_drawing_set.pdf'):
    root=os.path.abspath(os.path.join(os.path.dirname(__file__),'..')); pdf_path=os.path.join(root,pdf_name); pngs=[]
    with PdfPages(pdf_path) as out:
        for i,fn in enumerate(SHEETS,1):
            s=fn(); png=os.path.join(root,f'MMOSON_station_sheet_{i:02d}.png'); s.fig.savefig(png,dpi=220,facecolor='white'); out.savefig(s.fig); plt.close(s.fig); pngs.append(png)
        info=out.infodict(); info['Title']='ММОСО\'Н. Комплект сборочных чертежей станции'; info['Author']='Бугаенко Р. С., НИК'; info['Subject']='Общая компоновка, рамы, подшипниковые узлы, цилиндр и транспортные шахты'
    return pdf_path,pngs

if __name__=='__main__':
    p,ps=build(); print(p); [print(x) for x in ps]
