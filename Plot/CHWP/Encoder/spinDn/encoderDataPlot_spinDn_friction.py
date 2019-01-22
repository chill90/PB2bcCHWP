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

#Include overplots of fits?
fits = True

if fits:
    print "*** Including fits in plots ***"
else:
    print "*** Not including fits in plots ***"

#For averaging down data
bs = 500
def avg(arr, binsize=bs):
    return arr[:-(len(arr)%binsize)].reshape(-1,binsize).mean(axis=1)

#Data points to eliminate from start and finish of array
#Can rid the array of edge effects during smoothing
s = 20
f = -20

#Changes of units
mRad2 = 1e6
mRad  = 1e3
mm    = 1e3
mW    = 1e3

if __name__ == '__main__':
    
    #Use user input to gather data to be plotted
    args = sys.argv[1:]
    if not len(args) == 1:
        sys.exit("Usage: python %s [Run Name]" % (sys.argv[0]))
    else:
        runName = str(args[0])
        loadDir = loc.masterDir+runName+"/Data/"
        if not os.path.exists(loadDir):
            sys.exit("FATAL: Data directory %s not found\n" % (loadDir))
        saveDir = loc.masterDir+runName+"/Plots/"
        if not os.path.exists(saveDir):
            print "Generating plot directory %s..." % (saveDir)
            os.makedirs(saveDir)

    print "Plotting data..."
    findex = 0

    # ****** Angle vs Time Plots ******

    print

    #Plots angle vs time
    print "Plotting angle vs time..."
    plt.figure(findex)
    loadArr = np.load(open(loadDir+"Angle_Time_"+runName+".pkl", 'rb'))
    time, angle = np.asarray(loadArr).T
    plt.plot(avg(time), avg(angle), 'b-', label='Data')
    plt.xlabel("Time [s]")
    plt.ylabel("Rotor Angle [rad]")
    plt.savefig(saveDir+"Angle_Time_"+runName+".png")
    findex += 1

    #Plots frequency vs time
    print "Plotting frequency vs time..."
    plt.figure(findex)
    loadArr = np.load(open(loadDir+"Frequency_Time_"+runName+".pkl", 'rb'))
    time, freq = np.asarray(loadArr).T
    plt.plot(avg(time)[s:f], avg(freq)[s:f]/(2*np.pi), 'b-', label='Data')
    if fits:
        loadArr = np.load(open(loadDir+"FitFrequency_Time_"+runName+".pkl", 'rb'))
        time, freq = np.asarray(loadArr).T
        plt.plot(time[s*bs:f*bs], freq[s*bs:f*bs]/(2*np.pi), 'r--', label='Fit')
        plt.legend()
    plt.xlabel("Time [s]")
    plt.ylabel("Rotor Frequency [Hz]")
    if fits:
        plt.savefig(saveDir+"Frequency_Time_"+runName+"_withFits.png")
    else:
        plt.savefig(saveDir+"Frequency_Time_"+runName+".png")
    findex += 1
    
    #Plots acceleration vs time
    print "Plotting acceleration vs time..."
    plt.figure(findex)
    loadArr = np.load(open(loadDir+"Acceleration_Time_"+runName+".pkl", 'rb'))
    time, accel = np.asarray(loadArr).T
    plt.plot(avg(time)[s:f], avg(accel)[s:f]*mRad, 'b-', label='Data')
    if fits:
        loadArr = np.load(open(loadDir+"FitAcceleration_Time_"+runName+".pkl", 'rb'))
        time, accel = np.asarray(loadArr).T
        plt.plot(time[s*bs:f*bs], accel[s*bs:f*bs]*mRad, 'r--', label='Fit')
        plt.legend()
    plt.xlabel("Time [s]")
    plt.ylabel("Rotor Acceleration ["+r"$\times 10^{-3} \; \mathrm{rad^{2}}$"+" s]")
    if fits:
        plt.savefig(saveDir+"Acceleration_Time_"+runName+"_withFits.png")
    else:
        plt.savefig(saveDir+"Acceleration_Time_"+runName+".png")
    findex += 1

    #Plots acceleration vs frequency
    print "Plotting acceleration vs frequency..."
    plt.figure(findex)
    loadArr = np.load(open(loadDir+"Acceleration_Frequency_"+runName+".pkl", 'rb'))
    freq, accel = np.asarray(loadArr).T
    plt.plot(avg(freq)[s:f]/(2*np.pi), avg(accel)[s:f]*mRad, 'b-', label='Data')
    if fits:
        loadArr = np.load(open(loadDir+"FitAcceleration_Frequency_"+runName+".pkl", 'rb'))
        freq, accel = np.asarray(loadArr).T
        plt.plot(freq[s*bs:f*bs]/(2*np.pi), accel[s*bs:f*bs]*mRad, 'r--', label='Fit')
        plt.legend()
    plt.xlabel("Frequency [Hz]")
    plt.ylabel("Rotor Acceleration ["+r"$\times 10^{-3} \; \mathrm{rad^{2} / s}$"+"]")
    if fits:
        plt.savefig(saveDir+"Acceleration_Frequency_"+runName+"_withFits.png")
    else:
        plt.savefig(saveDir+"Acceleration_Frequency_"+runName+".png")
    findex += 1

    #Plots torque vs time
    print "Plotting torque vs time..."
    plt.figure(findex)
    loadArr = np.load(open(loadDir+"Torque_Time_"+runName+".pkl", 'rb'))
    time, torque = np.asarray(loadArr).T
    plt.plot(avg(time)[s:f], avg(torque)[s:f]*mm, 'b-', label='Data')
    if fits:
        loadArr = np.load(open(loadDir+"FitTorque_Time_"+runName+".pkl", 'rb'))
        time, torque = np.asarray(loadArr).T
        plt.plot(time[s*bs:f*bs], torque[s*bs:f*bs]*mm, 'r--', label='Fit')
        plt.legend()
    plt.xlabel("Time [s]")
    plt.ylabel("Torque on Rotor [N mm]")
    if fits:
        plt.savefig(saveDir+"Torque_Time_"+runName+"_withFits.png")
    else:
        plt.savefig(saveDir+"Torque_Time_"+runName+".png")
    findex += 1

    #Plot torque vs frequency
    print "Plotting torque vs frequency..."
    plt.figure(findex)
    loadArr = np.load(open(loadDir+"Torque_Frequency_"+runName+".pkl", 'rb'))
    freq, torque = np.asarray(loadArr).T
    plt.plot(avg(freq)[s:f]/(2*np.pi), avg(torque)[s:f]*mm, 'b-', label='Data')
    if fits:
        loadArr = np.load(open(loadDir+"FitTorque_Frequency_"+runName+".pkl", 'rb'))
        freq, torque = np.asarray(loadArr).T
        plt.plot(freq[s*bs:f*bs]/(2*np.pi), torque[s*bs:f*bs]*mm, 'r--', label='Fit')
        plt.legend()
    plt.xlabel("Rotor Frequency [Hz]")
    plt.ylabel("Torque on Rotor [N mm]")
    if fits:
        plt.savefig(saveDir+"Torque_Frequency_"+runName+"_withFits.png")
    else:
        plt.savefig(saveDir+"Torque_Frequency_"+runName+".png")
    findex += 1    

    #Plot power vs time
    print "Plotting power vs time..."
    plt.figure(findex)
    loadArr = np.load(open(loadDir+"Power_Time_"+runName+".pkl", 'rb'))
    time, power = np.asarray(loadArr).T
    plt.plot(avg(time)[s:f], abs(avg(power)[s:f])*mW, 'b-', label='Data')
    if fits:
        loadArr = np.load(open(loadDir+"FitPower_Time_"+runName+".pkl", 'rb'))
        time, power = np.asarray(loadArr).T
        plt.plot(time[s*bs:f*bs], abs(power)[s*bs:f*bs]*mW, 'r--', label='Fit')
        plt.legend()
    plt.xlabel("Time [s]")
    plt.ylabel("Power Dissipation [mW]")
    if fits:
        plt.savefig(saveDir+"Power_Time_"+runName+"_withFits.png")
    else:
        plt.savefig(saveDir+"Power_Time_"+runName+".png")
    findex += 1

    #Plot power vs freq
    print "Plotting power vs frequency..."
    plt.figure(findex)
    loadArr = np.load(open(loadDir+"Power_Frequency_"+runName+".pkl", 'rb'))
    freq, power = np.asarray(loadArr).T
    plt.plot(avg(freq)[s:f]/(2*np.pi), abs(avg(power)[s:f])*mW, 'b-', label='Data')
    if fits:
        loadArr = np.load(open(loadDir+"FitPower_Frequency_"+runName+".pkl", 'rb'))
        freq, power = np.asarray(loadArr).T
        plt.plot(freq[s*bs:f*bs]/(2*np.pi), abs(power)[s*bs:f*bs]*mW, 'r--', label='Fit')
        plt.legend()
    plt.xlabel("Rotor Frequency [Hz]")
    plt.ylabel("Power Dissipation [mW]")
    if fits:
        plt.savefig(saveDir+"Power_Frequency_"+runName+"_withFits.png")
    else:
        plt.savefig(saveDir+"Power_Frequency_"+runName+".png")
    findex += 1

    #Plot power vs freq with motor power overplotted
    print "Plotting power vs frequency with motor power overplotted..."
    vfreqs = np.array([1.83, 2.33, 2.62, 2.89]) #Hz
    mpower  = np.array([53, 111, 182, 272]) #mW
    plt.figure(findex)
    loadArr = np.load(open(loadDir+"Power_Frequency_"+runName+".pkl", 'rb'))
    freq, power = np.asarray(loadArr).T
    plt.plot(avg(freq)[s:f]/(2*np.pi), abs(avg(power)[s:f])*mW, 'b-', label='Rotor Friction Data')
    if fits:
        loadArr = np.load(open(loadDir+"FitPower_Frequency_"+runName+".pkl", 'rb'))
        #loadArr = np.load(open(loadDir+"FitPower_Extended_Frequency_"+runName+".pkl", 'rb'))
        freq, power = np.asarray(loadArr).T
        plt.plot(freq[s*bs:f*bs]/(2*np.pi), abs(power)[s*bs:f*bs]*mW, 'g--', label='Rotor Friction Fit')
        #plt.plot(freq/(2*np.pi), abs(power)*mW, 'g--', label='Rotor Dissipation Fit')
    plt.plot(vfreqs, mpower, 'r--', marker='o', markersize=12, label='Motor Dissipation Data')
    plt.legend(fontsize=24)
    #plt.legend(loc='best', fontsize=24)
    plt.xlabel("Rotor Frequency [Hz]")
    plt.ylabel("Power Dissipation [mW]")
    plt.grid()
    if fits:
        plt.savefig(saveDir+"Power_Frequency_withMotor_"+runName+"_withFits.png")
    else:
        plt.savefig(saveDir+"Power_Frequency_withMotor_"+runName+".png")
    findex += 1

    print 'Done'
