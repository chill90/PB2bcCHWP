import numpy as np
import matplotlib.pyplot as plt
import sys
import time as tm
import datetime
import scipy.optimize as opt

#Fit function
def fitFunc(x, A, B, C, D, E):
    return A/(np.exp(B*x + C) + D) + E

#Fit function if ideal fit fails -- fifth-order polynomial
def fitFunc_arb(x, A, B, C, D, E):
    return A + B*x + C*x**2 + D*x**3 + E*x**4

#Function to fit the data
def fit(x, y):
    try:
        popt = opt.curve_fit(fitFunc, x, y)[0]
        yfit = fitFunc(x, *popt)
        yend = fitFunc(100, *popt) #Temperature after 100 hours
    except:
        popt = opt.curve_fit(fitFunc_arb, x, y)[0]
        print popt
        yfit = fitFunc_arb(x, *popt)
        yend = fitFunc_arb(100, *popt) #Temperature after 100 hours
    return yfit, yend

#Convert Kikusui logger file time to binary time
def tConv(time):
    arr = time.rstrip(']').lstrip('[').split()
    year, month, day = arr[0].split('-')
    hour, minute, sec = arr[1].split(':')
    dt = datetime.datetime(int(year), int(month), int(day), int(hour), int(minute), int(sec))
    btime = tm.mktime(dt.timetuple())
    return int(btime)

#Generate start and end times for voltage steps
def genTimes(karr):
    start = 'initial current' #Flag for start of voltage step
    finish = 'final current' #Flat for end of voltage step
    power = 'final power'
    stimes = []
    ftimes = []
    powers = []
    for i in range(len(karr[0])):
        if start in karr[1][i]:
            stimes.append(tConv(karr[0][i]))
        elif finish in karr[1][i]:
            ftimes.append(tConv(karr[0][i]))
        elif power in karr[1][i]:
            powers.append(float(karr[1][i].split()[-2]))
        else:
            continue
    return stimes, ftimes, powers

#Collect data files
args = sys.argv[1:]
if not len(args) == 3:
    sys.exit('\nUsage: python loadCurveAnalyze.py [hot thermometer file] [cold thermometer file] [kikusui log file]\n')
else:
    hotFile = args[0]
    coldFile = args[1]
    supplyFile = args[2]

#Load hot data
data = np.loadtxt(hotFile, skiprows=1, unpack=True)
htimes = data[0]
htherm = data[1:]

#Load cold data
data = np.loadtxt(coldFile, skiprows=1, unpack=True)
ctimes = data[0]
ctherm = data[1:]

#Load power supply data
data = np.loadtxt(supplyFile, delimiter=']', skiprows=0, unpack=True, dtype=np.str)
#Start and finish times for each voltage step
stimes, ftimes, powers = genTimes(data)

#Fit the data for each voltage step
hends = []
cends = []
hfits = []
cfits = []
print stimes
print ftimes
for i in range(len(stimes)):
    #Isolate hot data
    hmask = (htimes > stimes[i])*(htimes < ftimes[i])
    print len(htimes)
    print len(hmask)
    htime = htimes[hmask]
    hdata = np.array([h[hmask] for h in htherm])
    #Isolate cold data
    cmask = (ctimes > stimes[i])*(ctimes < ftimes[i])
    ctime = ctimes[cmask]
    cdata = np.array([c[cmask] for c in ctherm])
    #cdata = ctherm[cmask]
    #Fit hot data
    for h in hdata:
        hend, hfit = fit(htime, h)
        hends.append(hend)
        hfits.append(hfit)
    #Fit cold data
    for c in cdata:
        cend, cfit = fit(ctime, c)
        cends.append(cend)
        cfits.append(cfit)

#Print the finally achieved temperatures
for i in range(len(hend)):
    print "%.2f W: %.2fK - %.2f" % (powers[i], hend[i], cend[i])
