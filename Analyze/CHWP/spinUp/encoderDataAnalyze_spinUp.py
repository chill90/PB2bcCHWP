import numpy as np
import scipy.optimize as opt
from collections import deque
import copy
import location as loc
import os
import sys
import matplotlib.pyplot as plt

#Rotor moment of inertia
I = 0.33186 #kg-m^2

#Downsample arrays for faster processing
ds = 2

#Smoothing factor
sf = 10000

#Number of points to eliminate from the start of the data taking
st = 30000

#Smoothing function
def smooth(y, pts=sf):
    box = np.ones(pts)/pts
    y_smooth = np.convolve(y, box, mode='same')
    return y_smooth
    #return y

#****************** Main ***************************

# Portion of the code that runs
if __name__ == '__main__':
    #Use command-line arguments to obtain locaiton of the data to be processed
    args = sys.argv[1:]
    if not len(args) == 1:
        sys.exit("Usage: python encoderDataAnalyze.py [Run Name]\n")
    else:
        runName = str(args[0])
        loadDir = loc.masterDir+runName+"/Data/"
        if not os.path.exists(loadDir):
            sys.exit("FATAL: Data directory %s not found\n" % (loadDir))
        saveDir = loadDir

    # ********************************************************
    # Load Data
    # ********************************************************

    #Data files
    fname1 = loadDir+"/Angle_Time_"+runName+".pkl"
    if not os.path.exists(fname1):
        sys.exit("FATAL: Angle vs time data file %s not found\n" % (fname1))

    #Load the data
    loadArr      = np.load(open(fname1,'rb'))
    time, angle  = np.asarray(loadArr).T
    time = time[st::ds]
    angle = angle[st::ds]
    print angle
    print len(time)
    
    # ********************************************************
    # Analyze Data
    # ********************************************************

    #********** Analyze Angle vs Time Data **********

    print

    #Store smoothed frequency vs time
    print "Calculating angular frequency vs time..."
    ftime = time[1:]
    freq  = np.diff(angle)/np.diff(time)
    sfreq = smooth(freq)
    np.save(open(saveDir+'Frequency_Time_'+runName+'.pkl','wb'), np.array([ftime, sfreq]).T)

    '''
    #Store fitted frequency vs time
    print "Fitting tanh to frequency vs time..."
    def fitFunc(t, A, B, C, D):
        return A + B*np.tanh(C*t + D)
    #def fitFunc(t, A, B, C, D, E):
    #    return A/(B + C*np.exp(-D*t)) + E
    #def fitFunc(t, A, B, C, D):
    #    K = np.sqrt(B**2 + 4*A*C)
    #    return (-B + K*np.tanh(0.5*K*(t + D)))/(2*C)
    p0 = [1.0, 0.01, 0.01, 0.0]
    #p0 = [0.0, 1.7, 0.002, 0.0, 0.0]
    p1, cov = opt.curve_fit(fitFunc, ftime, sfreq, p0=p0)
    print p1
    fitFreq = fitFunc(ftime, *p1)
    np.save(open(saveDir+'FitFrequency_Time_'+runName+'.pkl','wb'), np.array([ftime, fitFreq]).T)
    '''
    #Store smoothed acceleration vs time
    print "Calculating angular acceleration vs time..."
    atime = ftime[1:]
    #accel = np.diff(freq)/np.diff(ftime)
    accel = np.diff(sfreq)/np.diff(ftime)
    saccel = smooth(accel)
    np.save(open(saveDir+'Acceleration_Time_'+runName+'.pkl','wb'), np.array([atime, saccel]).T)
    '''
    #Store fitted acceleration vs time
    print "Fitting angular acceleration vs time..."
    def fitDerv(t, A, B, C, D):
        return B*C*np.power((1./np.cosh(C*t + D)), 2.)
    #def fitDerv(t, A, B, C, D, E):
    #    return (A*C*D*np.exp(D*t))/np.power(B*np.exp(D*t) + C, 2)
    #def fitDerv(t, A, B, C, D):
    #    K = np.sqrt(B**2 + 4*A*C)
    #    return 0.25*(K**2)/(2*np.cosh(0.5*K*(C+t))**2)
    fitAccel = fitDerv(atime, *p1)
    np.save(open(saveDir+'FitAcceleration_Time_'+runName+'.pkl','wb'), np.array([atime, fitAccel]).T)
    '''
    #Store smoothed acceleration vs smoothed frequency
    print "Calculating angular acceleration vs frequency..."
    np.save(open(saveDir+'Acceleration_Frequency_'+runName+'.pkl','wb'), np.array([sfreq[1:], saccel]).T)

    '''
    #Fit smoothed acceleration vs smoothed frequency
    p1, cov = np.polyfit(sfreq[1:][200:-200], saccel[200:-200], 6, cov=True)
    dof = len(sfreq[1:])-len(p1)
    
    print
    print "Results of fitting frequency vs acceleration to"
    print "A + B*x + C*x^2 + D*x^3 + E*x^4 + F*x^5 + "
    print "where 'x' is the frequency:"
    print
    print "A = %.6f +/- %.6f" % (p1[3], np.sqrt(cov[3,3]/dof))
    print "B = %.6f +/- %.6f" % (p1[2], np.sqrt(cov[2,2]/dof))
    print "C = %.6f +/- %.6f" % (p1[1], np.sqrt(cov[1,1]/dof))
    print "D = %.6f +/- %.6f" % (p1[0], np.sqrt(cov[0,0]/dof))
    print

    print "Power dissipated at 2 Hz rotation:"
    omega = 2*np.pi*2 #rad/s
    val   = I*omega*np.polyval(p1, omega)
    err   = I*omega*np.polyval([np.sqrt(np.sum(abs(cov[:,i]))/dof) for i in range(len(p1))], omega)
    print "%.6f +/- %.6f" % (val, err)
    print
    '''
    '''
    #Store fitted acceleration vs fitted frequency
    print "Fitting angular acceleration vs frequency..."
    np.save(open(saveDir+'FitAcceleration_Frequency_'+runName+'.pkl','wb'), np.array([fitFreq[1:], fitAccel]).T)
    '''

    #Store smoothed torque vs time
    print "Calculating torque vs time..."
    storque = I*saccel
    np.save(open(saveDir+'Torque_Time_'+runName+'.pkl','wb'), np.array([atime, storque]).T)

    '''
    #Store fitted torque vs time
    fitTorque = I*fitAccel
    np.save(open(saveDir+'FitTorque_Time_'+runName+'.pkl','wb'), np.array([atime, fitTorque]).T)    
    '''

    #Store smoothed torque vs smoothed frequency
    print "Calculating torque vs frequency..."
    np.save(open(saveDir+'Torque_Frequency_'+runName+'.pkl','wb'), np.array([sfreq[1:], storque]).T)

    '''
    #Store fitted torque vs fitted frequency
    print "Fitting torque vs frequency..."
    np.save(open(saveDir+'FitTorque_Frequency_'+runName+'.pkl','wb'), np.array([fitFreq[1:], fitTorque]).T)
    '''

    #Store smoothed power vs time
    print "Calculating power vs time..."
    spower = storque*sfreq[1:]
    np.save(open(saveDir+'Power_Time_'+runName+'.pkl','wb'), np.array([atime, spower]).T)

    '''
    #Store fitted power vs time
    print "Fitting power vs time..."
    fitPower = fitTorque*fitFreq[1:]
    np.save(open(saveDir+'FitPower_Time_'+runName+'.pkl','wb'), np.array([atime, fitPower]).T)
    '''

    #Store smoothed power vs smoothed frequency
    print "Calculating power vs frequncy..."
    np.save(open(saveDir+'Power_Frequency_'+runName+'.pkl','wb'), np.array([sfreq[1:], spower]).T)

    '''
    #Store fitted power vs fitted frequency
    print "Fitting power vs frequency..."
    np.save(open(saveDir+'FitPower_Frequency_'+runName+'.pkl','wb'), np.array([fitFreq[1:], fitPower]).T)
    '''

    print 'Done'
