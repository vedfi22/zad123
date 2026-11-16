from __future__ import annotations

import csv
import hashlib
import json
import math
import shutil
from pathlib import Path

import numpy as np
from reportlab.graphics.shapes import Drawing, Line, Rect, String, Circle, PolyLine, Polygon
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, Flowable


ROOT = Path(r'C:/Users/Саня/Documents/ChatGPT/Учеба')
SUB = ROOT / '01_Предметы/Силовая_электроника'
WORK = Path(__file__).parent
SOURCE = Path(r'C:/Users/Саня/Downloads/Telegram Desktop/Лр3 портнягин.pdf')
ORIGINAL_DIR = SUB / '01_Исходники/2026-11-11_ДЗ3_Фотоотчёт_Портнягин'
ASSETS = SUB / '02_Конспекты/2026-11-11_ДЗ3_по_фотоотчёту'
OUT = SUB / '02_Конспекты/2026-11-11_ДЗ3_по_фотоотчёту_для_печати.pdf'
for folder in [ORIGINAL_DIR, ASSETS]:
    folder.mkdir(parents=True, exist_ok=True)
copy = ORIGINAL_DIR / SOURCE.name
if copy.exists():
    assert copy.read_bytes() == SOURCE.read_bytes(), 'An existing source copy differs'
else:
    shutil.copy2(SOURCE, copy)

# Every decimal string below was read from the supplied photographs, not the old CSV.
GAMMA = ['0,1', '0,2', '0,3', '0,4', '0,5', '0,6', '0,7', '0,8', '0,9']
LOADS = [500, 450, 400, 350, 300, 250, 200, 150, 100]
VOLTAGE = [
    ['13,33','14,98','17,10','19,92','23,87','29,80','39,68','59,44','118,69'],
    ['13,33','14,98','17,09','19,91','23,85','29,77','39,62','59,33','118,40'],
    ['13,33','14,97','17,09','19,90','23,83','29,72','39,54','59,16','117,99'],
    ['13,33','14,97','17,08','19,88','23,79','29,65','39,42','58,93','117,40'],
    ['13,32','14,97','17,06','19,85','23,73','29,55','39,24','58,57','116,50'],
    ['13,32','14,96','17,04','19,80','23,64','29,39','38,94','58,00','115,06'],
    ['13,32','14,94','16,99','19,71','23,47','29,09','38,41','56,98','112,52'],
    ['13,31','14,90','16,90','19,52','23,13','28,49','37,34','54,94','107,50'],
    ['13,29','14,81','16,66','19,04','22,27','27,00','34,76','50,12','95,87'],
]
CURRENT = [
    ['0,027','0,030','0,034','0,040','0,048','0,060','0,079','0,119','0,237'],
    ['0,030','0,033','0,038','0,044','0,053','0,066','0,088','0,132','0,263'],
    ['0,033','0,037','0,043','0,050','0,060','0,074','0,099','0,148','0,295'],
    ['0,038','0,043','0,049','0,057','0,068','0,085','0,113','0,168','0,335'],
    ['0,044','0,050','0,057','0,066','0,079','0,099','0,131','0,195','0,388'],
    ['0,053','0,060','0,068','0,079','0,095','0,118','0,156','0,232','0,460'],
    ['0,067','0,075','0,085','0,099','0,117','0,145','0,192','0,285','0,563'],
    ['0,089','0,099','0,113','0,130','0,154','0,190','0,249','0,366','0,717'],
    ['0,133','0,148','0,167','0,190','0,223','0,270','0,348','0,501','0,959'],
]
# gamma, U_model, K_model, K_theory, U_theory, delta_percent, ripple_pp
SERIES1 = [
    ['0,1','13,33','1,111','1,111','13,33','-0,04','0,5'],
    ['0,2','14,98','1,248','1,250','15,00','-0,14','1,2'],
    ['0,3','17,10','1,425','1,429','17,14','-0,27','2,0'],
    ['0,4','19,92','1,660','1,667','20,00','-0,40','3,2'],
    ['0,5','23,87','1,989','2,000','24,00','-0,54','4,7'],
    ['0,6','29,80','2,483','2,500','30,00','-0,67','7,1'],
    ['0,7','39,68','3,307','3,333','40,00','-0,79','11,1'],
    ['0,8','59,44','4,954','5,000','60,00','-0,93','19,0'],
    ['0,9','118,69','9,891','10,000','120,00','-1,09','42,7'],
]


def number(value):
    return float(str(value).replace(',', '.'))


assert all(len(row) == 9 for row in VOLTAGE + CURRENT)
assert len(VOLTAGE) == len(CURRENT) == len(SERIES1) == 9
assert [row[1] for row in SERIES1] == VOLTAGE[0]
assert len(set((r, g) for r in LOADS for g in GAMMA)) == 81
max_current_rounding = 0
for row_idx, resistance in enumerate(LOADS):
    for col_idx in range(9):
        diff = abs(number(CURRENT[row_idx][col_idx]) - number(VOLTAGE[row_idx][col_idx]) / resistance)
        max_current_rounding = max(max_current_rounding, diff)
        assert diff <= 0.000551, (resistance, GAMMA[col_idx], diff)

data = {
    'source': str(SOURCE),
    'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
    'source_pages': {'parameters': 2, 'series1': 3, 'voltage': [3, 4], 'current': 4, 'waveforms': 5},
    'gamma_text': GAMMA, 'loads_ohm': LOADS,
    'voltage_text_V': VOLTAGE, 'current_text_A': CURRENT, 'series1_text': SERIES1,
    'provenance': 'Exact transcription of printed decimal strings from supplied PDF photographs',
    'waveforms': 'Separate ideal-model reconstruction from stated parameters; not digitized measurements',
}
(ASSETS / 'Данные_из_фотоотчёта.json').write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
with (ASSETS / 'Все_81_режим_из_фотоотчёта.csv').open('w', encoding='utf-8-sig', newline='') as f:
    writer = csv.writer(f, delimiter=';')
    writer.writerow(['R, Ом', 'γ', 'Uн, В', 'Iн, А', 'Страница источника'])
    for ri, resistance in enumerate(LOADS):
        for gi, g in enumerate(GAMMA):
            writer.writerow([resistance, g, VOLTAGE[ri][gi], CURRENT[ri][gi], '3-4'])

for name, filename in [('Times','times.ttf'),('Times-Bold','timesbd.ttf'),('Times-Italic','timesi.ttf')]:
    pdfmetrics.registerFont(TTFont(name, 'C:/Windows/Fonts/' + filename))
pdfmetrics.registerFontFamily('Times', normal='Times', bold='Times-Bold', italic='Times-Italic', boldItalic='Times-Bold')

BODY = ParagraphStyle('Body', fontName='Times', fontSize=12, leading=15.2, alignment=TA_JUSTIFY,
                      spaceAfter=7, firstLineIndent=16)
PLAIN = ParagraphStyle('Plain', parent=BODY, alignment=TA_LEFT, firstLineIndent=0)
SMALL = ParagraphStyle('Small', parent=PLAIN, fontSize=10.2, leading=12.5, spaceAfter=4)
HEAD = ParagraphStyle('Head', parent=PLAIN, fontName='Times-Bold', fontSize=13, leading=16.5, spaceBefore=4, spaceAfter=9)
CAPTION = ParagraphStyle('Caption', parent=PLAIN, alignment=TA_CENTER, fontSize=11.2, leading=13.5, spaceAfter=8)
FORMULA = ParagraphStyle('Formula', parent=PLAIN, alignment=TA_CENTER, fontSize=12.5, leading=18, spaceAfter=8)
CELL = ParagraphStyle('Cell', parent=PLAIN, alignment=TA_CENTER, fontSize=11.2, leading=13.2, spaceAfter=0)
CELL_SMALL = ParagraphStyle('CellSmall', parent=CELL, fontSize=10.3, leading=12)
BLACK = colors.black
GRID = colors.HexColor('#cccccc')
PAGE_W, PAGE_H = A4
MARGIN = 19 * mm
WIDTH = PAGE_W - 2 * MARGIN


def p(text, style=BODY):
    return Paragraph(text, style)


def h(text):
    return p(text, HEAD)


def caption(text):
    return p(text, CAPTION)


def table(rows, widths, small=False, row_height=None, padding=4):
    style = CELL_SMALL if small else CELL
    cells = [[p(str(value), style) for value in row] for row in rows]
    t = Table(cells, colWidths=widths, rowHeights=row_height, hAlign='CENTER')
    t.setStyle(TableStyle([
        ('GRID',(0,0),(-1,-1),0.45,colors.HexColor('#555555')),
        ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#ededed')),
        ('FONTNAME',(0,0),(-1,0),'Times-Bold'),
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ('TOPPADDING',(0,0),(-1,-1),padding),
        ('BOTTOMPADDING',(0,0),(-1,-1),padding),
        ('LEFTPADDING',(0,0),(-1,-1),3),
        ('RIGHTPADDING',(0,0),(-1,-1),3),
    ]))
    return t


class Pair(Flowable):
    def __init__(self, left, right, gap=12):
        super().__init__()
        self.left, self.right, self.gap = left, right, gap
        self.width = left.width + right.width + gap
        self.height = max(left.height, right.height)

    def draw(self):
        self.left.drawOn(self.canv, 0, self.height-self.left.height)
        self.right.drawOn(self.canv, self.left.width+self.gap, self.height-self.right.height)


def label(d, x, y, text, size=10, anchor='start', bold=False):
    d.add(String(x,y,text,fontName='Times-Bold' if bold else 'Times',fontSize=size,
                 textAnchor=anchor,fillColor=BLACK))


def axes(width, height, xmin, xmax, ymin, ymax, xticks, yticks, xlabel, ylabel, title,
         bottom=37, left=42, right=13, top=26, small=False):
    d = Drawing(width, height)
    x0,y0,x1,y1=left,bottom,width-right,height-top
    sx=lambda v: x0+(v-xmin)/(xmax-xmin)*(x1-x0)
    sy=lambda v: y0+(v-ymin)/(ymax-ymin)*(y1-y0)
    for v in xticks:
        x=sx(v)
        d.add(Line(x,y0,x,y1,strokeColor=GRID,strokeWidth=.35))
        d.add(Line(x,y0,x,y0-3,strokeWidth=.6))
        s=f'{v:g}'.replace('.',',')
        label(d,x,y0-14,s,9.3,anchor='middle')
    for v in yticks:
        y=sy(v)
        d.add(Line(x0,y,x1,y,strokeColor=GRID,strokeWidth=.35))
        d.add(Line(x0-3,y,x0,y,strokeWidth=.6))
        label(d,x0-6,y-3,f'{v:g}'.replace('.',','),9.3,anchor='end')
    d.add(Rect(x0,y0,x1-x0,y1-y0,fillColor=None,strokeWidth=.65))
    label(d,(x0+x1)/2,y0-30,xlabel,10.5,anchor='middle')
    label(d,x0,y1+10,ylabel,10.5)
    label(d,width/2,height-10,title,11.5,anchor='middle',bold=True)
    return d,sx,sy,(x0,y0,x1,y1)


def marker(d,x,y,index,size=2.4,color=BLACK):
    k=index%5
    if k==0:
        d.add(Circle(x,y,size,fillColor=color,strokeColor=color,strokeWidth=.6))
    elif k==1:
        d.add(Rect(x-size,y-size,2*size,2*size,fillColor=colors.white,strokeColor=color,strokeWidth=.8))
    elif k==2:
        d.add(Polygon([x,y+size+1,x-size-1,y-size,x+size+1,y-size],fillColor=colors.white,strokeColor=color,strokeWidth=.8))
    elif k==3:
        d.add(Line(x-size,y-size,x+size,y+size,strokeColor=color,strokeWidth=.8))
        d.add(Line(x-size,y+size,x+size,y-size,strokeColor=color,strokeWidth=.8))
    else:
        d.add(Polygon([x,y+size+1,x-size-1,y,x,y-size-1,x+size+1,y],fillColor=colors.white,strokeColor=color,strokeWidth=.8))


def curve(d, sx, sy, xs, ys, color=BLACK, line_width=1.1, dash=None, dots=False, index=0):
    points=[]
    for x,y in zip(xs,ys):
        points.extend([float(sx(x)),float(sy(y))])
    if line_width > 0:
        d.add(PolyLine(points,strokeColor=color,strokeWidth=line_width,strokeDashArray=dash))
    if dots:
        for x,y in zip(xs,ys): marker(d,sx(x),sy(y),index,color=color)


def gain_pair():
    width=(WIDTH-14)/2
    height=185
    d1,x,y,_=axes(width,height,0,.9,0,10.5,[0,.2,.4,.6,.8],[0,2,4,6,8,10],'γ','Кп','Кп от γ',left=32,right=8)
    theory=np.linspace(0,.9,240)
    curve(d1,x,y,theory,1/(1-theory),line_width=1)
    curve(d1,x,y,[number(g) for g in GAMMA],[number(r[2]) for r in SERIES1],
          line_width=0,dots=True,index=0)
    label(d1,43,148,'Линия - теория',9)
    label(d1,43,135,'Точки - таблица 2',9)
    d2,x,y,_=axes(width,height,1,10,0,1,[2,4,6,8,10],[0,.2,.4,.6,.8,1],'Кп','γ','γ от Кп',left=32,right=8)
    theory=np.linspace(1,10,240)
    curve(d2,x,y,theory,1-1/theory,line_width=1)
    curve(d2,x,y,[number(r[2]) for r in SERIES1],[number(g) for g in GAMMA],
          line_width=0,dots=True,index=0)
    label(d2,95,66,'Линия - теория',9)
    label(d2,95,53,'Точки - таблица 2',9)
    return Pair(d1,d2,14)


def family(zoom=False):
    height=179 if zoom else 285
    d,x,y,_=axes(WIDTH,height,0,.26 if zoom else 1.02,12 if zoom else 0,26 if zoom else 125,
                 [0,.05,.10,.15,.20,.25] if zoom else [0,.2,.4,.6,.8,1],
                 [12,14,16,18,20,22,24,26] if zoom else [0,20,40,60,80,100,120],
                 'Iн, А','Uн, В','Увеличенный участок для γ = 0,1…0,5' if zoom else 'Семейство внешних характеристик',
                 bottom=35 if zoom else 82,left=40,right=13)
    indices=range(5) if zoom else range(9)
    for gi in indices:
        shade=[0,.26,.45,0,.26,.45,0,.26,.45][gi]
        col=colors.Color(shade,shade,shade)
        dash=None if gi<3 else ([4,2] if gi<6 else [1.2,1.8])
        xs=[number(row[gi]) for row in CURRENT]
        ys=[number(row[gi]) for row in VOLTAGE]
        curve(d,x,y,xs,ys,color=col,dash=dash,dots=True,index=gi)
        if zoom:
            label(d,min(x(xs[-1])+7,WIDTH-35),y(ys[-1])-3,'γ='+GAMMA[gi],9.5)
        else:
            lx=55+(gi%3)*146
            ly=39-(gi//3)*14
            d.add(Line(lx,ly,lx+21,ly,strokeColor=col,strokeWidth=1,strokeDashArray=dash))
            marker(d,lx+10,ly,gi,color=col)
            label(d,lx+27,ly-3,'γ = '+GAMMA[gi],10)
    return d


def schematic():
    d=Drawing(WIDTH,185)
    top,bottom=144,39
    source,sw,cap,res,volt=26,178,302,380,449
    def ln(a,b,c,e): d.add(Line(a,b,c,e,strokeWidth=1))
    ln(source,top,72,top)
    ln(116,top,sw,top)
    d.add(Rect(72,top-7,44,14,fillColor=colors.white,strokeWidth=1))
    label(d,94,165,'L1 = 1 Гн',10.5,anchor='middle')
    ln(source,top,source,99);ln(source,84,source,bottom)
    ln(source-12,99,source+12,99);ln(source-8,88,source+8,88)
    label(d,source+20,107,'+',11)
    label(d,source+18,82,'12 В',10.5)
    ln(source,bottom,volt,bottom)
    ln(sw,top,222,top)
    d.add(Polygon([222,top-9,222,top+9,240,top],fillColor=colors.white,strokeWidth=1))
    ln(242,top-10,242,top+10);ln(242,top,volt,top)
    label(d,232,165,'VD1',10.5,anchor='middle')
    # Ideal controlled transistor symbol, with gate connection kept separate from the power rail.
    ln(sw,top,sw,113);ln(sw,75,sw,bottom)
    d.add(Rect(sw-7,75,14,38,fillColor=colors.white,strokeWidth=1))
    label(d,sw-14,92,'VT1',10.5,anchor='end')
    ln(sw+7,94,220,94);ln(220,94,220,79)
    d.add(Circle(220,65,14,fillColor=colors.white,strokeWidth=1))
    label(d,220,61,'G1',9,anchor='middle');ln(220,51,220,bottom)
    ln(cap,top,cap,105);ln(cap-13,105,cap+13,105);ln(cap-13,96,cap+13,96);ln(cap,96,cap,bottom)
    label(d,cap+19,89,'C1',10.5);label(d,cap+19,75,'10 мкФ',10)
    ln(res,top,res,115);d.add(Rect(res-6,77,12,38,fillColor=colors.white,strokeWidth=1));ln(res,77,res,bottom)
    label(d,res+14,95,'Rн',10.5);label(d,res-14,57,'500…100 Ом',10,anchor='end')
    ln(volt,top,volt,110);d.add(Circle(volt,96,14,fillColor=colors.white,strokeWidth=1));ln(volt,82,volt,bottom)
    label(d,volt,92,'V',11,anchor='middle')
    for xx in [sw,cap,res,volt]:
        d.add(Circle(xx,top,1.7,fillColor=BLACK,strokeColor=BLACK))
        d.add(Circle(xx,bottom,1.7,fillColor=BLACK,strokeColor=BLACK))
    d.add(Circle(220,bottom,1.7,fillColor=BLACK,strokeColor=BLACK))
    label(d,WIDTH/2,18,'G1: прямоугольные импульсы 5 В, 500 Гц; коэффициент заполнения γ',10,anchor='middle')
    label(d,WIDTH/2,3,'VT1 и VD1 - идеальные элементы; V - вольтметр постоянного тока',10,anchor='middle')
    return d


# Reconstruct only the additional time-domain illustrations; source table strings remain immutable.
VIN, L, C, F = 12., 1., 10e-6, 500.
PERIOD, G, R = 1/F, .9, 500.
TON, TOFF = G*PERIOD, (1-G)*PERIOD
A=np.array([[0.,-1/L],[1/C,-1/(R*C)]])
B=np.array([VIN/L,0.])
eigen, vectors=np.linalg.eig(A)
vinv=np.linalg.inv(vectors)
def offmap(t):
    m=np.real_if_close(vectors @ np.diag(np.exp(eigen*t)) @ vinv).astype(float)
    return m,np.linalg.solve(A,(m-np.eye(2))@B)
ON=np.diag([1.,math.exp(-TON/(R*C))]); ON_B=np.array([VIN*TON/L,0.])
OFF,OFF_B=offmap(TOFF)
MAP=OFF@ON; MAP_B=OFF@ON_B+OFF_B
STEADY=np.linalg.solve(np.eye(2)-MAP,MAP_B)
def samples(x0, t0, n_on=38, n_off=15):
    ts=[]; xs=[]
    for dt in np.linspace(0,TON,n_on,endpoint=False):
        ts.append(t0+dt)
        xs.append([x0[0]+VIN*dt/L,x0[1]*math.exp(-dt/(R*C))])
    xend=ON@x0+ON_B
    for dt in np.linspace(0,TOFF,n_off+1):
        m,b=offmap(dt); ts.append(t0+TON+dt);xs.append(m@xend+b)
    return np.array(ts),np.array(xs)

startup_t=[];startup_u=[];mean_t=[];mean_u=[]
state=np.zeros(2)
for k in range(150):
    t,xs=samples(state,k*PERIOD)
    startup_t.extend(t*1000);startup_u.extend(xs[:,1])
    mean_t.append((k+.5)*PERIOD*1000)
    mean_u.append(float(np.trapezoid(xs[:,1],t)/PERIOD))
    state=MAP@state+MAP_B
steady_t=[];steady_u=[];steady_i=[]
for k in range(3):
    t,xs=samples(STEADY,k*PERIOD,n_on=90,n_off=30)
    steady_t.extend(t*1000);steady_i.extend(xs[:,0]);steady_u.extend(xs[:,1])
metrics={
    'max_current_rounding_difference_A':max_current_rounding,
    'reconstruction_U_min_V':min(steady_u),'reconstruction_U_max_V':max(steady_u),
    'reconstruction_IL_min_A':min(steady_i),'reconstruction_IL_max_A':max(steady_i),
    'original_table_cells_preserved':162,
    'original_series1_cells_preserved':63,
}
(ASSETS/'Проверка_переноса.json').write_text(json.dumps(metrics,ensure_ascii=False,indent=2),encoding='utf-8')


def wave_start():
    d,x,y,_=axes(WIDTH,198,0,300,0,145,[0,50,100,150,200,250,300],[0,20,40,60,80,100,120,140],
                 't, мс','uC, В','а) Начало переходного процесса',left=43)
    curve(d,x,y,startup_t,startup_u,color=colors.HexColor('#777777'),line_width=.35)
    curve(d,x,y,mean_t,mean_u,line_width=1.1)
    curve(d,x,y,[0,300],[120,120],line_width=.8,dash=[5,3])
    label(d,58,164,'Сплошная линия - среднее за период',9.5)
    label(d,58,151,'Штриховая линия - 120 В по приближённой теории',9.5)
    return d


def wave_steady(which):
    is_u=which=='voltage'
    d,x,y,_=axes(WIDTH,166,0,6,90 if is_u else 2.36,145 if is_u else 2.39,
                 [0,1,2,3,4,5,6],[100,110,120,130,140] if is_u else [2.36,2.37,2.38,2.39],
                 't, мс','uC, В' if is_u else 'iL, А',
                 'б) Напряжение в установившемся режиме' if is_u else 'в) Ток дросселя в установившемся режиме',left=43)
    curve(d,x,y,steady_t,steady_u if is_u else steady_i,line_width=1.15)
    return d


pages=[]
cover=[]
title_style=ParagraphStyle('Title',parent=PLAIN,fontName='Times-Bold',fontSize=19,leading=24,alignment=TA_CENTER,spaceAfter=16)
cover.extend([
    Spacer(1,22*mm),
    p('РГУ нефти и газа (НИУ) имени И. М. Губкина',ParagraphStyle('University',parent=PLAIN,alignment=TA_CENTER,fontSize=14,leading=18)),
    Spacer(1,42*mm),
    p('СИЛОВАЯ ЭЛЕКТРОНИКА',ParagraphStyle('Discipline',parent=PLAIN,alignment=TA_CENTER,fontSize=15,leading=20)),
    Spacer(1,10*mm),
    p('Отчёт по домашнему заданию 3',title_style),
    p('Повышающий преобразователь<br/>постоянного напряжения',ParagraphStyle('Topic',parent=PLAIN,alignment=TA_CENTER,fontSize=17,leading=22)),
    Spacer(1,33*mm),
    p('Выполнил: Шарипов Александр Александрович<br/>Группа АЭ-24-03',ParagraphStyle('Author',parent=PLAIN,leftIndent=160,fontSize=12,leading=18)),
    Spacer(1,6*mm),
    p('Преподаватель: Портнягин Николай Николаевич',ParagraphStyle('Teacher',parent=PLAIN,leftIndent=160,fontSize=12,leading=18)),
    Spacer(1,35*mm),
    p('Москва 2026',ParagraphStyle('Year',parent=PLAIN,alignment=TA_CENTER,fontSize=12,leading=16)),
])
pages.append((A4,cover))

pages.append((A4,[
    h('1 Цель работы'),
    p('Исследовать модель повышающего преобразователя постоянного тока, определить зависимость коэффициента передачи по напряжению от коэффициента заполнения импульсов управления, получить семейство внешних характеристик и сравнить результаты с теорией.'),
    h('2 Краткие теоретические сведения'),
    p('Повышающий преобразователь содержит дроссель L, ключ VT, диод VD, выходной конденсатор C и нагрузку R. Когда ключ замкнут в течение γT, ток дросселя нарастает за счёт источника, а нагрузку питает конденсатор. После размыкания ключа энергия дросселя вместе с энергией источника через диод передаётся конденсатору и нагрузке.'),
    p('Из баланса вольт-секунд на дросселе для непрерывного тока и малой пульсации выходного напряжения получаются зависимости:'),
    p('U<sub>вых</sub> ≈ U<sub>вх</sub> / (1 − γ); &nbsp;&nbsp; К<sub>п</sub> = U<sub>вых</sub> / U<sub>вх</sub> ≈ 1 / (1 − γ); &nbsp;&nbsp; γ ≈ 1 − 1 / К<sub>п</sub>.',FORMULA),
    p('Здесь γ = T<sub>и</sub> / T - коэффициент заполнения; T = 1/f - период коммутации. Условие непрерывного тока дросселя в принятом приближении:'),
    p('L &gt; L<sub>кр</sub> = γ(1 − γ)<super>2</super>R / (2f).',FORMULA),
    p('Максимум L<sub>кр</sub> достигается при γ = 1/3. При R = 500 Ом и f = 500 Гц он равен 0,074 Гн. Принятая индуктивность L = 1 Гн заметно больше этого значения, что соответствует непрерывному току в рассматриваемых установившихся режимах.'),
    p('При малых пульсациях размах выходного напряжения оценивается как ΔU ≈ I<sub>н</sub>γT / C. При существенной пульсации среднее напряжение может отличаться от результата приближённой формулы.'),
    h('3 Модель и параметры'),
    schematic(),
    caption('Рисунок 1 - Схема модели повышающего преобразователя'),
    p('Табличные результаты приведены по отчёту [1]. В нём указаны нулевые начальные условия, расчёт 3000 периодов (6 с) и усреднение напряжения за последние 20 периодов. Система для тока дросселя и напряжения конденсатора на каждом интервале работы ключа линейна.',SMALL),
]))

params=[
    ['<b>Параметр</b>','<b>Значение</b>'],
    ['Индуктивность L','1 Гн'],
    ['Ёмкость C','10 мкФ'],
    ['Сопротивление нагрузки R','500 Ом; во второй серии 500…100 Ом<br/>с шагом 50 Ом'],
    ['Входное напряжение U<sub>вх</sub>','12 В'],
    ['Частота коммутации f','500 Гц; T = 2 мс'],
    ['Амплитуда импульсов управления','5 В'],
    ['Коэффициент заполнения γ','0,1…0,9 с шагом 0,1'],
    ['Ключ и диод','Идеальные'],
]
series_headers=['<b>γ</b>','<b>U<sub>вых</sub>, В</b>','<b>К<sub>п</sub><br/>модель</b>','<b>К<sub>п</sub><br/>теория</b>',
                '<b>U<sub>вых теор</sub>, В</b>','<b>δ, %</b>','<b>ΔU, В</b>']
pages.append((A4,[
    caption('Таблица 1 - Параметры модели'),
    table(params,[WIDTH*.46,WIDTH*.54],small=True,padding=3),
    Spacer(1,5),
    h('4 Коэффициент передачи и заполнение импульсов'),
    p('При R = 500 Ом коэффициент γ изменяется от 0,1 до 0,9. Для каждой точки К<sub>п</sub> = U<sub>вых</sub> / 12. Значения и их исходное округление сохранены в таблице 2.'),
    caption('Таблица 2 - Результаты первой серии при R = 500 Ом'),
    table([series_headers]+SERIES1,[31,68,76,76,90,68,WIDTH-409],small=True),
    Spacer(1,7),
    p('δ = (U<sub>вых</sub> − U<sub>вых теор</sub>) / U<sub>вых теор</sub> · 100 %; ΔU - размах пульсаций на нагрузке.',SMALL),
    gain_pair(),
    caption('Рисунок 2 - Зависимости Кп(γ) и γ(Кп) в сравнении с теорией'),
]))

land=landscape(A4)
landwidth=land[0]-2*MARGIN
wideheaders=['<b>R, Ом</b>']+['<b>γ = '+g+'</b>' for g in GAMMA]
widths=[55]+[(landwidth-55)/9]*9
pages.append((land,[
    h('5 Семейство внешних характеристик'),
    p('При каждом γ сопротивление нагрузки изменяется от 500 до 100 Ом с шагом 50 Ом. Для 81 сочетания (γ, R) приведены напряжение U<sub>н</sub> и ток I<sub>н</sub>. В модели I<sub>н</sub> = U<sub>н</sub> / R; табличные значения округлены.'),
    caption('Таблица 3 - Напряжение на нагрузке Uн, В'),
    table([wideheaders]+[[str(r)]+row for r,row in zip(LOADS,VOLTAGE)],widths,row_height=18,padding=2),
    Spacer(1,10),
    caption('Таблица 4 - Ток нагрузки Iн, А'),
    table([wideheaders]+[[str(r)]+row for r,row in zip(LOADS,CURRENT)],widths,row_height=18,padding=2),
]))

pages.append((A4,[
    family(),
    Spacer(1,5),
    family(zoom=True),
    caption('Рисунок 3 - Внешние характеристики Uн(Iн) по таблицам 3 и 4'),
    h('6 Сравнение с теорией и анализ результатов'),
    p('В первой серии модельные точки близки к теоретической кривой К<sub>п</sub> = 1/(1 − γ). Коэффициент передачи растёт нелинейно: при γ = 0,5 он равен 1,989, а при γ = 0,9 - 9,891 (теоретически 2 и 10 соответственно).'),
    p('Относительное отклонение изменяется от −0,04 % при γ = 0,1 до −1,09 % при γ = 0,9. Модельное среднее напряжение ниже приближённого теоретического. При C = 10 мкФ и γ = 0,9 напряжение колеблется примерно от 98 до 141 В; табличный размах составляет 42,7 В.'),
    p('Внешние характеристики имеют падающий характер. При уменьшении R конденсатор сильнее разряжается за время γT, пульсации увеличиваются и среднее напряжение снижается. При γ = 0,1 изменение составляет 13,33 → 13,29 В, а при γ = 0,9 - 118,69 → 95,87 В, то есть около 19 %.'),
]))

pages.append((A4,[
    h('Переходный процесс и установившиеся пульсации'),
    p('При γ = 0,9 и R = 500 Ом средний ток дросселя в установившемся режиме составляет около 2,37 А. Баланс вольт-секунд относится к среднему напряжению на интервале разомкнутого ключа: в отчёте [1] для него указано 120,03 В. Полное среднее напряжение по таблице 2 равно 118,69 В.'),
    wave_start(),
    Spacer(1,8),
    wave_steady('voltage'),
    Spacer(1,8),
    wave_steady('current'),
    caption('Рисунок 4 - Расчётная иллюстрация переходного процесса и пульсаций<br/>при γ = 0,9 и R = 500 Ом'),
    p('Временные кривые восстановлены по идеальной модели с параметрами таблицы 1. На графике а показаны первые 300 мс; процесс на этом участке ещё не завершён. Графики б и в относятся к установившемуся периодическому режиму.',SMALL),
]))

pages.append((A4,[
    h('7 Источники расхождений и погрешности'),
    p('<b>Пульсации выходного напряжения.</b> Основная причина расхождения с формулой К<sub>п</sub> ≈ 1/(1 − γ) - её применение при заметных пульсациях. Вольтметр постоянного тока показывает среднее значение. Влияние пульсаций возрастает с γ и током нагрузки.'),
    p('<b>Незавершённый переходный процесс.</b> Если снять показание до установления режима, напряжение будет отличаться от установившегося. Перед записью результатов необходимо дождаться периодического повторения формы сигнала и стабилизации среднего значения; фиксированное короткое время ожидания этого не гарантирует.'),
    p('<b>Неидеальность элементов реальной схемы.</b> Падение напряжения на диоде и транзисторе, сопротивление обмотки дросселя, ESR конденсатора и потери в сердечнике могут понижать выходное напряжение. В идеальной модели эти эффекты не учитываются.'),
    p('<b>Погрешность отсчёта и усреднения.</b> Цифровое показание и таблицы округляются; результат также зависит от интервала усреднения и численного метода. Поэтому пересчёт по уже округлённым значениям может дать небольшое отличие в последнем знаке.'),
    p('<b>Режим тока дросселя.</b> Теоретическая зависимость относится к непрерывному току. При уменьшении L или увеличении R ток может стать прерывистым, и коэффициент передачи изменится. Здесь L = 1 Гн превышает максимальную оценку L<sub>кр</sub> = 0,074 Гн.'),
    h('8 Выводы'),
    p('В диапазоне γ = 0,1…0,9 выходное напряжение повышающего преобразователя превышает входные 12 В. При R = 500 Ом коэффициент передачи изменяется от 1,111 до 9,891.'),
    p('Зависимость γ(К<sub>п</sub>) хорошо согласуется с приближённой теорией γ ≈ 1 − 1/К<sub>п</sub>. Максимальное относительное отклонение в первой серии составляет 1,09 % при γ = 0,9.'),
    p('Внешние характеристики падают с ростом тока нагрузки. Наибольшее снижение напряжения наблюдается при больших γ и малых R: в таблице при γ = 0,9 и R = 100 Ом указано 95,87 В. Для уменьшения пульсаций следует увеличивать ёмкость фильтра либо частоту коммутации.'),
    p('Для рассмотренных установившихся режимов принята непрерывность тока дросселя. Условие L &gt; L<sub>кр</sub> выполняется с большим запасом.'),
    Spacer(1,7),
    h('Источники'),
    p('[1] Предоставленный отчёт «Лр3 портнягин.pdf», 7 страниц фотографий. Параметры - стр. 2; первая серия - стр. 3; таблицы напряжения и тока - стр. 3–4; временные графики - стр. 5.',SMALL),
    p('[2] Условие домашнего задания по силовой электронике «СЭ2025 эл трансформатор.pdf», 5 страниц. Схема и параметры - стр. 1–2; серии опытов и состав отчёта - стр. 3–5.',SMALL),
]))


def save_pages():
    cv=canvas.Canvas(str(OUT),pagesize=A4,pageCompression=1)
    cv.setTitle('Силовая электроника - Домашнее задание 3 - Повышающий преобразователь')
    cv.setAuthor('Шарипов Александр Александрович')
    layout=[]
    for index,(size,items) in enumerate(pages):
        w,ht=size
        cv.setPageSize(size)
        content_width=w-2*MARGIN
        top=ht-18*mm
        bottom=18*mm
        total=0
        measured=[]
        for element in items:
            space_before=element.getSpaceBefore() if hasattr(element,'getSpaceBefore') else 0
            space_after=element.getSpaceAfter() if hasattr(element,'getSpaceAfter') else 0
            ew,eh=element.wrap(content_width,10000)
            measured.append((element,ew,eh,space_before,space_after))
            total+=eh+space_before+space_after
        available=top-bottom
        layout.append({'page':index+1,'width_pt':w,'height_pt':ht,'used_pt':total,'available_pt':available,'spare_pt':available-total})
        if total>available+.1:
            print(json.dumps(layout,ensure_ascii=False,indent=2))
            raise RuntimeError(f'Page {index+1} overflow: {total:.1f} > {available:.1f}')
        y=top
        for el,ew,eh,sb,sa in measured:
            y-=sb+eh
            x=MARGIN+(content_width-ew)/2 if isinstance(el,(Table,Drawing,Pair)) else MARGIN
            el.drawOn(cv,x,y)
            y-=sa
        if index>0:
            cv.setFont('Times',10)
            cv.drawCentredString(w/2,10*mm,str(index+1))
        cv.showPage()
    cv.save()
    (WORK/'layout.json').write_text(json.dumps(layout,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'output':str(OUT),'pages':len(pages),'layout':layout,'metrics':metrics},ensure_ascii=False,indent=2))


if __name__=='__main__':
    save_pages()
