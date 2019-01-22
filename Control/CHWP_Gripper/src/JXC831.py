#Class to interface to the SMC actuator controller

class JXC831:
    def __init__(self, PLC=None):
        if PLC is None:
            raise Exception('FATAL: SMC controller requires a PLC interface')
        self.PLC = PLC

        #Assign SMC controller pins to PLC pins. Also listed are the I/O cable wire colors for the connections
        #Read/write -- controllable by the user
        self.IN0    = self.PLC.Y001 
        self.IN1    = self.PLC.Y002 
        self.IN2    = self.PLC.Y003 
        self.IN3    = self.PLC.Y004 
        self.IN4    = self.PLC.Y005 

        self.SETUP  = self.PLC.Y006 
        self.HOLD   = self.PLC.Y101 
        self.DRIVE  = self.PLC.Y102 
        self.RESET  = self.PLC.Y103
        self.SVON   = self.PLC.Y104

        self.BRAKE1 = self.PLC.Y105
        self.BRAKE2 = self.PLC.Y106
        self.BRAKE3 = self.PLC.Y107

        #Read only -- not controllable by the user
        self.OUT0   = self.PLC.X001
        self.OUT1   = self.PLC.X002
        self.OUT2   = self.PLC.X003
        self.OUT3   = self.PLC.X004
        self.OUT4   = self.PLC.X005

        self.BUSY   = self.PLC.X006
        self.AREA   = self.PLC.X007
        self.SETON  = self.PLC.X008

        self.INP    = self.PLC.X201
        self.SVRE   = self.PLC.X202
        self.ESTOP  = self.PLC.X203
        self.ALARM  = self.PLC.X204

        self.BUSY1  = self.PLC.X205
        self.BUSY2  = self.PLC.X206
        self.BUSY3  = self.PLC.X207
        
        self.AREA1  = self.PLC.X208
        self.AREA2  = self.PLC.X209
        self.AREA3  = self.PLC.X210
        
        self.INP1   = self.PLC.X211
        self.INP2   = self.PLC.X212
        self.INP3   = self.PLC.X213

        self.ALARM1 = self.PLC.X214
        self.ALARM2 = self.PLC.X215
        self.ALARM3 = self.PLC.X216
        
    # ***** Public Methods *****
    def read(self, addr):
        #try:
        return self.PLC.read_pin(addr)
        #except:
        #    raise Exception('JXC831 Error: Cannot read pin at address', addr)
    def set_on(self, addr):
        try:
            return self.PLC.set_pin_on(addr)
        except:
            return Exception('JXC831 Error: Cannot write to pin at address', addr)
    def set_off(self, addr):
        try:
            return self.PLC.set_pin_off(addr)
        except:
            return Exception('JXC831 Error: Cannot write to pin at address', addr)
    def toggle(self, addr):
        try:
            return self.PLC.toggle_pin(addr)
        except:
            return Exception('JXC831 Error: Cannot read/write to pin at address', addr)
    
