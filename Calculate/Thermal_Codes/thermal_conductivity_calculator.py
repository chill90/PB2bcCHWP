############################################################################################################################

## Thermal conductivity curve and integration for any material that follows log polynomial curve
## User inputs: coefficients, temperature range [K], inner and outer diameter [inch], length [cm]
## The function fn_integ_k(coeff) returns the integral over temperatures T1 and T2 (T2 > T1) for entered coefficients for
## log-polynomial expansion of thermal conductivity in units: [W/m-K]
## Ensure that the coefficients you enter are valid over the temperature range you enter 
## Author: Mayuri S.Rao
## Date created : 09 May 2018
## Modification history :
## For more on format of the log-polynomial expansion and for typical coefficient values refer to:
## https://trc.nist.gov/cryogenics/materials/materialproperties.htm

############################################################################################################################

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams['figure.figsize'] = (12, 8)
matplotlib.rcParams['lines.linewidth'] = 2.0
matplotlib.rcParams['xtick.labelsize']=14.0
matplotlib.rcParams['ytick.labelsize']=14.0
from matplotlib import rcParams
rcParams.update({'figure.autolayout': True})
import scipy.integrate as integrate
from scipy.integrate import quad
import sys
print('''
## Thermal conductivity curve and integration for any material that follows log polynomial curve
## User inputs: coefficients, temperature range [K], inner and outer diameter [cm], length [cm]
## The function fn_integ_k(coeff) returns the integral over temperatures T1 and T2 (T2 > T1) for entered coefficients for
## log-polynomial expansion of thermal conductivity in units: [W/m-K]
## Ensure that the coefficients you enter are valid over the temperature range you enter 
''')

print('Enter coefficients separated by ","')

coeff_str_arr = input().split(',') 
coeff_arr = [float(num) for num in coeff_str_arr]
print('The coeffecients you entered are: ',coeff_arr)

def thermal_conductivity(T,coeff):
    sum = 0.
    for i in range(np.size(coeff)):
            sum += coeff[i]*(np.log10(T)**i)
    return 10.0**(sum)

print('Enter T1, T2, where T2 > T1 :')
T1,T2 = input().split(',')
T1 = np.asfarray(T1)
T2 = np.asfarray(T2)
assert T2>T1,"T2 must be greater than T1"
T = np.arange(T1,T2)

kT = thermal_conductivity(T,coeff_arr)

plt.semilogy(T,kT,ls='--')
plt.grid()
plt.xlabel('T [K]',fontsize=14)
plt.ylabel('k(T) [W/m-K]',fontsize=14)
plt.show()

def fn_integ_k(coeff):
    return quad(thermal_conductivity,T1,T2,args=(coeff))[0]

integ_k = fn_integ_k(coeff_arr)
print('Conductivity at ',T1,' K is : ',kT[0],' [W/m-K]')
print('Integral of conductivity over ',T1,' to ',T2,' K is: ',integ_k,' [W/m]')

print('Do you want to compute for specific wire cross-section and length? [y/n]')
answer = input()
assert answer.lower()=='y' or answer.lower()=='n',"Enter either y or n"
if answer.lower()=='n':
    sys.exit()

print('Enter inner, outer diameter in [inch]. [inner diameter for wire/ solid tube.]')
d1,d2 = input().split(',')
d1 = np.asfarray(d1)
d2 = np.asfarray(d2)
assert d2>0,"outer diameter must be positive"
assert d1>=0,"inner diameter must be >= 0.0"
assert d2>d1,"d2 must be greater than d1"

print('Enter length [cm]')
L = input()
L = np.float(L)
assert L>0,"length must be positive"
r1 = ((d1*2.54)/2)*1e-2
r2 = ((d2*2.54)/2)*1e-2

area = np.pi*((r2)**2 - (r1)**2)
L = L*1e-2
P = integ_k * area / L
print ('Heat conducted by ',L*100,' cm of wire with cross-sectional area ',area*1e6,' [mm^2] between ',T1,' and ',T2,' K is ',P,'Watts.')

