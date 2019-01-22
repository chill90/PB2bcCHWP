import time
import os
import sys
import glob

import src.SIM_900     as SIM
import config.location as loc
import config.config   as cfg

if __name__ == "__main__":
    if len(sys.argv) > 3:
        sys.exit("\nUsage: python srsTemperatureMonitor.py [Run Name] ['Single']\n")
    elif len(sys.argv) == 1:
        noSave = True
    elif len(sys.argv) == 2 or len(sys.argv) == 3:
        noSave = False
        runName = str(sys.argv[1])
        runDir  = loc.masterDir+runName
        if not os.path.exists(runDir):
            print "Creating directory %s..." % (runDir)
            os.makedirs(runDir)
        #saveDir = runDir+'/Data/'
        saveDir = runDir+'/'
        if not os.path.exists(saveDir):
            print "Creating directory %s..." % (saveDir)
            os.makedirs(saveDir)
        if len(sys.argv) == 3:
            if str(sys.argv[2]).upper().strip() == 'SINGLE':
                appendFile = True
            else:
                sys.exit('Did not understand command %s' % (str(sys.argv[2])))
        else:
            appendFile = False

    #Connect to SIM922
    sim = SIM.SIM_900(cfg.SRSPort, cfg.SRSSlot)
    slots = cfg.SRSSlot

    #Construct title string
    titleStr = "%-20s" % ("Time [sec]")
    for slot in slots:
        titleStr = titleStr+"%-20s%-20s%-20s%-20s" % ("Slot %d, Ch 1 [K]" % (slot), "Slot %d, Ch 2 [K]" % (slot), "Slot %d, Ch 3 [K]" % (slot), "Slot %d, Ch 4 [K]" % (slot))
    titleStr = titleStr+'\n'

    #Connect to file
    if not noSave:
        if appendFile:
            arr = glob.glob(saveDir+'*.txt'); arr.sort(); fname = arr[-1]
        else:
            fname = saveDir+'srsTemperature_%d.txt' % (time.time())
        if not os.path.isfile(fname):
            f = open(fname, 'w+')
            f.write(titleStr)
            f.close()
        print "Saving temperature data to file '%s'" % (fname)
    else:
        print "*************************************"
        print "***** NOT SAVING DATA TO A FILE *****"
        print "*************************************"
    print titleStr,

    #Loop until a keyboard interrupt
    while True:
        try:
            t = sim.get_temps()
            writeStr = "%-20d" % (time.time())
            for i in range(len(slots)):
                writeStr = writeStr+("%-20.02f%-20.02f%-20.02f%-20.02f" % (float(t[i*4+0]), float(t[i*4+1]), float(t[i*4+2]), float(t[i*4+3])))
            writeStr = writeStr+'\n'
            if not noSave:
                f = open(fname, "a+")
	        f.write(writeStr)	
                f.close()
            print writeStr,
            if appendFile:
                break
            else:
                time.sleep(30)
        except KeyboardInterrupt:
            sys.exit('Exiting...')
