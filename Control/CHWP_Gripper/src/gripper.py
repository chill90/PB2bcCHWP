import datetime    as dt
import collections as cl
import                os

#Class that controls and interfaces to the CHWP Gripper
class Gripper:
    def __init__(self, CTL=None):
        if CTL is None:
            raise Exception('FATAL: No control object passed to CHWP_Gripper')
        self.CTL = CTL
        
        #Logging object
        self.log = self.CTL.log

        #Position file
        self.posDir  = os.path.dirname(os.path.realpath(__file__))+'/POS/'
        self.posFile = self.posDir+'chwpGripper_positionLog.txt'
        self.posf = open(self.posFile, 'a+')

        #Read initial positions
        self.__readPos()

        #Minimum and maximum allowed positions
        self.minPos = -2.0
        self.maxPos = +20.0

        #Dictionary of movements that correspond to each step
        self.steps = cl.OrderedDict({"01": (+0.1, 0.0, 0.0),
                                     "02": ( 0.0,+0.1, 0.0),
                                     "03": ( 0.0, 0.0,+0.1),
                                     "04": (-0.1, 0.0, 0.0),
                                     "05": ( 0.0,-0.1, 0.0),
                                     "06": ( 0.0, 0.0,-0.1),
                                     "07": (+0.2, 0.0, 0.0),
                                     "08": ( 0.0,+0.2, 0.0),
                                     "09": ( 0.0, 0.0,+0.2),
                                     "10": (-0.2, 0.0, 0.0),
                                     "11": ( 0.0,-0.2, 0.0),
                                     "12": ( 0.0, 0.0,-0.2),
                                     "13": (+0.5, 0.0, 0.0),
                                     "14": ( 0.0,+0.5, 0.0),
                                     "15": ( 0.0, 0.0,+0.5),
                                     "16": (-0.5, 0.0, 0.0),
                                     "17": ( 0.0,-0.5, 0.0),
                                     "18": ( 0.0, 0.0,-0.5),
                                     "19": (+1.0, 0.0, 0.0),
                                     "20": ( 0.0,+1.0, 0.0),
                                     "21": ( 0.0, 0.0,+1.0),
                                     "22": (-1.0, 0.0, 0.0),
                                     "23": ( 0.0,-1.0, 0.0),
                                     "24": ( 0.0, 0.0,-1.0),
                                     "25": (+5.0, 0.0, 0.0),
                                     "26": ( 0.0,+5.0, 0.0),
                                     "27": ( 0.0, 0.0,+5.0),
                                     "28": (-5.0, 0.0, 0.0),
                                     "29": ( 0.0,-5.0, 0.0),
                                     "30": ( 0.0, 0.0,-5.0)})
                      
    def __del__(self):
        self.posf.close()

    #***** Public Methods *****
    def ON(self):
        return self.CTL.ON()

    def OFF(self):
        return self.CTL.OFF()
    
    def MOVE(self, axisNo, dist):
        startPos  = self.axisPos[axisNo-1] 
        targetPos = startPos + dist
        if targetPos < self.minPos:
            self.log.log("FATAL: 'MOVE' failed in 'Gripper.MOVE()' due to target position %.02f mm being less than minimum allowed position %.02f mm" % (targetPos, self.minPos))
            return False
        if targetPos > self.maxPos:
            self.log.log("FATAL: 'MOVE' failed in 'Gripper.MOVE()' due to target position %.02f mm being less than maximum allowed position %.02f mm" % (targetPos, self.maxPos))
            return False
        steps = self.__selectSteps(axisNo, dist)
        for st in steps:
            if self.CTL.STEP(st):
                self.axisPos[axisNo-1] += self.steps[st][axisNo-1]
                continue
            else:
                self.log.log("FATAL: 'MOVE' failed in 'Gripper.MOVE()' for Axis %d during execution." % (axisNo))
                self.log.log("FATAL: Target position for Axis %d = %.02f mm. Starting position = %.02f mm. Achieved position = %.02f mm." % (axisNo, targetPos, startPos, self.axisPos[axisNo-1]))
                self.__writePos()
                return False
        self.log.log("NOTIFY: 'MOVE' completed for Axis %d. Current position = %.02f mm" % (axisNo, self.axisPos[axisNo-1]))
        self.__writePos()
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
    
    def STATUS(self):
        return self.CTL.STATUS()

    # ***** Private Methods *****
    def __readPos(self):
        lastWrite = self.posf.readlines()[-1]
        date, time  = lastWrite.split('[')[1].split(']')[0].split()
        axis1, axis2, axis3 = lastWrite.split()[2:]
        self.log.log("*** Last-recorded Gripper Position ***")
        self.log.log("Date   = %s"    % (date ))
        self.log.log("Time   = %s"    % (time ))
        self.log.log("Axis 1 = %.02f" % (float(axis1)))
        self.log.log("Axis 2 = %.02f" % (float(axis2)))
        self.log.log("Axis 3 = %.02f" % (float(axis3)))
        self.axisPos = [float(axis1), float(axis2), float(axis3)]
        return True

    def __writePos(self):
        now = dt.datetime.now()
        date = '%04d-%02d-%02d' % (now.year, now.month, now.day)
        time = '%02d:%02d:%02d' % (now.hour, now.minute, now.second)
        wrmsg = '[%s %s] %s %-20.2f %-20.2f %-20.2f\n' % (date, time, ' '*3, self.axisPos[0], self.axisPos[1], self.axisPos[2])
        self.posf.write(wrmsg)
        self.log.log("*** Newly-recorded Gripper Position ***")
        self.log.log("Date   = %s"    % (date ))
        self.log.log("Time   = %s"    % (time ))
        self.log.log("Axis 1 = %.02f" % (self.axisPos[0]))
        self.log.log("Axis 2 = %.02f" % (self.axisPos[1]))
        self.log.log("Axis 3 = %.02f" % (self.axisPos[2]))
        return True

    def __selectSteps(self, axisNo, dist):
        d = dist
        steps = []
        while abs(d) >= 0.1: #mm
            for k in self.steps.keys()[::-1]:
                moveStep = float(self.steps[k][axisNo-1])
                try:
                    div = float(d)/moveStep
                except ZeroDivisionError:
                    continue
                if div >= 1:
                    steps.append(k)
                    d -= moveStep
                    break
                else:
                    continue
        return steps
