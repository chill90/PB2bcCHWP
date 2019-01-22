############################################################################################################################

## Specific heat curve and integration for any material that follows log polynomial curve
## User inputs: coefficients, temperature range [K], weight [kg]
## The function fn_integ_k(coeff) returns the integral over temperatures T1 and T2 (T2 > T1) for entered coefficients for
## log-polynomial expansion of specific heat in units: [J/kg-K]
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
## Specific heat curve and integration for any material that follows log polynomial curve
## User inputs: coefficients, temperature range [K], weight [kg]
## The function fn_integ_k(coeff) returns the integral over temperatures T1 and T2 (T2 > T1) for entered coefficients for
## log-polynomial expansion of specific heat in units: [J/kg-K]
## Ensure that the coefficients you enter are valid over the temperature range you enter 
''')

print('Enter coefficients separated by ","')

coeff_str_arr = input().split(',') 
coeff_arr = [float(num) for num in coeff_str_arr]
print('The coeffecients you entered are: ',coeff_arr)

def specific_conductivity(T,coeff):
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

kT = specific_conductivity(T,coeff_arr)

plt.semilogy(T,kT,ls='--')
plt.grid()
plt.xlabel('T [K]',fontsize=14)
plt.ylabel('k(T) [J/kg-K]',fontsize=14)
plt.show()

def fn_integ_k(coeff):
    return quad(specific_conductivity,T1,T2,args=(coeff))[0]

integ_k = fn_integ_k(coeff_arr)
print('Conductivity at ',T1,' K is : ',kT[0],' [J/kg-K]')
print('Integral of conductivity over ',T1,' to ',T2,' K is: ',integ_k,' [J/kg]')

print('Do you want to compute for given weight of material ? [y/n]')
answer = input()
assert answer.lower()=='y' or answer.lower()=='n',"Enter either y or n"
if answer.lower()=='n':
    sys.exit()

print('Enter weighr in kg')
weight = input()
weight = np.asfarray(weight)
assert weight>0,"weight must be positive"

energy = integ_k * weight
print ('Enrgy to cool ',weight,' kg of material from',T2,' to ',T2,' [K] is ',energy,'Joules.')

