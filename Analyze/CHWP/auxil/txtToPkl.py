import numpy as np
import csv
import sys
import os
from collections import deque
import location as loc

#****************** Main ***************************

# Portion of the code that runs
if __name__ == '__main__':
    #Use command-line arguments to obtain locaiton of the data to be processed
    args = sys.argv[1:]
    if not len(args) == 1:
        sys.exit("Usage: python txtToPkl.py [Run Name]\n")
    else:
        runName = str(args[0])
        loadDir = loc.masterDir+runName+"/Data/"
        if not os.path.exists(loadDir):
            sys.exit("FATAL: Raw data directory %s not found\n" % (loadDir))
        saveDir = loadDir

    #Data files
    lfname1 = loadDir+"/Angle_Time_"+runName+".txt"
    lfname2 = loadDir+"/Clock_Count_"+runName+".txt"
    sfname1 = saveDir+"/Angle_Time_"+runName+".pkl"
    sfname2 = saveDir+"/Clock_Count_"+runName+".pkl"
    if not os.path.exists(lfname1):
        sys.exit("FATAL: Encoder Data file %s does not exist\n" % (lfname1))
    if not os.path.exists(lfname2):
        sys.exit("FATAL: IRIG Data file %s does not exist\n" % (lfname2))
    
    # Opens files
    print "Loading angle vs time txt file..."
    angle, time  = np.loadtxt(lfname1, unpack=True, dtype=np.float)
    clock, count = np.loadtxt(lfname2, unpack=True, dtype=np.float)

    #Saves files
    np.save(open(sfname1, 'wb'), np.array([angle, time ]).T)
    np.save(open(sfname2, 'wb'), np.array([clock, count]).T)

    print 'Done'
