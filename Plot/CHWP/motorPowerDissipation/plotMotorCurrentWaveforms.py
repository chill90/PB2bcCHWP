import numpy as np
import matplotlib.pyplot as plt
import sys

#Gather files to be plotted
files = sys.argv[1:]
if len(files) != 1:
    sys.exit('Usage: python plotMotorCurrentWaveforms.py [current waveform]')

#Gather data
time, data = np.loadtxt(files[0], unpack=True, dtype=np.float)

#Motor voltage for this data
voltage = files[0].split('.')[-2].split('_')[-1]

time = time - time[0]

#Plot the waveform
plt.figure(0)
plt.plot(time, data*1000, 'b-')
plt.xlabel('Time [s]')
plt.ylabel('Coil Current [mA]')
plt.savefig('motorCurrentWaveform_%s.png' % (voltage))

#Plot the absolute value of the waveform
plt.figure(1)
plt.plot(time, abs(data*1000), 'b-')
plt.xlabel('Time [s]')
plt.ylabel('Coil Current [mA]')
plt.savefig('motorCurrentWaveform_abs_%s.png' % (voltage))

#Print RMS of waveform
print "RMS: %.2f" % (np.sqrt((1./len(abs(data)))*np.sum(abs(data*1000)**2)))

#Take the FFT of the waveform
alen = len(time)
window = np.hanning(alen)
time_interp = np.linspace(time[0], time[-1], alen)
time_step   = time_interp[1] - time_interp[0]
data_interp = np.interp(time_interp, time, data)
rfreq = np.fft.rfftfreq(alen, time_step)
norm = np.sqrt(time_step/(alen**2))*(1./(np.trapz(window)/alen))
fft   = np.fft.rfft(data_interp*window*norm)
psd   = np.power(abs(fft),2)

#Plot the PSD of the waveform
plt.figure(2)
plt.loglog(rfreq, psd*10**6, 'b-')
plt.xlabel('Frequency [Hz]')
plt.ylabel('Motor Current Spectral Density [mA^2/Hz]')
plt.savefig('motorCurrentWaveform_%s_PSD.png' % (voltage))
