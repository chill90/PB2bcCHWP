import sys     as sy
import src.pmx as px

class Command:
    def __init__(self, pmx=None):
        #PMX connection
        if not pmx is None:
            self.pmx = pmx
        else:
            raise Exception("PMX object not passed to Command constructor\n")
        
        #List of commands
        self.setPrt  = 'P'
        self.checkV  = 'V?'
        self.checkC  = 'C?'
        self.checkVC = 'VC?'
        self.checkO  = 'O?'
        self.setV    = 'V'
        self.setC    = 'C'
        self.setOn   = 'ON'
        self.setOff  = 'OFF'
        self.gHelp   = 'H'
        self.stop    = 'Q'

        #Print the list of commands
        #self.getHelp()

    #Prints possible commands
    def getHelp(self):
        print
        print "Change ttyUSB port = '%s'" % (self.setPrt)
        print "Check output Voltage = '%s'" % (self.checkV)
        print "Check output Current = '%s'" % (self.checkC)
        print "Check output Voltage and Current = '%s'" % (self.checkVC)
        print "Check if output is on or off = '%s'" % (self.checkO)
        print "Set output voltage = '%s' [setting]" % (self.setV)
        print "Set output current = '%s' [setting]" % (self.setC)
        print "Turn output on = '%s'"  % (self.setOn )
        print "Turn output off = '%s'" % (self.setOff)
        print "Print possible commands = '%s'" % (self.gHelp)
        print "Quit program = '%s'" % (self.stop)
        print
        return True

    #Take user input and figure out what to do with it
    def userInput(self, val):
        #Parse the input command
        argv = val.split(' ')
        while len(argv):
            cmd = str(argv[0])
            if cmd.lower() == '':
                return
            elif cmd.lower() == self.checkV.lower():
                self.pmx.checkVoltage(); argv.pop(0)
            elif cmd.lower() == self.checkC.lower():
                self.pmx.checkCurrent(); argv.pop(0)
            elif cmd.lower() == self.checkVC.lower():
                self.pmx.checkVoltageCurrent(); argv.pop(0)
            elif cmd.lower() == self.checkO.lower():
                self.pmx.checkOutput(); argv.pop(0)
            elif cmd.lower() == self.setOn.lower():
                self.pmx.turnOn(); argv.pop(0)
            elif cmd.lower() == self.setOff.lower():
                self.pmx.turnOff(); argv.pop(0)
            elif cmd.lower() == self.gHelp.lower():
                self.getHelp(); argv.pop(0)
            elif cmd.lower() == self.stop.lower():
                sy.exit("Exiting...")
            elif cmd.lower() == self.setPrt.lower():
                try:
                    setVal = float(argv[1])
                except ValueError:
                    print "Command '%s' not understood..." % (cmd)
                    return
                del self.pmx
                self.pmx = px.PMX(setVal); argv.pop(0); argv.pop(0)
            elif cmd.lower() == self.setV.lower():
                try:
                    setVal = float(argv[1])
                except ValueError:
                    print "Command '%s' not understood..." % (cmd)
                    return
                self.pmx.setVoltage(setVal); argv.pop(0); argv.pop(0)
            elif cmd.lower() == self.setC.lower():
                try:
                    setVal = float(argv[1])
                except ValueError:
                    print "Command '%s' not understood..." % (cmd)
                    return
                self.pmx.setCurrent(setVal); argv.pop(0); argv.pop(0)
            else:
                print "Command '%s' not understood..." % (cmd)
        return True
