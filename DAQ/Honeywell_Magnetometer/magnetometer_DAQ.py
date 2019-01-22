#A script for retrieving calibration data from an already calibrated SIM922.
#Written by Samantha Rose Gilbert with assistanced from Dr. Mayuri Rao.
#October, 2017

import numpy as np
from scipy import loadtxt
import csv, sys
import serial 
from datetime import datetime
import matplotlib.pyplot as plt
import math

mag="/dev/ttyUSB0" #Connect to the USB port on the computer where you have plugged in the magnetometer 

#with open("/home/chill/Desktop/magnetometer/mag_out.txt", "w+") as f_out:
f_out = open("/home/chill/Desktop/magnetometer/mag_out.txt", "w+")
f_out.write("Sec\tBx\tBy\tBz\tBtot\n")

ser = serial.Serial(port=mag, baudrate=9600, timeout=1) #Set up the serial connection.

ret = ser.write('*00WE *00R=30\r')
print "wrote ", ret, "bytes"
reply = ser.readlines()
print reply

ret = ser.write('*00C\r')
print "wrote ", ret, "bytes"
for i in range(0, 32767):
	reply = ser.read(28)
	now = datetime.now()	
	#print reply	
	bx = round(float(int(reply[0:7].replace(',', ''))/15000.), 6)
	by = round(float(int(reply[9:16].replace(',', ''))/15000.), 6)
	bz = round(float(int(reply[18:25].replace(',', ''))/15000.), 6)
	btot = round(math.sqrt(bx**2 + by**2 + bz**2), 6)	
	print 3600*now.hour+60*now.minute+now.second+float(now.microsecond/1000000.), bx, by, bz, btot 
	f_out.write("%f\t%1.3f\t%1.3f\t%1.3f\t%1.3f\n" % (3600*now.hour+60*now.minute+now.second+float(now.microsecond/1000000.), bx, by, bz, btot))	
	#print int(reply[9:16].replace(',', ''))
	#print int(reply[18:25].replace(',', ''))

ret = ser.write('*00P\r')
f_out.close()
ser.close()

#with open("/home/chill/Desktop/magnetometer/mag_out.txt") as f_in:
#	t, B_X, B_Y, B_Z, B_TOT = loadtxt(f_in, skiprows=1, delimiter='\t', unpack=True)

#spec = np.fft.rfft(B_TOT)
#freq = np.fft.rfftfreq(B_TOT.size, d=(1.0/30.0))


#ax = plt.axes()
#ax.set_xlabel("Second of Day")
#ax.set_ylabel("B field [G]")
#ax.plot(t, B_X, 'b', label='B_X')
#ax.plot(t, B_Y, 'r', label='B_Y')
#ax.plot(t, B_Z, 'g', label='B_Z')
#ax.plot(t, B_TOT, 'k', label='B_TOT')
#ax.legend()
#print spec

#ax2 = plt.axes()
#ax2.plot(freq, abs(spec)) 
#ax2.semilogy(freq, abs(spec))

#plt.show()
#f_in.close()
