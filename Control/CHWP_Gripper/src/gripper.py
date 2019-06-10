import datetime    as dt
import collections as cl
import                os
import numpy       as np

#Custom classes
import motor as mt
import src.C000DRD      as c0
import src.JXC831       as jx
import src.controller   as ct
import src.gripper      as gp
import src.command      as cd
import ../config.config as cg

#Class that controls and interfaces to the CHWP Gripper
class Gripper:
    def __init__(self, controller=None):
        if controller is None:
            if cg.use_moxa:
                PLC = c0.C000DRD(tcp_ip=cg.moxa_ip, tcp_port=cg.moxa_port)
            else:
                PLC = c0.C000DRD(rtu_port=cg.ttyUSBPort)
            JXC = jx.JXC831(PLC)
            self.CTL = ct.Controller(JXC)
        else:
            self.CTL = controller

        #Instantiate motor objects
        self.motors = cl.OrderedDict({"1": mt.Motor("Axis 1")})
        self.motors["2"] = mt.Motor("Axis 2")
        self.motors["3"] = mt.Motor("Axis 3")
        self.numMotors = len(self.motors.keys())
        
        #Logging object
        self.log = self.CTL.log

        #Position file
        self.posDir  = os.path.dirname(os.path.realpath(__file__))+'/POS/'
        self.posFile = self.posDir+'chwpGripper_positionLog.txt'
        self.posf = open(self.posFile, 'a+')

        #Read initial positions
        self.__readPos()

        #Minimum and maximum allowed positions
        #self.minPos = -2.0
        self.minPos = -100.
        #self.maxPos = +20.0
        self.maxPos = 100.

        #Dictionary of movements that correspond to each step
        #This is for single-motor movements only
        #These are pushing operations
        self.steps_push = cl.OrderedDict({"01": (+0.1, 0.0, 0.0)})
        self.steps_push["02"] = ( 0.0,+0.1, 0.0)
        self.steps_push["03"] = ( 0.0, 0.0,+0.1)
        self.steps_push["04"] = (+0.5, 0.0, 0.0)
        self.steps_push["05"] = ( 0.0,+0.5, 0.0)
        self.steps_push["06"] = ( 0.0, 0.0,+0.5)
        self.steps_push["07"] = (+1.0, 0.0, 0.0)
        self.steps_push["08"] = ( 0.0,+1.0, 0.0)
        self.steps_push["09"] = ( 0.0, 0.0,+1.0)

        #Dictionary for all-motor movements
        self.steps_pos = cl.OrderedDict({"10": (+0.1, 0.0, 0.0)})
        self.steps_pos["11"] = ( 0.0,+0.1, 0.0)
        self.steps_pos["12"] = ( 0.0, 0.0,+0.1)
        self.steps_pos["13"] = (-0.1, 0.0, 0.0)
        self.steps_pos["14"] = ( 0.0,-0.1, 0.0)
        self.steps_pos["15"] = ( 0.0, 0.0,-0.1)
        self.steps_pos["16"] = (+0.5, 0.0, 0.0)
        self.steps_pos["17"] = ( 0.0,+0.5, 0.0)
        self.steps_pos["18"] = ( 0.0, 0.0,+0.5)
        self.steps_pos["19"] = (-0.5, 0.0, 0.0)
        self.steps_pos["20"] = ( 0.0,-0.5, 0.0)
        self.steps_pos["21"] = ( 0.0, 0.0,-0.5)
        self.steps_pos["22"] = (+1.0, 0.0, 0.0)
        self.steps_pos["23"] = ( 0.0,+1.0, 0.0)
        self.steps_pos["24"] = ( 0.0, 0.0,+1.0)
        self.steps_pos["25"] = (-1.0, 0.0, 0.0)
        self.steps_pos["26"] = ( 0.0,-1.0, 0.0)
        self.steps_pos["27"] = ( 0.0, 0.0,-1.0)
        self.steps_pos["28"] = (+5.0, 0.0, 0.0)
        self.steps_pos["29"] = ( 0.0,+5.0, 0.0)
        self.steps_pos["30"] = ( 0.0, 0.0,+5.0)
                      
    def __del__(self):
        self.posf.close()

    #***** Public Methods *****
    #Turn the controller on
    def ON(self):
        return self.CTL.ON()

    #Turn the controller off
    def OFF(self):
        return self.CTL.OFF()

    #Move a specific motor 'axisNo' a given distance 'dist' in pushing/positioning mode
    def MOVE(self, mode, dist, axisNo):
        motor = self.motors[str(axisNo)]
        startPos = motor.pos
        targetPos = startPos + dist
        steps = self.__selectSteps(mode, dist, axisNo)
        if steps is None:
            self.log.err("'MOVE' failed in 'GRIPPER.MOVE()' -- selected steps is empty")
            return False
        for st in steps:
            if self.CTL.STEP(st, axisNo):
                if mode == 'POS':
                    #self.axisPos[i] += self.steps_pos[st][axisNo-1]
                    motor.pos += self.steps_pos[st][axisNo-1]
                elif mode == 'PUSH':
                    #self.axisPos[i] += self.steps_push[st][axisNo-1]
                    motor.pos += self.steps_push[st][axisNo-1]
                continue
            else:
                self.log.err("MOVE failed in Gripper.MOVE() -- CTL.STEP() returned 'False'")
                self.__writePos()
                self.INP()
                return False
        #self.log.log("NOTIFY: 'MOVE' completed for Axis %d. Current position = %.02f mm" % (axisNo, self.axisPos[axisNo-1]))
        self.log.log("NOTIFY: 'MOVE' successfully completed")
        self.__writePos()
        self.INP()
        return True

    #Home all motors
    def HOME(self):
        result = self.CTL.HOME()
        if result:
            self.log.log("'HOME' operation completed. All actuator positions reset")
            for k in self.motors.keys():
                self.motors[k].pos = 0.
            self.__writePos()
            return True
        else:
            self.log.err("HOME operation failed in Gripper.HOME() -- CTL.HOME() returned 'False'.")
            self.log.wrn("Actuators may be at unknown positions due to failed home operation!")
            return False

    #Return the controller alarm status
    def ALARM(self):
        return self.CTL.ALARM()

    #Reset the controller alarm
    def RESET(self):
        #Obtain the alarm group
        group = self.CTL.ALARM_GROUP()
        if group is None:
            self.log.err("RESET failed in Gripper.RESET() -- no alarm group detected.")
            return False
        elif group == "B" or group == "C":
            self.log.log("Clearing Alarm group '%s' via a RESET." % (group))
            result = self.CTL.RESET()
        elif group == "D":
            self.log.log("Clearing Alarm group '%s' via a RESET followed by enabling SVON." % (group))
            result = self.CTL.RESET()
        elif group == "D":
            self.log.err("RESET failed in Gripper.RESET() --  alarm group '%s' detected. Power cycle of controller and motors required." % (group))
            return False
        else:
            self.log.err("RESET failed in Gripper.RESET() --  unknown alarm group.")
            return False
        if not self.ALARM():
            self.log.log("Alarm successfully reset.")
            self.ALARM()
            return True
        else:
            self.log.err("RESET failed in Gripper.RESET() --  unknown error.")
            return False

    #Print the positions of the motors
    def POSITION(self):
        for k in self.motors.keys():
            self.log.log("Axis %s = %.02f mm" % (k, self.motors[k]))
        return True

    #Set the a given motor 'axisNo' position manually to 'value'
    def SETPOS(self, axisNo, value):
        mot = self.motors[str(axisNo)]
        startPos = mot.pos
        #startPos = self.axisPos[axisNo-1]
        self.log.log("Axis %d old position = %.02f" % (axisNo, startPos))
        mot.pos = value
        mot.max_pos_err = 0
        self.log.log("Axis %d new position set manually = %.02f" % (axisNo, value))
        self.log.log("Axis %d position error zerod" % (axisNo))
        return True

    #Collect the INP values for the controller
    def INP(self):
        return self.CTL.INP()

    #Print the status bits for the controller
    def STATUS(self):
        return self.CTL.STATUS()

    # ***** Private Methods *****
    #Read the motor positions from the position file
    def __readPos(self):
        lastWrite = self.posf.readlines()[-1]
        date, time  = lastWrite.split('[')[1].split(']')[0].split()
        axis1, axis2, axis3 = lastWrite.split()[2:]
        self.log.log("*** Last-recorded Gripper Position ***")
        self.log.log("Axis 1 = %.02f" % (float(axis1)))
        self.log.log("Axis 2 = %.02f" % (float(axis2)))
        self.log.log("Axis 3 = %.02f" % (float(axis3)))
        #self.axisPos = [float(axis1), float(axis2), float(axis3)]
        self.motors["1"].pos = float(axis1)
        self.motors["2"].pos = float(axis2)
        self.motors["3"].pos = float(axis3)
        return True

    #Write the motor positions to the position file
    def __writePos(self, init=False):
        now = dt.datetime.now()
        date = '%04d-%02d-%02d' % (now.year, now.month, now.day)
        time = '%02d:%02d:%02d' % (now.hour, now.minute, now.second)
        wrmsg = '[%s %s] %s %-20.2f %-20.2f %-20.2f\n' % (date, time, ' '*3, self.motors["1"].pos, self.motors["2"].pos, self.motors["3"].pos)
        self.posf.write(wrmsg)
        self.log.log("*** Newly-recorded Gripper Position ***")
        self.log.log("Axis 1 = %.02f" % (self.motors["1"].pos))
        self.log.log("Axis 2 = %.02f" % (self.motors["2"].pos))
        self.log.log("Axis 3 = %.02f" % (self.motors["3"].pos))
        return True
    
    #Select the steps for a motor movement
    def __selectSteps(self, mode, dist, axisNo):
        d = dist
        steps_to_do = []
        while abs(d) >= 0.1: #mm
            if mode == 'PUSH':
                steps_to_check = self.steps_push
            elif mode == 'POS':
                steps_to_check = self.steps_pos
            else:
                self.log.log("FATAL: Could not understand mode '%s' in GRIPPER().__selectSteps()" % (mode))
                return None
            for k in steps_to_check.keys()[::-1]:
                moveStep = float(steps_to_check[k][axisNo-1])
                if np.round(moveStep, decimals=1) == 0.0:
                    continue
                try:
                    div = np.round(float(d)/moveStep, decimals=1)
                except ZeroDivisionError:
                    continue
                if div >= 1.0:
                    steps_to_do.append(k)
                    d -= moveStep
                    break
                else:
                    continue
        return steps_to_do
