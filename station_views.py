# -*- coding: utf-8 -*-
"""ММОСО'Н — согласованный технический лист внешней компоновки.

Четыре вида из одного канона:
A — боковой вид с пустым межцилиндровым зазором;
B — передняя неподвижная рама и причальные модули;
C — путь от причала через гермопереход и полый осевой вал в шахты;
D — встречное вращение, питание магнитных опор и перемещение станции.
"""
import math
import random
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Ellipse, FancyBboxPatch, FancyArrowPatch, Arc, Polygon
from matplotlib.lines import Line2D

plt.rcParams['font.family'] = 'DejaVu Sans'

# Канон документа, м
R = 5000.0
LCYL = 40000.0
CEND = 4500.0
LFULL = 49000.0
GAPAX = 21000.0
AXLEN = 9000.0
D_BEAR = 400.0
P_BEAR = 2.0

BG = '#080d16'; INK = '#e9eff7'; DIM = '#9aacc4'; FAINT = '#61758f'
STEEL = '#b8c2cc'; STEEL_D = '#687686'; STEEL_L = '#e6edf4'
GRAPH = '#273544'; SOLAR = '#173f7c'; SOLAR_L = '#4579c5'; GRID = '#79a7e6'
RAD = '#b83c32'; RAD_L = '#e46b52'; ANT = '#e8edf2'; DOCK = '#aeb9c5'
MAG = '#55a6c8'; POWER = '#f0bd57'; SAFE = '#78c89a'

W, H = 1900, 1500
fig = plt.figure(figsize=(W/150, H/150), dpi=150)
fig.patch.set_facecolor(BG)
ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis('off')

def T(x, y, text, size=9, color=INK, ha='left', va='center', weight=None, style=None, z=30):
    ax.text(x, y, text, fontsize=size, color=color, ha=ha, va=va,
            fontweight=weight, fontstyle=style, zorder=z)

def L(x0, y0, x1, y1, color=FAINT, lw=1.0, ls='-', z=20, alpha=1.0):
    ax.add_line(Line2D([x0, x1], [y0, y1], color=color, lw=lw,
                       ls=ls, zorder=z, alpha=alpha))

def arrow(x0, y0, x1, y1, color=INK, lw=1.2, z=25, ms=12):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle='-|>',
                                 mutation_scale=ms, linewidth=lw,
                                 color=color, zorder=z))

def leader(x0, y0, x1, y1, text, color=FAINT, size=8, side='left'):
    L(x0, y0, x1, y1, color=color, lw=.8, z=26)
    ax.add_patch(Circle((x0, y0), 3, fc=color, ec='none', zorder=27))
    T(x1 + (6 if side == 'left' else -6), y1, text, size=size, color=INK,
      ha='left' if side == 'left' else 'right', va='center', z=27)

def panel(x, y, w, h, title, subtitle=None):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.012,rounding_size=10',
                                fc='#0d1724', ec='#263c56', lw=1.0, zorder=2))
    T(x+22, y+h-30, title, size=11.5, color=INK, weight='bold', z=4)
    if subtitle:
        T(x+22, y+h-52, subtitle, size=7.4, color=DIM, z=4)

def hull(x0, x1, y, r):
    # Однотонная гладкая оболочка; без наружных колец, рёбер и оборудования.
    ax.add_patch(FancyBboxPatch((x0, y-r), x1-x0, 2*r,
                                boxstyle=f'round,pad=0,rounding_size={r}',
                                fc=STEEL, ec=STEEL_D, lw=1.0, zorder=8))
    ax.add_patch(FancyBboxPatch((x0+12, y-r+12), x1-x0-24, 2*r-24,
                                boxstyle=f'round,pad=0,rounding_size={max(r-12,1)}',
                                fc='#aeb9c5', ec='none', alpha=.22, zorder=9))

def trunnion(x_shell, x_frame, y):
    L(x_shell, y, x_frame, y, color=STEEL_D, lw=7, z=11)
    L(x_shell, y+4, x_frame, y+4, color=STEEL_L, lw=1.2, z=12)
    ax.add_patch(Circle((x_frame, y), 15, fc=GRAPH, ec=STEEL_L, lw=1.0, zorder=14))
    ax.add_patch(Circle((x_frame, y), 7, fc=MAG, ec='none', zorder=15))

def solar_wing(x, y, side=1, vertical=True, scale=1.0):
    if vertical:
        w, h = 34*scale, 120*scale
        xx = x if side > 0 else x-w
        yy = y-h/2
    else:
        w, h = 120*scale, 34*scale
        xx = x-w/2; yy = y if side > 0 else y-h
    ax.add_patch(Rectangle((xx, yy), w, h, fc=SOLAR, ec=SOLAR_L,
                           lw=.8, zorder=16))
    for i in range(1, 5):
        if vertical: L(xx+w*i/5, yy, xx+w*i/5, yy+h, GRID, .45, z=17, alpha=.7)
        else: L(xx, yy+h*i/5, xx+w, yy+h*i/5, GRID, .45, z=17, alpha=.7)

def radiator_panel(x, y, w, h, angle=0):
    # Красный только для радиаторов.
    ax.add_patch(Rectangle((x-w/2, y-h/2), w, h, angle=angle,
                           fc=RAD, ec=RAD_L, lw=.8, zorder=16))
    for i in range(1, 4):
        xx=x-w/2+w*i/4
        L(xx, y-h/2+3, xx, y+h/2-3, RAD_L, .45, z=17, alpha=.8)

def dish(x, y, scale=1.0, side=1):
    r=18*scale
    ax.add_patch(Ellipse((x, y), 2*r, 1.15*r, angle=side*18,
                         fc=ANT, ec=STEEL_D, lw=.8, zorder=17))
    L(x-side*r*.65, y, x+side*r*.65, y, STEEL_D, .6, z=18)
    ax.add_patch(Circle((x+side*r*.12, y), 2.5*scale, fc=GRAPH, ec=STEEL_D, lw=.4, zorder=18))

def front_frame(x, ys, scale=1.0):
    # Фиксированная поперечная рама только в торцевой плоскости.
    y0, y1 = min(ys)-105*scale, max(ys)+105*scale
    ax.add_patch(Rectangle((x-10*scale, y0), 20*scale, y1-y0,
                           fc=GRAPH, ec=STEEL_L, lw=1.0, zorder=10))
    for y in ys:
        ax.add_patch(Circle((x, y), 29*scale, fc=GRAPH, ec=STEEL_L, lw=1.0, zorder=14))
        ax.add_patch(Circle((x, y), 12*scale, fc=MAG, ec='none', zorder=15))
        trunnion(x-42*scale, x-9*scale, y)
        # Два защищённых docking corridor на каждый осевой узел.
        for dy in (-38, 38):
            ax.add_patch(FancyBboxPatch((x+8*scale, y+dy*scale-9*scale),
                                        75*scale, 18*scale,
                                        boxstyle='round,pad=0,rounding_size=7',
                                        fc=DOCK, ec=STEEL_L, lw=.7, zorder=15))
            ax.add_patch(Circle((x+84*scale, y+dy*scale), 8*scale,
                                fc=GRAPH, ec=STEEL_L, lw=.6, zorder=16))
        radiator_panel(x+6*scale, y+95*scale, 18*scale, 58*scale, angle=0)
        radiator_panel(x+27*scale, y-95*scale, 18*scale, 58*scale, angle=0)
        solar_wing(x+47*scale, y+80*scale, side=1, vertical=True, scale=scale*.78)
        solar_wing(x+47*scale, y-80*scale, side=-1, vertical=True, scale=scale*.78)

def rear_frame(x, ys, scale=1.0):
    y0, y1 = min(ys)-105*scale, max(ys)+105*scale
    ax.add_patch(Rectangle((x-10*scale, y0), 20*scale, y1-y0,
                           fc=GRAPH, ec=STEEL_L, lw=1.0, zorder=10))
    for j,y in enumerate(ys):
        ax.add_patch(Circle((x, y), 29*scale, fc=GRAPH, ec=STEEL_L, lw=1.0, zorder=14))
        ax.add_patch(Circle((x, y), 12*scale, fc=MAG, ec='none', zorder=15))
        trunnion(x+42*scale, x+9*scale, y)
    # Three dishes total on the rear frame, not a forest of antennas.
    for dy,sc in [(72, .78), (0, 1.0), (-72, .78)]:
        dish(x-50*scale, sum(ys)/2 + dy*scale, sc, side=-1)
    for y in ys:
        radiator_panel(x-18*scale, y+88*scale, 18*scale, 54*scale)
        radiator_panel(x-18*scale, y-88*scale, 18*scale, 54*scale)
        solar_wing(x-42*scale, y+74*scale, side=1, vertical=True, scale=scale*.78)
        solar_wing(x-42*scale, y-74*scale, side=-1, vertical=True, scale=scale*.78)
    # Two compact propulsion pods only on the rear fixed frame.
    for y in (sum(ys)/2-54*scale, sum(ys)/2+54*scale):
        ax.add_patch(Ellipse((x+29*scale, y), 22*scale, 12*scale,
                             fc=GRAPH, ec=STEEL_L, lw=.6, zorder=16))
        ax.add_patch(Ellipse((x+41*scale, y), 7*scale, 5*scale,
                             fc='#bf7444', ec='none', zorder=17))

# background stars
random.seed(11)
for _ in range(1200):
    x=random.uniform(0,W); y=random.uniform(0,H)
    a=.04+random.random()*.30
    ax.add_patch(Circle((x,y), .5+random.random()*1.1, fc='white', ec='none', alpha=a, zorder=0))

# header
T(58,1458,"ММОСО'Н", size=29, weight='bold')
T(58,1430,'Станция. Согласованные виды и трасса перемещения из переднего модуля стыковки', size=12, color=DIM)
T(58,1408,'Внешние элементы только на неподвижных передней и задней рамах; оболочки гладкие; зазор между цилиндрами пуст.', size=8.6, color=FAINT, style='italic')
L(58,1388,1842,1388,'#263c56',1)

# A — side
panel(50, 720, 1120, 640, 'A. БОКОВОЙ ВИД — ПОЛНАЯ КОМПОНОВКА',
      'R = 5 км · цилиндрическая часть 40 км · полная длина 49 км · межосевой зазор 11 км')
K=.0113
x0,x1=210,890
r=R*K
ys=[1030, 1030+GAPAX*K]
for y in ys: hull(x0,x1,y,r)
front_x=x1+94; rear_x=x0-94
for y in ys: trunnion(x1+15, front_x, y); trunnion(x0-15, rear_x, y)
front_frame(front_x,ys,.70)
rear_frame(rear_x,ys,.70)
# No longitudinal truss: show only the open gap and axes.
for y in ys: L(x0-4,y,x1+4,y, color=FAINT, lw=.7, ls='--', z=6, alpha=.5)
T((x0+x1)/2, min(ys)-r-38, '11 км свободного вакуумного зазора — никаких балок, тоннелей, кабелей или панелей', size=8.4, color='#f0bd57', ha='center')
leader(front_x+28, ys[0], front_x+175, ys[0]+95, 'передняя рама: 2 защищённых входа в шахты', color='#b8d0ef', size=8)
leader(rear_x-30, ys[1], rear_x-175, ys[1]+95, 'задняя рама: 3 антенны · радиаторы · батареи · ДМ', color='#b8d0ef', size=8, side='right')
leader(x1-80, ys[0]+r-18, x1-240, ys[0]+r+78, 'гладкая силовая оболочка', color='#b8d0ef', size=8)
# length dimension
L(x0, 810, x1, 810, FAINT, .8, z=20)
L(x0,800,x0,820,FAINT,.8,z=20); L(x1,800,x1,820,FAINT,.8,z=20)
T((x0+x1)/2,792,'49 км',size=8.4,color=DIM,ha='center')

# B — front frame
panel(1190, 720, 660, 640, 'B. ПЕРЕДНЯЯ РАМА · СТЫКОВКА',
      'вид со стороны причала · два независимых входа, по одному на цилиндр')
fx, fy1, fy2 = 1430, 1045, 865
# frame plane, two separate shell endcaps
for y in (fy1,fy2):
    ax.add_patch(Circle((fx,y), 92, fc=STEEL, ec=STEEL_D, lw=1.1, zorder=8))
    ax.add_patch(Circle((fx,y), 30, fc=GRAPH, ec=STEEL_L, lw=1, zorder=12))
    ax.add_patch(Circle((fx,y), 12, fc=MAG, ec='none', zorder=13))
# transverse stationary frame is drawn as a plane, not a longitudinal bridge
L(fx, fy2-120, fx, fy1+120, GRAPH, 12, z=6)
L(fx-12, fy2-120, fx-12, fy1+120, STEEL_L, 1, z=7)
for y in (fy1,fy2):
    for dy in (-44,44):
        ax.add_patch(FancyBboxPatch((fx+34,y+dy-10),150,20, boxstyle='round,pad=0,rounding_size=7',
                                    fc=DOCK, ec=STEEL_L, lw=.8, zorder=15))
        T(fx+108,y+dy,'Ш',size=7,color=GRAPH,ha='center',weight='bold',z=16)
    radiator_panel(fx-80,y+106,24,70); radiator_panel(fx-80,y-106,24,70)
    solar_wing(fx+100,y+75,1,True,.9); solar_wing(fx+100,y-75,-1,True,.9)
T(1218,1215,'КРАСНЫЕ',size=8,color=RAD_L,weight='bold')
T(1218,1197,'радиаторы — только на раме',size=8,color=INK)
T(1218,1162,'СИНИЕ',size=8,color=SOLAR_L,weight='bold')
T(1218,1144,'солнечные крылья — поворотные',size=8,color=INK)
leader(fx+185,fy1+44,1810,fy1+112,'2 независимых коридора → осевой вал',color='#b8d0ef',size=7.2,side='right')
leader(fx,fy2-30,1240,fy2-100,'подшипник + мотор-генератор',color=POWER,size=8)
T(1510,760,'Рама остаётся неподвижной.',size=8.4,color=SAFE,ha='center')
T(1510,744,'Цилиндры вращаются независимо.',size=8.4,color=SAFE,ha='center')

# C — transfer cross-section
panel(50, 55, 880, 610, 'C. ПУТЬ ИЗ СТЫКОВКИ В ЦИЛИНДР',
      'продольный разрез переднего торцевого узла; причал неподвижен')
# axis from left (fixed frame) to right (rotor interior)
yc=380
# fixed docking hub
ax.add_patch(FancyBboxPatch((105,yc-50),150,100,boxstyle='round,pad=0,rounding_size=18',fc=DOCK,ec=STEEL_L,lw=1,zorder=9))
T(180,yc,'П',size=25,color=GRAPH,ha='center',weight='bold')
# stationary airlocks
for i in range(2):
    xx=285+i*58
    ax.add_patch(Rectangle((xx,yc-38),42,76,fc='#657381',ec=STEEL_L,lw=1,zorder=10))
    L(xx+9,yc-30,xx+9,yc+30,STEEL_L,.7,z=12)
# magnetic bearing housing
ax.add_patch(Rectangle((420,yc-75),100,150,fc=GRAPH,ec=STEEL_L,lw=1,zorder=10))
for yy in (yc-35,yc+35):
    ax.add_patch(Rectangle((442,yy-10),56,20,fc=MAG,ec=STEEL_L,lw=.7,zorder=13))
T(470,yc+95,'активный\nмагнитный подшипник',size=8,color='#9ee4ff',ha='center')
# motor-generator
ax.add_patch(Ellipse((570,yc),70,120,fc='#4d5966',ec=STEEL_L,lw=1,zorder=10))
T(570,yc,'МГ',size=13,color=POWER,ha='center',weight='bold')
# hollow axial shaft
L(605,yc,780,yc,STEEL_L,22,z=10)
L(605,yc,780,yc,GRAPH,12,z=11)
# rotating seal
ax.add_patch(Rectangle((620,yc-42),32,84,fc='#b88749',ec=STEEL_L,lw=1,zorder=14))
T(636,yc+68,'вращающийся\nгермопереход',size=8,color='#ffd28a',ha='center')
# front dome and shaft
th=[math.pi*i/80 for i in range(81)]
xx=[780+210*math.sin(t) for t in th]; yy=[yc+180*math.cos(t) for t in th]
ax.add_patch(Polygon(list(zip(xx,yy))+[(780,yc-180)],closed=True,fc='#5f6d7a',ec=STEEL_L,lw=1,zorder=8))
# inclined shafts inside dome
for offset in (-26,26):
    L(780,yc+offset,930,yc+offset*2.8,SAFE,7,z=13)
    arrow(825,yc+offset*1.45,875,yc+offset*2.25,SAFE,1.1,z=18,ms=10)
T(760,yc+215,'две наклонные шахты\nв передней полусфере',size=7.4,color='#a4e4b9',ha='center')
T(180,190,'причал',size=8,color=INK,ha='center')
T(320,190,'шлюзы',size=8,color=INK,ha='center')
T(470,190,'опора',size=8,color=INK,ha='center')
T(570,190,'мотор',size=8,color=INK,ha='center')
T(700,190,'вал',size=8,color=INK,ha='center')
T(855,190,'к жилой\nповерхности',size=8,color=INK,ha='center')
# flow arrows
for a,b in [(250,285),(385,420),(520,570),(605,620),(652,780)]: arrow(a,yc+120,b,yc+120,POWER,1.2,z=20,ms=11)
T(470,120,'Герметичность обеспечивается шлюзами, вращающимся уплотнением и секционными гермодверями.',size=8.2,color=DIM,ha='center')

# D — motion and power
panel(960, 55, 890, 610, 'D. ВРАЩЕНИЕ И СИЛОВАЯ СХЕМА',
      'рамы неподвижны; собственные двигатели — только на задней раме')
# counter-rotating cylinders schematic
cx, cy = 1175, 450
for sy, col in [(cy+75,'#8095aa'),(cy-75,'#aeb9c5')]:
    ax.add_patch(FancyBboxPatch((1035,sy-38),280,76,boxstyle='round,pad=0,rounding_size=38',fc=col,ec=STEEL_L,lw=.8,zorder=8))
arrow(1100,cy+125,1230,cy+125, '#ffd28a',2,z=15,ms=14)
arrow(1230,cy-125,1100,cy-125, '#ffd28a',2,z=15,ms=14)
T(1175,cy+155,'два цилиндра вращаются встречно',size=9,color='#ffd28a',ha='center',weight='bold')
# fixed frames
for x in (990,1360):
    L(x,cy-155,x,cy+155,STEEL_L,8,z=10)
    L(x+8,cy-155,x+8,cy+155,GRAPH,4,z=11)
T(990,cy+175,'передняя\nрама',size=8,color=INK,ha='center')
T(1368,cy+175,'задняя рама:\nантенны + ДМ',size=8,color=INK,ha='center')
# power bus
T(1080,315,'РЕАКТОРНАЯ ШИНА',size=9,color=POWER,weight='bold')
ax.add_patch(Rectangle((1080,285),220,24,fc='#715b2d',ec=POWER,lw=.8,zorder=8))
arrow(1300,297,1395,297,POWER,1.5,z=15,ms=12)
for j,(label,val) in enumerate([('магнитные подшипники','управление и удержание'),('мотор-генераторы','раскрутка / торможение'),('шахты и гермопереход','насосы и автоматика')]):
    yy=235-j*45
    ax.add_patch(FancyBboxPatch((1395,yy-16),350,32,boxstyle='round,pad=0,rounding_size=8',fc='#122b3d',ec='#4a89a8',lw=.8,zorder=8))
    T(1410,yy,f'{label} · {val}',size=7.8,color=INK)
    if j<2: arrow(1395,yy-20,1395,yy-27,POWER,1,z=14,ms=8)
T(1080,98,'Квота узлов вращения, приводов и силовой электроники: 2 ГВт.',size=8.4,color=DIM)
T(1080,80,'Реакторы → неподвижные рамы; солнечные крылья — резервный источник.',size=8.4,color=DIM)
# station movement
T(1080,60,'Перемещение: задние сопла → тяга через цапфы и опоры.',size=8.2,color=SAFE)

# footer
L(58,38,1842,38,'#263c56',1)
T(58,18,"ММОСО'Н · ред. 7.0 · 09.09.2026 · внешние узлы только на рамах · verify_all.py 243/243",size=7.8,color=FAINT)
T(1840,18,'не масштабная схема · размеры и расчёты — в MMOSON_v7.docx',size=7.8,color=FAINT,ha='right')

fig.savefig('station_views.png', dpi=150, facecolor=BG)
print('station_views.png сохранён')
