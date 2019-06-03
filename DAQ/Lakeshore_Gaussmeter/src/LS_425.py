import time
from serial import Serial
from moxaSerial import Serial_TCPServer

class LS_425:
    #port = ttyUSB port name
    #mode = measurement mode: 1 = DC, 2 = RMS
    #filter = DC filter: 0 = Off, 1 = On
    #bandwidth = for RMS mode only: 0 = wideband, 1 = narrowband
    #units = measurement units: 1 = Gauss, 2 = Tesla, 3 = Oersted, 4 = Ampere/Meter
    def __init__(self, rtu_port=None, tcp_ip=None, tcp_port=None, mode=1, filt=1, band=1, units=1, term=''):
        #Connect to the device
        self.__conn(rtu_port, tcp_ip, tcp_port)
        #name="/dev/ttyUSB%d" % (port)
        #self.ser=serial.Serial(port=name, timeout=0.1, baudrate=57600, parity=serial.PARITY_ODD)
        self.term = term

        #Read Gaussmeter ID
        self.clean_serial()
        self.ser.write("*IDN?\n\r")
        self.wait()
        ID = self.ser.readline()

        #Set the readout mode
        self.ser.write('RDGMODE %d,%d,%d%s\n\r' % (mode, filt, band, self.term))
        #Set the units
        self.ser.write('UNIT %d%s\n\r' % (units, self.term))

    def __del__(self):
        self.ser.write('xyz\n\r')
        if not self.use_tcp:
            self.ser.close()
        else:
            pass
        return

    def wait(self):
        time.sleep(0.5)
        return

    def clean_serial(self):
        if not self.use_tcp:
            self.ser.reset_input_buffer()
            self.ser.reset_output_buffer()
            self.ser.flush()
        else:
            self.ser.flushInput()
        return

    def get_bfield(self):
        tries = 0
        maxTries = 10
        while tries < maxTries:
            try:
                self.clean_serial()
                self.ser.write("RDGFIELD?%s\n\r" % (self.term))
                self.wait()
                val = self.ser.readlines()
                #Format of outputted value
                return float(repr(val[0]).translate(None,r'\\x').translate(None, 'b').strip("'").rstrip('r8a').replace('ae', '.').replace('ad', '-').replace('a', '+'))
                break
            except:
                tries += 1
                continue
        return 0

        #Private methods
    #Connect to the device using either the MOXA box or a USB-to-serial converter
    def __conn(self, rtu_port=None, tcp_ip=None, tcp_port=None):
        if rtu_port is None and (tcp_ip is None or tcp_port is None):
            raise Exception('LS_425 Exception: no RTU or TCP port specified')
        elif rtu_port is not None and (tcp_ip is not None or tcp_port is not None):
            raise Exception('LS_425 Exception: RTU and TCP port specified. Can only have one or the other.')
        elif rtu_port is not None:
            self.ser = Serial(port=rtu_port, baudrate=9600, bytesize=8, parity='N', stopbits=1, timeout=1)
            self.use_tcp = False
        elif tcp_ip is not None and tcp_port is not None:
            self.ser = Serial_TCPServer((tcp_ip, tcp_port))
            self.use_tcp = True
