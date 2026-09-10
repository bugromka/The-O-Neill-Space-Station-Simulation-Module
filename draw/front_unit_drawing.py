# -*- coding: utf-8 -*-
"""ММОСО'Н — настоящий сборочный чертёж переднего торцевого узла.

В отличие от обзорных схем здесь нет блок-диаграмм: только ортогональные
проекции, разрезы, штриховка деталей, размерные линии и выноски.
"""
import math
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Rectangle, Circle, Arc, Polygon, Ellipse, FancyArrowPatch
from matplotlib.lines import Line2D
from eskd import Sheet, S_MAIN, S_THIN, C

BLUE = '#155d92'       # транспортный коридор в разрезе
BLUE_LIGHT = '#e2eef6'
HATCH = '#d8d8d8'
METAL = '#b7b7b7'
DARK = '#3e3e3e'
RED = '#ad1f1f'
RED_LIGHT = '#f4d9d5'
ORANGE = '#995a00'
GREY = '#777777'


def L(A, x1, y1, x2, y2, kind='main', color=C, lw=None, z=3):
    styles = {'main': (S_MAIN, '-'), 'thin': (S_THIN, '-'),
              'axis': (S_THIN, (0, (10, 3, 2, 3))),
              'hidden': (S_THIN, (0, (5, 3)))}
    w, ls = styles[kind]
    A.add_line(Line2D([x1, x2], [y1, y2], color=color, lw=lw or w,
                      ls=ls, zorder=z))


def T(A, x, y, value, size=7, ha='left', va='center', weight=None,
      color=C, style=None, z=20):
    A.text(x, y, value, fontsize=size, ha=ha, va=va, fontweight=weight,
           color=color, fontstyle=style, linespacing=1.2, zorder=z)


def ARR(A, x1, y1, x2, y2, color=BLUE, lw=1.0, ms=7, z=15):
    A.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle='-|>',
                                mutation_scale=ms, linewidth=lw,
                                color=color, zorder=z))


def hatch(s, x1, y1, x2, y2, step=2.6):
    s.hatch(x1, y1, x2, y2, step=step)


def header(s, h, sub):
    A = s.ax
    T(A, 30, 573, h, size=11, weight='bold')
    T(A, 30, 560, sub, size=7.2, style='italic')
    L(A, 30, 550, 810, 550, 'thin', color=GREY)


def bubble(s, x, y, tx, ty, n, label, side='right'):
    A = s.ax
    L(A, x, y, tx, ty, 'thin')
    A.add_patch(Circle((tx, ty), 5, fill=False, ec=C, lw=S_THIN, zorder=20))
    T(A, tx, ty, n, size=6.2, ha='center', weight='bold', z=21)
    T(A, tx+9 if side == 'right' else tx-9, ty, label, size=6.6,
      ha='left' if side == 'right' else 'right', z=21)


def dim_h(s, x1, x2, y, label, ext=None):
    s.dim_h(x1, x2, y, label, ext_from=ext)


def sheet1_assembly():
    s = Sheet('A1', title='Передний торцевой узел.\nСборочный чертёж',
              material='Сталь 18Ni(300)', scale='см. виды',
              number='ММОСО.01.930 СБ', mass='—', sheet_no='1', sheets='3',
              lit='П', date='10.09.2026')
    A = s.ax
    header(s, 'ЛИСТ 1. ПЕРЕДНИЙ ТОРЦЕВОЙ УЗЕЛ — СБОРКА И ПРОДОЛЬНЫЙ РАЗРЕЗ',
           'Главный вид — разрез А–А одного цилиндра. Второй цилиндр имеет независимый аналогичный узел.')

    # MAIN LONGITUDINAL SECTION: physically drawn walls, sections, and corridor tubes.
    xdock, xframe, xseal, xhub, xbody = 48, 130, 218, 325, 700
    cy = 350
    # Docking adapter and fixed frame, sectioned.
    A.add_patch(Rectangle((xdock, cy-34), 45, 68, fill=False, ec=C, lw=S_MAIN))
    hatch(s, xdock+2, cy-32, xdock+43, cy+32, 3.2)
    T(A, xdock+22, cy, 'П', size=15, ha='center', weight='bold')
    T(A, xdock+22, cy-46, 'стыковочный\nмодуль', size=6.2, ha='center')
    A.add_patch(Rectangle((xframe-10, cy-64), 20, 128, fc=DARK, ec=C, lw=S_MAIN))
    T(A, xframe, cy+77, 'передняя\nнеподвижная рама', size=6.6, ha='center', weight='bold')
    # Two physical corridor tubes A/B in section, each with walls and doors.
    for off, lab in ((18, 'A'), (-18, 'B')):
        y = cy+off
        # external tube walls, door leaves, and chamber segments
        L(A, xdock+45, y-6, xframe-10, y-6, 'main', color=BLUE, lw=1.5)
        L(A, xdock+45, y+6, xframe-10, y+6, 'main', color=BLUE, lw=1.5)
        A.add_patch(Rectangle((xframe+8, y-13), 32, 26, fill=False, ec=C, lw=S_MAIN))
        hatch(s, xframe+10, y-11, xframe+38, y+11, 2.2)
        for xx in (xframe+10, xframe+38):
            L(A, xx, y-12, xx, y+12, 'main')
        T(A, xframe+24, y, 'ШЛЮЗ', size=5.2, ha='center', weight='bold')
        A.add_patch(Rectangle((xframe+46, y-13), 40, 26, fill=False, ec=C, lw=S_MAIN))
        T(A, xframe+66, y, 'КАРАНТИН', size=5.2, ha='center')
        for xx in (xframe+48, xframe+84): L(A, xx, y-12, xx, y+12, 'thin')
        # channel continues to seal and shaft
        L(A, xframe+86, y-6, xseal-8, y-6, 'main', color=BLUE, lw=1.5)
        L(A, xframe+86, y+6, xseal-8, y+6, 'main', color=BLUE, lw=1.5)
        ARR(A, xframe+95, y, xseal-14, y, BLUE, .9, 7)
        T(A, xframe+66, y-22, f'канал {lab}', size=5.5, ha='center', color=BLUE, weight='bold')
    # fixed/rotating boundary and dual seal
    L(A, xseal, cy-78, xseal, cy+78, 'axis', color=ORANGE)
    A.add_patch(Rectangle((xseal-8, cy-42), 16, 84, fc=RED_LIGHT, ec=ORANGE, lw=S_MAIN))
    for off in (18, -18):
        L(A, xseal-20, cy+off-6, xseal+20, cy+off-6, 'main', color=BLUE, lw=1.4)
        L(A, xseal-20, cy+off+6, xseal+20, cy+off+6, 'main', color=BLUE, lw=1.4)
    T(A, xseal, cy+95, 'вращающийся\nдвухканальный гермопереход', size=6.4, ha='center', color=ORANGE, weight='bold')
    T(A, xseal, cy-95, 'граница: неподвижный статор / вращающийся ротор', size=6.0, ha='center', color=ORANGE)
    # bearing housing and hollow shaft with two actual passages
    A.add_patch(Circle((xhub, cy), 28, fill=False, ec=C, lw=S_MAIN))
    A.add_patch(Circle((xhub, cy), 20, fill=False, ec=C, lw=S_THIN))
    T(A, xhub, cy+44, 'активный магнитный\nрадиально-осевой узел', size=6.0, ha='center', weight='bold')
    for off, lab in ((18,'A'),(-18,'B')):
        L(A, xseal+20, cy+off-6, xhub-25, cy+off-6, 'main', color=BLUE, lw=1.6)
        L(A, xseal+20, cy+off+6, xhub-25, cy+off+6, 'main', color=BLUE, lw=1.6)
        T(A, (xseal+xhub)/2, cy+off+11, lab, size=5.4, ha='center', color=BLUE, weight='bold')
    # sectioned cylinder front dome and body
    A.add_patch(Arc((xhub, cy), 2*72, 2*72, theta1=90, theta2=270, ec=C, lw=S_MAIN))
    A.add_patch(Arc((xhub, cy), 2*64, 2*64, theta1=90, theta2=270, ec=C, lw=S_THIN))
    for ang in range(98, 263, 12):
        a=math.radians(ang)
        L(A, xhub+70*math.cos(a), cy+70*math.sin(a), xhub+64*math.cos(a), cy+64*math.sin(a), 'thin')
    L(A, xhub, cy+72, xbody, cy+72, 'main')
    L(A, xhub, cy-72, xbody, cy-72, 'main')
    L(A, xhub+10, cy+60, xbody-8, cy+60, 'thin', color=GREY)
    L(A, xhub+10, cy-60, xbody-8, cy-60, 'thin', color=GREY)
    T(A, 510, cy+47, 'внутренняя жилая поверхность', size=6.3, ha='center', color=GREY)
    T(A, 510, cy-47, 'гладкая наружная оболочка', size=6.3, ha='center')
    # Two inclined shafts in the front hemisphere, with double walls and bulkheads.
    for off, sign, lab in ((18,1,'A'),(-18,-1,'B')):
        x1,y1=xhub+17,cy+off
        x2,y2=xhub+72,cy+sign*57
        dx,dy=x2-x1,y2-y1; norm=math.hypot(dx,dy); nx,ny=-dy/norm*4,dx/norm*4
        L(A,x1+nx,y1+ny,x2+nx,y2+ny,'main',color=BLUE,lw=1.7)
        L(A,x1-nx,y1-ny,x2-nx,y2-ny,'main',color=BLUE,lw=1.7)
        ARR(A,x1+dx*.25,y1+dy*.25,x1+dx*.65,y1+dy*.65,BLUE,.9,7)
        L(A,x2-5,y2-6,x2-5,y2+6,'main',color=BLUE,lw=1.0)
        T(A,x2+35,y2,f'шахта {lab}\nгермодвери',size=5.8,color=BLUE,weight='bold')
    T(A, 430, cy+100, 'передняя полусфера', size=6.2, ha='center', weight='bold')
    # rear fixed frame in main view, to establish external relationship
    rear_x=760
    A.add_patch(Arc((xbody,cy),144,144,theta1=-90,theta2=90,ec=C,lw=S_MAIN))
    A.add_patch(Rectangle((rear_x-10,cy-64),20,128,fc=DARK,ec=C,lw=S_MAIN))
    T(A,rear_x,cy+77,'задняя\nнеподвижная рама',size=6.6,ha='center',weight='bold')
    A.add_patch(Ellipse((rear_x+30,cy),28,22,fill=False,ec=C,lw=S_MAIN)); T(A,rear_x+30,cy,'МГ',size=6,ha='center',weight='bold')
    # dimensions
    dim_h(s, xhub, xbody, cy+105, '40 000 цилиндрическая часть', ext=cy+72)
    dim_h(s, xdock, rear_x+10, cy-110, '49 000 общая длина', ext=cy-72)
    s.dim_v(cy-72, cy+72, xbody+42, 'Ø10 000', ext_from=xbody)
    dim_h(s, xseal, xhub, cy-92, '9 000 осевой узел', ext=cy-42)
    bubble(s,xframe,cy+50,45,cy+150,'1','передняя рама',side='left')
    bubble(s,xseal,cy+42,180,cy+155,'2','двухканальный\nгермопереход',side='right')
    bubble(s,xhub+25,cy+17,305,cy+155,'3','подшипник',side='right')
    bubble(s,xhub+45,cy+44,395,cy+150,'4','наклонные\nшахты',side='right')
    # projection line and title for lower views
    L(A,30,220,810,220,'thin',color=GREY)
    T(A,45,205,'Б. ФРОНТАЛЬНЫЙ ВИД РАМЫ',size=8.2,weight='bold')
    # front-view inset of the two cylinders and the fixed frame
    fx,fy=165,130
    L(A,fx,fy-55,fx,fy+55,'main')
    for yy in (fy+32,fy-32):
        A.add_patch(Circle((fx,yy),24,fill=False,ec=C,lw=S_MAIN))
        A.add_patch(Circle((fx,yy),5,fill=False,ec=C,lw=S_THIN))
        for off in (-9,9):
            # actual corridor mouths on the frame
            A.add_patch(Rectangle((fx+29,yy+off-3),30,6,fill=False,ec=BLUE,lw=S_THIN))
            ARR(A,fx+27,yy+off,fx+29,yy+off,BLUE,.7,6)
    T(A,fx-42,fy,'зазор\n11 000',size=5.8,ha='center',color=GREY,weight='bold')
    s.dim_v(fy-8,fy+8,fx+75,'21 000 оси',ext_from=fx+24)
    T(A,240,fy+55,'2 коридора на каждый цилиндр',size=6.0,color=BLUE,weight='bold')
    T(A,240,fy+45,'устья не соединяются между собой',size=5.8,color=BLUE)
    # small plan projection of one corridor
    px,py=480,130
    T(A,px,205,'В. ПЛАН КОРИДОРОВ В ПЕРЕДНЕМ УЗЛЕ',size=8.2,weight='bold')
    A.add_patch(Rectangle((px-80,py-35),40,70,fill=False,ec=C,lw=S_MAIN))
    T(A,px-60,py,'рама',size=6,ha='center')
    for off in (-14,14):
        L(A,px-40,py+off-4,px+76,py+off-4,'main',color=BLUE,lw=1.5)
        L(A,px-40,py+off+4,px+76,py+off+4,'main',color=BLUE,lw=1.5)
        ARR(A,px+10,py+off,px+50,py+off,BLUE,.8,7)
    A.add_patch(Circle((px+92,py),32,fill=False,ec=C,lw=S_MAIN))
    T(A,px+92,py,'цилиндр',size=6,ha='center')
    T(A,px,py-52,'две физические трубы\nдо переднего гермоперехода',size=5.8,ha='center',color=BLUE)
    return s


def sheet2_bearing_and_corridor():
    s=Sheet('A1',title='Транспортный коридор.\nДеталировка и сечения',material='Сталь 18Ni(300) / YBCO',
            scale='см. виды',number='ММОСО.01.940 СБ',mass='—',sheet_no='2',sheets='3',lit='П',date='10.09.2026')
    A=s.ax
    header(s,'ЛИСТ 2. ДЕТАЛИРОВКА ТРАНСПОРТНОГО КОРИДОРА И ПОДШИПНИКОВОГО УЗЛА',
          'Разрезы показывают реальные стенки, гермодвери, вал и опорные элементы; стрелки только указывают направление движения.')
    # Top main section of one corridor through fixed/rotating interface.
    y=375
    T(A,40,515,'А–А. ПРОДОЛЬНЫЙ РАЗРЕЗ КОРИДОРА ЧЕРЕЗ ГЕРМОПЕРЕХОД',size=8.8,weight='bold')
    # Fixed side left
    A.add_patch(Rectangle((55,y-60),22,120,fc=DARK,ec=C,lw=S_MAIN)); T(A,66,y+75,'рама',size=6.5,ha='center',weight='bold')
    # corridor is a physical pressurized tube with walls and door leaves
    L(A,77,y-15,180,y-15,'main',color=BLUE,lw=1.6); L(A,77,y+15,180,y+15,'main',color=BLUE,lw=1.6)
    T(A,130,y+27,'герметичный коридор',size=6.3,ha='center',color=BLUE,weight='bold')
    # dock/airlock chamber sections
    for x,w,lab in ((88,34,'ШЛЮЗ'),(132,40,'КАРАНТИН')):
        A.add_patch(Rectangle((x,y-22),w,44,fill=False,ec=C,lw=S_MAIN)); hatch(s,x+2,y-20,x+w-2,y+20,2.5)
        T(A,x+w/2,y,lab,size=5.8,ha='center',weight='bold')
        L(A,x+4,y-20,x+4,y+20,'main'); L(A,x+w-4,y-20,x+w-4,y+20,'main')
    # rotating seal: two stationary seals around rotating shell
    L(A,190,y-73,190,y+73,'axis',color=ORANGE)
    A.add_patch(Rectangle((182,y-35),16,70,fc=RED_LIGHT,ec=ORANGE,lw=S_MAIN))
    T(A,190,y+90,'вращающийся\nгермопереход',size=6.2,ha='center',color=ORANGE,weight='bold')
    # rotor shaft housing section
    A.add_patch(Rectangle((208,y-48),110,96,fill=False,ec=C,lw=S_MAIN))
    hatch(s,210,y-46,316,y+46,3.0)
    # Two actual inner channels separated by structural web
    for yy,lab in ((y+16,'A'),(y-16,'B')):
        A.add_patch(Rectangle((212,yy-9),98,18,fc=BLUE_LIGHT,ec=BLUE,lw=S_THIN))
        L(A,218,yy-5,303,yy-5,'thin',color=BLUE); L(A,218,yy+5,303,yy+5,'thin',color=BLUE)
        ARR(A,240,yy,285,yy,BLUE,.8,7)
        T(A,260,yy+14,lab,size=5.7,ha='center',color=BLUE,weight='bold')
    L(A,208,y,318,y,'main')
    T(A,263,y-62,'полый осевой вал; каналы A/B разделены стенкой',size=6.2,ha='center',color=BLUE,weight='bold')
    # end bearing ring and motor generator
    A.add_patch(Circle((338,y),38,fill=False,ec=C,lw=S_MAIN)); A.add_patch(Circle((338,y),27,fill=False,ec=C,lw=S_THIN))
    for yy in (y-23,y+23):
        A.add_patch(Rectangle((315,yy-6),18,12,fc=BLUE_LIGHT,ec=BLUE,lw=S_THIN)); T(A,324,yy,'АМП',size=4.7,ha='center',color=BLUE,weight='bold')
    A.add_patch(Ellipse((398,y),48,70,fill=False,ec=C,lw=S_MAIN)); T(A,398,y,'МГ',size=9,ha='center',weight='bold')
    L(A,377,y,362,y,'main')
    T(A,338,y+64,'активный магнитный\nрадиально-осевой подшипник',size=6.2,ha='center',weight='bold')
    T(A,398,y-50,'мотор-генератор',size=6.0,ha='center')
    # catcher above and below
    L(A,303,y-60,370,y-60,'main'); L(A,303,y+60,370,y+60,'main'); T(A,336,y-75,'резервный механический ловитель',size=5.8,ha='center')
    # dimensions
    dim_h(s,55,77,y-100,'стык рамы',ext=y-60); dim_h(s,208,318,y+86,'полый вал',ext=y+48); s.dim_v(y-48,y+48,325,'сечение корпуса',ext_from=318)
    # Lower left: bearing axial section larger
    T(A,45,240,'Б. ОСЕВОЙ РАЗРЕЗ ОПОРЫ  (увеличено)',size=8.2,weight='bold')
    bx,by=135,145
    A.add_patch(Rectangle((bx-42,by-50),84,100,fill=False,ec=C,lw=S_MAIN)); hatch(s,bx-40,by-48,bx+40,by+48,3)
    A.add_patch(Circle((bx+58,by),38,fill=False,ec=C,lw=S_MAIN)); A.add_patch(Circle((bx+58,by),27,fill=False,ec=C,lw=S_THIN))
    for yy in (by-23,by+23): A.add_patch(Rectangle((bx+28,yy-6),22,12,fc=BLUE_LIGHT,ec=BLUE,lw=S_THIN))
    A.add_patch(Rectangle((bx+88,by-10),80,20,fill=False,ec=C,lw=S_MAIN)); L(A,bx+92,by-5,bx+160,by-5,'thin',color=BLUE); L(A,bx+92,by+5,bx+160,by+5,'thin',color=BLUE)
    T(A,bx-1,by+67,'рама / статор',size=6.3,ha='center',weight='bold'); T(A,bx+58,by+55,'АМП',size=5.5,ha='center',color=BLUE,weight='bold'); T(A,bx+128,by+25,'полый вал',size=6.0,ha='center',color=BLUE)
    bubble(s,bx+58,by+23,55,230,'1','магнитный\nрадиальный контур',side='left')
    bubble(s,bx+58,by-23,55,72,'2','магнитный\nосевой контур',side='left')
    bubble(s,bx+128,by+10,245,225,'3','вращающийся\nротор',side='right')
    # Lower center: pressure/door section
    dx,dy=400,145
    T(A,dx,240,'В. СЕЧЕНИЕ СЕКЦИОННОЙ ГЕРМОДВЕРИ',size=8.2,weight='bold')
    # tube section, two walls, door leaves across tube
    A.add_patch(Rectangle((dx-75,dy-43),150,86,fill=False,ec=C,lw=S_MAIN)); hatch(s,dx-73,dy-41,dx+73,dy+41,3)
    A.add_patch(Rectangle((dx-6,dy-43),12,86,fc=RED_LIGHT,ec=ORANGE,lw=S_MAIN))
    L(A,dx-6,dy+5,dx-35,dy+30,'main'); L(A,dx+6,dy-5,dx+35,dy-30,'main')
    T(A,dx,dy+59,'гермодверь в закрытом положении',size=6.1,ha='center',weight='bold')
    T(A,dx,dy-59,'дверное полотно перекрывает оба стеновых контура',size=5.7,ha='center')
    # pressure arrows on both sides
    ARR(A,dx-108,dy,dx-82,dy,ORANGE,.9,7); ARR(A,dx+108,dy,dx+82,dy,ORANGE,.9,7)
    T(A,dx-105,dy+13,'P1',size=5.8,ha='center',color=ORANGE); T(A,dx+105,dy+13,'P2',size=5.8,ha='center',color=ORANGE)
    # Lower right: transport shaft cross-section
    ex,ey=650,145
    T(A,ex,240,'Г. СЕЧЕНИЕ НАКЛОННОЙ ШАХТЫ',size=8.2,weight='bold')
    A.add_patch(Circle((ex,ey),43,fill=False,ec=C,lw=S_MAIN)); A.add_patch(Circle((ex,ey),34,fill=False,ec=C,lw=S_THIN))
    A.add_patch(Rectangle((ex-25,ey-12),50,24,fc=BLUE_LIGHT,ec=BLUE,lw=S_THIN))
    L(A,ex-20,ey-7,ex+20,ey-7,'thin',color=BLUE); L(A,ex-20,ey+7,ex+20,ey+7,'thin',color=BLUE)
    T(A,ex,ey+58,'герметичный транспортный просвет',size=6.0,ha='center',color=BLUE,weight='bold')
    T(A,ex,ey-58,'наружный силовой корпус шахты',size=5.8,ha='center')
    s.dim_v(ey-43,ey+43,ex-58,'сечение шахты',ext_from=ex-43)
    # bottom technical note
    s.note(45,78,'Все показанные каналы — физические замкнутые объёмы с двумя стенками.\n'
           'Синим выделен транспортный просвет, штриховкой — материал корпуса/рамы.\n'
           'Размер просвета коридора и шахты должен быть назначен отдельным расчётом вместимости;\n'
           'этот комплект фиксирует геометрию, последовательность узлов и границы герметизации.',size=6.3)
    return s


def sheet3_dome():
    s=Sheet('A1',title='Цилиндр.\nПередняя полусфера и выходы шахт',material='Сталь 18Ni(300)',
            scale='см. виды',number='ММОСО.01.950 СБ',mass='—',sheet_no='3',sheets='3',lit='П',date='10.09.2026')
    A=s.ax
    header(s,'ЛИСТ 3. ЦИЛИНДР — ПЕРЕДНЯЯ ПОЛУСФЕРА, ШАХТЫ И ВЫХОД НА ЖИЛУЮ ПОВЕРХНОСТЬ',
          'Разрез показывает внутреннюю геометрию вращающейся передней полусферы; внешняя оболочка остаётся гладкой.')
    # large side section of the front hemisphere
    cx,cy=245,335
    r=110
    A.add_patch(Arc((cx,cy),2*r,2*r,theta1=90,theta2=270,ec=C,lw=S_MAIN))
    A.add_patch(Arc((cx,cy),2*(r-9),2*(r-9),theta1=90,theta2=270,ec=C,lw=S_THIN))
    for ang in range(96,265,10):
        a=math.radians(ang)
        L(A,cx+(r-2)*math.cos(a),cy+(r-2)*math.sin(a),cx+(r-9)*math.cos(a),cy+(r-9)*math.sin(a),'thin')
    # shaft from axis
    L(A,100,cy-9,cx,cy-9,'main',color=BLUE,lw=2); L(A,100,cy+9,cx,cy+9,'main',color=BLUE,lw=2); ARR(A,130,cy,205,cy,BLUE,1,8)
    A.add_patch(Circle((cx,cy),15,fill=False,ec=C,lw=S_MAIN)); A.add_patch(Circle((cx,cy),8,fill=False,ec=C,lw=S_THIN))
    T(A,160,cy+22,'полый вал A/B',size=6.5,ha='center',color=BLUE,weight='bold'); T(A,cx,cy-28,'распределительный узел',size=6.2,ha='center')
    # two separate shafts with actual cross-section walls
    for off,sign,lab in ((12,1,'A'),(-12,-1,'B')):
        x1,y1=cx+12,cy+off; x2,y2=cx+88,cy+sign*83
        dx,dy=x2-x1,y2-y1; norm=math.hypot(dx,dy); nx,ny=-dy/norm*5,dx/norm*5
        L(A,x1+nx,y1+ny,x2+nx,y2+ny,'main',color=BLUE,lw=1.8); L(A,x1-nx,y1-ny,x2-nx,y2-ny,'main',color=BLUE,lw=1.8)
        ARR(A,x1+dx*.25,y1+dy*.25,x1+dx*.65,y1+dy*.65,BLUE,.9,7)
        # pressure bulkheads along shaft
        for frac in (.35,.70):
            xx=x1+dx*frac; yy=y1+dy*frac
            L(A,xx-nx*1.4,yy-ny*1.4,xx+nx*1.4,yy+ny*1.4,'main',color=ORANGE,lw=1.0)
        A.add_patch(Circle((x2,y2),5,fill=False,ec=BLUE,lw=S_THIN))
        T(A,x2+28,y2,f'ШАХТА {lab}',size=6.2,color=BLUE,weight='bold')
        T(A,x2+35,y2-12,'гермодвери',size=5.6,color=ORANGE)
    # body continuation and living surface
    L(A,cx,cy+r,640,cy+r,'main'); L(A,cx,cy-r,640,cy-r,'main')
    L(A,cx+15,cy+r-14,640,cy+r-14,'thin',color=GREY); L(A,cx+15,cy-r+14,640,cy-r+14,'thin',color=GREY)
    T(A,520,cy+86,'жилой объём',size=6.7,ha='center',color=GREY); T(A,520,cy-86,'жилая поверхность',size=6.7,ha='center',color=GREY)
    # dimensions
    s.dim_v(cy-r,cy+r,70,'Ø10 000',ext_from=cx)
    dim_h(s,cx,640,cy+r+28,'цилиндрическая часть 40 000',ext=cy+r)
    dim_h(s,100,cx,cy-r-28,'радиус передней полусферы 5 000',ext=cy-r)
    bubble(s,cx,cy+15,34,490,'1','вход полого вала',side='left')
    bubble(s,cx+60,cy+78,465,500,'2','шахта A: две стенки\nи гермодвери',side='right')
    bubble(s,cx+60,cy-78,465,166,'3','шахта B: независимая\nот шахты A',side='right')
    # lower orthographic view of front hemisphere, clean
    T(A,55,135,'Б. ПОПЕРЕЧНЫЙ ВИД ПЕРЕДНЕЙ ПОЛУСФЕРЫ',size=8.5,weight='bold')
    hx,hy=175,92
    A.add_patch(Circle((hx,hy),40,fill=False,ec=C,lw=S_MAIN)); A.add_patch(Circle((hx,hy),34,fill=False,ec=C,lw=S_THIN)); A.add_patch(Circle((hx,hy),6,fill=False,ec=C,lw=S_MAIN))
    for ang,lab in ((38,'A'),(-38,'B')):
        a=math.radians(ang); x1=hx+8*math.cos(a);y1=hy+8*math.sin(a);x2=hx+32*math.cos(a);y2=hy+32*math.sin(a)
        L(A,x1,y1,x2,y2,'main',color=BLUE,lw=1.8); ARR(A,x1+5*math.cos(a),y1+5*math.sin(a),x2-3*math.cos(a),y2-3*math.sin(a),BLUE,.8,6); T(A,x2+10*math.cos(a),y2+10*math.sin(a),lab,size=5.7,color=BLUE,weight='bold',ha='center')
    T(A,hx,hy-54,'две шахты на передней полусфере',size=5.8,ha='center',color=BLUE)
    # section through one vestibule at lower right
    vx,vy=430,92
    T(A,vx,135,'В. ВЫХОД ШАХТЫ В ВЕСТИБЮЛЬ — СЕЧЕНИЕ',size=8.5,weight='bold')
    A.add_patch(Rectangle((vx-65,vy-25),130,50,fill=False,ec=C,lw=S_MAIN)); hatch(s,vx-63,vy-23,vx+63,vy+23,3)
    A.add_patch(Rectangle((vx-12,vy-25),24,50,fill=False,ec=BLUE,lw=S_MAIN)); A.add_patch(Rectangle((vx-8,vy-14),16,28,fc=BLUE_LIGHT,ec=BLUE,lw=S_THIN))
    T(A,vx,vy+40,'гермодверь выхода',size=6.2,ha='center',color=BLUE,weight='bold'); T(A,vx,vy-40,'вестибюль → жилой объём',size=6.0,ha='center',color=GREY)
    # dedicated technical note and legend
    s.note(600,126,'Трасса в полусфере\n1. Вал приходит к распределительному узлу.\n2. Каналы A/B расходятся в две шахты.\n3. В каждой шахте есть секционные двери.\n4. Выходы ведут в разные вестибюли.\n5. В межцилиндровый зазор трасса не выходит.',size=6.2)
    return s


SHEETS=(sheet1_assembly,sheet2_bearing_and_corridor,sheet3_dome)


def build(pdf_name='MMOSON_front_unit_drawing.pdf'):
    root=os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
    pdf=os.path.join(root,pdf_name); pngs=[]
    with PdfPages(pdf) as out:
        for i,fn in enumerate(SHEETS,1):
            s=fn(); png=os.path.join(root,f'MMOSON_drawing_{i:02d}.png')
            s.fig.savefig(png,dpi=220,facecolor='white'); out.savefig(s.fig); plt.close(s.fig); pngs.append(png)
        info=out.infodict(); info['Title']='ММОСО\'Н. Передний торцевой узел — сборочный чертёж'; info['Author']='Бугаенко Р. С., НИК'; info['Subject']='Ортогональные виды, разрезы и деталировка транспортного коридора'
    return pdf,pngs

if __name__=='__main__':
    p,ps=build(); print(p); [print(x) for x in ps]
