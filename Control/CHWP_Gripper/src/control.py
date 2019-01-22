#Class for controlling the actuators
import time        as tm
import log         as lg
import collections as cl

class Control:
    def __init__(self, controller=None):
        if controller is None:
            raise Exception('FATAL: Gripper requires a controller object')
        self.JXC = controller

        #Logging object
        self.log = lg.Logging()

        #Timing variables
        self.timeout  = 5.0 #sec
        self.timestep = 0.5 #time between operations

        #Dictionary of pins to write for each step number
        #Binary input = step number + 1
        self.step_inputs = cl.OrderedDict({"01": [self.JXC.IN0                                       ],
                                           "02": [self.JXC.IN1                                       ],
                                           "03": [self.JXC.IN0,self.JXC.IN1                          ],
                                           "04": [self.JXC.IN2                                       ],
                                           "05": [self.JXC.IN0,self.JXC.IN2                          ],
                                           "06": [self.JXC.IN1,self.JXC.IN2                          ],
                                           "07": [self.JXC.IN0,self.JXC.IN1,self.JXC.IN2             ],
                                           "08": [self.JXC.IN3                                       ],
                                           "09": [self.JXC.IN0,self.JXC.IN3                          ],
                                           "10": [self.JXC.IN1,self.JXC.IN3                          ],
                                           "11": [self.JXC.IN0,self.JXC.IN1,self.JXC.IN3             ],
                                           "12": [self.JXC.IN2,self.JXC.IN3,                         ],
                                           "13": [self.JXC.IN0,self.JXC.IN2,self.JXC.IN3             ],
                                           "14": [self.JXC.IN1,self.JXC.IN2,self.JXC.IN3             ],
                                           "15": [self.JXC.IN0,self.JXC.IN1,self.JXC.IN2,self.JXC.IN3],
                                           "16": [self.JXC.IN4                                       ],
                                           "17": [self.JXC.IN0,self.JXC.IN4                          ],
                                           "18": [self.JXC.IN1,self.JXC.IN4                          ],
                                           "19": [self.JXC.IN0,self.JXC.IN1,self.JXC.IN4             ],
                                           "20": [self.JXC.IN2,self.JXC.IN4                          ],
                                           "21": [self.JXC.IN0,self.JXC.IN2,self.JXC.IN4             ],
                                           "22": [self.JXC.IN1,self.JXC.IN2,self.JXC.IN4             ],
                                           "23": [self.JXC.IN0,self.JXC.IN1,self.JXC.IN2,self.JXC.IN4],
                                           "24": [self.JXC.IN3,self.JXC.IN4                          ],
                                           "25": [self.JXC.IN0,self.JXC.IN3,self.JXC.IN4             ],
                                           "26": [self.JXC.IN1,self.JXC.IN3,self.JXC.IN4             ],
                                           "27": [self.JXC.IN0,self.JXC.IN1,self.JXC.IN3,self.JXC.IN4],
                                           "28": [self.JXC.IN2,self.JXC.IN3,self.JXC.IN4             ],
                                           "29": [self.JXC.IN0,self.JXC.IN2,self.JXC.IN3,self.JXC.IN4],
                                           "30": [self.JXC.IN1,self.JXC.IN1,self.JXC.IN3,self.JXC.IN4]})
                             
        #Dictionary of pins to write for each step number
        #Binary input = step number + 1
        self.step_outputs = cl.OrderedDict({"01": [self.JXC.OUT0                                          ],
                                            "02": [self.JXC.OUT1                                          ],
                                            "03": [self.JXC.OUT0,self.JXC.OUT1                            ],
                                            "04": [self.JXC.OUT2                                          ],
                                            "05": [self.JXC.OUT0,self.JXC.OUT2                            ],
                                            "06": [self.JXC.OUT1,self.JXC.OUT2                            ],
                                            "07": [self.JXC.OUT0,self.JXC.OUT1,self.JXC.OUT2              ],
                                            "08": [self.JXC.OUT3                                          ],
                                            "09": [self.JXC.OUT0,self.JXC.OUT3                            ],
                                            "10": [self.JXC.OUT1,self.JXC.OUT3                            ],
                                            "11": [self.JXC.OUT0,self.JXC.OUT1,self.JXC.OUT3              ],
                                            "12": [self.JXC.OUT2,self.JXC.OUT3,                           ],
                                            "13": [self.JXC.OUT0,self.JXC.OUT2,self.JXC.OUT3              ],
                                            "14": [self.JXC.OUT1,self.JXC.OUT2,self.JXC.OUT3              ],
                                            "15": [self.JXC.OUT0,self.JXC.OUT1,self.JXC.OUT2,self.JXC.OUT3],
                                            "16": [self.JXC.OUT4                                          ],
                                            "17": [self.JXC.OUT0,self.JXC.OUT4                            ],
                                            "18": [self.JXC.OUT1,self.JXC.OUT4                            ],
                                            "19": [self.JXC.OUT0,self.JXC.OUT1,self.JXC.OUT4              ],
                                            "20": [self.JXC.OUT2,self.JXC.OUT4                            ],
                                            "21": [self.JXC.OUT0,self.JXC.OUT2,self.JXC.OUT4              ],
                                            "22": [self.JXC.OUT1,self.JXC.OUT2,self.JXC.OUT4              ],
                                            "23": [self.JXC.OUT0,self.JXC.OUT1,self.JXC.OUT2,self.JXC.OUT4],
                                            "24": [self.JXC.OUT3,self.JXC.OUT4                            ],
                                            "25": [self.JXC.OUT0,self.JXC.OUT3,self.JXC.OUT4              ],
                                            "26": [self.JXC.OUT1,self.JXC.OUT3,self.JXC.OUT4              ],
                                            "27": [self.JXC.OUT0,self.JXC.OUT1,self.JXC.OUT3,self.JXC.OUT4],
                                            "28": [self.JXC.OUT2,self.JXC.OUT3,self.JXC.OUT4              ],
                                            "29": [self.JXC.OUT0,self.JXC.OUT2,self.JXC.OUT3,self.JXC.OUT4],
                                            "30": [self.JXC.OUT1,self.JXC.OUT1,self.JXC.OUT3,self.JXC.OUT4]})

        #Dictionary of Alarm OUTputs
        self.alarm_group = cl.OrderedDict({"B": self.JXC.OUT1,
                                           "C": self.JXC.OUT2,
                                           "D": self.JXC.OUT3,
                                           "E": None})

    # ***** Public Methods *****
    def ON(self):
        if not self.JXC.read(self.JXC.SVON):
            self.JXC.set_on(self.JXC.SVON)
        if not self.JXC.read(self.JXC.BRAKE1) or not self.JXC.read(self.JXC.BRAKE2) or not self.JXC.read(self.JXC.BRAKE3):
            self.BRAKE(False)
        return True

    def OFF(self):
        if self.JXC.read(self.JXC.BRAKE1) or self.JXC.read(self.JXC.BRAKE2) or self.JXC.read(self.JXC.BRAKE3):
            self.BRAKE(True)
        if self.JXC.read(self.JXC.SVON):
            return self.JXC.set_off(self.JXC.SVON)
        else:
            return True
        
    def HOME(self):
        self.ON()
        if not self.__isPowered():
            self.log.log("FATAL: 'HOME' aborted due to SVRE not being ON -- timeout")
            return False
        if not self.JXC.read(self.JXC.ALARM):
            self.log.log("FATAL: 'HOME' aborted due to triggered alarm")
            return False
        if not self.JXC.read(self.JXC.ESTOP):
            self.log.log("FATAL: 'HOME' aborted due to emergency stop being active")
            return False
        if not self.JXC.read(self.JXC.SVON):
            self.log.log("FATAL: 'HOME' aborted due to 'SVON' not being ON")
            return False
        if not self.JXC.read(self.JXC.SVRE):
            self.log.log("FATAL: 'HOME' aborted due to 'SVRE' not being ON")
            return False
        if not self.JXC.read(self.JXC.INP):
            self.log.log("FATAL: 'HOME' aborted due to 'INP' not being on")
            return False
        self.JXC.set_on(self.JXC.SETUP)
        if self.__wait():
            self.log.log("NOTIFY: 'HOME' operation finished", stdout=False)
            self.JXC.set_off(self.JXC.SETUP)
            return True
        else:
            self.log.log("FATAL: 'HOME' operation failed due to timout")
            self.JXC.set_off(self.JXC.SETUP)
            return False

    def STEP(self, stepNum):
        self.ON()
        stepNum = "%02d" % (int(stepNum))
        if stepNum not in self.step_inputs.keys():
            self.log.log("FATAL: Step number %02d not an available option" % (stepNum))
            return False
        self.__zeroInputs()
        self.JXC.set_off(self.JXC.DRIVE)
        if not self.__isReady():
            self.log.log("FATAL: 'STEP' operation failed due to motors not being ready")
            self.log.log("BUSY = %d" % (self.JXC.read(self.JXC.BUSY )))
            self.log.log("INP  = %d" % (self.JXC.read(self.JXC.INP  )))
            self.log.log("SVON = %d" % (self.JXC.read(self.JXC.SETON)))
            return False
        #Set the inputs
        for addr in self.step_inputs[stepNum]:
            self.JXC.set_on(addr)
        tm.sleep(0.1)
        self.JXC.set_on(self.JXC.DRIVE)
        if self.__wait():
            self.log.log("NOTIFY: 'STEP' operation finished", stdout=False)
            for addr in self.step_inputs[stepNum]:
                self.JXC.set_off(addr)
            self.__zeroInputs()
            self.JXC.set_off(self.JXC.DRIVE)
            return True
        else:
            self.log.log("NOTIFY: 'STEP' operation failed due to timeout")
            for addr in self.steps[stepNum]:
                self.JXC.set_off(addr)
            self.__zeroInputs()
            self.JXC.set_off(self.JXC.DRIVE)
            return False
            
    def HOLD(self, state=True):
        if state is True:
            if self.__isMoving():
                self.JXC.set_on(self.JXC.HOLD)
                return True
            else:
                self.JXC.set_off(self.JXC.HOLD)
                return False
        else:
            self.JXC.set_off(self.JXC.HOLD)
            return False

    def BRAKE(self, state=True):
        if state:
            self.JXC.set_off(self.JXC.BRAKE1)
            self.JXC.set_off(self.JXC.BRAKE2)
            self.JXC.set_off(self.JXC.BRAKE3)
            return True
        else:
            self.JXC.set_on(self.JXC.BRAKE1)
            self.JXC.set_on(self.JXC.BRAKE2)
            self.JXC.set_on(self.JXC.BRAKE3)
            return False
            
    def RESET(self):
        if self.__isAlarm():
            self.JXC.set_on(self.JXC.RESET)
            return True
        else:
            self.log.log("FATAL: 'RESET' operation ignored, as no alarm is detected")
            return False

    def STATUS(self):
        self.log.log("PRINTING STATUS:")
        self.log.log("IN0 = %d" % (self.JXC.read(self.JXC.IN0)))
        self.log.log("IN1 = %d" % (self.JXC.read(self.JXC.IN1)))
        self.log.log("IN2 = %d" % (self.JXC.read(self.JXC.IN2)))
        self.log.log("IN3 = %d" % (self.JXC.read(self.JXC.IN3)))
        self.log.log("IN4 = %d" % (self.JXC.read(self.JXC.IN4)))
        self.log.log("\n")
        self.log.log("SETUP = %d" % (self.JXC.read(self.JXC.SETUP)))
        self.log.log("HOLD  = %d" % (self.JXC.read(self.JXC.HOLD )))
        self.log.log("DRIVE = %d" % (self.JXC.read(self.JXC.DRIVE)))
        self.log.log("RESET = %d" % (self.JXC.read(self.JXC.RESET)))
        self.log.log("SVON  = %d" % (self.JXC.read(self.JXC.SETON)))
        self.log.log("\n")
        self.log.log("OUT0 = %d" % (self.JXC.read(self.JXC.OUT0)))
        self.log.log("OUT1 = %d" % (self.JXC.read(self.JXC.OUT1)))
        self.log.log("OUT2 = %d" % (self.JXC.read(self.JXC.OUT2)))
        self.log.log("OUT3 = %d" % (self.JXC.read(self.JXC.OUT3)))
        self.log.log("OUT4 = %d" % (self.JXC.read(self.JXC.OUT4)))
        self.log.log("\n")
        self.log.log("BUSY   = %d" % (self.JXC.read(self.JXC.BUSY  )))
        self.log.log("AREA   = %d" % (self.JXC.read(self.JXC.AREA  )))
        self.log.log("SETON  = %d" % (self.JXC.read(self.JXC.SETON )))
        self.log.log("INP    = %d" % (self.JXC.read(self.JXC.INP   )))
        self.log.log("SVRE   = %d" % (self.JXC.read(self.JXC.SVRE  )))
        self.log.log("*ESTOP = %d" % (self.JXC.read(self.JXC.ESTOP )))
        self.log.log("*ALARM = %d" % (self.JXC.read(self.JXC.ALARM )))
        self.log.log("\n")
        self.log.log("BUSY1   = %d" % (self.JXC.read(self.JXC.BUSY1 )))
        self.log.log("BUSY2   = %d" % (self.JXC.read(self.JXC.BUSY2 )))
        self.log.log("BUSY3   = %d" % (self.JXC.read(self.JXC.BUSY3 )))
        self.log.log("\n")
        self.log.log("AREA1   = %d" % (self.JXC.read(self.JXC.AREA1 )))
        self.log.log("AREA2   = %d" % (self.JXC.read(self.JXC.AREA2 )))
        self.log.log("AREA3   = %d" % (self.JXC.read(self.JXC.AREA3 )))
        self.log.log("\n")
        self.log.log("INP1    = %d" % (self.JXC.read(self.JXC.INP1  )))
        self.log.log("INP2    = %d" % (self.JXC.read(self.JXC.INP2  )))
        self.log.log("INP3    = %d" % (self.JXC.read(self.JXC.INP3  )))
        self.log.log("\n")
        self.log.log("*ALARM1 = %d" % (self.JXC.read(self.JXC.ALARM1)))
        self.log.log("*ALARM2 = %d" % (self.JXC.read(self.JXC.ALARM2)))
        self.log.log("*ALARM3 = %d" % (self.JXC.read(self.JXC.ALARM3)))
        self.log.log("\n")
        return True

    def ALARM(self):
        self.log.log("*ALARM1 = %d" % (self.JXC.read(self.JXC.ALARM1)))
        self.log.log("*ALARM2 = %d" % (self.JXC.read(self.JXC.ALARM2)))
        self.log.log("*ALARM3 = %d" % (self.JXC.read(self.JXC.ALARM3)))
        return self.__isAlarm()

    def ALARM_GROUP(self):
        if self.__isAlarm():
            for k in self.alarm_group.keys():
                if self.JXC.read(self.alarm_group[k]):
                    self.log.log("NOTIFY: ALARM_GROUP '%s' detected" % (k), stdout=False)
                    return k
                else:
                    continue
        else:
            self.log.log("FATAL: ALARM_GROUP identification failed: no alarm detected")
            return None
        self.log.log("FATAL: ALARM_GROUP idenfitication failed: unknown output")
        self.log.log("OUT0 = %d" % (self.JXC.read(self.JXC.OUT0)))
        self.log.log("OUT1 = %d" % (self.JXC.read(self.JXC.OUT1)))
        self.log.log("OUT2 = %d" % (self.JXC.read(self.JXC.OUT2)))
        self.log.log("OUT3 = %d" % (self.JXC.read(self.JXC.OUT3)))
        return None
            
    # ***** Private Methods ******
    def __isMoving(self):
        if self.JXC.read(self.JXC.BUSY) and not self.JXC.read(self.JXC.INP):
            return True
        else:
            return False
    def __isReady(self):
        if not self.JXC.read(self.JXC.BUSY) and self.JXC.read(self.JXC.INP) and self.JXC.read(self.JXC.SETON):
            return True
        else:
            return False
    def __isPowered(self,timeout=5.):
        t = 0. #stopwatch
        while t < timeout:
            if not self.JXC.read(self.JXC.SVRE):
                tm.sleep(self.timestep)
                t += self.timestep
                continue
            else:
                return True #Finished before timeout
        return False #Could not finish before timeout
    def __isAlarm(self):
        if not self.JXC.read(self.JXC.ALARM):
            return True
        else:
            return False
    def __wait(self,stepNum=None,timeout=None):
        if timeout is None:
            timeout = self.timeout
        #Check if step output has been turned on
        if stepNum is not None:
            for addr in self.step_inputs[stepNum]:
                if not self.JXC.read(addr):
                    self.log.log("FATAL: STEP FAILURE. 'OUT' values for Step Number %d not turned on")
                    return False
        #Check immediately to suspect a failed move operation
        if not self.__isMoving():
            self.log.log("WARNING: Suspected failed move due to an immediate finish!!")
        t = 0. #stopwatch
        while t < timeout:
            if self.__isMoving():
                tm.sleep(self.timestep)
                t += self.timestep
                continue
            else:
                return True #Finished before timeout
        return False #Could not finish before timeout
    def __zeroInputs(self):     
        self.JXC.set_off(self.JXC.IN0)
        self.JXC.set_off(self.JXC.IN1)
        self.JXC.set_off(self.JXC.IN2)
        self.JXC.set_off(self.JXC.IN3)
        self.JXC.set_off(self.JXC.IN4)
        if self.JXC.read(self.JXC.IN0) or self.JXC.read(self.JXC.IN1) or self.JXC.read(self.JXC.IN2) or self.JXC.read(self.JXC.IN3) or self.JXC.read(self.JXC.IN4):
            self.log.log("FATAL: Failed to zero inputs")
            return False
        else:
            return True
