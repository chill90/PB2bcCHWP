import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import time as tm
import sys

#Read in data from the file passed as a command-line argument
args = sys.argv[1:]
if not len(args) == 2:
    sys.exit("Usage: python cooldownMagneticField.py [cooldown magnetic field data file] [lakeshore cooldown file]")
else:
    magFname  = args[0]
    tempFname = args[1] 
    saveDir = '/'.join(magFname.split('/')[:-3])+'/Plots/MagneticField/'
    saveFile = saveDir+magFname.split('/')[-1].split('.')[0]+'.png'

#Load field data
mtime, Bx, By, Bz = np.loadtxt(magFname, unpack=True, skiprows=1)
startArr = [1521200000, 1521400000, 1521500000, 1521600000]
sindex = 0
start = startArr[sindex]
last = 0
for i in range(len(mtime)):
    if mtime[i] < last:
        sindex += 1
        start = startArr[sindex]
    last = mtime[i]
    mtime[i] = mtime[i] + start
print mtime
Btot = np.sqrt(Bx**2 + By**2 + Bz**2)
#Load temperature data
ttime, stage = np.loadtxt(tempFname, unpack=True, skiprows=1, usecols=[0,2])
print ttime

#Interpolate magnetic field data to match the stage temperature
temp = np.interp(mtime, ttime, stage)

#ttime = (ttime - mtime[0])/3600 #hours
#ttime = ttime[ttime >= 0]
#mtime = (mtime - mtime[0])/3600 #hours

#Plot the fields
plt.rc('font', size=28)
plt.rc('font', family='serif')
lw = 0
ms = 12
mG = 1000.

plt.figure(0, figsize=(15,10))
plt.plot(temp, Bx*mG,   linewidth=lw, label='Bx',   marker='o', markersize=ms)
plt.plot(temp, By*mG,   linewidth=lw, label='By',   marker='o', markersize=ms)
plt.plot(temp, Bz*mG,   linewidth=lw, label='Bz',   marker='o', markersize=ms)
plt.plot(temp, Btot*mG, linewidth=lw, label='Btot', marker='o', markersize=ms)
plt.title('Cooldown Magnetic Field')
plt.ylabel('Magnetic Field [mG]')
plt.xlabel('Stage Temperature [K]')
plt.legend(loc='best', fontsize=22)
plt.savefig(saveFile)
