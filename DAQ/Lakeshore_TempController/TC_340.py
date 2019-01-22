import time
import serial
import config

class TC_340:
    def __init__(self):
        port = config.LakeshorePort
        name="/dev/ttyUSB%d" % (port)
        self.ser=serial.Serial(port=name, timeout=2)
        self.clean_serial()
        self.ser.write("*IDN?\n\r")
        time.sleep(.1)
        ID = self.ser.readline()

    def __del__(self):
        self.ser.close()

    def clean_serial(self):
        self.ser.reset_input_buffer()
        self.ser.reset_output_buffer()
        self.ser.flush()
        return

    def get_temps(self):
        therms= ['A', 'B', 'C', 'D']
        temps = []
        for r in therms:
            self.clean_serial()
            self.ser.write(('KRDG? %s' % (r))+'\n\r')
            time.sleep(1)
            t = (self.ser.readlines())[0]
            t = t[t.find("['+")+1:t.find("']")]
            temps.append(float(t.rstrip('\r')))
        return temps
