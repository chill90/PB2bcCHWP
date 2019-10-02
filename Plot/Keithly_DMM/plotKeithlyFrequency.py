import matplotlib.pyplot as plt
import numpy as np
import sys

try:
    filename = sys.argv[1]
    dirName  = '/'.join(filename.split('/')[:-1])
except:
    print 'Usage: python plotMonitor.py [dataFile]'
    sys.exit(1)

#Only load the last two columns for time and pressure
time, data = np.loadtxt(filename, dtype=np.float, unpack=True, skiprows=1)

timeRel = (time - time[0])

plt.figure(0, figsize=(10,8))
plt.rc('font', family='serif')
plt.rc('font', size=32)
lw = 4

plt.plot(timeRel, data/570., linewidth=lw)
title = '%s' % (filename.split('/')[-1].split('.')[0])
plt.title(title)
plt.xlabel('Time [s]')
plt.ylabel('Frequency [Hz]')
plt.grid(which='major')
#plt.savefig('%s/%s.png' % (dirName, title))
plt.show()

 
