from __future__ import print_function, unicocde_literals

class Command:
    def __init__(selfm, NP05B=None):
        if NP05B is None:
            raise Exception("ERROR in Synaccess_Cyberswitch.command.Command(): Must provide NP05B object to Command() init function")
        else:
            self.NP05B = NP05B
            self.log = self.NP05B.log
        return

    def HELP(self):
        print('\nAvailable commands to the NP-05B Cyberswitch:')
        print('ON [port]:  turn on port [port], for which the options are 1-5')
        print('OFF [port]: turn off port [port], for which the options are 1-5')
        print('ALL ON:  turn on all ports')
        print('ALL OFF: turn off all ports')
        print('REBOOT [port]: reboot port [port], for which the options are 1-5')
        print('STATUS: print status of each port')
        print('HELP: display this help menu')
        print('EXIT: quit program\n')

    def CMD(self, cmd):
        args = cmd.split()
        if len(args) == 0:
            return None
        cmdarg = args[0].upper()
        if cmdarg == 'ON' or cmdarg == 'OFF' or cmdarg == 'REBOOT':
            if len(args) == 2 and args[1].isdigit():
                port = int(args[1])
                if port <=5 and port >= 1:
                    if cmdarg == 'ON':
                        self.NP05B.ON(port)
                    elif cmdarg == 'OFF':
                        self.NP05B.OFF(port)
                    elif cmdarg == 'REBOOT':
                        self.NP05B.REBOOT(port)
                    else:
                        self.log.err('Parsing error for command %s' % (' '.join(args)))
                        return False
                else:
                    self.log.err('Provided port %d not in allowed range 1-5')
                    return False
            else:
                self.log.err('Could not understand command %s' % (cmd))
                return False
        elif cmdarg == 'ALL':
            if args[1].upper() == 'ON':
                self.NP05B.ALL_ON()
            elif args[1].upper() == 'OFF':
                self.NP05B.ALL_OFF()
            else:
                self.log.err('Could not understand command %s' % (cmd))
                return False
        elif cmdarg == 'STATUS':
            outputs = self.NP05B.STATUS()
            print('\nPort power status:')
            for i in range(len(outputs)):
                print('Port %d = %s\n' % (i+1, bool(int(outputs[i]))))
        elif cmdarg == 'HELP':
            HELP()
        elif cmdarg == 'EXIT':
            sy.exit(0)
        else:
            self.log.err('Could not understand command %s' % (cmd))
            return False
        return True
