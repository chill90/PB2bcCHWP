import socket
import numpy as np
import struct
import copy
import time
from collections import deque
import select
import csv
import datetime
import sys
import os
import location as loc

# The number of datapoints in every encoder packet from the Arduino
COUNTER_INFO_LENGTH = 150
# The size of the encoder packet from the Arduino (header + 3*150 datapoint information + 3 quadrature readout + 3 synch check)
COUNTER_PACKET_SIZE = 2 + 6 * COUNTER_INFO_LENGTH + 6 + 6
# The size of the IRIG packet from the Arduino
IRIG_PACKET_SIZE = 66


# Class which will parse the incoming packets from the Arduino and store the data in CSV files
class EncoderParser(object):
    # port: This must be the same as the localPort in the Arduino code
    # date, run: Used for naming the CSV file (will be changed later on in the code by a user input)
    # read_chunk_size: This value shouldn't need to change
    def __init__(self, saveDir, date = "test", run = "test", arduino_port = 8888, read_chunk_size = 8196):
        #Directory to save files
        self.saveDir = saveDir
        
        # Creates three lists to hold the data from the encoder, IRIG, and quadrature respectively
        self.counter_queue = deque()
        self.irig_queue = deque()
        self.quad_queue = deque()

        # Used for procedures that only run when data collection begins
        self.is_start = 1
        # Will hold the time at which data collection started [hours, mins, secs]
        self.start_time = [0,0,0]
        # Will be continually updated with the UTC time in seconds
        self.current_time = 0

        # Creates a UDP socket to connect to the Arduino
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Binds the socket to a specific ip address and port
        # The ip address should be the same as the remote_ip in the Arduino code
        self.s.bind(('192.168.1.1', arduino_port))
        self.s.setblocking(0)

        # String which will hold the raw data from the Arduino before it is parsed
        self.data = ''
        self.read_chunk_size = read_chunk_size

        # Keeps track of how many packets have been parsed
        self.counter = 0

        # Date and run number used to name the CSV file
        self.date = date
        self.run = run

        # Creates two PKL files to hold the Encoder and IRIG data
        self.fname_encoder = self.saveDir+"/Encoder_Data_"+self.run+".pkl"
        self.fname_irig    = self.saveDir+"/IRIG_Data_"+self.run+".pkl"

    # Converts the IRIG signal into sec/min/hours depending on the parameters
    def de_irig(self, val, base_shift=0):
        return (((val >> (0+base_shift)) & 1) + 
                ((val >> (1+base_shift)) & 1) * 2 + 
                ((val >> (2+base_shift)) & 1) * 4 + 
                ((val >> (3+base_shift)) & 1) * 8 + 
                ((val >> (5+base_shift)) & 1) * 10 + 
                ((val >> (6+base_shift)) & 1) * 20 + 
                ((val >> (7+base_shift)) & 1) * 40 )

    # Takes the IRIG information, prints it to the screen, sets the current time,
    # and returns the current time
    def pretty_print_irig_info(self, v, edge):
        # Calls self.de_irig() to get the sec/min/hour of the IRIG packet
        secs = self.de_irig(v[0], 1)
        mins = self.de_irig(v[1], 0)
        hours = self.de_irig(v[2], 0)

        # If it is the first time that the function is called then set self.start_time
        # to the current time
        if self.is_start == 1:
            self.start_time = [hours, mins, secs]
            self.is_start = 0

        # Find the sec/min/hour digit difference from the start time
        dsecs = secs - self.start_time[2]
        dmins = mins - self.start_time[1]
        dhours = hours - self.start_time[0]

        # Corrections to make sure that dsecs/dmins/dhours are all positive
        if dhours < 0:
            dhours = dhours + 24

        if (dmins < 0)or((dmins == 0)and(dsecs < 0)):
            dmins = dmins + 60
            dhours = dhours - 1

        if dsecs < 0:
            dsecs = dsecs + 60
            dmins = dmins - 1
        
        # Print UTC time, run time, and current clock count of the Arduino
        print "Current Time:",("%d:%d:%d"%(hours, mins, secs)),"Run Time",("%d:%d:%d"%(dhours, dmins, dsecs)), "Clock Count",edge

        # Set the current time in seconds
        self.current_time = secs + mins*60 + hours*3600

        return self.current_time

    # Checks to make sure that self.data is the right size
    # Return false if the wrong size, return true if the data is the right size
    def check_data_length(self, start_index, size_of_read):
        if start_index + size_of_read > len(self.data):
            self.data = self.data[start_index:]
            print "UH OH"
            return False
        else:
            return True

    # Grabs self.data, determine what packet it corresponds to, parses the data, and
    # records it to CSV file
    def grab_and_parse_data(self):
        while True:
            try :
                # If there is data from the socket attached to the Arduino then ready[0] = true
                # If not then continue checking for 2 seconds and if there is still no data ready[0] = false
                ready = select.select([self.s],[],[],2)
                if ready[0]:
                    # Add the data from the socket attached to the Arduino to the string self.data
                    self.data += self.s.recv(self.read_chunk_size)
                    while True:
                        # Check to make sure that there is at least 1 int in the packet
                        # The first int in every packet should be the header
                        if not self.check_data_length(0, 2):
                            print 'Error 0'
                            break

                        header = self.data[0 : 2]
                        # Convert a structure value from the Arduino (header) to an int
                        header = struct.unpack('<H', header)[0]

                        # 0x1EAF = Encoder Packet
                        # 0xCAFE = IRIG Packet
                        # 0xE12A = Error Packet
                        
                        # Encoder
                        if header == 0x1EAF:
                            # Make sure the data is the correct length for an Encoder Packet
                            if not self.check_data_length(0, COUNTER_PACKET_SIZE):
                                print 'Error 1'
                                break
                            # Call the meathod self.parse_counter_info() to parse the Encoder Packet
                            self.parse_counter_info(self.data[2 : COUNTER_PACKET_SIZE])
                            # Increment self.counter to signify that an Encoder Packet has been parsed
                            self.counter += 1
                            
                        # IRIG
                        elif header == 0xCAFE:
                            # Make sure the data is the correct length for an IRIG Packet
                            if not self.check_data_length(0, IRIG_PACKET_SIZE):
                                print 'Error 2'
                                break
                            # Call the meathod self.parse_irig_info() to parse the IRIG Packet
                            self.parse_irig_info(self.data[2 : IRIG_PACKET_SIZE])

                        # Error
                        # An Error Packet will be sent if there is a timing error in the 
                        # synchronization pulses of the IRIG packet
                        # If you see 'Packet Error' check to make sure the IRIG is functioning as
                        # intended and that all the connections are made correctly 
                        elif header == 0xE12A:
                            print 'Packet Error'
                            
                        else:
                            print 'Bad header'
                            
                        # Clear self.data
                        self.data = ''
                        break
                    break
            
                # If there is no data from the Arduino 'Looking for data ...' will print
                # If you see this make sure that the Arduino has been set up properly
                else:
                    print 'Looking for data ...'
            except KeyboardInterrupt:
                return

    # Method to parse the Encoder Packet
    def parse_counter_info(self, data):
        # Convert the Encoder Packet structure into a numpy array
        derter = np.array(struct.unpack('<' + 'HHH'*COUNTER_INFO_LENGTH + 'HHH' + 'HHH', data))

        # [0-149] clock counts of 150 data points
        # [150-299] corresponding clock overflow of the 150 data points (each overflow count
        # is equal to 2^16 clock counts)
        # [300-449] corresponding absolute number of the 150 data points ((1, 2, 3, etc ...)
        # or (150, 151, 152, etc ...) or (301, 302, 303, etc ...) etc ...)
        # [450-452] Readout from the quadrature

        # self.counter_queue = [[clock count array],[absolute number array]]
        self.counter_queue.append([derter[0:150] + (derter[150:300] << 16), derter[300:450]])
        # self.quad_queue = [[quad input 2 array],[quad input 3 array],[quad input 4 array]]
        self.quad_queue.append([[derter[450], derter[451], derter[452]], [derter[453], derter[454], derter[455]]])

    # Method to parse the IRIG Packet
    def parse_irig_info(self, data):
        # Convert the IRIG Packet structure into a numpy array
        unpacked_data = struct.unpack('<I' + 'H'*10 + 'I'*10, data)

        # [0] clock count of the IRIG Packet which the UTC time corresponds to
        # [1] binary encoding of the second data
        # [2] binary encoding of the minute data
        # [3] binary encoding of the hour data
        # [4-10] additional IRIG information which we do mot use
        # [11-21] synchronization pulse clock counts

        # Start of the packet clock count
        rising_edge_time = unpacked_data[0]
        # Stores IRIG time data
        irig_info = unpacked_data[1:11]
        # Prints the time information and returns the current time in seconds
        irig_time = self.pretty_print_irig_info(irig_info, rising_edge_time)
        # Stores synch pulse clock counts
        synch_pulse_clock_times = unpacked_data[11:21]

        # self.irig_queue = [Packet clock count,Packet UTC time in sec,[binary encoded IRIG data],[synch pulses clock counts]]
        self.irig_queue.append([[irig_time, rising_edge_time], np.transpose([range(10), synch_pulse_clock_times]).tolist()])

    def __del__(self):
        self.s.close()

# Portion of the code that runs
if __name__ == '__main__':
    #Use command-line arguments to obtain save directory
    args = sys.argv[1:]
    if not len(args) == 2:
        sys.exit("Usage: python encoderDAQ.py [Run Name] [Number of seconds to collect data]\n")
    else:
        runName = str(args[0])
        runtime = int(args[1])
        mode = 0 #Keep this fixed for now

        masterDir = loc.masterDir
        print "All encoder data collected on the CHWP NUC PC is stored in %s" % (masterDir)
        
        if not os.path.isdir(masterDir):
            sys.exit('Master path %s does not exist\n' % (masterDir))
        else:
            inputDir = masterDir+runName+"/"
            if os.path.exists(inputDir):
                while True:
                    overwrite = raw_input("CAUTION: Run name %s already exists at location %s. Overwrite existing data? Y/N [Y]: " % (runName, masterDir))
                    if overwrite == "":
                        break
                    elif "y" in overwrite or "Y" in overwrite:
                        break
                    elif "n" in overwtie or "N" in overwrite:
                        sys.exit("FATAL: Raw data at %s will not be overwritten" % (inputDir))
                    else:
                        print "Did not understand input %s..." % (overwrite)
                        continue
            else:
                os.makedirs(inputDir)
            saveDir = inputDir+"/rawData/"
            if not os.path.exists(saveDir):
                print "Creating directory %s..." % (saveDir)
                os.makedirs(saveDir)

    ep = EncoderParser(saveDir = saveDir, date = str(datetime.date.today()), run = runName)
    print 'Starting'
    
    if (mode == 0):
        # Run until current_time == strat_time + runtime
        start_time = 123456789
        while (start_time+runtime != ep.current_time) and (start_time+runtime != ep.current_time + 24*3600):
            ep.grab_and_parse_data()
            start_time = ep.start_time[0]*3600 + ep.start_time[1]*60 + ep.start_time[2]
    elif (mode == 1):
        # Run until the specified number of packets have been collected
        while data_points > ep.counter:
            ep.grab_and_parse_data()

    #Write data to files
    print 'Saving data to files...'
    np.save(open(ep.fname_encoder, 'wb'), np.array(ep.counter_queue))
    np.save(open(ep.fname_irig, 'wb'),    np.array(ep.irig_queue   ))
    
    print 'Done'
