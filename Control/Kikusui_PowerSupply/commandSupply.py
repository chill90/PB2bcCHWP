import sys           as sy
import readline

import config.config as cg
import src.pmx       as pm
import src.command   as cm

#Connect to PMX power supply
if cg.use_moxa:
    pmx = pm.PMX(tcp_ip=cg.moxa_ip, tcp_port=cg.moxa_port)
else:
    pmx = pm.PMX(rtu_port=cg.ttyUSBPort)
cmd = cm.Command(pmx)

#Check if inputs were passed via the command line
if len(sy.argv) > 1:
    val = ' '.join(sy.argv[1:])
    cmd.userInput(val)
else:
    while True:
        val = raw_input("Enter command ('H' for help): ")
        cmd.userInput(val)
