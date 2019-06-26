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
        self.GPR = gp.Gripper(logLevel=0)
        self.CS = cs.NP_05B()
        self.pos_file = os.path.dirname(os.path.realpath(__file__))+'/POS/chwp_control_positions.txt'
        self._read_pos()
        return
    
    def __del__(self):
        self._write_pos()
        return

    # ***** Public Methods *****
    #Squeeze the rotor with the grippers assuming that the rotor is supported by the installation stanchions
    def warm_grip(self):
        self._squeeze(1.0)
        self._pos_from_user("Warm_Centered")
        return self.GPR.OFF()
    
    #Squeeze the rotor once every hour
    def cooldown_grip(self, time_incr=3600.):
        while True: #User must exit this program
            try:
                #Move each gripper backwards first
                for ii in range(1,4):
                    self.GPR.MOVE('POS', -0.1, ii)
                #Then, re-squeeze the rotor
                result = self._squeeze(0.1)
                now = dt.datetime.now()
                if result:
                    msg = "CHWP_Control.cooldown_grip(): Rotor regripped"
                    wrmsg = '[%04d-%02d-%02d %02d:%02d:%02d] %s' % (now.year, now.month, now.day, now.hour, now.minute, now.second, msg)
                    print(wrmsg)
                    self.GPR.OFF()
                    print(time_incr)
                    self._sleep(time_incr)
                    print("Finished sleeping")
                    continue
                else:
                    msg = "ERROR: failed to regrip the rotor"
                    wrmsg = '[%04d-%02d-%02d %02d:%02d:%02d] %s' % (now.year, now.month, now.day, now.hour, now.minute, now.second, msg)
                    raise Exception(wrmsg)
            except KeyboardInterrupt:
                self._pos_from_user(mode="Cooldown_Finish")
                break
        return self.GPR.OFF()
    
    def cold_grip(self):
        #First squeeze the rotor
        self._squeeze(1.0)
        #Then, backup by 1 mm to allow some compliance for rotor expansion during warmup
        for ii in range(1,4):
            self.GPR.MOVE('POS', -1.0, ii)
        #Turn off the motors
        return self.GPR.OFF()
    
    def cold_ungrip(self):
        self._pos_from_user(mode="Cold_Ungrip")
        self._release()
        return self.GPR.OFF()

    def gripper_home(self):
        self.GPR.HOME()
        return self.GPR.OFF()

    def gripper_reboot(self):
        #print("Rebooting motors, controller, and PLC. This will take a few minutes...")
        #Gripper units stored on first three ports of the cyberswitch
        self.CS.OFF(1)
        self.CS.OFF(2)
        self.CS.OFF(3)
        self.CS.ON(1)
        self.CS.ON(2)
        self.CS.ON(3)
        return

    # ***** Private Methods *****
    def _sleep(self, duration=3600.):
        granular_time = 60.
        for ii in range(int(duration/granular_time)+1):
            tm.sleep(granular_time)
        return
    
    def _squeeze(self, incr=0.1):
        in_position = [False for ii in range(3)]
        finished = [False for ii in range(3)]
        first_pass = True #Need to iterate through all motors at least once
        while not all(in_position):
            for ii in range(3):
                #self.GPR.ON()
                try:
                    if not finished[ii] or first_pass:
                        #in_position = self.GPR.MOVE('PUSH', incr, ii+1)
                        in_position = self._push(incr, ii+1)
                        if in_position[ii]:
                            finished[ii] = True
                    else:
                        continue
                except KeyboardInterrupt:
                    print("User interrupted CHWP_Control._squeeze()")
                    return True
            first_pass = False
            #self.GPR.OFF()
        return True

    def _push(self, incr, axis):
        result = self.GPR.MOVE('PUSH', incr, axis)
        #If the pushing operation failed, the motor may be rocking back and forth
        #This can be fixed by positioning back and then forward again
        while not isinstance(result, tuple):
            self.GPR.MOVE('POS', -0.1, axis)
            result = self.GPR.MOVE('PUSH', 0.1, axis)
        return result
    
    def _release(self, incr=0.1):
        #Home the motors
        return self.GPR.HOME()

    def _pos_from_user(self, mode=None):
        if mode is None:
            raise Exception("ERROR: no mode passed to CHWP_Control._pos_from_user()")
        pos1 = float(raw_input("Position of Axis 1: "))
        pos2 = float(raw_input("Position of Axis 2: "))
        pos3 = float(raw_input("Position of Axis 3: "))
        self.pos[mode] = (pos1, pos2, pos3)
        
    def _write_pos(self):
        f = open(self.pos_file, 'w')
        for k in self.pos.keys():
            f.write("%-20s%-10.1f%-10.1f%-10.1f\n" % (k, self.pos[k][0], self.pos[k][1], self.pos[k][2]))
        f.close()
        return

    def _read_pos(self):
        pos_data = np.loadtxt(self.pos_file, unpack=True, dtype=np.str)
        self.pos = {pos_data[0][ii]: (float(pos_data[1][ii]), float(pos_data[2][ii]), float(pos_data[3][ii])) for ii in range(len(pos_data[0]))}
        return
