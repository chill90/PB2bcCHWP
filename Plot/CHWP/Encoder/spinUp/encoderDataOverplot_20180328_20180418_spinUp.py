import csv
import numpy as np
import scipy.optimize as opt
from collections import deque
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import copy
import os
import sys
import location as loc

#Overplot frequency vs time for various spin-up runs

#For averaging down data
bs = 500
def avg(arr, binsize=bs):
    return arr[:-(len(arr)%binsize)].reshape(-1,binsize).mean(axis=1)

#Data points to eliminate from start and finish of array
#Can rid the array of edge effects during smoothing
s = 20
f = -20

if __name__ == '__main__':
    
    #Use user input to gather data to be plotted
    #args = sys.argv[1:]
    #if len(args) < 1:
    #    sys.exit("Usage: python %s [Run Names]" % (sys.argv[0]))
    #else:
    #    runNames  = args
    runNames = ['20180328_Spinup_8V',
                '20180328_Spinup_16V',
                '20180328_Spinup_24V',
                '20180328_Spinup_32V',
                '20180418_spinUp_08V',
                '20180418_spinUp_16V',
                '20180418_spinUp_24V',
                '20180418_spinUp_32V']
    #Achieved frequencies
    ffreqs = [1.596, 2.002, 2.195, 2.418,
              1.833, 2.332, 2.619, 2.896]

    print 'Overplotting the following runs:'
    for runName in runNames:
        print runName
    loadDirs  = [loc.masterDir+runName+"/Data/" for runName in runNames]
    for loadDir in loadDirs:
        if not os.path.exists(loadDir):
            sys.exit("FATAL: Data directory %s not found\n" % (loadDir))
    saveDirs  = [loc.masterDir+runName+"/Plots/" for runName in runNames]
    for saveDir in saveDirs:
        if not os.path.exists(saveDir):
            print "Generating plot directory %s..." % (saveDir)
            os.makedirs(saveDir)

    print
    print "Plotting data..."
    findex = 0

    # ****** Angle vs Time Plots ******

    print

    #Plots frequency vs time for both before and after recovery
    print "Plotting frequency vs time for before and after recovery..."
    voltages = [8, 16, 24, 32, 8, 16, 24, 32]
    colors   = ['b', 'r', 'c', 'm', 'b', 'r', 'c', 'm']
    linestyles = ['-', '-', '-', '-', '--', '--', '--', '--']
    linelabels = ['Before recovery', 'After recovery']
    plt.figure(findex)
    for i in range(len(runNames)):
        runName = runNames[i]
        loadArr = np.load(open(loadDirs[i]+"Frequency_Time_"+runName+".pkl", 'rb'))
        time, freq = np.asarray(loadArr).T
        time = time - time[0]
        plt.plot(avg(time)[s:f], avg(freq)[s:f]/(2*np.pi), color=colors[i], linestyle=linestyles[i])
    #Plot phantom lines for labeling
    for i in range(4):
        plt.axhline(-1, color=colors[i], linestyle='-', linewidth=6, label='%02d V' % (voltages[i]))
    for i in range(2):
        plt.axhline(-1, color='k', linestyle=linestyles[i*4], linewidth=6, label='%s' % (linelabels[i]))
    plt.xlabel("Time [s]")
    plt.ylabel("Rotor Frequency [Hz]")
    plt.legend()
    plt.ylim(ymin=0.5)
    plt.savefig("Plots/Frequency_Time_Overplot_20180328_20180418_beforeAfterRecovery.png")
    findex +=1 

    #Plots frequency vs time for before recovery only
    print "Plotting frequency vs time for before recovery..."
    voltages = [8, 16, 24, 32]
    colors   = ['b', 'r', 'c', 'm']
    linestyles = ['-', '-', '-', '-']
    plt.figure(findex)
    for i in range(len(runNames)/2):
        runName = runNames[i]
        loadArr = np.load(open(loadDirs[i]+"Frequency_Time_"+runName+".pkl", 'rb'))
        time, freq = np.asarray(loadArr).T
        time = time - time[0]
        plt.plot(avg(time)[s:f], avg(freq)[s:f]/(2*np.pi), color=colors[i], linestyle=linestyles[i])
    #Plot phantom lines for labeling
    for i in range(4):
        plt.axhline(-1, color=colors[i], linestyle='-', linewidth=6, label='%02d V' % (voltages[i]))
    plt.xlabel("Time [s]")
    plt.ylabel("Rotor Frequency [Hz]")
    plt.legend()
    plt.ylim(ymin=0.5)
    plt.savefig("Plots/Frequency_Time_Overplot_20180328_20180418_beforeRecovery.png")
    findex +=1 

    #Plots frequency vs time for before recovery only
    print "Plotting frequency vs time for after recovery..."
    voltages = [8, 16, 24, 32]
    colors   = ['b', 'r', 'c', 'm']
    linestyles = ['-', '-', '-', '-']
    plt.figure(findex)
    for i in range(4,8):
        runName = runNames[i]
        loadArr = np.load(open(loadDirs[i]+"Frequency_Time_"+runName+".pkl", 'rb'))
        time, freq = np.asarray(loadArr).T
        time = time - time[0]
        plt.plot(avg(time)[s:f], avg(freq)[s:f]/(2*np.pi), color=colors[i-4], linestyle=linestyles[i-4])
    #Plot phantom lines for labeling
    for i in range(4):
        plt.axhline(-1, color=colors[i], linestyle='-', linewidth=6, label='%02d V' % (voltages[i]))
    plt.xlabel("Time [s]")
    plt.ylabel("Rotor Frequency [Hz]")
    plt.legend(loc='best', fontsize=24, title='Motor Voltage')
    plt.grid()
    plt.ylim(ymin=0.5)
    plt.savefig("Plots/Frequency_Time_Overplot_20180328_20180418_afterRecovery.png")
    findex +=1 

    #Plots final frequency vs time for both before and after recovery
    print "Plotting final frequency vs motor voltage for before and after recovery..."
    voltages = [8, 16, 24, 32]
    plt.figure(findex)
    plt.plot(voltages, ffreqs[:4], 'b-', label='Before Recovery', marker='o', markersize=12)
    plt.plot(voltages, ffreqs[4:], 'r--', label='After Recovery', marker='o', markersize=12)
    plt.xlabel("Motor Voltage [V]")
    plt.ylabel("Final Rotor Frequency [Hz]")
    plt.legend()
    plt.savefig("Plots/FinalFrequency_MotorVoltage_20180328_20180418_beforeAfterRecovery.png")
    findex +=1 

    #Plots final frequency vs time for both before recovery
    print "Plotting final frequency vs motor voltage for before recovery..."
    voltages = [8, 16, 24, 32]
    plt.figure(findex)
    plt.plot(voltages, ffreqs[:4], 'b-', label='Before Recovery', marker='o', markersize=12)
    plt.xlabel("Motor Voltage [V]")
    plt.ylabel("Final Rotor Frequency [Hz]")
    plt.savefig("Plots/FinalFrequency_MotorVoltage_20180328_20180418_beforeRecovery.png")
    findex +=1 

    #Plots final frequency vs time for both before and after recovery
    print "Plotting final frequency vs motor voltage for after recovery..."
    voltages = [8, 16, 24, 32]
    plt.figure(findex)
    plt.plot(voltages, ffreqs[4:], 'b-', label='After Recovery', marker='o', markersize=12)
    plt.xlabel("Motor Voltage [V]")
    plt.ylabel("Final Rotor Frequency [Hz]")
    plt.savefig("Plots/FinalFrequency_MotorVoltage_20180328_20180418_afterRecovery.png")
    findex +=1 
