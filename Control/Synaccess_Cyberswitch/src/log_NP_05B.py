#Python 2 compatibility
from __future__ import print_function, unicode_literals

#Class that logs actuator activity
import time     as tm
import datetime as dt
import             os
import termcolor as tc

class Logging:
    def __init__(self):
        self.logdir = '/'.join(os.path.realpath(__file__).split('/')[:-1])+("/../LOG/")
        self.logfile = open("%s/log_%d.txt" % (self.logdir, tm.time()), 'w')

    def log(self, msg, stdout=True):
        now = dt.datetime.now()
        wrmsg = '[%04d-%02d-%02d %02d:%02d:%02d] %s' % (now.year, now.month, now.day, now.hour, now.minute, now.second, msg)
        self.logfile.write(wrmsg+'\n')
        if stdout:
            print(wrmsg,)

    def err(self, msg):
        now = dt.datetime.now()
        wrmsg = '[%04d-%02d-%02d %02d:%02d:%02d] '+termcolor('CYBERSWITCH ERROR: %s' % (now.year, now.month, now.day, now.hour, now.minute, now.second, msg), 'red')
        self.logfile.write(wrmsg+'\n')
        if stdout:
            print(wrmsg,)
        return

    def wrn(self, msg):
        now = dt.datetime.now()
        wrmsg = '[%04d-%02d-%02d %02d:%02d:%02d] '+termcolor('CYBERSWITCH WARNING: %s' % (now.year, now.month, now.day, now.hour, now.minute, now.second, msg), 'yellow')
        self.logfile.write(wrmsg+'\n')
        if stdout:
            print(wrmsg,)
        return
