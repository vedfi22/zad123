"""Reproduce the 12-page A4 report. Requires reportlab.
The exact numerical checks live in расчёт.py. Run from any working directory.
Temporary graphics are created under the system temporary directory.
"""
from pathlib import Path
import importlib.util, math, tempfile, json
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('circuit',ROOT/'расчёт.py')
calc=importlib.util.module_from_spec(spec); spec.loader.exec_module(calc)
RESULT=calc.calculate()
OUT=ROOT/'2026-10-24_ДЗ1_Цепь_постоянного_тока_В3_Г3_Для_печати.pdf'
FONTS=Path('C:/Windows/Fonts')
pdfmetrics.registerFont(TTFont('Body',str(FONTS/'arial.ttf')))
pdfmetrics.registerFont(TTFont('Bold',str(FONTS/'arialbd.ttf')))
pdfmetrics.registerFont(TTFont('Math',str(FONTS/'times.ttf')))
pdfmetrics.registerFontFamily('Body',normal='Body',bold='Bold',italic='Body',boldItalic='Bold')
ST={
 'body':ParagraphStyle('body',fontName='Body',fontSize=11,leading=15,spaceAfter=6),
 'small':ParagraphStyle('small',fontName='Body',fontSize=9.5,leading=12.8,spaceAfter=5),
 'eq':ParagraphStyle('eq',fontName='Body',fontSize=11.4,leading=16,spaceAfter=6,leftIndent=10),
 'title':ParagraphStyle('title',fontName='Bold',fontSize=19,leading=24,spaceAfter=12),
 'h':ParagraphStyle('h',fontName='Bold',fontSize=14,leading=18,spaceAfter=8),
 'sub':ParagraphStyle('sub',fontName='Bold',fontSize=11.5,leading=16,spaceAfter=7),
 'cell':ParagraphStyle('cell',fontName='Body',fontSize=10,leading=13),
}
W,H=A4; L=19*mm; RIGHT=19*mm; WIDTH=W-L-RIGHT; BOTTOM=18*mm
c=canvas.Canvas(str(OUT),pagesize=A4,pageCompression=1)
c.setTitle('ДЗ №1. Линейная цепь постоянного тока. Вариант 3, группа 3')
c.setAuthor('Учебный расчёт по DZ1_GI_GF.pdf')
page=0; y=0; page_bottoms=[]; transcript=[]

def new(title):
 global page,y
 if page:
  page_bottoms.append((page,y)); c.showPage()
 page+=1
 c.setFont('Body',8.5); c.setFillGray(0)
 c.drawString(L,H-13*mm,'ДЗ №1  |  Вариант 3 / группа 3  |  расчёт при 3×ЭДС')
 c.setLineWidth(.6); c.line(L,H-16*mm,W-RIGHT,H-16*mm)
 c.setFont('Body',8.5); c.drawRightString(W-RIGHT,11*mm,f'{page} / 12')
 y=H-23*mm
 para(title,'h')
 transcript.append('\n## '+title+'\n')

def para(text,kind='body',gap=None):
 global y
 p=Paragraph(text,ST[kind]); _,hh=p.wrap(WIDTH,1000)
 if y-hh<BOTTOM: raise RuntimeError(f'Page {page} overflow: {text[:60]} at y={y}')
 p.drawOn(c,L,y-hh); y-=hh+(ST[kind].spaceAfter if gap is None else gap)
 transcript.append(text+'\n')

def eq(t): para(t,'eq')
def sub(t): para(t,'sub')
def table(rows,widths=None):
 global y
 data=[[Paragraph(str(v),ST['cell']) for v in row] for row in rows]
 if widths: widths=[WIDTH*x/sum(widths) for x in widths]
 t=Table(data,colWidths=widths,repeatRows=1,hAlign='LEFT')
 t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'MIDDLE'),('GRID',(0,0),(-1,-1),.45,colors.black),
  ('LINEBELOW',(0,0),(-1,0),1,colors.black),('BACKGROUND',(0,0),(-1,0),colors.Color(.94,.94,.94)),
  ('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),
  ('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5)]))
 _,hh=t.wrap(WIDTH,1000)
 if y-hh<BOTTOM: raise RuntimeError(f'Table overflow on page {page}')
 t.drawOn(c,L,y-hh); y-=hh+10
 transcript.extend(' | '.join(str(v) for v in row)+'\n' for row in rows)

def figure(fn,height,base_width=500,base_height=None):
 global y
 if y-height<BOTTOM: raise RuntimeError(f'Figure overflow page {page}')
 c.saveState(); c.translate(L,y-height)
 if base_height: c.scale(WIDTH/base_width,height/base_height)
 else: c.scale(WIDTH/base_width,WIDTH/base_width)
 fn(c); c.restoreState(); y-=height+8

def txt(x,y,s,size=11,bold=False,align='left'):
 c.setFont('Bold' if bold else 'Body',size)
 if align=='center': c.drawCentredString(x,y,s)
 elif align=='right': c.drawRightString(x,y,s)
 else: c.drawString(x,y,s)

def line(*points,width=1.3):
 c.setLineWidth(width)
 for a,b in zip(points,points[1:]): c.line(*a,*b)

def arrow(x1,y1,x2,y2,label=None,dx=0,dy=0):
 c.setLineWidth(1); c.line(x1,y1,x2,y2)
 angle=math.atan2(y2-y1,x2-x1); a=5
 p=c.beginPath(); p.moveTo(x2,y2)
 p.lineTo(x2-a*math.cos(angle-.42),y2-a*math.sin(angle-.42))
 p.lineTo(x2-a*math.cos(angle+.42),y2-a*math.sin(angle+.42));p.close()
 c.drawPath(p,fill=1,stroke=1)
 if label: txt((x1+x2)/2+dx,(y1+y2)/2+dy,label,10,align='center')

def dot(x,y,name=None,dx=7,dy=5):
 c.circle(x,y,2.7,fill=1,stroke=0)
 if name: txt(x+dx,y+dy,name,11,True)

def resistor(x,y,label,vertical=False):
 c.setFillGray(1); c.setStrokeGray(0); c.setLineWidth(1.3)
 if vertical:
  c.rect(x-8,y-18,16,36,fill=1,stroke=1); c.setFillGray(0)
  txt(x-13 if x>450 else x+13,y-3,label,align='right' if x>450 else 'left')
 else:
  c.rect(x-21,y-7,42,14,fill=1,stroke=1);c.setFillGray(0);txt(x,y+12,label,11,align='center')
 c.setFillGray(0)

def source(x,y,label,up=True):
 c.setFillGray(1);c.circle(x,y,16,fill=1,stroke=1);c.setFillGray(0)
 arrow(x,y-12 if up else y+12,x,y+12 if up else y-12)
 txt(x-24,y-3,label,11,align='right')

def circuit(cv,actual=False):
 # Same labelled junctions and all instrument terminals as original p.3.
 # Coordinates have bottom padding for direction arrows.
 line((26,370),(480,370),(480,65),(26,65),(26,370))
 line((240,370),(240,120))
 line((75,65),(75,215),(118,215),(118,120),(420,120),(420,105))
 line((420,85),(420,65))
 resistor(26,220,'R6',True);resistor(480,220,'R5',True)
 resistor(240,65,'R4');resistor(75,100,'R03',True)
 source(75,165,'E3',True);resistor(170,120,'R3');resistor(345,120,'R1')
 resistor(240,337,'R2',True);resistor(240,273,'R02',True);source(240,225,'E2',False)
 # Voltage-source terminal convention U1, plus at D, minus at E.
 for yy in [105,85]:
  c.setFillGray(1);c.circle(420,yy,4.5,stroke=1,fill=1);c.setFillGray(0)
  line((417,yy+3),(423,yy-3),width=.8)
 txt(430,101,'+',11);txt(430,81,'−',11)
 arrow(405,108,405,82);txt(394,92,'U1',10,align='right')
 # Ideal wattmeter, current coil upper star, voltage coil left star.
 c.setFillGray(1);c.circle(240,164,18,fill=1,stroke=1);c.setFillGray(0)
 line((240,190),(240,120),width=2.8)
 line((240,190),(200,190),(200,164),(300,164),(300,305),(240,305),width=.7)
 txt(225,182,'*',15);txt(212,149,'*',15);txt(263,180,'pW',11)
 # Voltmeter between M and B.
 line((240,305),(75,305),(75,215),width=.7)
 c.setFillGray(1);c.circle(75,260,17,fill=1,stroke=1);c.setFillGray(0)
 txt(75,256,'pV',11,align='center')
 for x0,y0,name,dx,dy in [(75,65,'A',-4,-19),(240,120,'C',5,-18),(420,120,'D',5,8),
   (420,65,'E',-4,-19),(240,370,'F',-4,8),(75,215,'B',7,5),
   (240,305,'M',-22,0),(240,190,'N',7,5)]: dot(x0,y0,name,dx,dy)
 # Current arrows are deliberately beside components, not superposed on wires.
 arrow(323,146,367,146,'6 А' if actual else 'I1',dy=7)
 if actual: arrow(330,270,330,310,'3 А',dx=19)
 else: arrow(330,310,330,270,'I2',dx=13)
 arrow(147,145,192,145,'9 А' if actual else 'I3',dy=7)
 if actual: arrow(265,35,215,35,'7,5 А',dy=-16)
 else: arrow(215,35,265,35,'I4',dy=-16)
 if actual: arrow(460,310,460,270,'1,5 А',dx=-24)
 else: arrow(460,270,460,310,'I5',dx=-15)
 arrow(8,310,8,270,'1,5 А' if actual else 'I6',dx=22)

def simplified(cv):
 line((45,42),(45,220));line((455,42),(455,220))
 for n,yy in enumerate([220,131,42],1):
  line((45,yy),(455,yy)); resistor(170,yy,f'r{n}′ = {[3,4,2][n-1]} Ом')
  c.setFillGray(1);c.circle(310,yy,17,fill=1,stroke=1);c.setFillGray(0)
  arrow(297,yy,323,yy);txt(310,yy+25,f'E{n} = {[18,24,54][n-1]} В',10,align='center')
  if n==1: arrow(430,yy+24,380,yy+24,'I1',dy=7)
  else: arrow(380,yy+24,430,yy+24,f'I{n}',dy=7)
  dot(45,yy);dot(455,yy)
 txt(25,130,'O',12,True);txt(468,130,'C',12,True)

def build():
 new('Расчёт линейной электрической цепи постоянного тока')
 para('Домашнее задание №1<br/>Вариант 3, группа 3','title')
 para('Расчёт по 12 пунктам задания. Чёрно-белый формат A4. Подготовлено 24.10.2026.','small')
 sub('Исходные данные и правило группы')
 para('Источник: DZ1_GI_GF.pdf. Условие и примечания - PDF-стр. 1; таблица 1, строка 3 - стр. 2; нижняя схема №3 - стр. 3.')
 para('В примечании 2 сказано об увеличении значений активных элементов по номеру группы, но формула не приведена. <b>Для этого расчёта принято E<sub>i,3</sub> = 3E<sub>i,1</sub>.</b> Сопротивления сохраняются. Это явно указанное допущение, требующее сверки с разъяснением преподавателя.')
 table([['Величина','Группа 1 (таблица)','Группа 3 (принято)'],
  ['E1 / U1','6 В','3·6 = 18 В'],['E2','8 В','3·8 = 24 В'],['E3','18 В','3·18 = 54 В'],
  ['R01; R02; R03','прочерк; 0,6; 0,3 Ом','0; 0,6; 0,3 Ом'],
  ['R1; R2; R3','2,8; 2; 1 Ом','2,8; 2; 1 Ом'],['R4; R5; R6','1; 2; 7 Ом','1; 2; 7 Ом']],[1.2,1.65,1.65])
 para('На схеме U1 обозначен зажимами D(+) и E(−). В таблице это E1; прочерк R01 и отсутствие последовательного внутреннего сопротивления означают идеальный источник: U1 = E1, R01 = 0. Стрелка U1 указывает отсчёт напряжения от плюса к минусу; она не является стрелкой ЭДС.','small')
 sub('Принятые условия и границы результата')
 para('Приборы идеальные: сопротивление вольтметра и обмотки напряжения ваттметра бесконечно, токовой обмотки - нулевое. Поэтому они не изменяют токи основной цепи.','small')
 para('Правило выбора ветви пункта 11 по номеру в журнале не расшифровано. Поэтому эквивалентный генератор рассчитан для <b>всех трёх активных ветвей</b>. Название дисциплины не дано; оно не подставлено по догадке.','small')

 new('1. Исходная схема и положительные направления токов')
 figure(lambda cv:circuit(cv,False),379,base_height=395)
 para('Рис. 1. Схема №3 перерисована по PDF-стр. 3. Точка N введена для вывода ваттметра; оба отмеченных начала его обмоток соединены с N. Тонкие линии обозначают цепи измерения.','small')
 table([['Ток','Положительный обход ветви','Элементы'],
  ['I1','C → D → E','R1, U1 = E1'],['I2','F → M → N → C','R2, R02, E2, токовая обмотка pW'],
  ['I3','A → B → C','R03, E3, R3'],['I4','A → E','R4'],['I5','E → F','R5'],['I6','F → A','R6']],[.6,1.6,2.4])
 para('Для расчёта силовой цепи существенны четыре узла A, C, E, F и шесть ветвей. B, D, M, N - точки внутри последовательных ветвей. Вольтметр включён между B и M, обмотка напряжения pW - между N и M; они не создают проводящего обхода источника E2.','small')

 new('2. Система уравнений по законам Кирхгофа')
 para('Введём суммарные сопротивления активных ветвей исходной схемы:')
 eq('r<sub>1</sub> = R1 = 2,8 Ом;<br/>r<sub>2</sub> = R2 + R02 = 2 + 0,6 = 2,6 Ом;<br/>r<sub>3</sub> = R3 + R03 = 1 + 0,3 = 1,3 Ом.')
 para('Число независимых уравнений: по первому закону 4 − 1 = 3; по второму 6 − 4 + 1 = 3. Для узлов C, A, F:')
 eq('I1 − I2 − I3 = 0;<br/>I3 + I4 − I6 = 0;<br/>I2 + I6 − I5 = 0.')
 para('Для контуров C→E→A→C, C→F→E→C и C→A→F→C соответственно:')
 eq('r<sub>1</sub>I1 − R4·I4 + r<sub>3</sub>I3 = E3 − E1;<br/>−r<sub>1</sub>I1 − r<sub>2</sub>I2 − R5·I5 = E1 − E2;<br/>r<sub>2</sub>I2 − r<sub>3</sub>I3 − R6·I6 = E2 − E3.')
 para('После подстановки сопротивлений (Ом) и ЭДС (В):')
 eq('2,8I1 + 1,3I3 − I4 = 54 − 18 = 36;<br/>−2,8I1 − 2,6I2 − 2I5 = 18 − 24 = −6;<br/>2,6I2 − 1,3I3 − 7I6 = 24 − 54 = −30.')
 para('Вторая группа уравнений имеет размерность напряжения: произведение сопротивления в омах на ток в амперах даёт вольты. Отрицательная ЭДС возникает при обходе от её положительного зажима к отрицательному.','small')
 table([['Контур','Источники при выбранном обходе','Сумма ЭДС'],
 ['C→E→A→C','E1 пересекается от D(+) к E(−); E3 - по стрелке','−18 + 54 = 36 В'],
 ['C→F→E→C','E2 пересекается против стрелки; E1 - от E(−) к D(+)','−24 + 18 = −6 В'],
 ['C→A→F→C','E3 пересекается против стрелки; E2 - по стрелке','−54 + 24 = −30 В']],[1.1,2.5,1.25])
 new('3. Метод контурных токов')
 para('Контурные токи Jа, Jб, Jв направим по трём обходам выше. Тогда:','small')
 eq('I1 = Jа − Jб; I2 = Jв − Jб; I3 = Jа − Jв;<br/>I4 = −Jа; I5 = −Jб; I6 = −Jв.')
 eq('(r1 + R4 + r3)Jа − r1·Jб − r3·Jв = E3 − E1;<br/>−r1·Jа + (r1 + R5 + r2)Jб − r2·Jв = E1 − E2;<br/>−r3·Jа − r2·Jб + (r3 + R6 + r2)Jв = E2 − E3.')
 eq('5,1Jа − 2,8Jб − 1,3Jв = 36;<br/>−2,8Jа + 7,4Jб − 2,6Jв = −6;<br/>−1,3Jа − 2,6Jб + 10,9Jв = −30.')
 para('Сложим три уравнения: внутренние общие ветви сокращаются. Получим уравнение внешнего контура и выразим Jа:')
 eq('R4·Jа + R5·Jб + R6·Jв = 0;<br/>Jа + 2Jб + 7Jв = 0; Jа = −2Jб − 7Jв.')
 para('Подставим его в первые два уравнения системы:')
 eq('13Jб + 37Jв = −36;<br/>13Jб + 17Jв = −6;<br/>(37 − 17)Jв = −36 − (−6); Jв = −30/20 = −1,5 А.')
 eq('Jб = (−6 − 17Jв)/13 = [−6 − 17·(−1,5)]/13 = 1,5 А;<br/>Jа = −2Jб − 7Jв = −2·1,5 − 7·(−1,5) = 7,5 А.')
 eq('Jа = 7,5 А; Jб = 1,5 А; Jв = −1,5 А.')
 eq('I1 = 7,5 − 1,5 = 6 А; I2 = −1,5 − 1,5 = −3 А;<br/>I3 = 7,5 − (−1,5) = 9 А;<br/>I4 = −7,5 А; I5 = −1,5 А; I6 = −(−1,5) = 1,5 А.')

 # Remaining pages are defined below.
 build_remaining()
 page_bottoms.append((page,y))
 assert page==12,page
 c.save()
 # Original text transcript is unchanged; preserve it.
 # Exact numerical results are unchanged; preserve the existing JSON.
 print('Saved',OUT)
 print('Page bottoms in points:',page_bottoms)

def build_remaining():
 new('4. Треугольник - звезда. Метод двух узлов')
 para('Треугольник R4, R5, R6 имеет вершины A, E, F. Вводим центр звезды O и сопротивления R<sub>A</sub>, R<sub>E</sub>, R<sub>F</sub>, соединяющие эти вершины с O. Сумма сторон треугольника:')
 eq('S = R4 + R5 + R6 = 1 + 2 + 7 = 10 Ом.')
 eq('R<sub>A</sub> = R4·R6/S = 1·7/10 = 0,7 Ом;<br/>R<sub>E</sub> = R4·R5/S = 1·2/10 = 0,2 Ом;<br/>R<sub>F</sub> = R5·R6/S = 2·7/10 = 1,4 Ом.')
 eq('r1′ = R1 + R<sub>E</sub> = 2,8 + 0,2 = 3 Ом;<br/>r2′ = R2 + R02 + R<sub>F</sub> = 2 + 0,6 + 1,4 = 4 Ом;<br/>r3′ = R3 + R03 + R<sub>A</sub> = 1 + 0,3 + 0,7 = 2 Ом.')
 figure(simplified,220,base_height=265)
 para('Рис. 2. Упрощённая схема. Все ЭДС направлены от O к C. I1 направлен от C к O; I2 и I3 - от O к C. r′ включает все последовательные сопротивления соответствующей ветви.','small')
 eq('U = φ<sub>C</sub> − φ<sub>O</sub>; I1 = (U − E1)/r1′;<br/>I2 = (E2 − U)/r2′; I3 = (E3 − U)/r3′.')
 eq('I1 = I2 + I3.<br/>Отсюда U = (E1/r1′ + E2/r2′ + E3/r3′)/(1/r1′ + 1/r2′ + 1/r3′).')
 eq('U = (18/3 + 24/4 + 54/2)/(1/3 + 1/4 + 1/2)<br/>= 39/(13/12) = 36 В.')
 eq('I1 = (36 − 18)/3 = 6 А; I2 = (24 − 36)/4 = −3 А;<br/>I3 = (54 − 36)/2 = 9 А.')

 new('5. Возврат к токам исходного треугольника')
 para('Выберем φ<sub>E</sub> = 0. В звезде ток I1 идёт E→O, токи I2 и I3 приняты от O к F и A. Определим потенциалы:')
 eq('φ<sub>O</sub> = φ<sub>E</sub> − I1·R<sub>E</sub> = 0 − 6·0,2 = −1,2 В;<br/>φ<sub>C</sub> = φ<sub>O</sub> + U = −1,2 + 36 = 34,8 В;<br/>φ<sub>A</sub> = φ<sub>O</sub> − I3·R<sub>A</sub> = −1,2 − 9·0,7 = −7,5 В;<br/>φ<sub>F</sub> = φ<sub>O</sub> − I2·R<sub>F</sub> = −1,2 − (−3)·1,4 = 3 В.')
 para('По закону Ома для исходных сторон треугольника:')
 eq('I4 = (φ<sub>A</sub> − φ<sub>E</sub>)/R4 = (−7,5 − 0)/1 = −7,5 А;<br/>I5 = (φ<sub>E</sub> − φ<sub>F</sub>)/R5 = (0 − 3)/2 = −1,5 А;<br/>I6 = (φ<sub>F</sub> − φ<sub>A</sub>)/R6 = [3 − (−7,5)]/7 = 1,5 А.')
 sub('6. Проверка обоих законов Кирхгофа')
 table([['Узел','Подстановка токов, А','Остаток'],
 ['C: I1 − I2 − I3','6 − (−3) − 9','0 А'],
 ['A: I3 + I4 − I6','9 + (−7,5) − 1,5','0 А'],
 ['F: I2 + I6 − I5','−3 + 1,5 − (−1,5)','0 А'],
 ['E: I5 − I1 − I4','−1,5 − 6 − (−7,5)','0 А']],[1.3,2,1])
 eq('C→E→A→C:<br/>2,8·6 + 1,3·9 − 1·(−7,5) = 16,8 + 11,7 + 7,5 = 36 В;<br/>E3 − E1 = 54 − 18 = 36 В.')
 eq('C→F→E→C:<br/>−2,8·6 − 2,6·(−3) − 2·(−1,5) = −16,8 + 7,8 + 3 = −6 В;<br/>E1 − E2 = 18 − 24 = −6 В.')
 eq('C→A→F→C:<br/>2,6·(−3) − 1,3·9 − 7·1,5 = −7,8 − 11,7 − 10,5 = −30 В;<br/>E2 − E3 = 24 − 54 = −30 В.')
 para('Во всех уравнениях невязка равна нулю. Отрицательные I2, I4, I5 означают обратное направление соответствующих токов.','small')

 new('7. Метод наложения для упрощённой схемы')
 para('Оставляем по одному источнику. Не действующие идеальные источники ЭДС заменяем коротким замыканием; все сопротивления, включая R02 и R03, сохраняем. Используем r1′ = 3 Ом, r2′ = 4 Ом, r3′ = 2 Ом.')
 eq('G = 1/r1′ + 1/r2′ + 1/r3′ = 1/3 + 1/4 + 1/2 = 13/12 См.')
 para('Для каждого частичного режима U<sup>(j)</sup> = (E<sub>j</sub>/r<sub>j</sub>′)/G. Токи считаем по тем же положительным направлениям, что на рис. 2.')
 sub('Действует только E1')
 eq('U<sup>(1)</sup> = (18/3)/(13/12) = 72/13 В;<br/>I1<sup>(1)</sup> = (U<sup>(1)</sup> − E1)/r1′ = (72/13 − 18)/3 = −54/13 А;<br/>I2<sup>(1)</sup> = −U<sup>(1)</sup>/r2′ = −(72/13)/4 = −18/13 А;<br/>I3<sup>(1)</sup> = −U<sup>(1)</sup>/r3′ = −(72/13)/2 = −36/13 А.')
 sub('Действует только E2')
 eq('U<sup>(2)</sup> = (24/4)/(13/12) = 72/13 В;<br/>I1<sup>(2)</sup> = U<sup>(2)</sup>/r1′ = (72/13)/3 = 24/13 А;<br/>I2<sup>(2)</sup> = (E2 − U<sup>(2)</sup>)/r2′ = (24 − 72/13)/4 = 60/13 А;<br/>I3<sup>(2)</sup> = −U<sup>(2)</sup>/r3′ = −(72/13)/2 = −36/13 А.')
 sub('Действует только E3')
 eq('U<sup>(3)</sup> = (54/2)/(13/12) = 324/13 В;<br/>I1<sup>(3)</sup> = U<sup>(3)</sup>/r1′ = (324/13)/3 = 108/13 А;<br/>I2<sup>(3)</sup> = −U<sup>(3)</sup>/r2′ = −(324/13)/4 = −81/13 А;<br/>I3<sup>(3)</sup> = (E3 − U<sup>(3)</sup>)/r3′ = (54 − 324/13)/2 = 189/13 А.')
 table([['Источник','I1, А','I2, А','I3, А'],['E1','−4,153846','−1,384615','−2,769231'],
 ['E2','1,846154','4,615385','−2,769231'],['E3','8,307692','−6,230769','14,538462'],
 ['Сумма','6','−3','9']],[1,1,1,1])
 eq('I1 = (−54 + 24 + 108)/13 = 6 А;<br/>I2 = (−18 + 60 − 81)/13 = −3 А;<br/>I3 = (−36 − 36 + 189)/13 = 9 А.')

 new('8. Действительные направления и режимы источников')
 figure(lambda cv:circuit(cv,True),379,base_height=395)
 para('Рис. 3. Действительные направления токов. Для I2, I4, I5 стрелки развёрнуты относительно положительных направлений рис. 1. Стрелки ЭДС и знаки U1 сохранены.','small')
 table([['Источник','Фактический ток и полярность','Режим'],
 ['U1 = E1','6 А от D(+) к E(−), ток входит в плюс','Потребитель'],
 ['E2 с R02','3 А от C к M, против стрелки ЭДС','Потребитель'],
 ['E3 с R03','9 А от A к B, по стрелке ЭДС','Генератор']],[1,2.4,1.1])
 para('ЭДС E3 передаёт энергию цепи. Элементы E1 и E2 принимают энергию; внутренние сопротивления источников рассеивают тепло. Сопротивления R1–R6 относятся к внешней цепи.','small')
 eq('P<sub>ЭДС,отд</sub> = −E1·I1 + E2·I2 + E3·I3;<br/>= −18·6 + 24·(−3) + 54·9 = −108 − 72 + 486 = 306 Вт.')

 new('8. Баланс мощностей. 9. КПД активных элементов')
 para('Для каждого сопротивления P<sub>R</sub> = I²R. Используем ток той ветви, в которой оно находится:')
 table([['Элемент','Подстановка I²R','Мощность, Вт'],
 ['R1','6²·2,8','100,8'],['R2','(−3)²·2','18'],['R3','9²·1','81'],
 ['R4','(−7,5)²·1','56,25'],['R5','(−1,5)²·2','4,5'],['R6','1,5²·7','15,75'],
 ['R02','(−3)²·0,6','5,4'],['R03','9²·0,3','24,3']],[1,1.8,1.1])
 eq('ΣP<sub>R1…R6</sub> = 100,8 + 18 + 81 + 56,25 + 4,5 + 15,75 = 276,3 Вт;<br/>ΣP<sub>внутр</sub> = 5,4 + 24,3 = 29,7 Вт;<br/>ΣP<sub>R</sub> = 276,3 + 29,7 = 306 Вт.')
 para('Баланс с учётом генераторного и потребительского режимов:')
 eq('E3·I3 = E1·I1 + E2·|I2| + ΣP<sub>R</sub>;<br/>54·9 = 18·6 + 24·3 + 306;<br/><b>486 = 108 + 72 + 306 = 486 Вт.</b>')
 para('Проверка по зажимам реальных источников:')
 eq('P3<sub>отд</sub> = E3·I3 − I3²R03 = 54·9 − 9²·0,3 = 461,7 Вт;<br/>P2<sub>вх</sub> = E2·|I2| + I2²R02 = 24·3 + 3²·0,6 = 77,4 Вт;<br/>461,7 = 108 + 77,4 + 276,3 Вт.')
 sub('9. КПД: полезная мощность / затраченная мощность')
 para('Для генератора полезна мощность, отдаваемая через зажимы. Для потребителя полезна мощность преобразования E|I|, а потери - I²R0. Такой расчёт не включает внешние сопротивления R1–R6.','small')
 eq('η3 = (E3 − I3R03)/E3 = (54 − 9·0,3)/54 = 0,95 = <b>95 %</b>;<br/>η2 = E2/(E2 + |I2|R02) = 24/(24 + 3·0,6)<br/>= 40/43 ≈ 0,93023 = <b>93,02 %</b>;<br/>η1 = E1/(E1 + I1R01) = 18/(18 + 6·0) = 1 = <b>100 %</b>.')
 para('КПД идеального элемента E1 равен 100 % в принятой модели, поскольку его внутренние потери равны нулю.','small')

 new('10. Показания вольтметра и ваттметра')
 para('При φ<sub>E</sub> = 0 известны φ<sub>C</sub> = 34,8 В, φ<sub>F</sub> = 3 В. Определим потенциалы точек присоединения приборов:')
 eq('φ<sub>M</sub> = φ<sub>F</sub> − I2·R2 = 3 − (−3)·2 = 9 В;<br/>φ<sub>B</sub> = φ<sub>C</sub> + I3·R3 = 34,8 + 9·1 = 43,8 В;<br/>φ<sub>N</sub> = φ<sub>C</sub> = 34,8 В, так как R<sub>токовой обмотки</sub> = 0.')
 sub('Вольтметр между M и B')
 eq('U<sub>MB</sub> = φ<sub>M</sub> − φ<sub>B</sub> = 9 − 43,8 = −34,8 В;<br/>pV = |U<sub>MB</sub>| = |−34,8| = <b>34,8 В</b>.')
 para('Полярность вольтметра в исходнике не отмечена, поэтому его показание дано по модулю. Положительный потенциал имеет вывод B.','small')
 sub('Ваттметр: обязательно учитывать оба начала обмоток')
 figure(watt_detail,190,base_height=200)
 para('Рис. 4. Начало токовой обмотки - сверху, у N. Начало обмотки напряжения - слева, также у N. Её второй вывод присоединён к M. Внутри круга две обмотки электрически не соединены.','small')
 eq('U<sub>*</sub> = φ<sub>N</sub> − φ<sub>M</sub> = 34,8 − 9 = 25,8 В;<br/>I<sub>*</sub> = I2 = −3 А;<br/>pW = U<sub>*</sub>I<sub>*</sub> = 25,8·(−3) = <b>−77,4 Вт</b>.')
 para('Фактический ток входит в нижний, неотмеченный вывод токовой обмотки. Поэтому отклонение при данном включении отрицательное. Модуль 77,4 Вт равен мощности, принимаемой элементом E2 вместе с R02; сопротивление R2 в измеряемый двухполюсник не входит.','small')

 new('11. Метод эквивалентного генератора: все три ветви')
 para('В упрощённой схеме удаляем всю рассматриваемую ветвь вместе с её ЭДС и r′. Остальные две ветви заменяем источником U<sub>хх</sub> с сопротивлением R<sub>экв</sub>. Напряжение U<sub>хх</sub> отсчитывается от C к O.')
 eq('U<sub>хх</sub> = (E<sub>a</sub>/r<sub>a</sub>′ + E<sub>b</sub>/r<sub>b</sub>′)/(1/r<sub>a</sub>′ + 1/r<sub>b</sub>′);<br/>R<sub>экв</sub> = r<sub>a</sub>′r<sub>b</sub>′/(r<sub>a</sub>′ + r<sub>b</sub>′).')
 para('Для определения R<sub>экв</sub> оба оставшихся идеальных источника ЭДС закорачиваются. При возврате удалённой активной ветви её собственная ЭДС обязательно входит в уравнение тока.','small')
 sub('Ветвь 1: E1, r1′; направление I1 от C к O')
 eq('U<sub>хх,1</sub> = (E2/r2′ + E3/r3′)/(1/r2′ + 1/r3′)<br/>= (24/4 + 54/2)/(1/4 + 1/2) = 44 В;<br/>R<sub>экв,1</sub> = r2′r3′/(r2′ + r3′) = 4·2/(4 + 2) = 4/3 Ом;<br/>I1 = (U<sub>хх,1</sub> − E1)/(R<sub>экв,1</sub> + r1′)<br/>= (44 − 18)/(4/3 + 3) = <b>6 А</b>.')
 sub('Ветвь 2: E2, r2′; направление I2 от O к C')
 eq('U<sub>хх,2</sub> = (E1/r1′ + E3/r3′)/(1/r1′ + 1/r3′)<br/>= (18/3 + 54/2)/(1/3 + 1/2) = 39,6 В;<br/>R<sub>экв,2</sub> = r1′r3′/(r1′ + r3′) = 3·2/(3 + 2) = 1,2 Ом;<br/>I2 = (E2 − U<sub>хх,2</sub>)/(R<sub>экв,2</sub> + r2′)<br/>= (24 − 39,6)/(1,2 + 4) = <b>−3 А</b>.')
 sub('Ветвь 3: E3, r3′; направление I3 от O к C')
 eq('U<sub>хх,3</sub> = (E1/r1′ + E2/r2′)/(1/r1′ + 1/r2′)<br/>= (18/3 + 24/4)/(1/3 + 1/4) = 144/7 В;<br/>R<sub>экв,3</sub> = r1′r2′/(r1′ + r2′) = 3·4/(3 + 4) = 12/7 Ом;<br/>I3 = (E3 − U<sub>хх,3</sub>)/(R<sub>экв,3</sub> + r3′)<br/>= (54 − 144/7)/(12/7 + 2) = <b>9 А</b>.')
 para('Все три результата совпали с расчётом другими методами. Личная ветвь не назначается по догадке: правило соответствия номеру в журнале в исходнике не дано.','small')

 new('12. Масштабная потенциальная диаграмма')
 para('Внешний контур исходной схемы: A→F→E→A, то есть R6→R5→R4. В нём нет источников ЭДС, поэтому скачков потенциала нет. Для диаграммы выберем новый нуль φ<sub>A</sub> = 0; разности потенциалов и токи от этого не меняются.')
 eq('φ<sub>F</sub> = φ<sub>A</sub> + I6·R6 = 0 + 1,5·7 = 10,5 В;<br/>φ<sub>E</sub> = φ<sub>F</sub> + I5·R5 = 10,5 + (−1,5)·2 = 7,5 В;<br/>φ<sub>A,возврат</sub> = φ<sub>E</sub> + I4·R4 = 7,5 + (−7,5)·1 = 0 В.')
 para('Абсцисса - накопленная сумма сопротивлений по обходу. При печати в масштабе 100 %: <b>1 Ом = 12 мм; 1 В = 6 мм</b>. Наклоны показывают изменение потенциала на 1 Ом: +1,5; −1,5; −7,5 В/Ом.','small')
 potential_figure()
 table([['Точка','Пройденный элемент','ΣR, Ом','φ относительно A, В'],
 ['A (начало)','-','0','0'],['F','R6 = 7 Ом','7','10,5'],['E','R5 = 2 Ом','9','7,5'],['A (возврат)','R4 = 1 Ом','10','0']],[1,1.8,1,1.9])
 eq('ΣΔφ = I6·R6 + I5·R5 + I4·R4<br/>= 1,5·7 + (−1,5)·2 + (−7,5)·1 = 10,5 − 3 − 7,5 = 0 В.')
 sub('Проверка полного результата')
 para('Топология и подключения приборов независимо сверены с исходной схемой. Токи подтверждены законами Кирхгофа, контурным методом, методом двух узлов после преобразования, наложением и эквивалентными генераторами. Рациональная арифметика даёт нулевые невязки; баланс мощностей замыкается.','small')
 para('Итоги: I1 = 6 А; I2 = −3 А; I3 = 9 А; I4 = −7,5 А; I5 = −1,5 А; I6 = 1,5 А. pV = 34,8 В; pW = −77,4 Вт. ЭДС E3 работает генератором, E1 и E2 - потребителями.','small')

def watt_detail(cv):
 # A separate instrument diagram, all four terminals visibly independent.
 line((235,175),(235,25),width=1.4)
 c.setFillGray(1);c.circle(235,87,28,stroke=1,fill=1);c.setFillGray(0)
 line((235,115),(235,59),width=3)
 line((235,135),(172,135),(172,87),(207,87),width=.8)
 line((263,87),(345,87),(345,175),(235,175),width=.8)
 # Voltage winding is two separated coil leads; no conductive junction at cross.
 line((207,87),(228,87),width=.8);line((242,87),(263,87),width=.8)
 c.setLineWidth(.8);c.arc(228,80,242,94,startAng=0,extent=180)
 for xx,yy,name in [(235,175,'M'),(235,135,'N'),(235,25,'C')]:dot(xx,yy,name,8,-5 if name=='N' else 3)
 txt(220,117,'*',17);txt(191,72,'*',17);txt(278,120,'pW',12,True)
 txt(38,154,'Обмотка напряжения:',11);txt(38,137,'N(*) → M',11)
 arrow(387,150,387,110,'U* = 25,8 В',dx=42)
 arrow(113,36,113,91,'3 А',dx=-20)
 txt(70,16,'Фактический ток C → N',10)
 txt(278,48,'I* = I2 = −3 А',11)
 # E2/R02 belong between M and N, not a wire shorting those nodes.
 c.setFillGray(1);c.rect(213,143,44,26,stroke=1,fill=1);c.setFillGray(0)
 txt(235,159,'E2',8,align='center');txt(235,148,'R02',8,align='center')

def potential_figure():
 global y
 from reportlab.graphics.shapes import Drawing,String
 from reportlab.graphics.charts.lineplots import LinePlot
 from reportlab.graphics.widgets.markers import makeMarker
 from reportlab.graphics import renderPDF
 # Physical axes area: 120 mm horizontally for 10 ohms, 72 mm for 12 volts.
 fw,fh=170,101
 drawing=Drawing(fw*mm,fh*mm)
 chart=LinePlot();chart.x=26*mm;chart.y=19*mm
 chart.width=120*mm;chart.height=72*mm
 chart.data=[[(0,0),(7,10.5),(9,7.5),(10,0)]]
 chart.joinedLines=1;chart.lines[0].strokeColor=colors.black
 chart.lines[0].strokeWidth=1.5;chart.lines[0].symbol=makeMarker('FilledCircle',size=4)
 for axis in [chart.xValueAxis,chart.yValueAxis]:
  axis.valueMin=0;axis.labels.fontName='Body';axis.labels.fontSize=9
  axis.visibleGrid=True;axis.gridStrokeColor=colors.Color(.72,.72,.72)
  axis.gridStrokeWidth=.4;axis.gridStrokeDashArray=[1,2]
 chart.xValueAxis.valueMax=10;chart.xValueAxis.valueSteps=list(range(11))
 chart.yValueAxis.valueMax=12;chart.yValueAxis.valueSteps=list(range(0,13,2))
 drawing.add(chart)
 drawing.add(String(86*mm,2*mm,'Накопленное сопротивление ΣR, Ом',fontName='Body',fontSize=10,textAnchor='middle'))
 drawing.add(String(26*mm,96*mm,'Потенциал φ, В',fontName='Body',fontSize=10))
 for xx,vv,lab,dx,dy in [(0,0,'A',5,7),(7,10.5,'F (10,5 В)',-20,9),(9,7.5,'E (7,5 В)',-58,-16),(10,0,'A',-12,7)]:
  drawing.add(String(26*mm+xx*12*mm+dx,19*mm+vv*6*mm+dy,lab,fontName='Body',fontSize=10))
 for xx,lab in [(3.5,'R6'),(8,'R5'),(9.5,'R4')]:
  drawing.add(String(26*mm+xx*12*mm,19*mm+11.7*6*mm,lab,fontName='Body',fontSize=9,textAnchor='middle'))
 ht=fh*mm
 if y-ht<BOTTOM: raise RuntimeError('potential figure overflow')
 renderPDF.draw(drawing,c,L+(WIDTH-fw*mm)/2,y-ht);y-=ht+10
 transcript.append('Рис. 5. Масштаб 12 мм/Ом и 6 мм/В. Точки (ΣR;φ): (0;0), (7;10,5), (9;7,5), (10;0).\n')

if __name__=='__main__': build()

