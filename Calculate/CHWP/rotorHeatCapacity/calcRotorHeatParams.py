import numpy as np
import rotorHeatCapacity as RHC
import sys

def linearTemp(Tf, Ti, t):
    return Ti + ((Tf - Ti)/(t[-1] - t[0]))*t

def linearTempDeriv(Tf, Ti, t):
    return ((Tf - Ti)/(t[-1] - t[0]))

#The time intervals being investigated
delta_t = np.array([16, 64])*3600 #sec
#Initial rotor temperatures
rotor_Ti = np.array([27.4, 31.7])
#Final rotor temperatures
rotor_Tf = np.array([29.8, 35.7])
#Initial stator temperatures
stator_Ti = np.array([21.3, 24.4])
#Final stator temperatures
stator_Tf = np.array([22.6, 24.8])

#Rotor delta T
rotor_delta_T = rotor_Tf - rotor_Ti
#Stator delta T
stator_delta_T = stator_Tf - stator_Ti

#Time arrays
time = []
for dt in delta_t:
    time.append(np.linspace(0, dt, 1000))
#Rotor temperature arrays
rotor_T  = np.array([linearTemp(rotor_Tf[i], rotor_Ti[i], time[i]) for in range(len(time))])
#Stator temperature arrays
stator_T = np.array([linearTemp(stator_Tf[i], stator_Ti[i], time[i]) for in range(len(time))])

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
