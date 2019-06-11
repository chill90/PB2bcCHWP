#Python 2 compatibility
from __future__ import print_function

#Python classes
import datetime as dt
import time as tm
import numpy as np
import readline
import os
import sys

#Custom classes
sys.path.append('/'.join(os.path.realpath(__file__).split('/')[:-1])+"/../CHWP_Gripper/src/")
import gripper as gp
sys.path.append('/'.join(os.path.realpath(__file__).split('/')[:-1])+"/../Synaccess_Cyberswitch/src/")
import NP_05B  as cs
from . import log     as lg

class CHWP_Control:
    def __init__(self):
        #Connect to the gripper using default settings
        self.GPR = gp.Gripper()
        self.CS = cs.NP_05B()
        self.pos_file = os.path.dirname(os.path.realpath(__file__))+'/POS/chwp_control_positions.txt'
        self.__read_pos()
        return
    
    def __del__(self):
        self.__write_pos()
        return

    # ***** Public Methods *****
    #Squeeze the rotor with the grippers assuming that the rotor is supported by the installation stanchions
    def warm_grip(self):
        result = self.__squeeze(1.0)
        self.__pos_from_user("Warm_Centered")
    
    #Squeeze the rotor once every hour
    def cooldown_grip(self, time_incr=3600):
        while True: #User must exit this program
            try:
                result = self.__squeeze(0.1)
                now = dt.datetime.now()
                if result:
                    msg = "CHWP_Control.cooldown_grip(): Rotor regripped"
                    wrmsg = '[%04d-%02d-%02d %02d:%02d:%02d] %s' % (now.year, now.month, now.day, now.hour, now.minute, now.second, msg)
                    print(wrmsg)
                    tm.sleep(time_incr)
                else:
                    msg = "ERROR: failed to regrip the rotor"
                    wrmsg = '[%04d-%02d-%02d %02d:%02d:%02d] %s' % (now.year, now.month, now.day, now.hour, now.minute, now.second, msg)
                    raise Exception(wrmsg)
            except KeyboardInterrupt:
                self.__pos_from_user(mode="Cooldown_Finish")
        return
    
    def cold_grip(self):
        result = self.__squeeze(1.0)
        return result
    
    def cold_ungrip(self):
        self.__pos_from_user(mode="Cold_Ungrip")
        result = self.__release()

    def gripper_home(self):
        return self.GPR.HOME()

    def gripper_reboot(self):
        #Gripper units stored on first three ports of the cyberswitch
        self.CS.OFF(1)
        self.CS.OFF(2)
        self.CS.OFF(3)
        self.CS.ON(1)
        self.CS.ON(2)
        self.CS.ON(3)
        return

    # ***** Private Methods *****
    def __squeeze(self, incr=0.1):
        in_position = [False for ii in range(3)]
        first_pass = True #Need to iterate through all motors at least once
        while not all(in_position):
            for ii in range(3):
                try:
                    if not in_position[ii] or first_pass:
                        in_position = self.GPR.MOVE('POS', incr, ii+1)
                    else:
                        continue
                except KeyboardInterrupt:
                    print("User interrupted CHWP_Control.__squeeze()")
                    return True
            first_pass = False
        return True
    
    def __release(self, incr=0.1):
        #Back away slowly for the first 2 mm to help estimate the rotor floating point
        #in_position = [False for ii in range(1,4)]
        #while not all(in_position):
        #    for ii in range(1,4):
        #        if not in_position[ii]:
        #            in_position = self.GPR.MOVE('PUSH', incr, ii)
        #        else:
        #            continue
        #return True
        return self.GPR.HOME()

    def __pos_from_user(self, mode=None):
        if mode is None:
            raise Exception("ERROR: no mode passed to CHWP_Control.__pos_from_user()")
        pos1 = float(raw_input("Position of Axis 1: "))
        pos2 = float(raw_input("Position of Axis 2: "))
        pos3 = float(raw_input("Position of Axis 3: "))
        self.pos[mode] = (pos1, pos2, pos3)
        
    def __write_pos(self):
        f = open(self.pos_file, 'w')
        for k in self.pos.keys():
            f.write("%-20s%-10.1f%-10.1f%-10.1f\n" % (k, self.pos[k][0], self.pos[k][1], self.pos[k][2]))
        f.close()
        return

    def __read_pos(self):
        pos_data = np.loadtxt(self.pos_file, unpack=True, dtype=np.str)
        self.pos = {pos_data[0][ii]: (float(pos_data[1][ii]), float(pos_data[2][ii]), float(pos_data[3][ii])) for ii in range(len(pos_data[0]))}
        return
