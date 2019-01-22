############################################################################################################################

## Coefficient of thermal expansion and integration for any material that follows polynomial curve
## User inputs: coefficients, temperature range [K], length [m]
## Ensure that the coefficients you enter are valid over the temperature range you enter 
## Author: Mayuri S.Rao -- adopted by Charlie Hill
## Date created : 07 Aug 2018
## Modification history :
## For more on format of the polynomial expansion and for typical coefficient values refer to:
## https://trc.nist.gov/cryogenics/materials/materialproperties.htm

############################################################################################################################

import numpy as np
import sys
print('''
## Thermal expansion for any material that follows polynomial curve
## User inputs: coefficients, final temperature [K], length [m]
## Ensure that the coefficients you enter are valid over the temperature range you enter 
''')

print('Enter coefficients separated by ","')

coeff_str_arr = str(input()).strip('()').split(',') 
coeff_arr = [float(num) for num in coeff_str_arr]
print('The coeffecients you entered are: ',coeff_arr)

def thermal_expansion_coefficient(T,coeff):
    sum = 0.
    for i in range(np.size(coeff)):
            sum += coeff[i]*(T**i)
    return sum*1.e-5

print('Enter final temperature')
Tf = str(input()).strip('()')
print Tf
Tf = float(Tf)
assert Tf>0,"Tf must be greater than 0"

CTE = thermal_expansion_coefficient(Tf,coeff_arr)

print('Enter length in m')
length = str(input()).strip('()')
length = float(length)
assert length>0,"length must be positive"

contr = CTE * length
print ('Thermal contraction of ',length,' m of material from 293 to ',Tf,' K is ',contr,'m')

