import numpy as np
import matplotlib.pyplot as plt

class RotorHeatCapacity:
    def __init__(self):
        #Masses of the various elements on the rotor
        #Al6061, Steel, G10, NdFeB
        self.m = np.array([(3.580+9.437), 0.434, 0.787, 2.967]) #Al = rotor stage + sapphire proxy
        return

    #NIST Cryogenics Group data on specific heat vs tempearture for various materials
    def Form(self, p, T):
        exp = p[0] + p[1]*np.log10(T) + p[2]*np.power(np.log10(T),2) + p[3]*np.power(np.log10(T),3) + p[4]*np.power(np.log10(T),4) + p[5]*np.power(np.log10(T),5) + p[6]*np.power(np.log10(T),6) + p[7]*np.power(np.log10(T),7) + p[8]*np.power(np.log10(T),8)
        return np.power(10, exp) 
    #6061 Aluminum
    def Al6061(self, T):
        p = [46.6467, -314.292, 866.662, -1298.30, 1162.27, -637.795, 210.351, -38.3094, 2.96334]
        print self.Form(p, 90)*3
        return self.Form(p, T)
    #Low-carbon steel
    #At 20 degC, Cold-rolled iron has a specific heat of ~450 J/kg-C, which is about half that of aluminum
    def Steel(self, T):
        return self.Al6061(T)/2.
    #G10
    def G10(self, T):
        p = [-2.4083, 7.6006, -8.2982, 7.3301, -4.2386, 1.4294, -0.24396, 0.015236, 0.00000]
        return self.Form(p, T)
    #NdFeB
    #At 20 degC, NdFeB has a specific heat of ~450 J/kg-C, which is about half of that of aluminum
    #Therefore, I will assume, due to the lack of literature, that this ratio persists down to low temperatures
    def NdFeB(self, T):
        return self.Al6061(T)/2.
    #Heat Capacity of the rotor vs temperature
    def heatCapacity(self, T):
        return self.m[0]*self.Al6061(T) + self.m[1]*self.Steel(T) + self.m[2]*self.G10(T) + self.m[3]*self.NdFeB(T)
