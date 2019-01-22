#Class that logs actuator activity
import time     as tm
import datetime as dt

class Logging:
    def __init__(self):
        self.logdir = "./LOG"
        self.logfile = open("%s/log_%d.txt" % (self.logdir, tm.time()), 'w')

    def log(self, msg, stdout=True):
        now = dt.datetime.now()
        wrmsg = '[%04d-%02d-%02d %02d:%02d:%02d] %s\n' % (now.year, now.month, now.day, now.hour, now.minute, now.second, msg)
        self.logfile.write(wrmsg)
        if stdout:
            print wrmsg,
