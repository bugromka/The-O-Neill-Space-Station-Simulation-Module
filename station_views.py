# -*- coding: utf-8 -*-
"""ММОСО'Н: четыре согласованных вида станции.

Все виды строятся из ОДНОГО набора констант, поэтому детали
(цапфы, узлы, балка, панели, радиаторы, антенны, стыковка)
совпадают между видами по построению.
"""
import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import (Rectangle, Circle, Ellipse, Polygon,
                                FancyArrowPatch, Wedge, Arc)
from matplotlib.lines import Line2D
import random

plt.rcParams['font.family'] = 'DejaVu Sans'

# ═══ ЕДИНЫЕ ПАРАМЕТРЫ (метры) ═══
R      = 5000.        # радиус цилиндра
LCYL   = 40000.       # цилиндрическая часть
CEND   = 4500.        # полуось купола вдоль оси
LFULL  = 49000.       # полная длина корпуса
GAPAX  = 16000.       # расстояние между осями цилиндров
AXLEN  = 6000.        # вылет цапфы наружу
AXR    = 260.         # радиус цапфы (как светотепловая балка)
HUBR   = 900.         # радиус подшипникового узла
HUBW   = 1400.        # длина узла вдоль оси
RADL   = 7000.        # вылет радиатора
RADW   = 2600.        # ширина панели радиатора
DISH   = 1500.        # диаметр антенны

# ═══ ПАЛИТРА ═══
BG='#080d16'; INK='#e9eff7'; DIM='#8ea3bf'; FAINT='#5d6f8a'
STEEL='#c3cad3'; STEEL_D='#8e97a3'; STEEL_L='#e6eaef'
SOLAR='#1d3f7a'; SOLAR_L='#3563b5'; GRID='#5f8fd8'
RADC='#c14a36'; RADG='#e8734f'; HUB='#7d8794'; TRUSS='#9aa5b4'
ANT='#dfe5ec'; DOCK='#aab3c0'

fig = plt.figure(figsize=(1900/150, 1500/150), dpi=150)
fig.patch.set_facecolor(BG)
ax = fig.add_axes([0,0,1,1]); ax.set_xlim(0,1900); ax.set_ylim(0,1500)
ax.axis('off')

def T(x,y,s,size=9,color=INK,ha='left',va='center',w=None,st=None,rot=0,z=30):
    ax.text(x,y,s,fontsize=size,color=color,ha=ha,va=va,fontweight=w,
            fontstyle=st,rotation=rot,zorder=z)

def lead(x0,y0,x1,y1,c=FAINT,lw=0.8):
    ax.add_line(Line2D([x0,x1],[y0,y1],color=c,lw=lw,zorder=25))
    ax.add_patch(Circle((x0,y0),3.0,fc=c,ec='none',zorder=25))

random.seed(5)
for _ in range(1400):
    x,y=random.uniform(0,1900),random.uniform(0,1500); r=random.random()
    ax.add_patch(Circle((x,y),0.5+r*1.1,fc='white',alpha=0.05+r*0.30,
                        ec='none',zorder=0))

# ════════════════════ ЭЛЕМЕНТЫ (общие для видов) ════════════════════

def solar_dome(cx, cy, rx, ry, side, K):
    """Купол, сплошь покрытый фотоэлементами. side=+1 нос вправо."""
    th1,th2 = (-90,90) if side>0 else (90,270)
    ax.add_patch(Wedge((cx,cy), rx, th1, th2, fc=SOLAR, ec=STEEL_D,
                       lw=1.0, zorder=8))
    # сетка ячеек по дуге
    for k in range(1,9):
        f=k/9.
        w_=rx*math.sqrt(max(0.,1-(2*f-1)**2)) if False else rx*(1-abs(2*f-1))
        yy=cy-ry+2*ry*f
        hw=rx*math.sqrt(max(0.,1-((yy-cy)/ry)**2))
        ax.add_line(Line2D([cx,cx+side*hw],[yy,yy],color=GRID,lw=0.5,
                           alpha=.55,zorder=9))
    for k in range(1,5):
        f=k/5.
        ax.add_patch(Arc((cx,cy), 2*rx*f, 2*ry*f, theta1=th1, theta2=th2,
                         color=GRID, lw=0.5, alpha=.55, zorder=9))

def axle_hub(hx, hy, side, K, front, label=True):
    """Цапфа + подшипниковый узел на оси вращения."""
    L_=AXLEN*K; r_=max(AXR*K,1.2); HR=max(HUBR*K,3.0); HW=max(HUBW*K,3.0)
    ax.add_patch(Rectangle((hx if side>0 else hx-L_, hy-r_), L_, 2*r_,
                           fc=STEEL_D, ec=STEEL, lw=0.7, zorder=11))
    ex = hx+side*L_
    ax.add_patch(Rectangle((ex-side*HW/2-HW/2+HW/2 if False else ex-HW/2,
                            hy-HR), HW, 2*HR, fc=HUB, ec=STEEL_L,
                           lw=0.9, zorder=13))
    ax.add_patch(Circle((ex,hy), HR*0.55, fc='#39424e', ec=STEEL_L,
                        lw=0.8, zorder=14))
    return ex

def radiators(ex, hy, side, K, n=3):
    """Радиаторы на узле — плоскости поперёк."""
    RL=RADL*K; RW=RADW*K
    for i in range(n):
        off=(i-(n-1)/2)*RW*1.15
        for s2 in (+1,-1):
            ax.add_patch(Polygon([[ex+off-RW*0.30, hy+s2*HUBR*K*0.6],
                                  [ex+off+RW*0.30, hy+s2*HUBR*K*0.6],
                                  [ex+off+RW*0.22, hy+s2*(HUBR*K*0.6+RL)],
                                  [ex+off-RW*0.22, hy+s2*(HUBR*K*0.6+RL)]],
                                 closed=True, fc=RADC, ec=RADG, lw=0.6,
                                 alpha=.95, zorder=12))

def dock(ex, hy, side, K):
    """Модули стыковки на носовом узле."""
    d=max(DISH*K*0.55,2.0)
    for i in range(3):
        yy=hy+(i-1)*d*2.2
        ax.add_patch(Rectangle((ex+side*d*0.8, yy-d*0.45), d*2.0, d*0.9,
                               fc=DOCK, ec=STEEL_L, lw=0.6, zorder=15))
        ax.add_patch(Circle((ex+side*d*2.9, yy), d*0.42, fc='#5b6675',
                            ec=STEEL_L, lw=0.6, zorder=15))

def antennas(ex, hy, side, K):
    """Антенны на кормовом узле; тарелки независимо наводятся на Землю."""
    d=max(DISH*K,2.4)
    for i,(dy,sc) in enumerate([(2.6,1.0),(0.0,1.35),(-2.6,0.85)]):
        yy=hy+dy*d
        ax.add_line(Line2D([ex,ex+side*d*0.9],[yy,yy],color=STEEL,lw=0.9,
                           zorder=15))
        ax.add_patch(Ellipse((ex+side*d*1.35, yy), d*0.85*sc, d*1.7*sc,
                             fc=ANT, ec=STEEL_D, lw=0.7, zorder=16))
        ax.add_patch(Ellipse((ex+side*d*1.50, yy), d*0.40*sc, d*1.1*sc,
                             fc='#b9c2cd', ec='none', zorder=17))

def truss(x1,y1,x2,y2,K,seg=13):
    """Балка между узлами: только по линии осей."""
    ax.add_line(Line2D([x1,x2],[y1,y2],color=TRUSS,lw=2.2,zorder=12))
    dx,dy=(x2-x1)/seg,(y2-y1)/seg
    w=max(HUBR*K*0.42,1.6)
    nx,ny=-(y2-y1),(x2-x1); ln=math.hypot(nx,ny) or 1; nx,ny=nx/ln*w,ny/ln*w
    ax.add_line(Line2D([x1+nx,x2+nx],[y1+ny,y2+ny],color=TRUSS,lw=1.0,zorder=12))
    ax.add_line(Line2D([x1-nx,x2-nx],[y1-ny,y2-ny],color=TRUSS,lw=1.0,zorder=12))
    for i in range(seg):
        a=(x1+dx*i, y1+dy*i); b=(x1+dx*(i+1), y1+dy*(i+1))
        ax.add_line(Line2D([a[0]+nx,b[0]-nx],[a[1]+ny,b[1]-ny],
                           color=TRUSS,lw=0.5,alpha=.85,zorder=12))

def hull_side(cx, cy, K):
    """Корпус цилиндра сбоку: обечайка + два купола в панелях."""
    hl=LCYL/2*K; r=R*K; ce=CEND*K
    ax.add_patch(Rectangle((cx-hl, cy-r), 2*hl, 2*r, fc=STEEL,
                           ec=STEEL_D, lw=1.0, zorder=8))
    for k in range(1,10):
        xx=cx-hl+2*hl*k/10
        ax.add_line(Line2D([xx,xx],[cy-r,cy+r],color=STEEL_D,lw=0.5,
                           alpha=.55,zorder=9))
    ax.add_line(Line2D([cx-hl,cx+hl],[cy+r*0.45,cy+r*0.45],color=STEEL_L,
                       lw=1.4,alpha=.5,zorder=9))
    solar_dome(cx+hl, cy, ce, r, +1, K)
    solar_dome(cx-hl, cy, ce, r, -1, K)

# ════════════════════ ВИД A: СБОКУ ════════════════════
T(60,1442,"ММОСО\u2019Н", size=30, w='bold')
T(60,1414,"Модуль моделирования орбитальной станции О\u2019Нилла · внешний вид",
  size=12, color=DIM)
T(60,1394,"один набор деталей во всех проекциях: цапфа — подшипниковый узел — "
          "балка; панели на куполах; спереди стыковка, сзади антенны",
  size=8.6, color=FAINT, st='italic')
ax.add_line(Line2D([60,1180],[1380,1380],color='#22334d',lw=1.0,zorder=5))

T(60,1330,'A.  ВИД СБОКУ', size=13, w='bold')
T(60,1314,'боковые оболочки гладкие; между ними 11 км свободного вакуумного зазора; связь только по осям', size=8.4,
  color=DIM)

K=0.0088
xc, yA = 640., 1120.
dyc = GAPAX*K/2
for s in (+1,-1):
    hull_side(xc, yA+s*dyc, K)
hl=LCYL/2*K
hubs={}
for s in (+1,-1):
    yy=yA+s*dyc
    ex_f=axle_hub(xc+hl+CEND*K, yy, +1, K, True)     # нос — вправо
    ex_r=axle_hub(xc-hl-CEND*K, yy, -1, K, False)    # корма — влево
    hubs[s]=(ex_f,ex_r,yy)
    radiators(ex_f, yy, +1, K, 3)
    radiators(ex_r, yy, -1, K, 3)
    dock(ex_f, yy, +1, K)
    antennas(ex_r, yy, -1, K)
truss(hubs[+1][0], hubs[+1][2], hubs[-1][0], hubs[-1][2], K)   # нос
truss(hubs[+1][1], hubs[+1][2], hubs[-1][1], hubs[-1][2], K)   # корма

T(xc+hl+CEND*K+AXLEN*K+90, yA+dyc+95, 'НОС — условный видимый торец', size=9, w='bold',
  color='#ffd98a')
T(xc-hl-CEND*K-AXLEN*K-90, yA+dyc+95, 'КОРМА — условный видимый торец', size=9, w='bold',
  color='#9fd0ff', ha='right')

lead(xc+hl+CEND*K*0.4, yA+dyc+R*K*0.75, xc+hl-40, yA+dyc+R*K+92)
T(xc+hl-36, yA+dyc+R*K+96, 'купол — полированная сталь', size=8)
lead(hubs[+1][0], hubs[+1][2]+HUBR*K, xc+hl+330, yA+dyc+150)
T(xc+hl+334, yA+dyc+154, 'подшипниковый узел на цапфе', size=8)
lead((hubs[+1][0]+hubs[-1][0])/2, yA, (hubs[+1][0]+hubs[-1][0])/2+250, yA-40)
T((hubs[+1][0]+hubs[-1][0])/2+254, yA-44,
  'балка: узел — узел, поверхности не касается', size=8)
lead(hubs[+1][1], hubs[+1][2]-HUBR*K*2.2, xc-hl-260, yA+dyc-150)
T(xc-hl-256, yA+dyc-154, 'антенны — независимое наведение на Землю', size=8, ha='left')

ax.add_line(Line2D([xc-hl-CEND*K, xc+hl+CEND*K],[yA-dyc-R*K-58]*2,
                   color=FAINT,lw=0.8,zorder=20))
for xx in (xc-hl-CEND*K, xc+hl+CEND*K):
    ax.add_line(Line2D([xx,xx],[yA-dyc-R*K-52,yA-dyc-R*K-64],color=FAINT,
                       lw=0.8,zorder=20))
T(xc, yA-dyc-R*K-74, 'полная длина 49 км', size=8.4, color=DIM, ha='center')

# ════════════════════ ВИД B: СПЕРЕДИ ════════════════════
T(1250,1330,'B.  ВИД СПЕРЕДИ (условное направление камеры)', size=13, w='bold')
T(1250,1314,'видны носовые купола в панелях и балка между узлами',
  size=8.4, color=DIM)

KB=0.0092
xB,yB=1510.,1120.
rB=R*KB; dB=GAPAX*KB/2
for s in (+1,-1):
    yy=yB+s*dB
    ax.add_patch(Circle((xB,yy), rB, fc=SOLAR, ec=STEEL_D, lw=1.1, zorder=8))
    for k in range(1,5):
        ax.add_patch(Circle((xB,yy), rB*k/5, fc='none', ec=GRID, lw=0.5,
                            alpha=.5, zorder=9))
    for k in range(12):
        a=math.radians(k*30)
        ax.add_line(Line2D([xB,xB+rB*math.cos(a)],[yy,yy+rB*math.sin(a)],
                           color=GRID,lw=0.5,alpha=.5,zorder=9))
    ax.add_patch(Circle((xB,yy), max(HUBR*KB,4.5), fc=HUB, ec=STEEL_L,
                        lw=0.9, zorder=14))
    for i in range(3):
        an=math.radians(90+i*120)
        ax.add_patch(Polygon([[xB+math.cos(an)*rB*0.28, yy+math.sin(an)*rB*0.28],
                              [xB+math.cos(an+0.30)*rB*1.34, yy+math.sin(an+0.30)*rB*1.34],
                              [xB+math.cos(an-0.30)*rB*1.34, yy+math.sin(an-0.30)*rB*1.34]],
                             closed=True, fc=RADC, ec=RADG, lw=0.5,
                             alpha=.9, zorder=7))
truss(xB, yB+dB, xB, yB-dB, KB, seg=9)
T(xB, yB+dB+rB+40, 'радиаторы — лучами от узла', size=8, color='#e8a58a',
  ha='center')
T(xB, yB-dB-rB-46, 'балка соединяет только узлы', size=8, color=DIM,
  ha='center')
T(xB+rB+60, yB, 'крылья батарей\nна узлах —\nповоротные', size=8.2,
  color='#9fc4ff')

# ════════════════════ ВИД C: УЗЕЛ КРУПНО ════════════════════
T(60,850,'C.  УЗЕЛ: ЦАПФА — ПОДШИПНИК — БАЛКА', size=13, w='bold')
T(60,889,'вынесено; корпус слева, узел не вращается', size=8.4, color=DIM)

KC=0.019
xCv,yCv=250.,650.
rC=R*KC
ax.add_patch(Wedge((xCv,yCv), CEND*KC*1.6, -90, 90, fc=SOLAR, ec=STEEL_D,
                   lw=1.0, zorder=8))
for k in range(1,6):
    ax.add_patch(Arc((xCv,yCv), 2*CEND*KC*1.6*k/6, 2*rC*k/6,
                     theta1=-90, theta2=90, color=GRID, lw=0.6, alpha=.6,
                     zorder=9))
axl=AXLEN*KC; axr=AXR*KC
ax.add_patch(Rectangle((xCv, yCv-axr), axl, 2*axr, fc=STEEL_D, ec=STEEL_L,
                       lw=0.8, zorder=11))
hx=xCv+axl
HR=HUBR*KC; HW=HUBW*KC
ax.add_patch(Rectangle((hx-HW/2, yCv-HR), HW, 2*HR, fc=HUB, ec=STEEL_L,
                       lw=1.0, zorder=13))
for k in range(7):
    a=math.radians(k*51)
    ax.add_patch(Circle((hx, yCv+HR*0.62*math.sin(a)), HR*0.13,
                        fc='#39424e', ec=STEEL_L, lw=0.5, zorder=14))
ax.add_patch(Circle((hx,yCv), HR*0.42, fc='#2b333d', ec=STEEL_L, lw=0.8,
                    zorder=15))
truss(hx+HW/2, yCv, hx+HW/2+330, yCv, KC, seg=11)
for i in range(3):
    ax.add_patch(Rectangle((hx+HW*0.8, yCv+(i-1)*HR*0.85-HR*0.18),
                           HR*1.5, HR*0.36, fc=DOCK, ec=STEEL_L, lw=0.6,
                           zorder=15))
lead(xCv+axl*0.5, yCv+axr, xCv+30, yCv+120)
T(xCv+34, yCv+124, 'цапфа: вылет 6 км, Ø 520 м', size=8)
lead(hx, yCv+HR, hx+20, yCv+165)
T(hx+24, yCv+169, 'подшипниковый узел — не вращается', size=8)
lead(hx+HW*1.6, yCv+HR*0.9, hx+150, yCv-150)
T(hx+154, yCv-154, 'модули стыковки', size=8)
lead(hx+HW/2+150, yCv, hx+200, yCv-95)
T(hx+204, yCv-99, 'балка к соседнему узлу', size=8)
lead(xCv+CEND*KC*1.1, yCv-rC*0.55, xCv+60, yCv-215)
T(xCv+64, yCv-219, 'купол цилиндра', size=8)

# ════════════════════ ВИД D: СЛЕЖЕНИЕ ЗА СОЛНЦЕМ ════════════════════
T(860,850,'D.  ОРИЕНТАЦИЯ В ТЕЧЕНИЕ ГОДА', size=13, w='bold')
T(860,834,'ось неподвижна (п. 11.6), Солнце обходит станцию за год',
  size=8.4, color=DIM)

ox,oy,ORB=1140.,640.,132.
ax.add_patch(Circle((ox,oy), 26, fc='#ffd98a', ec='#ffb347', lw=1.2,
                    zorder=12))
T(ox,oy,'Солнце',size=7.6,ha='center',color='#3a2a08',w='bold',z=13)
ax.add_patch(Circle((ox,oy), ORB, fc='none', ec='#33465f', lw=0.9,
                    ls=(0,(5,4)), zorder=6))
for k,(a,lab) in enumerate([(0,'весна'),(90,'лето'),(180,'осень'),(270,'зима')]):
    A=math.radians(a)
    sxp,syp=ox+ORB*math.cos(A), oy+ORB*math.sin(A)
    for s in (+1,-1):
        ax.add_patch(Ellipse((sxp, syp+s*9), 34, 12, angle=0,
                             fc=STEEL, ec=STEEL_D, lw=0.6, zorder=10))
        # носовой купол всегда СПРАВА (ось неподвижна)
        ax.add_patch(Wedge((sxp+17, syp+s*9), 7, -90, 90, fc=SOLAR,
                           ec='none', zorder=11))
    ax.add_line(Line2D([sxp,ox],[syp,oy],color='#ffd98a',lw=0.6,
                       alpha=.35,zorder=7))
    T(sxp, syp+30, lab, size=7.4, color=DIM, ha='center')
T(ox, oy-ORB-56,
  'Ось станции не поворачивается: разворот требовал бы 2,41·10¹² Н·м.',
  size=8, color=DIM, ha='center')
T(ox, oy-ORB-70,
  'За год направление Солнца в корпусной системе проходит полный оборот.', size=8,
  color=DIM, ha='center')
T(ox, oy-ORB-86,
  'ПОЭТОМУ КРЫЛЬЯ БАТАРЕЙ ПОВОРОТНЫЕ: привод на узле наводит их',
  size=8.4, color='#9fc4ff', ha='center', w='bold')
T(ox, oy-ORB-100,
  'на светило круглый год; корпус станции при этом не поворачивается.', size=8.4,
  color='#9fc4ff', ha='center', w='bold')

# ════════════════════ СВОДКА ════════════════════
ax.add_line(Line2D([60,1840],[300,300],color='#22334d',lw=1.0,zorder=5))
T(60,272,'СОЛНЕЧНЫЕ БАТАРЕИ (п. 7.7)', size=10, w='bold', color='#9fd0ff')
for i,(k,v) in enumerate([
    ('поворотные крылья','586,8 км² · по 146,7 км² на узел'),
    ('исполнение','складные секции, шарнир 2 степени свободы'),
    ('мощность при КПД 25 %','53,4 ГВт = 7,41 % станции'),
    ('масса при 2 кг/м²','1,17 млн т = 0,0025 % массы'),
    ('деградация','0,5 %/год: 88 % через 25 лет, 61 % через 100'),
    ('привод наведения','0,986 °/сут — оборот за год')]):
    T(60, 246-i*17, k, size=8, color=DIM)
    T(330, 246-i*17, v, size=8, color=INK)

T(980,272,'КОНСТРУКЦИЯ УЗЛА', size=10, w='bold', color='#9fd0ff')
for i,(k,v) in enumerate([
    ('цапфа','выходит из купола по оси вращения'),
    ('подшипниковый узел','магнитная опора · мотор-генератор · статор на раме'),
    ('балка','соединяет узлы; поверхности не касается'),
    ('передний торец','стыковка · радиаторы · крылья батарей'),
    ('задний торец','антенны · радиаторы · батареи · двигатели'),
    ('станция','2 цилиндра · 49 км · 46,70 млрд т · L1')]):
    T(980, 246-i*17, k, size=8, color=DIM)
    T(1250, 246-i*17, v, size=8, color=INK)

T(1840,60,'Бугаенко Р. С. · НИК   ·   ред. 7.0, 08.09.2026   ·   '
          'verify_all.py 243/243', size=8, color=FAINT, ha='right')

fig.savefig('station_views.png', dpi=150, facecolor=BG)
print('station_views.png сохранён')
