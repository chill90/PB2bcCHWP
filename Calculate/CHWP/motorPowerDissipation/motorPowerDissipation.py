import numpy as np
import scipy.signal as sig
import scipy.optimize as opt
import sys
import os

#Series Resistor resistnace
Rseries = 47 #Ohms

#Coil resistances during each run at each voltage
Rcoil = np.array([17.2, 21.7, 32.5, 57.5]) #Ohms
numCoilChannels = 12

#Motor waveform files to be read in
input_files = sys.argv[1:]
if not len(input_files) or len(input_files)%2:
    sys.exit('Usage: python motorPowerDissipation.py [motor waveforms at various voltages on both the IC-side WP-side of series resistor')
else:
    savedir = '/'.join(input_files[0].split('/')[:-1])

#Extract the voltages to be analyzed
voltages = []
for f in input_files:
    v = '%02d' % (int(f.split('_')[-2].rstrip('V')))
    if v not in voltages:
        voltages.append(v)
voltages = np.array(voltages)

#Identify which files are on the IC-side of the series resistor and which are on the waveplate-side (WP-side)
files = []
ICstr = 'ICside'
WPstr = 'WPside'
for i in range(len(voltages)):
    fs = []
    v = voltages[i]
    for f in input_files:
        fname = f.split('/')[-1]
        if v in fname:
            if ICstr in f:
                fs.append(f)
            elif WPstr in f:
                fs.append(f)
            else:
                sys.exit("Wasn't able to ID file %s" % (f))
    files.append(fs)

#Load data from files and convert to current output
currentVals = []
powerVals   = []

for i in range(len(files)):
    #Fetch motor voltage waveforms
    print "Analyzing data for motor voltage %02d V" % (int(voltages[i]))
    
    time_ICside, data_ICside = np.loadtxt(files[i][0], delimiter=',', unpack=True, dtype=np.float)
    time_WPside, data_WPside = np.loadtxt(files[i][1], delimiter=',', unpack=True, dtype=np.float)
    #Match the two square waves
    diff = []
    for j in range(0, 200): #1/5 of total number of points
        diff.append(np.sum(abs(data_ICside - np.roll(data_WPside, j))))
    rollVal = np.argmin(abs(np.array(diff)))
    print 'Rolled', rollVal
    data_WPside = np.roll(data_WPside, rollVal)

    if rollVal >= 0:
        time = time_ICside[rollVal:]
        time = time - time[0]
        data_WPside = data_WPside[rollVal:]
        data_ICside = data_ICside[rollVal:]
    else:
        time = time_ICside[:rollVal]
        time = time - time[0]
        data_WPside = data_WPside[:rollVal]
        data_ICside = data_ICside[:rollVal]

    #Write the voltage waveforms to a text file
    savefile = savedir+('/VoltageWaveform_%02dV.txt' % (int(voltages[i])))
    np.savetxt(savefile, np.array([time, data_ICside, data_WPside]).T)
    #Subtract the voltages to get the current waveform
    current = (data_ICside - data_WPside)/Rseries
    #Write the current waveform to a text file
    savefile = savedir+('/CurrentWaveform_%02dV.txt' % (int(voltages[i])))
    np.savetxt(savefile, np.array([time, current]).T)
    #Calculate the RMS current for this motor voltage
    window = np.blackman(len(current))
    currentVal = np.sqrt(np.average(np.power(current,2), weights=window))
    print 'Current =', currentVal
    currentVals.append(currentVal)
    #Calculate the power for this motor voltage
    powerVal = (currentVal**2)*Rcoil[i]*numCoilChannels
    print 'Power =', powerVal
    powerVals.append(powerVal)

#Write current RMS values to a text file
savefile = savedir+'/CurrentRMS.txt'
np.savetxt(savefile, np.array([voltages.astype(np.float), currentVals]).T, fmt='%-10.5f')

#Write power values to a text file
savefile = savedir+'/PowerRMS.txt'
np.savetxt(savefile, np.array([voltages.astype(np.float), powerVals]).T, fmt='%-10.5f')

    
