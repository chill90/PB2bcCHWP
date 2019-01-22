import time
import serial

class SIM_900:
    def __init__(self, port, slot):
        self.port  = port
        self.slots = slot
        name="/dev/ttyUSB%d" % (self.port)
        print "SIM 900 USB Port ID:", name
        self.ser=serial.Serial(port=name, timeout=2)

        self.clean_serial()
        self.ser.write("*IDN?\n\r")
        time.sleep(.1)
        ID = self.ser.readline()
        print "SIM 900 Serial ID:", ID
        self.clean_serial()

    def __del__(self):
        self.ser.write('xyz\n\r')
        self.ser.close()

    def clean_serial(self):
        self.ser.reset_input_buffer()
        self.ser.reset_output_buffer()
        self.ser.flush()
        return

    def get_temps(self):
        ret = []
        for slot in self.slots:
            #Keep trying until you got it
            while True:
                self.clean_serial()
                self.ser.write('CONN %d, "xyz"\n\r' % (slot))
                time.sleep(.1)
                
                self.ser.write("TVAL? 0\n\r") #Read all channels
                time.sleep(.1)
                val = self.ser.readlines()
                temps = ''.join(val).strip('\n\r').split(',')
                if not temps[0] == '':
                    ret = ret + temps
                    break
                else:
                    continue
        return ret
