import numpy as np
import matplotlib.pyplot as plt
import sys

#Get power vs motor voltage from the command line
file = sys.argv[1]
if not len(file):
    sys.exit('Usage: python plotMotorPowerDissipation.py [power RMS file]')

#Load the data
voltage, power = np.loadtxt(file, unpack=True, dtype=np.float)

lw = 4
ms = 12

plt.figure(0, figsize=(15,10))

plt.plot(voltage, power, linewidth=lw, marker='o', markersize=ms)
plt.xlabel('Motor Voltage [V]')
plt.ylabel('Power Dissipation [W]')
plt.savefig('motorPowerDissipation.png')
