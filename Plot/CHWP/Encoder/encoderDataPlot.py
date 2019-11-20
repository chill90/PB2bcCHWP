import csv
import numpy as np
import scipy.optimize as opt
from collections import deque
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import copy
import os
import sys
import location as loc

#Set plotting parameters
plt.rc('font', size=28)
plt.rc('font', family='serif')
lw  = 3
lw2 = 4
frameSize = (15,10)

#Elimante initial points in power spectrum plots
start = 2

#Angle jitter requirement for PB2
jitterReq = np.sqrt(2)*(1.3e-6) #rad/rtHz

#Normalization correction from the analyzed data
normCorr = (2966.96764391**2)
normCorr = 1.
print "***** USING NORMALIZATION CORRECTION = %.1f FOR ALL PLOTS IN rad^2/Hz*****" % (normCorr)

#Function to bin the PSD (Akito's code)
def PSDBin(freq, psd, high_resolution=False):
    kbins = [(1,2)]
    while True:
        i = kbins[-1][1]
        di = int(0.1*i)
        if di < 1:
            di = 1
        if di > 100:
            di = int(10*np.sqrt(di))
        if (i+di) >= len(psd):
            break
        if high_resolution:
            di = int(di/10.0) + 1
        kbins.append((i,i+di))
    retFreq = np.array([np.sum(freq[lo:hi],axis=0)/(hi-lo) for (lo, hi) in kbins])
    retPSD  = np.array([np.sum(psd[lo:hi],axis=0)/(hi-lo)  for (lo, hi) in kbins])
    return retFreq, retPSD
'''
#Function to bin the PSD
def PSDBin(freq, psd, start=0.01, end=1000.): #Start binning at "start"
    ints = range(0, int(np.round(np.log10(end)-np.log10(start))))
    print ints
    startIter = [start*(10**i) for i in np.array(ints)]
    endIter   = [start*(10**i) for i in np.array(ints)+1]
    binsize   = [int(10**i) for i in range(len(endIter))]
    retFreq = freq[(freq <= startIter[0])]
    retPSD  = psd[ (freq <= startIter[0])]
    for i in range(len(binsize)):
        freqChunk = freq[(freq>startIter[i])*(freq<=endIter[i])]
        psdChunk  = psd[ (freq>startIter[i])*(freq<=endIter[i])]
        alen = len(freqChunk)
        while True:
            np.append(retFreq, np.mean(freqChunck[:binsize[i]
        remainder = len(freqChunk)%binsize[i]
        if remainder:
            freqChunk_1 = freqChunk[:-remainder]
            psdChunk_1  = psdChunk[:-remainder]
            freqChunk_2 = freqChunk[-remainder:]
            psdChunk_2  = psdChunk[-remainder:]
            retFreq = np.concatenate((retFreq, np.mean(np.reshape(freqChunk_1, (-1, binsize[i])), axis=-1), np.array([np.mean(freqChunk_2)])))
            retPSD  = np.concatenate((retPSD,  np.mean(np.reshape(psdChunk_1,  (-1, binsize[i])), axis=-1), np.array([np.mean(psdChunk_2 )])))
        else:
            retFreq = np.concatenate((retFreq, np.mean(np.reshape(freqChunk, (-1, binsize[i])), axis=-1)))
            retPSD  = np.concatenate((retPSD,  np.mean(np.reshape(psdChunk,  (-1, binsize[i])), axis=-1)))
    return retFreq, retPSD


#Function to bin the PSD
def PSDBin(freq, psd, start=0.01, end=1000.): #Start binning at "start"
    ints = range(0, int(np.round(np.log10(end)-np.log10(start))))
    print ints
    startIter = [start*(10**i) for i in np.array(ints)]
    endIter   = [start*(10**i) for i in np.array(ints)+1]
    binsize   = [int(10**i) for i in range(len(endIter))]
    retFreq = freq[(freq <= startIter[0])]
    retPSD  = psd[ (freq <= startIter[0])]
    for i in range(len(binsize)):
        freqChunk = freq[(freq>startIter[i])*(freq<=endIter[i])]
        psdChunk  = psd[ (freq>startIter[i])*(freq<=endIter[i])]
        remainder = len(freqChunk)%binsize[i]
        if remainder:
            freqChunk_1 = freqChunk[:-remainder]
            psdChunk_1  = psdChunk[:-remainder]
            freqChunk_2 = freqChunk[-remainder:]
            psdChunk_2  = psdChunk[-remainder:]
            retFreq = np.concatenate((retFreq, np.mean(np.reshape(freqChunk_1, (-1, binsize[i])), axis=-1), np.array([np.mean(freqChunk_2)])))
            retPSD  = np.concatenate((retPSD,  np.mean(np.reshape(psdChunk_1,  (-1, binsize[i])), axis=-1), np.array([np.mean(psdChunk_2 )])))
        else:
            retFreq = np.concatenate((retFreq, np.mean(np.reshape(freqChunk, (-1, binsize[i])), axis=-1)))
            retPSD  = np.concatenate((retPSD,  np.mean(np.reshape(psdChunk,  (-1, binsize[i])), axis=-1)))
    return retFreq, retPSD
'''
'''
    retFreq = freq
    retPSD  = psd
    binSize = 0
    storedBin = False
    for start in startIter:
        #Don't touch the first samples in the array
        beginMask = (retFreq < start)
        retFreq_1 = retFreq[beginMask]
        retPSD_1  = retPSD[ beginMask]
        #Bin the rest of the frequencies
        endMask = (retFreq >= start)
        retFreq_2 = retFreq[endMask]
        retPSD_2  = retPSD[ endMask]
        #Throw away samples that don't fit within the bin size division
        #The bin size is set by the number of samples that we don't touch. We will bin linearly for now
        if not storedBin:
            binSize = len(retFreq_1)
            storedBin = True
        remainder = len(retFreq_2)%binSize
        retFreq_2 = np.delete(retFreq_2, np.s_[-remainder:])
        retPSD_2  = np.delete(retPSD_2,  np.s_[-remainder:])
        #Concatenate binned values 
        retFreq = np.concatenate((retFreq_1, np.mean(np.reshape(retFreq_2, (-1,binSize)), axis=-1)))
        retPSD  = np.concatenate((retPSD_1,  np.mean(np.reshape(retPSD_2,  (-1,binSize)), axis=-1)))
    return retFreq, retPSD
'''
'''
def PSDBin(freq, psd):
    retFreq = []
    retPSD  = []
    binEdgs = np.array([1,100,1000])
    masks = np.array([(freq > binEdgs[i])*(freq < binEdgs[1+]) for i in range(len(binEdgs)-1)])
    freqSubSets = np.array([freq[mask] for mask in masks])
    alen = len(freq)
    blen = alen/chunkSize #Number of chunks
    left = alen%chunkSize
    binSize = np.array([[i+1 for j in range(chunkSize)] for i in range(blen)]).flatten()
    binSize = np.concatenate((binSize, np.array([chunkSize for i in range(left)])))
    #binSize = int(freq/freqStep)
    print len(freq)
    for i in range(len(freq)):
        if not i%10000:
            print i
        f = freq[i]
        b = binSize[i]
        retFreq.append(np.mean(freq[:b]))
        retPSD.append( np.mean(psd[:b] ))
        freq = np.delete(freq, np.s_[:b])
        psd  = np.delete(psd,  np.s_[:b])
    return np.array(retFreq), np.array(retPSD)
''' 
if __name__ == '__main__':
    
    #Use user input to gather data to be plotted
    args = sys.argv[1:]
    if not len(args) == 1:
        sys.exit("Usage: python encoderDataPlot.py [Run Name]")
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
    loadArr = np.load(open(loadDir+"Angle_Time_"+runName+".pkl", 'rb'))
    time, angle = np.asarray(loadArr).T
    plt.figure(findex, figsize=frameSize)
    plt.plot(time, angle, linewidth=lw)
    plt.xlabel("Time [s]")
    plt.ylabel("Rotor Angle [rad]")
    plt.savefig(saveDir+"Angle_Time_"+runName+".png")
    findex += 1

    #Plots sine of angle vs time
    print "Plotting sine of angle vs time..."
    sine = np.sin(angle)
    plt.figure(findex, figsize=frameSize)
    plt.plot(time, sine, linewidth=lw)
    plt.xlabel("Time [s]")
    plt.ylabel("Sine of Rotor Angle")
    plt.savefig(saveDir+"AngleSine_Time_"+runName+".png")    
    findex += 1

    # Plots the PSD of the sine of the rotor angle
    print "Plotting PSD of sine of angle..."
    loadArr = np.load(open(loadDir+"AngleSine_rPSD_"+runName+".pkl", 'rb'))
    rfreq, sine_pow = np.asarray(loadArr).T
    plt.figure(findex, figsize=frameSize)
    pltFreq, pltSinePow = PSDBin(rfreq[start:], normCorr*sine_pow[start:])
    plt.loglog(pltFreq, pltSinePow, basex = 10, basey = 10, linewidth=lw)
    #plt.loglog(rfreq[start:], normCorr*sine_pow[start:], basex = 10, basey = 10, linewidth=lw)
    plt.xlim(xmax=1000)
    plt.grid()
    plt.xlabel("Frequency [Hz]")
    plt.ylabel("PSD of Sine of Rotor Angle [1/Hz]")
    plt.savefig(saveDir+"AngleSine_rPSD_"+runName+".png")
    findex += 1

    # Plots the PSD of the cosine of the rotor angle
    print "Plotting PSD of cosine of angle..."
    loadArr = np.load(open(loadDir+"AngleCosine_rPSD_"+runName+".pkl", 'rb'))
    rfreq, cosine_pow = np.asarray(loadArr).T
    plt.figure(findex, figsize=frameSize)
    plt.loglog(rfreq[start:], normCorr*cosine_pow[start:], basex = 10, basey = 10, linewidth=lw)
    plt.xlabel("Frequency [Hz]")
    plt.ylabel("PSD of Cosine of Rotor Angle [1/Hz]")
    plt.savefig(saveDir+"AngleCosine_rPSD_"+runName+".png")
    findex += 1
    
    #Plots the PSD of the complex exponential of the rotor angle
    print "Plotting PSD of complex exponential of angle..."
    loadArr = np.load(open(loadDir+"AngleComplexExp_PSD_"+runName+".pkl", 'rb'))
    freq, comp_pow = np.asarray(loadArr).T
    plt.figure(findex, figsize=frameSize)
    plt.semilogy(freq, normCorr*comp_pow, linewidth=lw)
    plt.xlabel("Frequency [Hz]")
    plt.ylabel("PSD of Complex Exp of Rotor Angle [1/Hz]")
    plt.xlim([-5.0,2.5])
    plt.grid()
    plt.savefig(saveDir+"AngleComplexExp_PSD_Zoom_"+runName+".png")
    plt.xlim([-100,100])
    plt.savefig(saveDir+"AngleComplexExp_PSD_"+runName+".png")
    findex += 1

    # Plots the PSD of the angle jitter
    print "Plotting PSD of angle jitter..."
    loadArr = np.load(open(loadDir+"AngleJitter_rPSD_"+runName+".pkl", 'rb'))
    rfreq, jitter_pow = np.asarray(loadArr).T
    plt.figure(findex, figsize=frameSize)
    plt.loglog(rfreq, normCorr*jitter_pow, basex = 10, basey = 10, linewidth=lw, label='Jitter')
    plt.axhline(jitterReq**2, linewidth=lw2, linestyle='--', color='r', label='Requirement')
    plt.xlabel("Frequency [Hz]")
    plt.ylabel("PSD of Angle Jitter [rad^2/Hz]")
    plt.legend(loc="best", fontsize=22)
    plt.savefig(saveDir+"AngleJitter_rPSD_"+runName+".png")
    findex += 1
    
    # Plots the PSD of the fit-subtracted sine of the rotor angle
    print "Plotting PSD of residual of sine of angle..."
    loadArr = np.load(open(loadDir+"AngleSineFitResidual_rPSD_"+runName+".pkl", 'rb'))
    rfreq, resid_pow = np.asarray(loadArr).T
    plt.figure(findex, figsize=frameSize)
    plt.loglog(rfreq, normCorr*resid_pow, basex = 10, basey = 10, linewidth=lw)
    plt.xlabel("Frequency [Hz]")
    plt.ylabel("PSD of Residual of Sine of Rotor Angle [rad^2/Hz]")
    plt.savefig(saveDir+"AngleSineFitResidual_rPSD_"+runName+".png")
    findex += 1

    # Plots the PSD of the notched sine of the rotor angle
    print "Plotting PSD of notched sine of angle..."
    loadArr = np.load(open(loadDir+"AngleSine_notched_rPSD_"+runName+".pkl", 'rb'))
    rfreq, sine_pow = np.asarray(loadArr).T
    plt.figure(findex, figsize=frameSize)
    plt.loglog(rfreq, normCorr*sine_pow, basex = 10, basey = 10, linewidth=lw)
    plt.xlabel("Frequency [Hz]")
    plt.ylabel("PSD of Notched Sine of Rotor Angle [1/Hz]")
    plt.savefig(saveDir+"AngleSine_notched_rPSD_"+runName+".png")
    findex += 1

    #Plots the PSD of the complex exponential of the rotor angle
    print "Plotting PSD of notched complex exponential of angle..."
    loadArr = np.load(open(loadDir+"AngleComplexExp_notched_PSD_"+runName+".pkl", 'rb'))
    freq, comp_pow = np.asarray(loadArr).T
    plt.figure(findex, figsize=frameSize)
    plt.semilogy(freq, normCorr*comp_pow, linewidth=lw)
    plt.xlabel("Frequency [Hz]")
    plt.ylabel("PSD of Notched Complex Exp of Rotor Angle [1/Hz]")
    plt.xlim([-5.0,2.5])
    plt.grid()
    plt.savefig(saveDir+"AngleComplexExp_notched_PSD_Zoom_"+runName+".png")
    plt.xlim([-100,100])
    plt.savefig(saveDir+"AngleComplexExp_notched_PSD_"+runName+".png")
    findex += 1

    #Plots the inverse FFT of the notched complex exponential of angle
    print "Plotting inverse FFT of notched complex exponential of angle..."
    loadArr = np.load(open(loadDir+"AngleComplexExp_notched_iFFT_"+runName+".pkl", 'rb'))
    time, comp_inv_real, comp_inv_imag = np.asarray(loadArr).T
    plt.figure(findex, figsize=frameSize)
    plt.plot(time[:1000], comp_inv_real[:1000], 'b-' , linewidth=lw, label='Real')
    plt.plot(time[:1000], comp_inv_imag[:1000], 'r--', linewidth=lw, label='Imag')
    plt.xlabel("Frequency [Hz]")
    plt.ylabel("iFFT of Notched Complex Exp of Rotor Angle")
    plt.legend(loc='best', fontsize=18)
    plt.savefig(saveDir+"AngleComplexExp_notched_iFFT_"+runName+".png")
    findex += 1
    
    # ****** Clock vs Count Plots ******

    print

    # Plots the PSD of the sine of the clock
    print "Plotting PSD of sine of clock..."
    loadArr = np.load(open(loadDir+"ClockSine_rPSD_"+runName+".pkl", 'rb'))
    crfreq, clockSine_pow = np.asarray(loadArr).T
    plt.figure(findex, figsize=frameSize)
    plt.loglog(crfreq, clockSine_pow, basex = 10, basey = 10, linewidth=lw)
    plt.xlabel("Inverse Counts")
    plt.ylabel("PSD of Sine of Clock [A.U.]")
    plt.savefig(saveDir+"ClockSine_rPSD_"+runName+".png")
    findex += 1
    '''
    # Plots the PSD of the clock jitter
    print "Plotting PSD of clock jitter..."
    loadArr = np.load(open(loadDir+"ClockJitter_rPSD_"+runName+".pkl", 'rb'))
    crfreq, clockJitter_pow = np.asarray(loadArr).T
    plt.figure(findex, figsize=frameSize)
    plt.loglog(crfreq, clockJitter_pow, basex = 10, basey = 10, linewidth=lw)
    plt.xlabel("Inverse Counts")
    plt.ylabel("PSD of Clock Jitter [A.U.]")
    plt.savefig(saveDir+"ClockJitter_rPSD_"+runName+".png")
    findex += 1
    '''
    # ***** Other Plots ******

    print

    #Plot angle jitter vs time
    print "Plotting angle jitter vs time..."
    loadArr = np.load(open(loadDir+"AngleJitter_Time_"+runName+".pkl", 'rb'))
    jtime, jitter = np.asarray(loadArr).T
    plt.figure(findex, figsize=frameSize)
    plt.plot(jtime[0:25000], jitter[0:25000], linewidth=lw)
    plt.xlabel("Time [s]")
    plt.ylabel("Rotor Angle Jitter [rad]")
    plt.savefig(saveDir+"AngleJitter_Time_"+runName+".png")
    findex += 1
    
    #Plot angle jitter vs angle
    print "Plotting angle jitter vs angle..."
    loadArr = np.load(open(loadDir+"AngleJitter_Angle_"+runName+".pkl", 'rb'))
    jangle, jitter = np.asarray(loadArr).T
    plt.figure(findex, figsize=frameSize)
    plt.plot(jangle[0:5000], jitter[0:5000], linewidth=lw)
    plt.xlabel("Rotor Angle [rad]")
    plt.ylabel("Rotor Angle Jitter [rad]")
    plt.savefig(saveDir+"AngleJitter_Angle_"+runName+".png")
    findex += 1
    
    #Plot residual of fit-subtracted sine of rotor angle
    print "Plotting sine of angle residual vs time..."
    loadArr = np.load(open(loadDir+"AngleSineFitResidual_Time_"+runName+".pkl", 'rb'))
    rtime, residSine = np.asarray(loadArr).T
    plt.figure(findex, figsize=frameSize)
    plt.plot(rtime[0:25000], residSine[0:25000], linewidth=lw)
    plt.xlabel("Time [s]")
    plt.ylabel("Residual of Sine Fit of Rotor Angle")
    plt.savefig(saveDir+"AngleSineFitResidual_Time_Free_"+runName+".png")
    plt.ylim([-0.30,0.30])
    plt.savefig(saveDir+"AngleSineFitResidual_Time_"+runName+".png")
    plt.xlim([0,2])
    plt.savefig(saveDir+"AngleSineFitResidual_Time_Zoom_"+runName+".png")
    findex += 1
    
    #Plot of clock vs count
    print "Plotting angle clock vs count..."
    loadArr = np.load(open(loadDir+"Clock_Count_"+runName+".pkl", 'rb'))
    count, clock = np.asarray(loadArr).T
    plt.figure(findex, figsize=frameSize)
    plt.plot(count[0:5000], clock[0:5000])
    plt.xlabel("Count")
    plt.ylabel("Clock")
    plt.savefig(saveDir+"Clock_Count_"+runName+".png")
    findex += 1

    #Plot of clock jitter vs count
    print "Plotting clock jitter vs count.."
    loadArr = np.load(open(loadDir+"ClockJitter_Count_"+runName+".pkl", 'rb'))
    count, clockJitter = np.asarray(loadArr).T
    plt.figure(findex, figsize=frameSize)
    plt.plot(count[0:5000], clockJitter[0:5000])
    plt.xlabel("Count")
    plt.ylabel("Clock Jitter")
    plt.savefig(saveDir+"ClockJitter_Count_"+runName+".png")
    findex += 1

    #Plot of clock jitter vs clock
    print "Plotting clock jitter vs clock..."
    loadArr = np.load(open(loadDir+"ClockJitter_Clock_"+runName+".pkl", 'rb'))
    clock, clockJitter = np.asarray(loadArr).T
    plt.figure(findex, figsize=frameSize)
    plt.plot(clock[0:5000], clockJitter[0:5000])
    plt.xlabel("Clock")
    plt.ylabel("Clock Jitter")
    plt.savefig(saveDir+"ClockJitter_Clock_"+runName+".png")
    findex += 1
    
    print 'Done'
