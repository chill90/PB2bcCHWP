import config.config as cg
import src.NP_05B    as np
import sys           as sy
import readline

def HELP():
    print
    print 'Available commands to the NP-05B Cyberswitch:'
    print 'ON [port]:  turn on port [port], for which the options are 1-5'
    print 'OFF [port]: turn off port [port], for which the options are 1-5'
    print 'ALL ON:  turn on all ports'
    print 'ALL OFF: turn off all ports'
    print 'REBOOT [port]: reboot port [port], for which the options are 1-5'
    print 'STATUS: print status of each port'
    print 'HELP: display this help menu'
    print 'EXIT: quit program'
    print

def CMD(cmd, NP05B):
    args = cmd.split()
    cmdarg = args[0].upper()
    if cmdarg == 'ON' or cmdarg == 'OFF' or cmdarg == 'REBOOT':
        if len(args) == 2 and args[1].isdigit():
            port = int(args[1])
            if port <=5 and port >= 1:
                if cmdarg == 'ON':
                    NP05B.ON(port)
                elif cmdarg == 'OFF':
                    NP05B.OFF(port)
                elif cmdarg == 'REBOOT':
                    NP05B.REBOOT(port)
                else:
                    print 'CYBERSWITCH CONTROL ERROR: parsing error for command %s' % (' '.join(args))
                    return False
            else:
                print 'CYBERSWITCH CONTROL ERROR: provided port %d not in allowed range 1-5'
                return False
        else:
            print 'CYBERSWITCH CONTROL ERROR: Could not understand command %s' % (cmd)
            return False
    elif cmdarg == 'ALL':
        if args[1].upper() == 'ON':
            NP05B.ALL_ON()
        elif args[1].upper() == 'OFF':
            NP05B.ALL_OFF()
        else:
            print 'CYBERSWITCH CONTROL ERROR: Could not understand command %s' % (cmd)
            return False
    elif cmdarg == 'STATUS':
        outputs = NP05B.STATUS()
        print
        print 'Port power status:'
        for i in range(len(outputs)):
            print 'Port %d = %s' % (i+1, bool(int(outputs[i])))
        print
    elif cmdarg == 'HELP':
        HELP()
    elif cmdarg == 'EXIT':
        sy.exit(0)
    else:
        print 'CYBERSWITCH CONTROL ERROR: Could not understand command %s' % (cmd)
        return False
    return True
        
if __name__ == "__main__":
    if cg.use_moxa:
        NP05B = np.NP_05B(tcp_ip=cg.moxa_ip, tcp_port=cg.moxa_port)
    else:
        NP05B = np.NP_05B(rtu_port=cg.ttyUSBPort)

    #If user supplies a command-line argument, interpret it as a command to the cyberswitch
    if len(sy.argv[1:]) > 0:
        args = sy.argv[1:]
        command = ' '.join(args)
        result = CMD(command, NP05B)
    else:
        #Otherwise, ask the user for a command
        while True:
            command = raw_input('Cyberswitch command [HELP for help]: ')
            result = CMD(command, NP05B)
            if result:
                print 'Command executed successfully'
            else:
                print 'Command failed...'
