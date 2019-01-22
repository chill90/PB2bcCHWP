import numpy as np
import matplotlib.pyplot as plt
import sys

#Get power vs motor voltage from the command line
file = sys.argv[1]
if not len(file):
    sys.exit('Usage: python plotMotorCurrent.py [current RMS file]')

#Load the data
voltage, current = np.loadtxt(file, unpack=True, dtype=np.float)

lw = 4
ms = 12

plt.figure(0)

plt.plot(voltage, power, linewidth=lw, marker='o', markersize=ms)
plt.xlabel('Motor Voltage [V]')
plt.ylabel('Coil Current [W]')
plt.savefig('motorCurrent.png')
