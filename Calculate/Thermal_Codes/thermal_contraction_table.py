############################################################################################################################

## Thermal contraction of any material from 4 K to 293 K
## User inputs: coefficients, length  at 293 K [m]
## Ensure that the coefficients you enter are valid over the temperature range you enter 
## Author: Mayuri S.Rao -- adopted by Charlie Hill
## Date created : 22 Sep 2018
## Modification history :
## For more on format of the polynomial expansion and for typical coefficient values refer to:
## https://trc.nist.gov/cryogenics/materials/materialproperties.htm

############################################################################################################################

import numpy as np
import sys
import time
print('''
## Thermal expansion for any material that follows polynomial curve
## User inputs: coefficients, length at 293 K [mm]
## Ensure that the coefficients you enter are valid over the temperature range you enter 
''')

print('Enter coefficients separated by ","')

coeff_str_arr = str(input()).strip('()').split(',') 
coeff_arr = [float(num) for num in coeff_str_arr]
print coeff_arr
print('The coeffecients you entered are: ',coeff_arr)

def thermal_expansion_coefficient(T,coeff):
    sum = 0.
    for i in range(np.size(coeff)):
            sum += coeff[i]*(T**i)
    return sum*1.e-5

#Temperature range
temps = np.linspace(4, 293, 290) #Every 1 K

CTE = thermal_expansion_coefficient(temps,coeff_arr)

print CTE

print('Enter length in [mm] at 293 K: ')
length = str(input()).strip('()')
length = float(length)

newLens = length + CTE * length
#print ('Thermal contraction of ',length,' m of material from 293 to ',Tf,' K is ',contr,'m')
fname = 'thermalContractionTable_%d.txt' % (time.time())
print ("Saving to file '%s'" % (fname))
np.savetxt(fname, np.array([temps, newLens]).T, fmt='%-15.2f')
