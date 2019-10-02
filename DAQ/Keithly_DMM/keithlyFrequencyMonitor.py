import time
import serial
import sys
import os
import src.DMM_2700 as DMM
import config.location as loc

if __name__ == "__main__":
    if not len(sys.argv) == 2 and not len(sys.argv) == 1:
        sys.exit("Usage: python keithlyFrequencyMonitor.py [Run Name]\n")
    elif len(sys.argv) == 1:
        noSave = True
    else:
        noSave = False
        runName = str(sys.argv[1])
        saveDir = loc.masterDir+runName+'/Data/'
        if not os.path.exists(saveDir):
            print "Creating directory %s..." % (saveDir)
            os.makedirs(saveDir)

    dmm = DMM.DMM_2700()
    titleStr = "%-20s%-20s\n" % ("Time [sec]", "Frequency [Hz]")
    if not noSave:
        fname = saveDir+'keithlyFrequency_%d.txt' % (time.time())
        print "Saving frequency data to file '%s'" % (fname)
        f = open(fname, 'w+')
        f.write(titleStr)
        f.close()
    else:
        print "\n***** NOT SAVING DATA TO A FILE *****\n"
    print titleStr,

    #Loop until a keyboard interrupt
    while True:
        f = dmm.get_frequency()
        writeStr = "%-20f%-20.05f\n" % (time.time(), float(f))
        if not noSave:
            f = open(fname, "a+")
	    f.write(writeStr)	
            f.close()
        print writeStr,
        time.sleep(0.2)
