import time
import serial
import sys
import config.config as config

class DMM_2700:
    def __init__(self):
        port = config.keithlyPort
        name="/dev/ttyUSB%d" % (port)
        self.ser=serial.Serial(port=name, timeout=0.1)
        self.clean_serial()
        self.ser.write("*IDN?\n\r")
        time.sleep(.1)
        ID = self.ser.readline()
        #Enable continuous measurement
        self.clean_serial()
        self.ser.write("INIT:CONT ON\n\r")
        #Disable the beeper
        self.ser.write("SYST:BEEP:STAT OFF\n\r")

    def __del__(self):
        self.ser.close()

    def clean_serial(self):
        self.ser.reset_input_buffer()
        self.ser.reset_output_buffer()
        self.ser.flush()
        return

    def get_frequency(self):
        self.clean_serial()
        self.ser.write("ROUT:OPEN (@101)\n\r")
        self.ser.write("FUNC 'FREQ'\n\r")
        self.ser.write("ROUT:CLOS (@101)\n\r")
        self.ser.write("DATA?\n\r")
        time.sleep(.1)
        f = self.ser.readline().split(',')[0][2:].rstrip('HZ')
        return f

    def get_voltage(self):
        self.clean_serial()
        self.ser.write("ROUT:OPEN (@101)\n\r")
        self.ser.write("FUNC 'VOLT'\n\r")
        self.ser.write("ROUT:CLOS (@101)\n\r")
        self.ser.write("DATA?\n\r")
        time.sleep(.1)
        v = self.ser.readline().split(',')[0][2:].rstrip('VDC')
        return v

    def get_pressure(self):
        v = self.get_voltage()
        #Convert voltage to pressure
        p = 10**(float(v)-6.)
        return p
