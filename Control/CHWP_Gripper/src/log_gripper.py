# Built-in python modules
import time as tm
import datetime as dt
import os


class Logging:
    """ The Logging object saves logging messages """
    def __init__(self):
        self._log_dir = os.path.join(
            os.path.split(os.path.realpath(__file__))[0], "..", "LOG")
        fname = os.path.join(self._log_dir, ("log_%d" % (tm.time())))
        self._log_file = open(fname, 'w')

    def __del__(self):
        self.logfile.close()

    # ***** Public Methods *****
    def log(self, msg):
        wrmsg = self._wrmsg(msg)
        self._log_file.write(wrmsg + '\n')
        return

    def err(self, msg):
        self._wrmsg(msg)
        self._log_file.write(wrmsg + '\n')
        print(wrmsg,)
        return

    def out(self, msg):
        self._wrmsg(msg)
        self._log_file.write(wrmsg + '\n')
        print(msg)
        return

    # ***** Helper Methods *****
    def _wrmsg(self, msg):
        now = dt.datetime.now()
        wrmsg = (
            "[%04d-%02d-%02d %02d:%02d:%02d] %s"
            % (now.year, now.month, now.day, now.hour,
               now.minute, now.second, msg))
        return wrmsg
