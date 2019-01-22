import matplotlib.pyplot as plt
import numpy as np
import sys

#Channels to read out (base 1)
LakeshoreChs = [1, 2]
SRSChs       = [1]

#Channel names
LakeshoreNames = ['20 K Cold Head', 'CHWP Stage']
SRSNames       = ['CHWP Rotor']
names          = LakeshoreNames+SRSNames

print "Usage: python plotCAPMAPCooldown.py [Lakeshore File] [SRS File]"
#print "Lakeshore channels to read: "+LakeshoreChs
#print "Lakeshore channel names: "+LakeshoreNames
#print "SRS channels to read: "+SRSChs
#print "SRS channel names: "+SRSNames

files = sys.argv[1:]

if not len(files) == 2:
    sys.exit('Need the Lakeshore file, followed by the SRS file...')

dirName  = '/'.join(files[0].split('/')[:-1])

#Load the data
arr1 = np.loadtxt(files[0], dtype=np.float, unpack=True, skiprows=1, usecols=[0]+LakeshoreChs)
arr2 = np.loadtxt(files[1], dtype=np.float, unpack=True, skiprows=1, usecols=[0]+SRSChs)

time1 = (arr1[0] - arr1[0][0])/3600.
time2 = (arr2[0] - arr2[0][0])/3600.

data1 = arr1[1:]
data2 = arr2[1:]

plt.rc('font', family='serif')
plt.rc('font', size=32)
lw = 4

#Zoomed out
plt.figure(0, figsize=(15,10))
for i in range(len(data1)):
    plt.plot(time1, data1[i], linewidth=lw, label=LakeshoreNames[i])
for i in range(len(data2)):
    plt.plot(time2, data2[i], linewidth=lw, label=SRSNames[i]      )
title = '%s' % (files[0].split('/')[-1].split('.')[0])
plt.title(title)
plt.xlabel('Time [hr]')
plt.ylabel('Temperature [K]')
plt.ylim([0, 300])
plt.legend(loc='best', fontsize=24)
plt.grid(which='major')
plt.savefig('%s/%s.png' % (dirName, title))
plt.show()

#Zoomed out, log
plt.figure(1, figsize=(15,10))
for i in range(len(data1)):
    plt.semilogy(time1, data1[i], linewidth=lw, label=LakeshoreNames[i])
for i in range(len(data2)):
    plt.semilogy(time2, data2[i], linewidth=lw, label=SRSNames[i]      )
title = '%s' % (files[0].split('/')[-1].split('.')[0])
plt.title(title)
plt.xlabel('Time [hr]')
plt.ylabel('Temperature [K]')
plt.ylim([0, 300])
plt.legend(loc='best', fontsize=24)
plt.grid(which='major')
plt.savefig('%s/%s_log.png' % (dirName, title))
plt.show()

#Zoomed in
plt.figure(2, figsize=(15,10))
for i in range(len(data1)):
    plt.plot(time1, data1[i], linewidth=lw, label=LakeshoreNames[i])
for i in range(len(data2)):
    plt.plot(time2, data2[i], linewidth=lw, label=SRSNames[i]      )
title = '%s' % (files[0].split('/')[-1].split('.')[0])
plt.title(title)
plt.xlabel('Time [hr]')
plt.xlim([100, 110])
plt.ylabel('Temperature [K]')
plt.ylim([10, 40])
plt.legend(loc='best', fontsize=24)
plt.grid(which='major')
plt.savefig('%s/%s_zoom.png' % (dirName, title))
plt.show()
