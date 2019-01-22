import time
import serial

class NP_05B:
    #port = ttyUSB port name
    def __init__(self, port):
        name="/dev/ttyUSB%d" % (port)
        self.ser=serial.Serial(port=name, baudrate=9600, bytesize=8, parity='N', stopbits=1, timeout=1)
        self.numTries = 10

    def __del__(self):
        self.ser.close()

    def wait(self):
        time.sleep(0.2)
        return True

    def clean_serial(self):
        self.ser.reset_input_buffer()
        self.ser.reset_output_buffer()
        self.ser.flush()
        return

    def write(self, cmd):
        self.clean_serial()
        self.ser.write((cmd+'\r'))
        self.wait()

    def checkOut(self, cmd):
        out = self.ser.readlines()
        if len(out) == 0:
            return False
        elif '$A0' in out[-1]: #and cmd.replace(' ','') in out[-1].replace(' ',''):
            return True
        elif not len([s for s in out if 'Telnet active.' in s]) == 0:
            print 'Telnet active. Resetting... try command again.'
            self.deactivate_telnet()
            return False
        else:
            print "Cyberswitch Error:", out
            return False

    def command(self, cmd):
        numTries = 10
        for n in range(self.numTries):
            self.write(cmd)
            result = self.checkOut(cmd)
            if result:
                return True
            else:
                continue
        return False

    def ON(self, port):
        cmd = '$A3 %d 1' % (port)
        self.command(cmd)
        return self.checkOut(cmd)

    def OFF(self, port):
        cmd = '$A3 %d 0' % (port)
        self.command(cmd)
        return self.checkOut(cmd)

    def ALL_ON(self):
        cmd = '$A7 1'
        self.command(cmd)
        return self.checkout(cmd)

    def ALL_OFF(self):
        cmd = '$A7 0'
        self.command(cmd)
        return self.checkout(cmd)

    def REBOOT(self, port):
        cmd = '$A4 %d' % (port)
        self.command(cmd)
        return self.checkOut()

    def STATUS(self):
        cmd = '$A5'
        for n in range(self.numTries):
            self.write(cmd)
            out = self.ser.readlines()
            if len(out) == 0:
                continue
            elif cmd in out[-1]:
                return list(out[-1].lstrip(cmd).strip()[:-1])[::-1]
            else:
                print 'Cyberswitch error:', out
                continue
        return False

    def deactivate_telnet(self):
        print "Telnet session active! Trying to deactivate..."
        cmd = '!'
        self.write(cmd)
        out = self.ser.readlines()[0]
        if cmd in out:
            return True
        else:
            print 'Cyberswitch error:', out
            return False
