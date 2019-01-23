#Interactive program for controlling the CHWP gripper
import sys           as sy
import readline
import src.C000DRD   as c0
import src.JXC831    as jx
import src.control   as ct
import src.gripper   as gp
import config.config as cfg

def HELP():
    print ()
    print ("*** Gripper Control: Command Menu ***")
    print ("HELP = help menu (you're here right now)")
    print ("ON = turn grippers (SVON) on")
    print ("OFF = turn grippers (SVON) off")
    print ("BRAKE ON  [axis number (1-3)] = Engage brake on given axis. If axis not provided, engage brake on all axes.")
    print ("BRAKE OFF [axis number (1-3)] = Release brake on given axis. If axis not provided, release brake on all axes.")
    print ("MOVE [axis number (1-3)] [distance (mm)] = move axis a given distance. Minimum step size = 0.1 mm")
    print ("HOME = home all axes, resetting their positions to 0.0 mm")
    print ("ALARM = display alarm state")
    print ("RESET = reset alarm")
    print ("POSITION = display actuator positions")
    print ("SETPOS [axis number (1-3)] [distance (mm)] = manually set motor position without moving")
    print ("STATUS = display status of all JXC controller bits")
    print ("EXIT = exit this program")
    print ()
    return

def CMD(GPR, inp):
    args = inp.split(' ')
    cmd = args[0]
    if cmd.upper() == 'HELP':
        HELP()
        return True
    elif cmd.upper() == 'ON':
        GPR.ON()
        return True
    elif cmd.upper() == 'OFF':
        GPR.OFF()
        return True
    elif cmd.upper() == 'BRAKE':
        ON = None
        if not (len(args) == 2 or len(args) == 3):
            print ("\nFATAL: Could not understand 'BRAKE' arguments: %s" % (' '.join(args[1:])))
            print ("Usage: BRAKE ON/OFF [axis number (1-3)]\n")
            return False
        if args[1].upper() == 'ON':
            ON = True
        elif args[1].upper() == 'OFF':
            ON = False
        else:
            print ("\nFATAL: Could not understand 'BRAKE' argument: %s" % (args[1]))
            print ("Usage: BRAKE ON/OFF [axis number (1-3)]\n") 
            return False
        if len(args) == 3:
            try:
                axis = int(args[2])
            except ValueError:
                print ("\nFATAL: Could not understand 'BRAKE' argument: %s" % (args[2]))
                print ("Usage: BRAKE ON/OFF [axis number (1-3)]\n")
                return False
            if axis < 1 or axis > 3:
                print ("\nFATAL: Could not understand 'BRAKE' argument: %s" % (args[2]))
                print ("Usage: BRAKE ON/OFF [axis number (1-3)]\n")
                return False
            else:
                if ON:
                    GPR.CTL.BRAKE(state=True, axis=axis)
                elif not ON:
                    GPR.CTL.BRAKE(state=False,  axis=axis)
        else:
            if ON:
                GPR.CTL.BRAKE(state=True)
            else:
                GPR.CTL.BRAKE(state=False)
    elif cmd.upper() == 'MOVE':
        if not len(args) == 3:
            print
            print "FATAL: Could not understand 'MOVE' argument: %s" % (' '.join(args[1:]))
            print "Usage: MOVE [axis number (1-3)] [distance (mm)]"
            print
            return False
        else:
            try:
                axis = int(args[1])
            except ValueError:
                print "FATAL: Could not understand axis number = '%s'. Must be an integer (1-3)." % (str(axis))
                return False
            if int(args[1]) == 1 or int(args[1]) == 2 or int(args[1]) == 3:
                try:
                    dist = float(args[2])
                    GPR.ON()
                    result = GPR.MOVE(axis, dist)
                    GPR.OFF()
                    return result
                except ValueError:
                    print "FATAL: Could not understand relative move distance '%s'. Must be a float." % (str(dist))
                    return False
            else:
                print "FATAL: Could not understand axis number '%d'. Must be an integer (1-3)." % (axis)
                return False
    elif cmd.upper() == 'HOME':
        GPR.ON()
        result = GPR.HOME()
        GPR.OFF()
        return result
    elif cmd.upper() == 'ALARM':
        return GPR.ALARM()
    elif cmd.upper() == 'RESET':
        return GPR.RESET()
    elif cmd.upper() == 'POSITION':
        return GPR.POSITION()
    elif cmd.upper() == 'SETPOS':
        return GPR.SETPOS()
    elif cmd.upper() == 'STATUS':
        return GPR.STATUS()
    elif cmd.upper() == 'EXIT':
        GPR.OFF()
        sy.exit(0)
    else:
        print
        print "Could not understand command '%s'. Type 'HELP' for a list of commands."
        return False

# ***** MAIN PROGRAM *****
if __name__ == "__main__":
    #Establish connection to gripper
    port = cfg.ttyUSBPort
    PLC = c0.C000DRD(port)
    JXC = jx.JXC831(PLC)
    CTL = ct.Control(JXC)
    GPR = gp.Gripper(CTL)
    #Command passed from the command line?
    if len(sy.argv) > 1:
        inp = ' '.join(sy.argv[1:])
        CMD(GPR, inp)        
    else: #Prompt user for command at command line
        while True:
            try:
                inp = raw_input("Gripper command ('HELP' for help): ")
                CMD(GPR, inp)
            except KeyboardInterrupt:
                GPR.OFF()
                sy.exit('\nExiting gripper_control\n')
