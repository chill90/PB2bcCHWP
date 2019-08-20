# Built-in python modules
import sys as sy
import readline

# Gripper modules
import src.config_gripper as cg
import src.C000DRD as c0
import src.JXC831 as jx
import src.controller as ct
import src.gripper as gp
import src.command_gripper as cd

if cg.use_tcp:
    PLC = c0.C000DRD(tcp_ip=cg.tcp_ip, tcp_port=cg.tcp_port)
else:
    PLC = c0.C000DRD(rtu_port=cg.rtu_port)
JXC = jx.JXC831(PLC)
CTL = ct.Controller(JXC)
GPR = gp.Gripper(CTL)
CMD = cd.Command(GPR)

# Execute user argument
# Command passed from the command line?
if len(sy.argv) > 1:
    user_input = ' '.join(sy.argv[1:])
    CMD.CMD(GPR, user_input)
# Prompt user for command at command line
else:
    while True:
        try:
            user_input = raw_input("Gripper command ('HELP' for help): ")
            if user_input.strip() == '':
                continue
            CMD.CMD(user_input)
        except KeyboardInterrupt:
            GPR.OFF()
            sy.exit('\nExiting gripper_control\n')
