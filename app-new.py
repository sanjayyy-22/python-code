import numpy as np
import matplotlib as plt
import skfuzzy as fuzz
from skfuzzy import control as ctrl

speed=100
acceleration=70

def trapezoidal(x,a,b,c,d):
    if x<=a:
        return 0
    elif x<=b:
        return ((x-a)/(b-a))
    elif x<=c:
        return 1
    elif x<=d:
        return ((d-x)/(d-c))
    else:
        return 0


def triangular(x,a,b,c):
    return max(min((x-a)/(b-a),(c-x)/(c-b)),0)

def partition(x):
    NL=0
    NM=0
    NS=0
    ZE=0
    PS=0
    PM=0
    PL=0

    if x>0 and x<61:
        NL=trapezoidal(x,0,0,31,61)
    if x>31 and x<95:
        NM=triangular(x, 31, 61, 95)
    if x>61 and x<127:
        NS=triangular(x, 61, 95, 127)
    if x>95 and x<159:
        ZE=triangular(x, 95, 127, 159)
    if x>127 and x<191:
        PS=triangular(x, 127, 159, 191)
    if x>159 and x<223:
        PM=triangular(x, 159,191, 223)
    if x>191 and x<255:
        PL=trapezoidal(x,191,223,255,255)

    return NL,NM,NS,ZE,PS,PM,PL



def compare(TC1,TC2):
    TC=0
    if TC1>TC2 and TC1!=0 and TC2!=0:
        TC=TC2
    else:
        TC=TC1

    if TC1==0 and TC2!=0:
        TC=TC2
    if TC2==0 and TC1!=0:
        TC=TC1

    return TC

def rule(NLSD,NMSD,NSSD,ZESD,PSSD,PMSD,PLSD,NLAC,NMAC,NSAC,ZEAC,PSAC,PMAC,PLAC):
    PLTC1=min(NLSD,ZEAC)
    PLTC2=min(ZESD,NLAC)
    PLTC=compare(PLTC1,PLTC2)

    PMTC1=min(NMSD,ZEAC)
    PMTC2=min(ZESD,NMAC)
    PMTC=compare(PMTC1,PMTC2)

    PSTC1=min(NSSD,PSAC)
    PSTC2=min(ZESD,NSAC)
    PSTC=compare(PSTC1, PSTC2)

    NSTC=min(PSSD,NSAC)
    NLTC=min(PLSD,ZEAC)

    return PLTC,PMTC,PSTC,NSTC,NLTC

def areaTR(mu,a,b,c):
    x1=mu*(b-a)+a
    x2=c-mu*(c-b)
    d1=(c-a)
    d2=x2-x1
    a=(0.5)*mu*(d1+d2)
    return a

def areaOL(mu,a,b):
    xOL=b-mu*(b-a)
    return 0.5*mu*(b+xOL),b/2

def areaOR(mu,a,b):
    xOR=(b-a)*mu+a
    aOR=0.5*mu*((240-a)+(240-xOR))
    return aOR,(240-a)/2+a

def defuzzyfication(PLTC,PMTC,PSTC,NSTC,NLTC):
    areaPL=0
    areaPM=0
    areaPS=0
    areaNS=0
    areaNL=0

    cPL=0
    cPM=0
    cPS=0
    cNS=0
    cNL=0

    if PLTC!=0:
        areaPL,cPL=areaOR(PLTC, 191, 255)
    if PMTC!=0:
        areaPM=areaTR(PMTC, 159, 191, 223)
        cPM=191
    if PSTC!=0:
        areaPS=areaTR(PSTC, 127, 159, 191)
        cPS=159
    if NSTC != 0:
        areaNS = areaTR(NSTC, 61, 95, 127)
        cNS = 95

    if NLTC !=0:
        areaNL, cNL = areaOL(NLTC, 0, 61)
    print(cPL,cNL)

    numerator = areaPL*cPL + areaPM*cPM + areaPS*cPS + areaNS*cNS + areaNL*cNL
    denominator = areaPL + areaPM + areaPS + areaNS + areaNL
    if denominator ==0:
        print("No rules exist to give the result")
        return 0
    else:
        crispOutput = numerator/denominator
        return crispOutput

NLSD,NMSD,NSSD,ZESD,PSSD,PMSD,PLSD=partition(speed)
NLAC,NMAC,NSAC,ZEAC,PSAC,PMAC,PLAC=partition(acceleration)

output=[[NLSD,NMSD,NSSD,ZESD,PSSD,PMSD,PLSD],[NLAC,NMAC,NSAC,ZEAC,PSAC,PMAC,PLAC]]

print("The fuzzy values of the crisp inputs:")
print(np.round(output,2))

PLTC, PMTC, PSTC, NSTC, NLTC = rule(NLSD,NMSD,NSSD,ZESD,PSSD,PMSD,PLSD,NLAC,NMAC,NSAC,ZEAC,PSAC,PMAC,PLAC)
crispOutputFinal = defuzzyfication(PLTC, PMTC, PSTC, NSTC, NLTC)
print(crispOutputFinal)

# ip1 = np.array([NLSD,NMSD,NSSD,ZESD,PSSD,PMSD,PLSD])
# ip2 = np.array([NLAC,NMAC,NSAC,ZEAC,PSAC,PMAC,PLAC])
ip1=np.arange(0,255,1)
spd = ctrl.Antecedent(ip1, 'spd')
acc = ctrl.Antecedent(ip1, 'acc')
throttle = ctrl.Consequent(ip1, 'throttle')

spd['NL']=fuzz.trapmf(spd.universe, [0,0,31,61])
spd['NM']=fuzz.trimf(spd.universe, [31,61,95])
spd['NS']=fuzz.trimf(spd.universe, [61,95,127])
spd['ZE']=fuzz.trimf(spd.universe, [95,127,159])
spd['PS']=fuzz.trimf(spd.universe, [127,159,191])
spd['PM']=fuzz.trimf(spd.universe, [159,191,223])
spd['PL']=fuzz.trapmf(spd.universe, [191,223,255,255])

acc['NL']=fuzz.trapmf(spd.universe, [0,0,31,61])
acc['NM']=fuzz.trimf(spd.universe, [31,61,95])
acc['NS']=fuzz.trimf(spd.universe, [61,95,127])
acc['ZE']=fuzz.trimf(spd.universe, [95,127,159])
acc['PS']=fuzz.trimf(spd.universe, [127,159,191])
acc['PM']=fuzz.trimf(spd.universe, [159,191,223])
acc['PL']=fuzz.trapmf(spd.universe, [191,223,255,255])

throttle['NL']=fuzz.trapmf(spd.universe, [0,0,31,61])
throttle['NM']=fuzz.trimf(spd.universe, [31,61,95])
throttle['NS']=fuzz.trimf(spd.universe, [61,95,127])
throttle['ZE']=fuzz.trimf(spd.universe, [95,127,159])
throttle['PS']=fuzz.trimf(spd.universe, [127,159,191])
throttle['PM']=fuzz.trimf(spd.universe, [159,191,223])
throttle['PL']=fuzz.trapmf(spd.universe, [191,223,255,255])


r1=ctrl.Rule(spd['NL'] & acc['ZE'] , throttle['PL'])
r2=ctrl.Rule(spd['NL'] & acc['ZE'] , throttle['PL'])
r3=ctrl.Rule(spd['NM'] & acc['ZE'] , throttle['PM'])
r4=ctrl.Rule(spd['NS'] & acc['PS'] , throttle['PS'])
r5=ctrl.Rule(spd['PS'] & acc['NS'] , throttle['NS'])
r6=ctrl.Rule(spd['PL'] & acc['ZE'] , throttle['NL'])
r7=ctrl.Rule(spd['ZE'] & acc['NS'] , throttle['PS'])
r8=ctrl.Rule(spd['ZE'] & acc['NM'] , throttle['PM'])

spd.view()
throttle_control = ctrl.ControlSystem([r1,r2,r3,r4,r5,r6,r7,r8])
sA = ctrl.ControlSystemSimulation(throttle_control)
sA.input['spd']=100
sA.input['acc']=70
sA.compute()
throttle.view(sim = sA)
print(sA.output)

# Defuzzification
crispOutputFinal = defuzzyfication(PLTC, PMTC, PSTC, NSTC, NLTC)
print("Crisp Output:", crispOutputFinal)
