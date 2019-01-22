import numpy as np
import scipy.optimize as opt
from collections import deque
import location as loc
import os
import sys

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
        self.__clean_clock()
        self.__check_sync()
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
    
    #Clean the clock array
    #Basic algorithm: if subsequent revolutions are not synchronized, the some revolution has the wrong number of packets
    #Eventually, we probably want to divide this up into smaller than one-hour chunks
    #Allowed deviation from perfect rotation is 10%
    def __clean_clock(self):
        self.encoder_clock_byRev = self.encoder_clock.reshape(self.numRevs, self.edgesPerRev)
        #Take difference over revolutions
        vert_diff = np.diff(self.encoder_clock_byRev, axis=0)
        print "Number of revolutions before cleaning:", self.numRevs

        #Mandate that the first two revolutions are clean
        while True:
            rotPeriod = np.mean(vert_diff[0])
            slitDist = rotPeriod/self.edgeScalar #Average time difference between slits
            if np.logical_or(np.any(vert_diff[0] > rotPeriod + self.dev*slitDist),
                             np.any(vert_diff[0] < rotPeriod - self.dev*slitDist)):
                self.encoder_clock_byRev = np.delete(self.encoder_clock_byRev, 0, axis=0)
                vert_diff                = np.delete(vert_diff,                0, axis=0)
                self.numRevs -= 1
            else:
                self.period   = rotPeriod
                self.slitDist = slitDist
                break

        #Find location of reference slit using the first revolution
        horiz_diff = np.diff(self.encoder_clock_byRev[0])
        self.refIndex = np.where(np.logical_and(horiz_diff < 3.*self.slitDist*(1 + self.dev),
                                                horiz_diff > 3.*self.slitDist*(1 - self.dev)))[0][0]+1
        #Find dropped or added packets using reference slit for each revolution
        for i in range(self.numRevs-1):
            #Index names for self.encoder_clock_byRev to avoid confusion with indexing of diff
            lastRev = i
            thisRev = i+1
            nextRev = i+2

            horiz_diff = np.diff(self.encoder_clock_byRev[thisRev])
            #If reference slit is in the wrong location, this revolution has dropped or added packets
            #Interpolate the entire revolution and correct all future revolutions
            if (horiz_diff[self.refIndex-1] < 3.*self.slitDist*(1 - self.dev)):
                #Where is reference slit in this revolution?
                refLoc = np.where(horiz_diff > 3.*self.slitDist*(1 - self.dev))[0]+1
                #If there is more than one reference slit located, this revolution has > 2 packets dropped in a row at least once
                if len(refLoc) > 1:
                    #Interpolate the entire revolution and trust next revolution to correct the offset
                    self.encoder_clock_byRev[thisRev] = self.encoder_clock_byRev[lastRev] + np.diff(self.encoder_clock_byRev[(lastRev-1):thisRev], axis=0)
                    continue
                #Else try to synchronize revolutions
                else:
                    #Number of packets to add
                    pcktsToAdd = int(self.refIndex - refLoc)
                    #Packets need to be added
                    if pcktsToAdd > 0:
                        #Shift the last [pktsToAdd] packets from this revolution into the next
                        self.encoder_clock_byRev = np.insert(self.encoder_clock_byRev.flatten(), nextRev*self.edgesPerRev,
                                                             self.encoder_clock_byRev[-pktsToAdd:])[:-pktsToAdd].reshape(self.numRevs, self.edgesPerRev)
                        #Interpolate entire revolution
                        self.encoder_clock_byRev[thisRev] = self.encoder_clock_byRev[lastRev] + np.diff(self.encoder_clock_byRev[(lastRev-1):thisRev], axis=0)
                        continue
                    #Packets need to be subtracted
                    elif pcktsToAdd < 0:
                        #Delete the first [-pktsToAdd] packets from the next revolution
                        self.encoder_clock_byRev = np.append(np.delete(self.encoder_clock_byRev.flatten(), nextRev*self.edgesPerRev+np.arange(-pcktsToAdd),
                                                                       np.array([-1 for i in range(-pcktsToAdd)]))).reshape(self.numRevs, self.edgesPerRev)
                        #Interpolate entire revolution
                        self.encoder_clock_byRev[thisRev] = self.encoder_clock_byRev[lastRev] + np.diff(self.encoder_clock_byRev[(lastRev-1):thisRev], axis=0)
                        continue
                    else:
                        print "Something weird is going on with logical comparisons..."
                        #Array is actually fine?
                        continue
            #Packet drop falling on top of reference slit
            elif (horiz_diff[self.refIndex-1] > 3.*self.slitDist*(1 + self.dev)):
                #Interpolate the entire revolution and trust next revolution to correct the offsets
                self.encoder_clock_byRev[thisRev] = self.encoder_clock_byRev[lastRev] + np.diff(self.encoder_clock_byRev[(lastRev-1):thisRev], axis=0)
                continue
            #Else the revolution is synchronized
            else:
                continue
        #Clean the end of the arrays
        self.encoder_clock_byRev = np.delete(self.encoder_clock_byRev, np.where(self.encoder_clock_byRev < 0)[0], axis=0)
        self.numRevs = len(self.encoder_clock_byRev)

        #Clean the arrays of jitter
        vert_diff = np.diff(self.encoder_clock_byRev, axis=0)
        #Rotation period and standard deviation at each rotation
        vert_diff_avg = np.mean(vert_diff, axis=1)
        vert_diff_std = np.std( vert_diff, axis=1)
        #Jitter locations
        jitter_locs = np.where(np.logical_or(vert_diff < (vert_diff_avg*(1 - 5.*vert_diff_std)).reshape(self.numRevs-1,1),
                                             vert_diff > (vert_diff_avg*(1 + 5.*vert_diff_std)).reshape(self.numRevs-1,1)))
        if np.array(jitter_locs).size:
            jitter_locs = jitter_locs[0] + 1 #Account for fact diff index is off from target index by one
            #Replace with averages
            np.put(self.encoder_clock_byRev, jitter_locs, vert_diff_avg[jitter_locs[0]-1])

        #Finished cleaning
        print "Number of revolutions after cleaning:", self.numRevs
        return

    #Check whether the revolutions are synchronized
    def __check_sync(self):
        horiz_diff = np.diff(self.encoder_clock_byRev, axis=1)
        refIndexes = np.where(np.logical_and(horiz_diff < 3.*self.slitDist*(1 + self.dev),
                                             horiz_diff > 3.*self.slitDist*(1 - self.dev)))[1]+1
        if np.any(refIndexes != self.refIndex):
            print "Cleaning failed!"
            print "Following revolutions failed cross-check:", np.where(refIndexes != self.refIndex)[0]
            return False
        else:
            print "Data synchronized"
            return True
                        
    #Function to fill in the empty slits on the blocked-off refrence slit
    def __fill_ref_slit(self):
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
    for i in (11*np.array(range(len(IRIGList)/11))):
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
