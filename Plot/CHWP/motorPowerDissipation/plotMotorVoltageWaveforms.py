import numpy as np
import matplotlib.pyplot as plt
import sys

#Gather files to be plotted
files = sys.argv[1:]
if len(files) != 1:
    sys.exit('Usage: python plotMotorVoltageWaveforms.py [voltage waveform file]')

#Gather data
time, ic_data, wp_data = np.loadtxt(files[0], unpack=True, dtype=np.float)

#Motor voltage for this data
voltage = files[0].split('.')[-2].split('_')[-1]

time = time - time[0]

lw = 3

#Overplot the waveforms
plt.figure(0)
plt.plot(time, ic_data, 'b-',  linewidth=lw, label='Source')
plt.plot(time, wp_data, 'r--', linewidth=lw, label='Coils')
plt.xlabel('Time [s]')
plt.ylabel('Voltage [V]')
plt.legend(loc='lower left')
plt.savefig('motorVoltageWaveforms_%s.png' % (voltage))

#Take the FFT of the waveforms
alen = len(time)
window = np.hanning(alen)
time_interp = np.linspace(time[0], time[-1], alen)
time_step   = time_interp[1] - time_interp[0]
ic_data_interp = np.interp(time_interp, time, ic_data)
ic_rfreq = np.fft.rfftfreq(alen, time_step)
norm = np.sqrt(time_step/(alen**2))*(1./(np.trapz(window)/alen))
ic_fft   = np.fft.rfft(ic_data_interp*window*norm)
ic_psd   = np.power(abs(ic_fft),2)

wp_data_interp = np.interp(time_interp, time, wp_data)
wp_rfreq = np.fft.rfftfreq(alen, time_step)
norm = np.sqrt(time_step/(alen**2))*(1./(np.trapz(window)/alen))
wp_fft   = np.fft.rfft(wp_data_interp*window*norm)
wp_psd   = np.power(abs(wp_fft),2)

#Overplot the PSD of the waveforms
plt.figure(1)
plt.loglog(ic_rfreq, ic_psd, 'b-',  linewidth=lw, label='Source')
plt.loglog(wp_rfreq, wp_psd, 'r--', linewidth=lw, label='Coils')
plt.xlabel('Frequency [Hz]')
plt.ylabel('Motor Voltage Spectral Density [V^2/Hz]')
plt.legend(loc='lower left', fontsize=18)
plt.savefig('motorVoltageWaveforms_%s_PSD.png' % (voltage))
