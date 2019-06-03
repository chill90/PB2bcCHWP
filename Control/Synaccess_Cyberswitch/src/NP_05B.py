import time
from serial import Serial

from moxaSerial import Serial_TCPServer


class NP_05B:
    #port = ttyUSB port name
    def __init__(self, rtu_port=None, tcp_ip=None, tcp_port=None):
        #Connect to device
        self.__conn(rtu_port, tcp_ip, tcp_port)

        self.numTries = 10
        self.bytesToRead = 20

    def __del__(self):
        if not self.use_tcp:
            self.ser.close()
        else:
            pass
        return

    def wait(self):
        time.sleep(0.2)
        return True

    def clean_serial(self):
        if not self.use_tcp:
            self.ser.reset_input_buffer()
            self.ser.reset_output_buffer()
            self.ser.flush()
        else:
            self.ser.flushInput()
        return

    def write(self, cmd):
        self.clean_serial()
        self.ser.write((cmd+'\r'))
        self.wait()

    def read(self):
        if not self.use_tcp:
            return self.ser.readlines()
        else:
            out = self.ser.read(self.bytesToRead).replace('\r', ' ').replace('\x00', '')
            return out

    def checkOut(self, cmd):
        out = self.read()
        if len(out) == 0:
            return False
        elif cmd.split()[0] in out.split()[0] and '$A0' in out:
            return True
        #elif '$A0' in out[-1]: #and cmd.replace(' ','') in out[-1].replace(' ',''):
        #    return True
        elif not len([s for s in out if 'Telnet active.' in s]) == 0:
            print 'Telnet active. Resetting... try command again.'
            self.deactivate_telnet()
            return False
        else:
            print "Cyberswitch Error 1:", out
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
        return self.checkOut(cmd)

    def ALL_OFF(self):
        cmd = '$A7 0'
        self.command(cmd)
        return self.checkOut(cmd)

    def REBOOT(self, port):
        cmd = '$A4 %d' % (port)
        self.command(cmd)
        return self.checkOut()

    def STATUS(self):
        cmd = '$A5'
        for n in range(self.numTries):
            self.write(cmd)
            out = self.read()
            if len(out) == 0:
                continue
            elif cmd in out:
                return list(out.lstrip(cmd).strip()[:-1])[::-1]
                #return list(out[-1].lstrip(cmd).strip()[:-1])[::-1]
            else:
                print 'Cyberswitch error 1:', out
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
            print 'Cyberswitch error 3:', out
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
