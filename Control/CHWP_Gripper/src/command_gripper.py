#Python 2 compatibility
from __future__ import print_function

#Standard modules
import sys as sy

#Custom modules
import C000DRD    as c0
import JXC831     as jx
import controller as ct
import gripper    as gp
import log_gripper as lg


class Command:
    def __init__(self, GPR=None):
        if GPR is None:
            raise Exception("Command error: No gripper object passed to Command() constructor")
        else:
            self.GPR = GPR
        #Create logging object
        self.log = lg.Logging()

    def CMD(self, user_input):
        args = user_input.split(' ')
        cmd = args[0].upper()
        if cmd == 'HELP':
            self._help()
            return True
        elif cmd == 'ON':
            self.GPR.ON()
            return True
        elif cmd == 'OFF':
            self.GPR.OFF()
            return True
        elif cmd == 'BRAKE':
            ON = None
            if not (len(args) == 2 or len(args) == 3):
                self.log("\nFATAL: Could not understand 'BRAKE' arguments: %s" % (' '.join(args[1:])))
                self.log("Usage: BRAKE ON/OFF [axis number (1-3)]\n")
                return False
            if args[1].upper() == 'ON':
                ON = True
            elif args[1].upper() == 'OFF':
                ON = False
            else:
                self.log("\nFATAL: Could not understand 'BRAKE' argument: %s" % (args[1]))
                self.log("Usage: BRAKE ON/OFF [axis number (1-3)]\n")
                return False
            if len(args) == 3:
                try:
                    axis = int(args[2])
                except ValueError:
                    self.log("\nFATAL: Could not understand 'BRAKE' argument: %s" % (args[2]))
                    self.log("Usage: BRAKE ON/OFF [axis number (1-3)]\n")
                    return False
            if axis < 1 or axis > 3:
                self.log("\nFATAL: Could not understand 'BRAKE' argument: %s" % (args[2]))
                self.log("Usage: BRAKE ON/OFF [axis number (1-3)]\n")
                return False
            else:
                if ON:
                    self.GPR.CTL.BRAKE(state=True, axis=axis)
                elif not ON:
                    self.GPR.CTL.BRAKE(state=False,  axis=axis)
        elif cmd == 'MOVE':
            if not len(args) == 4:
                self.log("Command error: Could not understand 'MOVE' argument: %s" % (' '.join(args[1:])))
                return False
            else:
                mode = str(args[1]).upper()
                if not (mode == 'PUSH' or mode == 'POS'):
                    self.log("Command error: Could not understand move mode '%s'. Must be either 'PUSH' or 'POS'" % (mode))
                    return False
                try:
                    axis = int(args[2])
                except ValueError:
                    self.log("Command error: Could not understand axis number = '%s'. Must be an integer (1-3)." % (str(axis)))
                    return False
                if axis == 1 or axis == 2 or axis == 3:
                    try:
                        dist = float(args[3])
                        self.GPR.ON()
                        result = self.GPR.MOVE(mode, dist, axis)
                        #self.GPR.OFF()
                        return result
                    except ValueError:
                        self.log("Command error: Could not understand relative move distance '%s'. Must be a float." % (str(dist)))
                        return False
                else:
                    self.log("Command error: Could not understand axis number '%d'. Must be an integer (1-3)." % (axis))
                    return False
        elif cmd == 'HOME':
            self.GPR.ON()
            result = self.GPR.HOME()
            self.GPR.OFF()
            return result
        elif cmd == 'INP':
            return self.GPR.INP()
        elif cmd == 'ALARM':
            return self.GPR.ALARM()
        elif cmd == 'RESET':
            return self.GPR.RESET()
        elif cmd == 'POSITION':
            return self.GPR.POSITION()
        elif cmd == 'SETPOS':
            return self.GPR.SETPOS()
        elif cmd == 'STATUS':
            return self.GPR.STATUS()
        elif cmd == 'EXIT':
            self.GPR.OFF()
            sy.exit(0)
        else:
            self.log("Could not understand command '%s'. Type 'HELP' for a list of commands.")
            return False

    #***** Private Functions*****
    def _help(self):
        print()
        print("*** Gripper Control: Command Menu ***")
        print("HELP = help menu (you're here right now)")
        print("ON = turn grippers (SVON) on")
        print("OFF = turn grippers (SVON) off")
        print("BRAKE ON  [axis number (1-3)] = Engage brake on given axis. If axis not provided, engage brake on all axes.")
        print("BRAKE OFF [axis number (1-3)] = Release brake on given axis. If axis not provided, release brake on all axes.")
        print("MOVE [mode 'PUSH' or 'POS'] [axis number (1-3)] [distance (mm)] = move axis a given distance. Minimum step size = 0.1 mm")
        print("HOME = home all axes, resetting their positions to 0.0 mm")
        print("INP = in position (positioning operation) or pushing (pushing operation) flag")
        print("ALARM = display alarm state")
        print("RESET = reset alarm")
        print("POSITION = display actuator positions")
        print("SETPOS [axis number (1-3)] [distance (mm)] = manually set motor position without moving")
        print("STATUS = display status of all JXC controller bits")
        print("EXIT = exit this program")
        print()
        return
