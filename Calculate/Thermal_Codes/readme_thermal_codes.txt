CODE: thermal_conductivity_calculator.py
Description:
Thermal conductivity curve and integration for any material that follows log polynomial curve
User inputs: coefficients, temperature range [K], inner and outer diameter [inch], length [cm]
The function fn_integ_k(coeff) returns the integral over temperatures T1 and T2 (T2 > T1) for entered coefficients for
log-polynomial expansion of thermal conductivity in units: [W/m-K]
Ensure that the coefficients you enter are valid over the temperature range you enter 
Author: Mayuri S.Rao
Date created : 09 May 2018
Modification history :
For more on format of the log-polynomial expansion and for typical coefficient values refer to:
https://trc.nist.gov/cryogenics/materials/materialproperties.htm

CODE: specific_heat_calculator.py
Description:
Specific heat curve and integration for any material that follows log polynomial curve
User inputs: coefficients, temperature range [K], weight [kg]
The function fn_integ_k(coeff) returns the integral over temperatures T1 and T2 (T2 > T1) for entered coefficients for
log-polynomial expansion of specific heat in units: [J/kg-K]
Ensure that the coefficients you enter are valid over the temperature range you enter 
Author: Mayuri S.Rao
Date created : 09 May 2018
Modification history :
For more on format of the log-polynomial expansion and for typical coefficient values refer to:
https://trc.nist.gov/cryogenics/materials/materialproperties.htm
