"""Vector diagrams for the revised report; original node and current conventions."""
import math


def text(c, x, y, label, size=11, bold=False, align='center'):
    c.setFillGray(0)
    c.setFont('Bold' if bold else 'Body', size)
    if align == 'center':
        c.drawCentredString(x, y, label)
    elif align == 'right':
        c.drawRightString(x, y, label)
    else:
        c.drawString(x, y, label)


def arrow(c, a, b, width=1):
    c.setStrokeGray(0); c.setFillGray(0); c.setLineWidth(width)
    c.line(*a, *b)
    angle = math.atan2(b[1]-a[1], b[0]-a[0])
    p = c.beginPath(); p.moveTo(*b)
    for d in (-.42, .42):
        p.lineTo(b[0]-5*math.cos(angle+d), b[1]-5*math.sin(angle+d))
    p.close(); c.drawPath(p, stroke=1, fill=1)


def node(c, p, name, dx=0, dy=8):
    c.setFillGray(0); c.circle(*p, 2.8, fill=1, stroke=0)
    text(c, p[0]+dx, p[1]+dy, name, 12, True)


def point(a, b, t):
    return (a[0]+t*(b[0]-a[0]), a[1]+t*(b[1]-a[1]))


def normal(a, b):
    dx, dy = b[0]-a[0], b[1]-a[1]
    d = math.hypot(dx, dy)
    return (-dy/d, dx/d)


def resistance(c, a, b, at, label, offset=15, size=11, half=18):
    x, y = point(a, b, at); nx, ny = normal(a, b)
    angle = math.degrees(math.atan2(b[1]-a[1], b[0]-a[0]))
    c.saveState(); c.translate(x, y); c.rotate(angle)
    c.setFillGray(1); c.setStrokeGray(0); c.setLineWidth(1.25)
    c.rect(-half, -6, 2*half, 12, fill=1, stroke=1); c.restoreState()
    text(c, x+nx*offset, y+ny*offset-3, label, size)


def emf(c, a, b, at, label, forward=True, offset=20):
    x, y = point(a, b, at); nx, ny = normal(a, b)
    dx, dy = b[0]-a[0], b[1]-a[1]; d=math.hypot(dx,dy)
    ux, uy = dx/d, dy/d
    c.setFillGray(1); c.setStrokeGray(0); c.setLineWidth(1.25)
    c.circle(x, y, 12, fill=1, stroke=1)
    s=1 if forward else -1
    arrow(c, (x-s*9*ux,y-s*9*uy), (x+s*9*ux,y+s*9*uy))
    text(c, x+nx*offset, y+ny*offset-3, label, 11)


def current(c, a, b, t0, t1, label, offset=12, size=11):
    arrow(c, point(a,b,t0),point(a,b,t1))
    x,y=point(a,b,(t0+t1)/2); nx,ny=normal(a,b)
    text(c,x+nx*offset,y+ny*offset-3,label,size)


def wire(c, a, b):
    c.setStrokeGray(0); c.setLineWidth(1.3); c.line(*a,*b)


def loop(c, x, y, radius, label, clockwise=True):
    start=math.radians(120)
    angles=[start+(-1 if clockwise else 1)*math.radians(300)*i/70 for i in range(71)]
    pts=[(x+radius*math.cos(v),y+radius*math.sin(v)) for v in angles]
    p=c.beginPath(); p.moveTo(*pts[0])
    for pt in pts[1:]: p.lineTo(*pt)
    c.setLineWidth(.9); c.drawPath(p,stroke=1,fill=0)
    arrow(c,pts[-3],pts[-1],.9)
    text(c,x,y-4,label,12,True)


def mesh_diagram(c):
    C=(250,350); F=(70,45); E=(430,45); A=(250,150)
    for a,b in [(C,E),(F,C),(A,C),(A,E),(E,F),(F,A)]: wire(c,a,b)
    resistance(c,C,E,.28,'r1'); emf(c,C,E,.67,'E1',False,19)
    current(c,C,E,.43,.54,'I1',15)
    resistance(c,F,C,.68,'r2'); emf(c,F,C,.25,'E2',True,19)
    current(c,F,C,.44,.55,'I2',15)
    resistance(c,A,C,.35,'r3',-24); emf(c,A,C,.65,'E3',True,-25)
    current(c,A,C,.05,.18,'I3',-23)
    resistance(c,A,E,.53,'R4',-16); current(c,A,E,.14,.32,'I4',13)
    resistance(c,E,F,.50,'R5',15); current(c,E,F,.16,.30,'I5',-14)
    resistance(c,F,A,.53,'R6',-16); current(c,F,A,.14,.32,'I6',14)
    loop(c,307,205,18,'Jа')
    loop(c,193,205,18,'Jв')
    c.saveState(); c.setDash(5,3); c.setLineWidth(.85)
    p=c.beginPath(); p.moveTo(250,411);p.lineTo(15,10);p.lineTo(485,10);p.lineTo(250,411)
    c.drawPath(p,stroke=1,fill=0);c.restoreState()
    arrow(c,(347,10),(397,10),.9);text(c,372,23,'Jб',12,True)
    node(c,C,'C',0,9);node(c,A,'A',-16,-5)
    node(c,F,'F',-13,7);node(c,E,'E',13,7)


def local_delta(c, cx, currents=True):
    A=(cx,187); E=(cx+87,28); F=(cx-87,28)
    for a,b in [(A,E),(E,F),(F,A)]:wire(c,a,b)
    resistance(c,A,E,.56,'',18,10,16)
    resistance(c,E,F,.5,'R5 = 2',17,10,16)
    resistance(c,F,A,.44,'',18,10,16)
    x4,y4=point(A,E,.56);x6,y6=point(F,A,.44)
    text(c,x4+19,y4-3,'R4 = 1',10,align='left')
    text(c,x6-19,y6-3,'R6 = 7',10,align='right')
    if currents:
        current(c,A,E,.15,.32,'I4',-13,10)
        current(c,E,F,.13,.32,'I5',-13,10)
        current(c,F,A,.67,.84,'I6',-13,10)
    node(c,A,'A',0,9);node(c,E,'E',7,-16);node(c,F,'F',-7,-16)


def local_star(c,cx,currents=True):
    A=(cx,187); E=(cx+87,28); F=(cx-87,28);O=(cx,83)
    for a,b in [(O,A),(O,E),(O,F)]:wire(c,a,b)
    resistance(c,O,A,.48,'RA = 0,7',-39,10,16)
    resistance(c,O,E,.52,'RE = 0,2',27,10,16)
    resistance(c,O,F,.52,'RF = 1,4',-27,10,16)
    if currents:
        current(c,O,A,.72,.94,'I3',-16,10)
        current(c,E,O,.04,.25,'I1',-14,10)
        current(c,O,F,.72,.95,'I2',13,10)
    node(c,A,'A',0,9);node(c,E,'E',7,-16);node(c,F,'F',-7,-16);node(c,O,'O',-15,-5)


def delta_star_pair(c, reverse=False):
    if reverse:
        local_star(c,120);local_delta(c,380)
        left,right='Звезда','Исходный треугольник'
    else:
        local_delta(c,120);local_star(c,380)
        left,right='Исходный треугольник','Эквивалентная звезда'
    text(c,120,220,left,11,True);text(c,380,220,right,11,True)
    arrow(c,(238,113),(262,113),1.2)
    text(c,250,132,'Y → Δ' if reverse else 'Δ → Y',10)


def star_full(c):
    # Original external terminals remain visible before series reduction.
    rows=[(230,'E','RE = 0,2 Ом','R1 = 2,8 Ом','E1'),
          (135,'F','RF = 1,4 Ом','R2+R02 = 2,6 Ом','E2'),
          (40,'A','RA = 0,7 Ом','R3+R03 = 1,3 Ом','E3')]
    wire(c,(40,40),(40,230));wire(c,(460,40),(460,230))
    for i,(yy,name,arm,res,source) in enumerate(rows,1):
        a=(40,yy);b=(460,yy);wire(c,a,b)
        resistance(c,a,b,1/6,arm,16,10,18)
        resistance(c,a,b,.55,res,16,10,18)
        emf(c,a,b,.80,source,True,24)
        node(c,(180,yy),name,0,-18)
        if i==1:current(c,b,a,.04,.13,'I1',-16,11)
        else:current(c,a,b,.87,.96,f'I{i}',16,11)
        c.setFillGray(0);c.circle(*a,2.6,fill=1,stroke=0);c.circle(*b,2.6,fill=1,stroke=0)
    text(c,22,132,'O',12,True);text(c,478,132,'C',12,True)


def verify_delta_star():
    from fractions import Fraction as Q
    ra,re,rf=Q(7,10),Q(1,5),Q(7,5)
    k=ra*re+re*rf+rf*ra
    assert k==Q(7,5)
    assert [k/rf,k/ra,k/re]==[Q(1),Q(2),Q(7)]
    assert [ra+re,re+rf,rf+ra]==[Q(9,10),Q(8,5),Q(21,10)]
    # Directed incidence of the three preserved cycles, I1...I6.
    cycles=[[1,0,1,-1,0,0],[-1,-1,0,0,-1,0],[0,1,-1,0,0,-1]]
    ja,jb,jv=Q(15,2),Q(3,2),Q(-3,2)
    assert [sum(v*row[j] for v,row in zip([ja,jb,jv],cycles)) for j in range(6)]==[6,-3,9,Q(-15,2),Q(-3,2),Q(3,2)]
    return True
