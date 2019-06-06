import datetime    as dt
import collections as cl
import                os
import numpy       as np

#Custom classes
import motor as mt

#Class that controls and interfaces to the CHWP Gripper
class Gripper:
    def __init__(self, CTL=None):
        if CTL is None:
            raise Exception('Gripper error: No control object passed to Gripper() constructor')
        self.CTL = CTL

        #Instantiate motor objects
        self.motors = cl.OrderedDict({"1": mt.Motor("Axis 1")})
        self.motors["2"] = mt.Motor("Axis 2")
        self.motors["3"] = mt.Motor("Axis 3")
        
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
    def ON(self):
        return self.CTL.ON()

    def OFF(self):
        return self.CTL.OFF()
    
    def MOVE(self, mode, dist, axisNo):
        #startPos  = self.axisPos[axisNo-1]
        
        targetPos = startPos + dist
        steps = self.__selectSteps(mode, dist, axisNo)
        if steps is None:
            self.log.log("FATAL: 'MOVE' failed in 'GRIPPER.MOVE()'")
            return False
        for st in steps:
            if self.CTL.STEP(st, axisNo):
                #if axisNo is None:
                #    for i in range(len(self.axisPos)):
                #        self.axisPos[i] += self.steps_all[st]
                #else:
                for i in range(len(self.axisPos)):
                    if mode == 'POS':
                        self.axisPos[i] += self.steps_pos[st][i]
                    elif mode == 'PUSH':
                        self.axisPos[i] += self.steps_push[st][i]
                continue
            else:
                #self.log.log("FATAL: 'MOVE' failed in 'Gripper.MOVE()' for Axis %d during execution." % (axisNo))
                self.log.log("FATAL: 'MOVE' failed in 'Gripper.MOVE()'")
                #self.log.log("FATAL: Target position for Axis %d = %.02f mm. Starting position = %.02f mm. Achieved position = %.02f mm."
                #             % (axisNo, targetPos, startPos, self.axisPos[axisNo-1]))
                self.__writePos()
                self.INP()
                return False
        #self.log.log("NOTIFY: 'MOVE' completed for Axis %d. Current position = %.02f mm" % (axisNo, self.axisPos[axisNo-1]))
        self.log.log("NOTIFY: 'MOVE' successfully completed")
        self.__writePos()
        self.INP()
        return True

    def HOME(self):
        result = self.CTL.HOME()
        if result:
            self.log.log("NOTIFY: 'HOME' operation completed. All actuator positions = 0.00 mm.")
            for i in range(len(self.axisPos)):
                self.axisPos[i] = 0
            self.__writePos()
            return True
        else:
            self.log.log("FATAL: 'HOME' operation failed in Gripper.HOME().")
            self.log.log("WARNING: actuators may be at unknown positions due to failed home operation!")
            return False

    def ALARM(self):
        return self.CTL.ALARM()

    def RESET(self):
        group = self.CTL.ALARM_GROUP()
        if group is None:
            self.log.log("FATAL: 'RESET' failed in Gripper.RESET(): no alarm group detected.")
            return False
        elif group == "B" or group == "C":
            self.log.log("NOTIFY: Clearing Alarm group '%s' via a 'RESET'." % (group))
            result = self.CTL.RESET()
        elif group == "D":
            self.log.log("NOTIFY: Clearing Alarm group '%s' via a 'RESET' followed by enabling 'SVON'." % (group))
            result = self.CTL.RESET()
        elif group == "D":
            self.log.log("FATAL: 'RESET' failed in Gripper.RESET(): alarm group '%s' detected. Power cycle of controller and motors required." % (group))
            return False
        else:
            self.log.log("FATAL: 'RESET' failed in Gripper.RESET(): unknown alarm group.")
            return False
        if not self.ALARM():
            self.log.log("NOTIFY: Alarm successfully reset.")
            self.ALARM()
            return True
        else:
            self.log.log("FATAL: 'RESET' failed in Gripper.RESET(): unknown error.")
            return False

    def POSITION(self):
        for i in range(len(self.axisPos)):
            self.log.log("Axis %d = %.02f mm" % (i, self.axisPos[i]))
        return True

    def SETPOS(self, axisNo, value):
        startPos = self.axisPos[axisNo-1]
        self.log.log("NOTIFY: Axis %d old position = %.02f" % (axisNo, startPos))
        self.axisPos[axis-1] = value
        self.log.log("NOTIFY: Axis %d new position set manually = %.02f" % (axisNo, value))
        return True

    def INP(self):
        return self.CTL.INP()
    
    def STATUS(self):
        return self.CTL.STATUS()

    # ***** Private Methods *****
    def __readPos(self):
        lastWrite = self.posf.readlines()[-1]
        date, time  = lastWrite.split('[')[1].split(']')[0].split()
        axis1, axis2, axis3 = lastWrite.split()[2:]
        self.log.log("*** Last-recorded Gripper Position ***")
        self.log.log("Axis 1 = %.02f" % (float(axis1)))
        self.log.log("Axis 2 = %.02f" % (float(axis2)))
        self.log.log("Axis 3 = %.02f" % (float(axis3)))
        self.axisPos = [float(axis1), float(axis2), float(axis3)]
        self.motors["1"].pos = float(axis1)
        self.motors["2"].pos = float(axis2)
        self.motors["3"].pos = float(axis3)
        return True

    def __writePos(self, init=False):
        #if init:
        #    self.posf.write("***Timestamp***           ***Axis 1***         ***Axis 2***         ***Axis 3***\n")
        #    self.axisPos = [0., 0., 0.]
        now = dt.datetime.now()
        date = '%04d-%02d-%02d' % (now.year, now.month, now.day)
        time = '%02d:%02d:%02d' % (now.hour, now.minute, now.second)
        wrmsg = '[%s %s] %s %-20.2f %-20.2f %-20.2f\n' % (date, time, ' '*3, self.axisPos[0], self.axisPos[1], self.axisPos[2])
        self.posf.write(wrmsg)
        self.log.log("*** Newly-recorded Gripper Position ***")
        self.log.log("Axis 1 = %.02f" % (self.axisPos[0]))
        self.log.log("Axis 2 = %.02f" % (self.axisPos[1]))
        self.log.log("Axis 3 = %.02f" % (self.axisPos[2]))
        #self.log.log("***Gripper positions are not measured but instead are computed based on input commands***")
        return True

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
#
#                for k in self.steps_all.keys()[::-1]:
#                    moveStep = float(self.steps_all[k])
#                    if np.round(moveStep, decimals=1) == 0.0:
#                        continue
#                    try:
#                        div = np.round(float(d)/moveStep, decimals=1)
#                    except ZeroDivisionError:
#                        continue
#                    if div >= 1.0:
#                        steps_to_do.append(k)
#                        d -= moveStep
#                        break
#                    else:
#                        continue
#            else:
#                for k in self.steps.keys()[::-1]:
#                    moveStep = float(self.steps[k][axisNo-1])
#                    if np.round(moveStep, decimals=1) == 0.0:
#                        continue
#                    try:
#                        div = np.round(float(d)/moveStep, decimals=1)
#                    except ZeroDivisionError:
#                        continue
#                    if div >= 1.0:
#                        steps_to_do.append(k)
#                        d -= moveStep
#                        break
#                    else:
#                        continue
#                
#        return steps_to_do
