import time
import sys
import os
import location as loc
import TC_340 as TC

if __name__ == "__main__":
    if not len(sys.argv) == 2 and not len(sys.argv) == 1:
        sys.exit("Usage: python lakeshoreTemperatureMonitor.py [Run Name]\n")
    elif len(sys.argv) == 1:
        noSave = True
    else:
        noSave = False
        runName = str(sys.argv[1])
        saveDir = loc.masterDir+runName+'/Data/'
        if not os.path.exists(saveDir):
            print "Creating directory %s..." % (saveDir)
            os.makedirs(saveDir)

    tc = TC.TC_340()
    titleStr = "%-20s%-10s%-10s%-10s%-10s\n" % ("Time [sec]", "Ch A [K]", "Ch B [K]", "Ch C [K]", "Ch D [K]")
    if not noSave:
        fname = saveDir+'lakeshoreTemperature_%d.txt' % (time.time())
        print "Saving temperature data to file '%s'" % (fname)
        f = open(fname, 'w+')
        f.write(titleStr)
        f.close()
    else:
        print "\n***** NOT SAVING DATA TO A FILE *****\n"
    print titleStr,

    #Loop until a keyboard interrupt
    while True:
        t = tc.get_temps()
        writeStr = "%-20d%-10.02f%-10.02f%-10.02f%-10.02f\n" % (time.time(), t[0], t[1], t[2], t[3])
        if not noSave:
            f = open(fname, "a+")
	    f.write(writeStr)	
            f.close()
        print writeStr,
        time.sleep(30)
