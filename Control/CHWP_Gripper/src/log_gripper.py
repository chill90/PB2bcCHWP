#Python 2 compatibility
from __future__ import print_function

#Class that logs actuator activity
import time     as tm
import datetime as dt
import             os

#Logging class
# logLevel = 1 -- print everything
# logLevel = 0 -- print only some things
class Logging:
    def __init__(self, logLevel=1):
        self.logLevel = logLevel
        self.logdir = '/'.join(os.path.realpath(__file__).split('/')[:-1])+("/../LOG/")
        self.logfile = open("%s/log_%d.txt" % (self.logdir, tm.time()), 'w')
        
    def __del__(self):
        self.logfile.close()

    # ***** Public Methods *****
    def log(self, msg):
        now = dt.datetime.now()
        wrmsg = '[%04d-%02d-%02d %02d:%02d:%02d] %s' % (now.year, now.month, now.day, now.hour, now.minute, now.second, msg)
        self.logfile.write(wrmsg+'\n')
        if self.logLevel == 1:
            print(wrmsg,)

    def err(self, msg):
        now = dt.datetime.now()
        wrmsg = '[%04d-%02d-%02d %02d:%02d:%02d] ERROR: %s' % (now.year, now.month, now.day, now.hour, now.minute, now.second, msg)
        self.logfile.write(wrmsg+'\n')
        raise Exception(wrmsg)

    def wrn(self, msg):
        now = dt.datetime.now()
        wrmsg = '[%04d-%02d-%02d %02d:%02d:%02d] WARNING: %s' % (now.year, now.month, now.day, now.hour, now.minute, now.second, msg)
        self.logfile.write(wrmsg+'\n')
        if self.logLevel == 1:
            print(wrmsg,)
        return
