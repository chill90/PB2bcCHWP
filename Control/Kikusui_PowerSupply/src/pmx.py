import time
from serial import Serial

from moxaSerial import Serial_TCPServer


#Class that handles serial communication with the Kikusui PMX power supply
class PMX:
    def __init__(self, rtu_port=None, tcp_ip=None, tcp_port=None):
    #def __init__(self, port):
        #Connect to device
        self.__conn(rtu_port, tcp_ip, tcp_port)

        #name="/dev/ttyUSB%d" % (port)
        #self.ser=serial.Serial(port=name, timeout=1, baudrate=19200)
        #self.ser.write("*IDN?\n\r")
        #time.sleep(.1)
        #ID = self.ser.readline()
        #print ID
        self.remoteMode()
        #time.sleep(.1)

    def __del__(self):
        if not self.use_tcp:
            self.ser.close()
        else:
            pass
        return
        #self.clean_serial()
        #self.ser.close()

    def wait(self):
        time.sleep(0.1)
        return True

    def clean_serial(self):
        if not self.use_tcp:
            self.ser.reset_input_buffer()
            self.ser.reset_output_buffer()
            self.ser.flush()
        else:
            self.ser.flushInput()
        return True

    #Enable remote communication
    def remoteMode(self):
        self.clean_serial()
        self.ser.write("SYST:REM\n\r") #Enable remote control
        self.wait()
        return True

    #Check the voltage
    def checkVoltage(self):
        self.clean_serial()
        bts = self.ser.write("MEAS:VOLT?\n\r")
        self.wait()
        val = self.ser.readline()
        print "Measured Voltage = %f V\n" % (float(val))
        return val
    
    #Check the current
    def checkCurrent(self):
        self.clean_serial()
        self.ser.write("MEAS:CURR?\n\r")
        self.wait()
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
        self.wait()
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
        self.wait()
        self.ser.write("VOLT?\n\r")
        self.wait()
        val = self.ser.readline()
        print "Voltage Set = %f V" % (float(val))
        return True

    #Set the output current
    def setCurrent(self, val):
        self.clean_serial()
        self.ser.write("CURR %f\n\r" % (float(val)))
        self.wait()
        self.ser.write("CURR?\n\r")
        self.wait()
        val = self.ser.readline()
        print "Current Set = %f A\n" % (float(val))
        return True

    #Turn the output on
    def turnOn(self):
        self.clean_serial()
        self.ser.write("OUTP ON\n\r")
        self.wait()
        self.ser.write("OUTP?\n\r")
        self.wait()
        val = self.ser.readline()
        print "Output state = %s" % (val)
        return True

    #Turn the output off
    def turnOff(self):
        self.clean_serial()
        self.ser.write("OUTP OFF\n\r")
        self.wait()
        self.ser.write("OUTP?\n\r")
        self.wait()
        val = self.ser.readline()
        print "Output state = %s" % (val)
        return False

    #Private methods
    #Connect to the device using either the MOXA box or a USB-to-serial converter
    def __conn(self, rtu_port=None, tcp_ip=None, tcp_port=None):
        if rtu_port is None and (tcp_ip is None or tcp_port is None):
            raise Exception('NP_05B Exception: no RTU or TCP port specified')
        elif rtu_port is not None and (tcp_ip is not None or tcp_port is not None):
            raise Exception('NP_05B Exception: RTU and TCP port specified. Can only have one or the other.')
        elif rtu_port is not None:
            self.ser = Serial(port=rtu_port, baudrate=9600, bytesize=8, parity='N', stopbits=1, timeout=1)
            self.use_tcp = False
        elif tcp_ip is not None and tcp_port is not None:
            self.ser = Serial_TCPServer((tcp_ip, tcp_port))
            self.use_tcp = True
