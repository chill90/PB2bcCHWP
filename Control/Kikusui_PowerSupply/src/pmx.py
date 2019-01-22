import serial
import sys
import time

#Class that handles serial communication with the Kikusui PMX power supply
class PMX:
    def __init__(self, port):
        name="/dev/ttyUSB%d" % (port)
        self.ser=serial.Serial(port=name, timeout=1, baudrate=19200)
        self.ser.write("*IDN?\n\r")
        time.sleep(.1)
        ID = self.ser.readline()
        print ID
        self.ser.write("SYST:REM\n\r") #Enable remote control
        time.sleep(.1)

    def __del__(self):
        self.clean_serial()
        self.ser.close()

    def clean_serial(self):
        self.ser.reset_input_buffer()
        self.ser.reset_output_buffer()
        self.ser.flush()
        return True

    #Check the voltage
    def checkVoltage(self):
        self.clean_serial()
        bts = self.ser.write("MEAS:VOLT?\n\r")
        time.sleep(.1)
        val = self.ser.readline()
        print "Measured Voltage = %f V\n" % (float(val))
        return val
    
    #Check the current
    def checkCurrent(self):
        self.clean_serial()
        self.ser.write("MEAS:CURR?\n\r")
        time.sleep(.1)
        val = self.ser.readline()
        print "Measured Current = %f A" % (float(val))
        return val

    #Check the voltage and current
    def checkVoltageCurrent(self):
        self.clean_serial()
        voltage = self.checkVoltage()
        current = self.checkCurrent()
        return voltage, current

    #Check output
    def checkOutput(self):
        self.clean_serial()
        self.ser.write("OUTP?\n\r")
        time.sleep(.1)
        val = self.ser.readline()
        if int(val) == 0:
            print "Measured output = OFF"
            return False
        elif int(val) == 1:
            print "Measured output = ON"
            return True
        else:
            print "Failed to measure output..."
            return None

    #Set the output voltage
    def setVoltage(self, val):
        self.clean_serial()
        self.ser.write("VOLT %f\n\r" % (float(val)))
        time.sleep(.1)
        self.ser.write("VOLT?\n\r")
        time.sleep(.1)
        val = self.ser.readline()
        print "Voltage Set = %f V" % (float(val))
        return True

    #Set the output current
    def setCurrent(self, val):
        self.clean_serial()
        self.ser.write("CURR %f\n\r" % (float(val)))
        time.sleep(.1)
        self.ser.write("CURR?\n\r")
        time.sleep(.1)
        val = self.ser.readline()
        print "Current Set = %f A\n" % (float(val))
        return True

    #Turn the output on
    def turnOn(self):
        self.clean_serial()
        self.ser.write("OUTP ON\n\r")
        time.sleep(.1)
        self.ser.write("OUTP?\n\r")
        time.sleep(.1)
        val = self.ser.readline()
        print "Output state = %s" % (val)
        return True

    #Turn the output off
    def turnOff(self):
        self.clean_serial()
        self.ser.write("OUTP OFF\n\r")
        time.sleep(.1)
        self.ser.write("OUTP?\n\r")
        time.sleep(.1)
        val = self.ser.readline()
        print "Output state = %s" % (val)
        return False
