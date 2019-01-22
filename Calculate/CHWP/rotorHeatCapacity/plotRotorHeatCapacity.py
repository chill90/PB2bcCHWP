import numpy as np
import matplotlib.pyplot as plt
import rotorHeatCapacity as RHC

#Rotor heat capacity object
rhc = RHC.RotorHeatCapacity()

#Plotting
plt.rc('font', size=28)
plt.rc('font', family='serif')
lw = 3

temps = np.linspace(10, 300, 100)

plt.figure(0, figsize=(15,10))
plt.plot(temps, rhc.heatCapacity(temps), linewidth=lw)
plt.title("CHWP LBNL Test Rotor")
plt.ylabel("Heat Capacity [J/K]")
plt.xlabel("Temperature [K]")
plt.grid()
plt.savefig("Plots/rotorHeatCapacity.png")
plt.show()

plt.figure(1, figsize=(15,10))
plt.semilogy(temps, rhc.heatCapacity(temps), linewidth=lw)
plt.title("CHWP LBNL Test Rotor")
plt.ylabel("Heat Capacity [J/K]")
plt.xlabel("Temperature [K]")
plt.grid()
plt.savefig("Plots/rotorHeatCapacity_log.png")
plt.show()
