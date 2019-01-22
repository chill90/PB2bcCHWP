#A script to calibrate the SIM922 Diode Temperature Module in the SIM900 Mainframe by communicating via serial.
#Written by Samantha Rose Gilbert with assistance from Dr. Mayuri Rao
#October, 2017

import numpy as np
from scipy import loadtxt, optimize
import csv, sys
import serial 
import time
import matplotlib.pyplot as plt

#Clean the serial connection
def clean(ser):
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        ser.flush()

#Which diode is being calibrated for
diode = "DT670_0919"

#Which channels and slots to calibrate
slots = [3]
channels = [1,2,3,4] #0 for all channels

#Calibration file
args = sys.argv[1:]
if not len(args) == 1:
        sys.exit("\nUsage: sudo python SIM922calibrate.py [calibration file]\n")
else:
        fname = args[0]

port="/dev/ttyUSB3" #Connect to the USB port on the computer where you have plugged in the mainframe (serial>USB).
ser=serial.Serial(port=port,timeout=2,baudrate=9600) #Set up the serial connection.

#clean(ser)
#ser.write("*IDN?\n\r") #Ping the module to ensure you are connected.
#reply=ser.readlines() #Request a reply from the mainframe: should be "Stanford Research Systems SIM 922. . ."
#if reply == []:
#	print "Not connected to SIM900 mainframe"
#	ser.write('xyz\n\r') #Nonsense escape string.
#        ser.close()
#        sys.exit()

#Load the calibration data
#Data must be loaded in order of increasing voltage
v2,t2 = loadtxt(fname, unpack=True) 
								   
if __name__ == "__main__":
        try:
                for slot in slots:
                        clean(ser)
	                ser.write('CONN %d, "xyz"\n\r' % (slot)) 
                        time.sleep(0.5)
                        for channel in channels:
                                #Initialize calibration
                                clean(ser)
		                ser.write("CINI %d,0,%s\n\r" % (channel, diode))
                                time.sleep(0.5)

                                #This loop will go through each row of calibration data (V, T) and upload it to channel you chose above.
		                for i in range(np.size(v2)):
                                        clean(ser)
                                        print "Writing data point %d: %f, %f" % (i, v2[i], t2[i])
			                ser.write('CAPT %d,%f,%f\n\r' % (channel, v2[i], t2[i])) #Upload calibration points to channel 4, x=Voltage v, y = Temperature t.
			                time.sleep(0.1)

                                clean(ser)
		                ser.write("CURV %d,1\n\r" % (channel))
                                time.sleep(0.5)
                                
                                #curvQuery = "CURV? %d\n\r" % (channel) 
                                #clean(ser)
                                #ser.write(curvQuery)
                                #print "Reply to 'CURV? %d': " % (channel),
                                #print ser.readlines()
                                #print

			
	        ser.write('xyz\n\r') #Nonsense escape string.
                ser.close()
        except KeyboardInterrupt:
		ser.write('xyz\n\r') #Nonsense escape string.
                ser.close()
