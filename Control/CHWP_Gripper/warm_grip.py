#Script for gripping the CHWP while warm
#This script assumes that the rotor is aligned and that it is bolted to the stator
import src.C000DRD   as c0
import src.JXC831    as jx
import src.control   as ct
import src.gripper   as gp
import config.config as cfg

#Method which 
def MOVE(GPR, step_dist=0.1):
    #Inch the actuators in until they are all pushing on the rotor
    while True:
        inp = GPR.INP()
        #Stop if all actuators are gripped
        if int(inp[0]) and int(inp[1]) and int(inp[2]):
            break
        #Otherwise move the actuators
        for i in range(3):
            #If already gripped, then don't move the motor
            if int(inp[i]):
                continue
            else:
                GPR.MOVE(step_dist, axisNo=i+1)
    #When finished, turn the motors off
    GPR.OFF()
    return

# ***** MAIN *****
if __name__ == "__main__":
    #Establish connection to gripper
    if cfg.use_moxa:
        PLC = c0.C000DRD(tcp_ip=cfg.moxa_ip, tcp_port=cfg.moxa_port)
    else:
        PLC = c0.C000DRD(rtu_port=cfg.ttyUSBPort)
    port = cfg.ttyUSBPort
    JXC = jx.JXC831(PLC)
    CTL = ct.Control(JXC)
    GPR = gp.Gripper(CTL)

    #Home
    GPR.HOME()

    #Inch the actuators to set to pushing mode
    GPR.MOVE(2.0, axisNo=1)
    GPR.MOVE(2.0, axisNo=2)
    GPR.MOVE(2.0, axisNo=3)
    
    #Grip
    MOVE(GPR)
