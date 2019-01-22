import numpy as np
import scipy.optimize as opt
from collections import deque
import location as loc
import os
import sys

#Difference between spin-up and spin-down files is how the reference slit is searched for
#Spin-up is searched from the back, spin-down is searched from the front

class EncoderProcess:
    def __init__(self, IRIG_time, IRIG_clock, encoder_clock, encoder_count, edgeScalar=1140):
        if ((len(IRIG_time) != len(IRIG_clock)) or (len(encoder_clock) != len(encoder_count))):
            print "Data Length Error"
            return

        #Save passed parameters
        self.IRIG_time = np.array(IRIG_time)
        self.IRIG_clock = np.array(IRIG_clock)
        self.encoder_clock = np.array(encoder_clock)
        self.encoder_count = np.array(encoder_count)
        self.edgeScalar  = int(edgeScalar)

        #Number of edges per revolution taking into account the reference slit
        self.edgesPerRev = int(self.edgeScalar-2)

        #Divide up the encoder data into revolutions
        self.numEncoderCounts    = len(self.encoder_clock)
        self.numRevs             = self.numEncoderCounts/self.edgesPerRev
        self.numClippedPackets   = self.numEncoderCounts%self.edgesPerRev
        self.encoder_clock       = self.encoder_clock[:-self.numClippedPackets]
        self.encoder_clock_byRev = self.encoder_clock.reshape(self.numRevs,self.edgesPerRev)

        #Tolerances for packet drop and jitter
        self.dev = 0.1 #10% of the slit width for now

        return

    #Generate angle vs time
    def convert_to_angle(self):
        #Clean the data
        self.__account_for_missed_overflow()
        self.__account_for_wrapping()
        self.__account_for_next_day()
        self.__fill_ref_slit()
        self.__check_shape()

        #Create clock vs count
        self.encoder_clock = self.encoder_clock_byRev.flatten()
        self.encoder_count = np.arange(self.encoder_clock.size)
        #Create angle vs time
        self.angle = self.encoder_count*(2.*np.pi/float(self.edgeScalar))
        self.time  = np.interp(self.encoder_clock, self.IRIG_clock, self.IRIG_time, left=-1, right=-1)
        mask = self.time >= 0
        self.time  = self.time[mask]
        self.angle = self.angle[mask]
        self.time  = self.time - self.time[0]
        
        return

    # Due to the nature of the Arduino code that are times when a clock count is 2^16 lower
    # than it should be and this function corrects for that
    def __account_for_missed_overflow(self):
        diff = np.ediff1d(self.encoder_clock,to_begin=0)
        self.encoder_clock = self.encoder_clock + (2**16)*(diff < -2**12)*(diff > -2**24)
        return

    # Whenever input_array[i] > input_array[i+1], add 2^nbits to input_array[j] for all j>i
    # This accounts for the Arduino counter overflowing and insures that the the array is always increasing
    def __account_for_wrapping(self):
        for i in np.where(np.diff(self.encoder_clock) < 0)[0]:
            self.encoder_clock[i+1:] += int(2.**32)
        for i in np.where(np.diff(self.IRIG_clock,  ) < 0)[0]:
            self.IRIG_clock[i+1:]    += int(2.**32)
        return

    # Accounts for wrapping in the IRIG time when the day changes
    def __account_for_next_day(self):
        for i in np.where(np.diff(self.IRIG_time) < 0)[0]:
            self.IRIG_time[i+1:] += 24*3600
        return
    
    #Function to fill in the empty slits on the blocked-off refrence slit
    def __fill_ref_slit(self):
        self.encoder_clock_byRev = self.encoder_clock.reshape(self.numRevs, self.edgesPerRev)

        #Find location of reference slit using the final revolution
        horiz_diff = np.diff(self.encoder_clock_byRev[-1])
        slitDist   = np.mean(horiz_diff)
        self.refIndex = np.where(np.logical_and(horiz_diff < 3.*slitDist*(1 + self.dev),
                                                horiz_diff > 3.*slitDist*(1 - self.dev)))[0][0]+1

        insertArrs    = np.array([[(self.encoder_clock_byRev[:,self.refIndex-2][i] + self.encoder_clock_byRev[:,self.refIndex+0][i])/2.,
                                   (self.encoder_clock_byRev[:,self.refIndex-1][i] + self.encoder_clock_byRev[:,self.refIndex+1][i])/2.] for i in range(self.numRevs)])
        self.encoder_clock_byRev = np.insert(self.encoder_clock_byRev, self.refIndex, np.round(insertArrs.T), axis=1)
        return

    #Function to check data array shape
    def __check_shape(self):
        shape = np.shape(self.encoder_clock_byRev)
        if shape[0]%self.numRevs or shape[1]%self.edgeScalar:
            print "Non-integer number of rotation or irregular array shape..."
        return

#****************** Main ***************************

# Portion of the code that runs
if __name__ == '__main__':
    #Use command-line arguments to obtain locaiton of the data to be processed
    args = sys.argv[1:]
    if not len(args) == 1:
        sys.exit("Usage: python encoderDataProcess.py [Run Name]\n")
    else:
        runName = str(args[0])
        loadDir = loc.masterDir+runName+"/rawData/"
        if not os.path.exists(loadDir):
            sys.exit("FATAL: Raw data directory %s not found\n" % (loadDir))
        saveDir = loc.masterDir+runName+"/Data/"
        if not os.path.exists(saveDir):
            print "Creating directory %s..." % (saveDir)
            os.makedirs(saveDir)
        #For now, process all the data points
        startTime = 0
        endTime   = None

    #Data files
    fname1 = loadDir+"/Encoder_Data_"+runName+".pkl"
    fname2 = loadDir+"/IRIG_Data_"+runName+".pkl"
    if not os.path.exists(fname1):
        sys.exit("FATAL: Encoder Data file %s does not exist\n" % (fname1))
    if not os.path.exists(fname2):
        sys.exit("FATAL: IRIG Data file %s does not exist\n" % (fname2))
    
    # Opens the Encoder file
    print "Loading Encoder data..."
    EncoderList = np.load(open(fname1, 'rb'))
    # Opens the IRIG file
    print "Loading IRIG data..."
    IRIGList = np.load(open(fname2, 'rb'))
    
    #********************************
    #***** Prepare Encoder Data *****
    #********************************

    print "Preparing encoder data..."
    # Convert the deque() to a list
    EncoderList = list(EncoderList)

    # Arrays to hold the data point's number and clock count
    EcntList = deque()
    EclkList = deque()
     
    # Iterate through every packet of information
    #for i in range((len(EncoderList))/152):
    for i in range(len(EncoderList)):
        # Use either the correction from the packet or the last correction value
        #packet_correction = EncoderList[1+i*152][1]-(EncoderList[1+i*152][2]+EncoderList[1+i*152][0])/2
        #if (packet_correction > -5000) and (packet_correction < 5000):
        #    correct_value = packet_correction
        #    last_correction = packet_correction
        #else:
        #    correct_value = last_correction
 
        # Within the packet only use the data values
        # Ignore the quadrature values
        for j in range(150):
            #EcntList.append(EncoderList[2+i*152+j][0])
            #EclkList.append(EncoderList[2+i*152+j][1]+correct_value)
            #EclkList.append(EncoderList[2+i*152+j][1])
            EclkList.append(EncoderList[i][0][j])
            EcntList.append(EncoderList[i][1][j])


    #*****************************
    #***** Prepare IRIG Data *****
    #*****************************

    print "Preparing IRIG data..."
    # Convert the deque() to a list
    IRIGList = list(IRIGList)

    # Arrays to hold the data point's UTC time and clock count
    ItimeList = deque()
    IclkList = deque()

    # Iterate through every packet of information
    #for i in (11*np.array(range(len(IRIGList)/11))):
    #    ItimeList.append(IRIGList[i][0])
    #    IclkList.append( IRIGList[i][1])
    for i in range(len(IRIGList)):
        ItimeList.append(IRIGList[i][0][0])
        IclkList.append(IRIGList[i][0][1])

    #************************
    #***** Process Data *****
    #************************

    print "Processing data..."
    ep = EncoderProcess(ItimeList, IclkList, EclkList, EcntList)
    ep.convert_to_angle()

    print "Storing angle vs time data..."
    if endTime:
        mask     = ((ep.time > startTime) and (ep.time < endTime))
        ep.angle = ep.angle[mask]
        ep.time  = ep.time[mask]
    else:
        mask     = (ep.time > startTime)
        ep.angle = ep.angle[mask]    
        ep.time  = ep.time[mask]

    #Save angle vs time to a PKL file
    savefile = saveDir+"/Angle_Time_"+runName+".pkl"
    savearr  = np.array([ep.time, ep.angle]).T
    np.save(open(savefile, 'wb'), savearr)

    #Save encoder count vs encoder clock to a file
    savefile = saveDir+"/Clock_Count_"+runName+".pkl"
    savearr  = np.array([ep.encoder_clock, ep.encoder_count]).T
    np.save(open(savefile, 'wb'), savearr)

    print 'Done'
