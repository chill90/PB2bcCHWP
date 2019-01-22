import rotorHeatCapacity as RHC
import sys

try:
    temp = float(sys.argv[1])
except:
    sys.exit('Usage: getRotorHeatCapacity.py [Temperature]')

rhc = RHC.RotorHeatCapacity()
print rhc.heatCapacity(temp), 'J/K'
