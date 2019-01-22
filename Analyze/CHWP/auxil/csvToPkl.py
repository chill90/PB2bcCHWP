import numpy
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
        sys.exit("Usage: python csvToPkl.py [Run Name]\n")
    else:
        runName = str(args[0])
        loadDir = loc.masterDir+runName+"/rawData/"
        if not os.path.exists(loadDir):
            sys.exit("FATAL: Raw data directory %s not found\n" % (loadDir))
        saveDir = loadDir

    #Data files
    lfname1 = loadDir+"/Encoder_Data_"+runName+".csv"
    lfname2 = loadDir+"/IRIG_Data_"+runName+".csv"
    sfname1 = saveDir+"/Encoder_Data_"+runName+".pkl"
    sfname2 = saveDir+"/IRIG_Data_"+runName+".pkl"
    if not os.path.exists(lfname1):
        sys.exit("FATAL: Encoder Data file %s does not exist\n" % (lfname1))
    if not os.path.exists(lfname2):
        sys.exit("FATAL: IRIG Data file %s does not exist\n" % (lfname2))
    
    # Opens the Encoder file
    print "Loading encoder CSV file..."
    with open(lfname1,"r") as EncoderFile:
        EncoderFileReader = csv.reader(EncoderFile)
        # List which will hold the Encoder information
        EncoderList = deque()

        # Iterate through the rows of the file
        for row in EncoderFileReader:
            # Only use non empty rows
            if len(row) != 0:
                # Convert the row entries to ints and then append them to EncoderList
                try:
                    EncoderList.append(map(int,row))
                # If the row cannot be converted to an int then pass
                except:
                    pass

    # Opens the IRIG file
    print "Loading IRIG CSV file..."
    with open(lfname2, "r") as IRIGFile:
        IRIGFileReader = csv.reader(IRIGFile)
        # List which will hold the IRIG information
        IRIGList = deque()

        # Iterate through the rows of the file
        for row in IRIGFileReader:
            # Only use non empty rows
            if len(row) != 0:
                #Convert the row entries to ints and then append them to IRIGList
                try:
                    IRIGList.append(map(int,row))
                # If the row cannot be converted to an int then pass
                except:
                    pass

    #Save encoder and irig files
    print "Saving encoder data to PKL file..."
    numpy.save(open(sfname1, 'wb'), numpy.array(EncoderList))
    print "Saving IRIG data to PKL file..."
    numpy.save(open(sfname2, 'wb'), numpy.array(IRIGList))
    print "Done"
    
