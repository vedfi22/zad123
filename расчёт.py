"""Exact independent circuit checks, variant 3; sources scaled by k=3.
Run with Python 3. No third party dependencies are needed for this file.
Node basis: phi_E=0. Currents: I1 C->E, I2 F->C, I3 A->C,
I4 A->E, I5 E->F, I6 F->A. All magnitudes in SI.
"""
from fractions import Fraction as Q
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent

def solve(a, b):
    m = [[Q(x) for x in row] + [Q(rhs)] for row, rhs in zip(a, b)]
    n = len(m)
    for j in range(n):
        pivot = next(i for i in range(j, n) if m[i][j])
        m[j], m[pivot] = m[pivot], m[j]
        d = m[j][j]
        m[j] = [x / d for x in m[j]]
        for i in range(n):
            if i != j:
                d = m[i][j]
                m[i] = [x - d*y for x, y in zip(m[i], m[j])]
    return [row[-1] for row in m]

def calculate():
    r1,r2,r3,r4,r5,r6 = map(Q, ['2.8','2','1','1','2','7'])
    r02,r03 = Q('.6'),Q('.3')
    e1,e2,e3 = map(Q, [18,24,54])
    # Six branch equations: three KCL and three independent KVL equations.
    mat = [[1,-1,-1,0,0,0], [0,0,1,1,0,-1], [0,1,0,0,-1,1],
           [r1,0,r3+r03,-r4,0,0],
           [-r1,-r2-r02,0,0,-r5,0],
           [0,r2+r02,-r3-r03,0,0,-r6]]
    rhs = [0,0,0,e3-e1,e1-e2,e2-e3]
    currents = solve(mat, rhs)
    assert currents == list(map(Q,['6','-3','9','-7.5','-1.5','1.5']))
    i1,i2,i3,i4,i5,i6 = currents
    # Three meshes, independently built from shared resistors.
    mesh_mat = [[r1+r4+r3+r03, -r1, -r3-r03],
                [-r1,r1+r5+r2+r02,-r2-r02],
                [-r3-r03,-r2-r02,r3+r03+r6+r2+r02]]
    ja,jb,jc = solve(mesh_mat,[e3-e1,e1-e2,e2-e3])
    assert [ja-jb,jc-jb,ja-jc,-ja,-jb,-jc] == currents
    # Delta-star, then two nodes.
    s = r4+r5+r6
    ra,re,rf = r4*r6/s,r4*r5/s,r5*r6/s
    rp = [r1+re,r2+r02+rf,r3+r03+ra]
    g = sum(1/r for r in rp)
    u = sum(e/r for e,r in zip([e1,e2,e3],rp))/g
    star_currents = [(u-e1)/rp[0],(e2-u)/rp[1],(e3-u)/rp[2]]
    assert star_currents == currents[:3]
    # Full potentials with E=0.
    ve = Q(0); vd=e1; vc=vd+r1*i1; vm=vc-e2+r02*i2
    vf=vm+r2*i2; vb=vc+r3*i3; va=vb-e3+r03*i3; vo=-re*i1
    nodes={'A':va,'B':vb,'C':vc,'D':vd,'E':ve,'F':vf,'M':vm,'N':vc,'O':vo}
    assert [(va-ve)/r4,(ve-vf)/r5,(vf-va)/r6]==currents[3:]
    # Superposition, ideal sources deactivated by shorts; all resistors retained.
    superposition=[]
    for j in range(3):
        es=[Q(0),Q(0),Q(0)]; es[j]=[e1,e2,e3][j]
        us=sum(e/r for e,r in zip(es,rp))/g
        row=[(us-es[0])/rp[0],(es[1]-us)/rp[1],(es[2]-us)/rp[2]]
        assert row[0]-row[1]-row[2] == 0
        superposition.append({'source':j+1,'U_CO':us,'currents':row})
    assert [sum(row['currents'][j] for row in superposition) for j in range(3)]==currents[:3]
    # Thevenin port uses the whole removed active branch, C positive relative O.
    th=[]
    es=[e1,e2,e3]
    for j in range(3):
        keep=[l for l in range(3) if l!=j]
        gg=sum(1/rp[l] for l in keep)
        rth=1/gg; uth=sum(es[l]/rp[l] for l in keep)/gg
        current=((uth-es[j]) if j==0 else (es[j]-uth))/(rp[j]+rth)
        assert current==currents[j]
        th.append({'branch':j+1,'U_open':uth,'R_th':rth,'current':current})
    # Signed power balance, explicit real-source terminal powers.
    resistors=[r1,r2,r3,r4,r5,r6,r02,r03]
    branch_is=[i1,i2,i3,i4,i5,i6,i2,i3]
    dissipations=[r*i*i for r,i in zip(resistors,branch_is)]
    generated=-e1*i1+e2*i2+e3*i3
    assert generated==sum(dissipations)==Q(306)
    assert e3*i3 == e1*i1-e2*i2+sum(dissipations)
    p3out=e3*i3-r03*i3*i3
    p2in=-e2*i2+r02*i2*i2
    assert p3out==e1*i1+p2in+sum(dissipations[:6])
    eta=[Q(1),e2/(e2+abs(i2)*r02),(e3-i3*r03)/e3]
    voltmeter=abs(vm-vb)
    wattmeter=(vc-vm)*i2  # Both starred terminals at N; current star is upper.
    assert wattmeter == -p2in == Q('-77.4')
    # Exterior contour A-F-E-A, abscissa = accumulated resistance.
    potential_path=[(Q(0),Q(0)),(r6,vf-va),(r6+r5,ve-va),(s,Q(0))]
    assert (vf-va)+(ve-vf)+(va-ve)==0
    residuals=[sum(Q(a)*x for a,x in zip(row,currents))-Q(b) for row,b in zip(mat,rhs)]
    assert all(x==0 for x in residuals)
    return {'scale':Q(3),'source_emf':[e1,e2,e3],'currents':currents,
      'mesh_currents':[ja,jb,jc],'star_resistances':[ra,re,rf],
      'simplified_resistances':rp,'U_CO':u,'nodes_E_zero':nodes,
      'superposition':superposition,'thevenin':th,'resistor_powers':dissipations,
      'total_resistor_power':sum(dissipations),'E3_terminal_output':p3out,
      'E2_terminal_input':p2in,'efficiencies':eta,'voltmeter_abs':voltmeter,
      'wattmeter_signed':wattmeter,'potential_path_A_zero':potential_path,
      'kirchhoff_residuals':residuals}

def serial(value):
    if isinstance(value,Q): return {'exact':str(value),'decimal':float(value)}
    if isinstance(value,dict): return {k:serial(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)): return [serial(x) for x in value]
    return value

if __name__=='__main__':
    result=calculate()
    (HERE/'Расчётные_данные.json').write_text(json.dumps(serial(result),ensure_ascii=False,indent=2),encoding='utf-8')
    print('Exact checks passed: Kirchhoff, mesh, delta-star, superposition, all 3 Thevenin branches, power balance.')
    print('I1-I6:',*[str(i) for i in result['currents']])
    print('PV:',result['voltmeter_abs'],'V; PW:',result['wattmeter_signed'],'W')
