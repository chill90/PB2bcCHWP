import matplotlib.pyplot as plt
import numpy as np
import sys

#Channel names
#chs = ['20 K Head', '50 K Stage', 'YBCO']
chs = ['20 K Head', 'CHWP Stage']

try:
    filename = sys.argv[1]
    dirName  = '/'.join(filename.split('/')[:-1])
except:
    print 'Usage: python plotTemperature.py [dataFile]'
    sys.exit(1)

#Only load the last two columns for time and pressure
arr = np.loadtxt(filename, dtype=np.float, unpack=True, skiprows=1)

timeRel = (arr[0] - arr[0][0])/3600. #hrs
data = arr[1:]

plt.figure(0, figsize=(15,10))
plt.rc('font', family='serif')
plt.rc('font', size=32)
lw = 4

for i in range(len(data)):
    plt.plot(timeRel, data[i], linewidth=lw, label=chs[i])

#Flagged points
#plt.axvline((1501551266 - arr[0][0])/3600., label='ADR Shutoff', linewidth=lw, linestyle='--', color='k') #hrs

#Labels
title = '%s' % (filename.split('/')[-1].split('.')[0])
plt.title(title)
plt.xlabel('Time [hr]')
plt.ylabel('Temperature [K]')
plt.legend(loc='best', fontsize=24)
plt.grid(which='major')
plt.savefig('%s/%s.png' % (dirName, title))
plt.show()

 
