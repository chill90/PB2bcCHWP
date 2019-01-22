import numpy as np
import rotorHeatCapacity as RHC
import sys

def linearTemp(Tf, Ti, t):
    return Ti + ((Tf - Ti)/(t[-1] - t[0]))*t

def linearTempDeriv(Tf, Ti, t):
    return ((Tf - Ti)/(t[-1] - t[0]))

#Get the initial and final temperature of the rotor
args = sys.argv[1:]
if not len(args) == 4:
    sys.exit('Usage: python getRotorHeatLoad.py [Initial Rotor Temp] [Final Rotor Temp] [Initial Stator Temp] [Final Stator Temp]')
else:
    rtemp1 = float(args[0])
    rtemp2 = float(args[1])
    stemp1 = float(args[2])
    stemp2 = float(args[3])

#Rotor heat capacity 
rhc = RHC.RotorHeatCapacity()

#Integrate the heat capacity, correcting for the change in stator temperature 
rTemps = np.linspace(rtemp1, rtemp2, 100)
sTemps = np.linspace(stemp1, stemp2, 100)
heatLoad = np.trapz(rhc.heatCapacity(rTemps), rTemps) - np.trapz(rhc.heatCapacity(sTemps), sTemps)

print "Rotor Heat Load = %.1f J" % (heatLoad)
