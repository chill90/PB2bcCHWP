#Interactive program for controlling the CHWP gripper
import sys           as sy
import readline

import src.C000DRD    as c0
import src.JXC831     as jx
import src.controller as ct
import src.gripper    as gp
import src.command    as cd
import src.config     as cg

#Establish connection to gripper
if cg.use_moxa:
    PLC = c0.C000DRD(tcp_ip=cg.moxa_ip, tcp_port=cg.moxa_port)
else:
    PLC = c0.C000DRD(rtu_port=cg.ttyUSBPort)
JXC = jx.JXC831(PLC)
CTL = ct.Control(JXC)
GPR = gp.Gripper(CTL)
CMD = cd.Command(GPR)

#Execute user argument
#Command passed from the command line?
if len(sy.argv) > 1:
    user_input = ' '.join(sy.argv[1:])
    CMD.CMD(GPR, user_input)        
else: #Prompt user for command at command line
    while True:
        try:
            user_input = raw_input("Gripper command ('HELP' for help): ")
            if user_input.strip() == '':
                continue
            CMD.CMD(user_input)
        except KeyboardInterrupt:
            GPR.OFF()
            sy.exit('\nExiting gripper_control\n')
