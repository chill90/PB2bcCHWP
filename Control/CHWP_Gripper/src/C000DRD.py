#Class for handling of the Click PLC
import serial
import pymodbus
from pymodbus.client.sync import ModbusSerialClient as ModbusClient


class C000DRD:
    def __init__(self, port=None):
        if port is None:
            port = '/dev/ttyUSB0'
	self.client = ModbusClient(method='rtu', port=port, baudrate=38400, timeout=0.1, parity=serial.PARITY_ODD)
	self.conn   = self.client.connect()

        #Private variables
        self.__count = 1 #Number of bytes to read -- defaults to 1
        self.__unit  = 1 #ID of the slave -- always 1 for the CHWP gripper
        
        #Click PLC Addresses as shown in the Windows software
        #Hardware configuration from right to left:
        #C0-00DR-D : C0-08TR : C0-16NE3
        
        #Unit 00 = C0-00DR-D
        #Read only -- not controllable by user
        self.X001 = 100001
        self.X002 = 100002
        self.X003 = 100003
        self.X004 = 100004
        self.X005 = 100005
        self.X006 = 100006
        self.X007 = 100007
        self.X008 = 100008
        #Read/write -- controllable by user
        self.Y001 =   8192
        self.Y002 =   8193
        self.Y003 =   8194
        self.Y004 =   8195
        self.Y005 =   8196
        self.Y006 =   8197
        
        #Unit 10 = C0-08TR
        #Read/write -- controllable by user
        self.Y101 =   8224
        self.Y102 =   8225
        self.Y103 =   8226
        self.Y104 =   8227
        self.Y105 =   8228
        self.Y106 =   8229
        self.Y107 =   8230
        self.Y108 =   8231
        
        #Unit 20 = C0-16NE3
        #Read only -- not controllable by user
        self.X201 = 100065
        self.X202 = 100066
        self.X203 = 100067
        self.X204 = 100068
        self.X205 = 100069
        self.X206 = 100070
        self.X207 = 100071
        self.X208 = 100072
        self.X209 = 100073
        self.X210 = 100074
        self.X211 = 100075
        self.X212 = 100076
        self.X213 = 100077
        self.X214 = 100078
        self.X215 = 100079
        self.X216 = 100080
        
    # ***** Public Methods *****
    def read_pin(self, addr):
        #return self.client.read_coils(self.__addr(addr), self.__count, unit=self.__unit).bits[0]
        return self.client.read_discrete_inputs(self.__addr(addr), self.__count, unit=self.__unit).bits[0]
    def set_pin_on(self, addr):
        return self.client.write_coils(self.__addr(addr), [True], unit=self.__unit)
        #return self.client.write_coils(addr, True)
    def set_pin_off(self, addr):
        return self.client.write_coils(self.__addr(addr), [False], unit=self.__unit)
        #return self.client.write_coils(addr, False)
    def toggle_pin(self, addr):
        return self.client.write_coils(self.__addr(addr), [not read_pin(addr)], unit=self.__unit)
        #return self.client.write_coils(addr, not read_pin(addr))

    # ***** Private Methods *****
    # Function that converts the provided address to the Modbus address
    def __addr(self, addr):
        if addr > 65535:
            return addr - 100000 - 1
        else:
            return addr
