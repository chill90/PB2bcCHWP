import numpy as np
import matplotlib.pyplot as plt

file = "20180213/TXT/18min_3Hz_30sps.txt"
outputFile = "20180213/PNG/18min_3Hz_30sps"
t, B_X, B_Y, B_Z, B_TOT = np.loadtxt(file, skiprows=1, unpack=True)

#Build arrays
time  = t - t[0]
field = B_TOT
timeInterp  = np.linspace(time[0], time[-1], len(time))
fieldInterp = np.interp(timeInterp, time, field)

#Calcualte power spectrum
tstep = timeInterp[1] - timeInterp[0]
alen = len(timeInterp)
window = np.hanning(alen)
norm = np.sqrt(tstep/(alen**2))*(1./(np.trapz(window)/alen))
freq = np.fft.rfftfreq(len(timeInterp), d=tstep)
fft = norm*np.fft.rfft(fieldInterp)
psd = np.power(abs(fft),2)

#Plotting parameters
plt.rc('font', family='serif')
plt.rc('font', size=28)
lw = 4

#Plot field vs time
plt.figure(0, figsize=(15,10))
plt.plot(time, field*1.e3, linewidth=lw)
plt.xlabel('Time [s]')
plt.ylabel('Total Field [mG]')
plt.xlim([0, 3])
plt.savefig('%s_TOD.png' % (file.split('.')[-2]))

#Plot PSD
plt.figure(1, figsize=(15,10))
plt.semilogy(freq, psd*1.e6, linewidth=2)
plt.xlabel('Frequency [Hz]')
plt.ylabel('Total Field [mG^2/Hz]')
plt.ylim([1e-13, 1e-1])
plt.savefig('%s_PSD.png' % (outputFile))
