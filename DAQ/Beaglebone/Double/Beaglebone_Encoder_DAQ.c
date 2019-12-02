//Used to load code for detecting Encoder and IRIG signals onto PRUs
//Encoder code is loaded onto PRU1 and IRIG code onto PRU0
//
// Usage:
// $ ./Beaglebone_Encoder_DAQ Encoder1.bin Encoder2.bin IRIG1.bin IRIG2.bin
//
// Compile with:
// gcc -o Beaglebone_Encoder_DAQ Beaglebone_Encoder_DAQ.c -lprussdrv

#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
// PRU Subsystem Driver
// (installed from https://github.com/beagleboard/am335x_pru_package)
#include <prussdrv.h>
// PRU Subsystem Interupt Controller Mapping
// (installed from https://github.com/beagleboard/am335x_pru_package)
#include <pruss_intc_mapping.h>
#include <string.h>
//The rest of these libraries are for UDP service
#include <sys/types.h> 
#include <sys/socket.h>
#include <arpa/inet.h>
#include <netinet/in.h>

// Port used for UDP connection
#define PORT 8080

// Below variables are defined in pruss_intc_mapping and prussdrv,
// they are mapping interrupts from PRUs to ARM processor
#define PRUSS_INTC_CUSTOM {   \
    { PRU0_PRU1_INTERRUPT, PRU1_PRU0_INTERRUPT, PRU0_ARM_INTERRUPT, \
      PRU1_ARM_INTERRUPT, ARM_PRU0_INTERRUPT, ARM_PRU1_INTERRUPT,  24, (char)-1  },  \
    { {PRU0_PRU1_INTERRUPT,CHANNEL1}, {PRU1_PRU0_INTERRUPT, CHANNEL0}, \
      {PRU0_ARM_INTERRUPT,CHANNEL2}, {PRU1_ARM_INTERRUPT, CHANNEL3}, \
      {ARM_PRU0_INTERRUPT, CHANNEL0}, {ARM_PRU1_INTERRUPT, CHANNEL1}, \
      {24, CHANNEL3}, {-1,-1}},  \
    { {CHANNEL0,PRU0}, {CHANNEL1, PRU1}, {CHANNEL2, PRU_EVTOUT0}, \
      {CHANNEL3, PRU_EVTOUT1}, {-1,-1} },  \
    (PRU0_HOSTEN_MASK | PRU1_HOSTEN_MASK | PRU_EVTOUT0_HOSTEN_MASK | PRU_EVTOUT1_HOSTEN_MASK) \
}

// Encoder packet size
#define ENCODER_COUNTER_SIZE 150

// Number of packets to send at once
// ~0.3 Hz in normal operation
#define ENCODER_PACKETS_TO_SEND 30
#define IRIG_PACKETS_TO_SEND 3
#define ERROR_PACKETS_TO_SEND 1

// Definining the offsets from the start of shared memory
// for the structures and variables used by PRUs
#define ON_OFFSET 0x0000
#define OVERFLOW_OFFSET 0x0002
#define COUNTER_READY_OFFSET 0x0010
#define COUNTER_OFFSET 0x0012
#define IRIG_READY_OFFSET 0x2000
#define IRIG_OFFSET 0x2002
#define ERROR_READY_OFFSET 0x2300
#define ERROR_OFFSET 0x2302

// Timeout values for each packet type [s]
#define ENCODER_TIMEOUT 10
#define IRIG_TIMEOUT 10

// Timeout flags
#define ENCODER_TIMEOUT_FLAG 1
#define IRIG_TIMEOUT_FLAG 2

// Function which returns pointer to shared memory
// Indexes over memory in 1-byte increments
volatile uint8_t* init_prumem()
{
    volatile uint8_t* p;
	prussdrv_map_prumem(PRUSS0_SHARED_DATARAM, (void**)&p);
	return p;
}

// Structure to store clock count of edges and
// the number of times the counter has overflowed
struct EncoderInfo {
    unsigned short int header;
    unsigned short int quad_value;
    unsigned long int clock[ENCODER_COUNTER_SIZE];
    unsigned long int clock_overflow[ENCODER_COUNTER_SIZE];
    unsigned long int count[ENCODER_COUNTER_SIZE];
};

// IRIG packet
struct IrigInfo{
    unsigned long int header;
    unsigned long int clock;
    unsigned long int clock_overflow;
    unsigned long int info[10];
    unsigned long int synch[10];
    unsigned long int synch_overflow[10];
};

// Error packets sent when IRIG isn't synced
struct ErrorInfo{
    unsigned int header;
    unsigned int err_code;
};

// Packet to send in the event of a data collection timeout
struct TimeoutInfo {
    unsigned short int header;
    unsigned short int type;
};

//Creating pointers to all shared variables and data structures in shared memory
//pointer to variable to let the ARM know that the PRUs are still executing code
volatile unsigned short int* on = (
    volatile unsigned short int*) (init_prumem() + ON_OFFSET);

// Pointer to flag signifying encoder packets are ready to be collected
volatile unsigned short int* encoder_ready = (
    volatile unsigned short int*) (init_prumem() + COUNTER_READY_OFFSET);
// Pointer to data structure for encoder/counter packets
volatile struct EncoderInfo* encoder_packets = (
    volatile struct EncoderInfo*) (init_prumem() + COUNTER_OFFSET);

// Pointer to flag signifying irig packets are ready to be collected
volatile unsigned short int* irig_ready = (
    volatile unsigned short int *) (init_prumem() + IRIG_READY_OFFSET);
// Pointer to data structure for IRIG packets
volatile struct IrigInfo* irig_packets = (
    volatile struct IrigInfo *) (init_prumem() + IRIG_OFFSET);

// Pointer to variable to identify that an error packet is ready to be writtento UDP
volatile unsigned short int* error_ready = (
    volatile unsigned short int *) (init_prumem() + ERROR_READY_OFFSET);
// Pointer to data structure for error packets
volatile struct ErrorInfo* error_packets = (
    volatile struct ErrorInfo *) (init_prumem() + ERROR_OFFSET);

// Local pointer to data structure for timeout packets
volatile struct TimeoutInfo* timeout_packet;

// Arrays for storing packets to be sent over UDP
volatile struct EncoderInfo encoder_to_send[ENCODER_PACKETS_TO_SEND];
volatile struct IrigInfo irig_to_send[IRIG_PACKETS_TO_SEND];
volatile struct ErrorInfo error_to_send[ERROR_PACKETS_TO_SEND];

// ***** LOCAL VARIABLES *****
// For swapping between the two stored packets
unsigned long int offset;
// For indexing over Encoder, IRIG, and Error packets to send out
unsigned short int encd_ind, irig_ind, err_ind;
// Monitor the time since the packet was sent
clock_t curr_time, encd_time, irig_time;
// Creates socket to write UDP packets with
int sockfd;
struct sockaddr_in servaddr;

// **************************
// ********** MAIN **********
// **************************

int main(int argc, char **argv) {
    // *** Configure the PRUs ***
    // Run a bash file to configure the input pins
    system("./pinconfig");
    //checks that the file is executed with correct arguments passed
    if (argc != 5) {
        printf("Usage: %s Beaglebone_Encoder_DAQ Encoder1.bin \
                Encoder2.bin IRIG1.bin IRIG2.bin\n", argv[0]);
        return 1;
    }
    // Initialize PRU subsystem driver
    prussdrv_init();
    // Allow the use of interrupt: PRU_EVTOUT_1
    // Used to notify the ARM that the PRUs have finished
    if (prussdrv_open(PRU_EVTOUT_1) == -1) {
        printf("prussdrv_open() failed\n");
        return 1;
    }
    // Functions to map and initialize the interrupts defined above
    tpruss_intc_initdata pruss_intc_initdata = PRUSS_INTC_CUSTOM;
    prussdrv_pruintc_init(&pruss_intc_initdata);
    // Load code to PRU1
    printf("Executing program on PRU1 and waiting for termination\n");
    if (argc > 2) {
        if (prussdrv_load_datafile(1, argv[2]) < 0) {
            fprintf(stderr, "Error loading %s\n", argv[2]);
            exit(-1);
        }
    }
    if (prussdrv_exec_program(1, argv[1]) < 0) {
        fprintf(stderr, "Error loading %s\n", argv[1]);
        exit(-1);
    }
    // Load code to PRU0
    printf("Executing program on PRU0 and waiting for termination\n");
    if (argc == 5) {
      if (prussdrv_load_datafile(0, argv[4]) < 0) {
          fprintf(stderr, "Error loading %s\n", argv[4]);
          exit(-1);
      }
    }
    if (prussdrv_exec_program(0, argv[3]) < 0) {
        fprintf(stderr, "Error loading %s\n", argv[3]);
        exit(-1);
    }

    // *** Set up UDP connection ***
    if ( (sockfd = socket(AF_INET, SOCK_DGRAM, 0)) < 0) {
        perror("socket creation failed");
        exit(EXIT_FAILURE);
    }
    memset(&servaddr, 0, sizeof(servaddr));
    servaddr.sin_family = AF_INET;
    servaddr.sin_port = htons(PORT);
    inet_pton(AF_INET, "192.168.2.54", &(servaddr.sin_addr.s_addr));

    // *** Configure memory allocation ***
    // Reset ready flags
    *encoder_ready = 0;
    *irig_ready = 0;
    *error_ready = 0;
    // Sets memory to be used by data structures to 0
    memset((struct IrigInfo *) &irig_packets[0], 0, sizeof(*irig_packets));
    memset((struct IrigInfo *) &irig_packets[1], 0, sizeof(*irig_packets));
    memset((struct EncoderInfo *) &encoder_packets[0], 0, sizeof(*encoder_packets));
    memset((struct EncoderInfo *) &encoder_packets[1], 0, sizeof(*encoder_packets));
    
    // Set the timeout header
    timeout_packet->header = 0x1234;

    // Start stashing data into data objects to send over UDP
    encd_ind = 0;
    irig_ind = 0;
    curr_time = clock();
    // Continuously loops, looking for data, while PRUs are executing
    while(*on != 1) {
        // Record the current time
        curr_time = clock();
        // Gather encoder data
        if(*encoder_ready != 0) {
            offset = *encoder_ready - 1;
            encoder_to_send[encd_ind] = encoder_packets[offset];
            encd_ind += 1;
            *encoder_ready = 0;
            // Update the last time the encoder data was recorded
            encd_time = curr_time;
        }
        if(*irig_ready != 0) {
            offset = *irig_ready - 1;
            irig_to_send[irig_ind] = irig_packets[offset];
            irig_ind += 1;
            *irig_ready = 0;
            // Update the last time the IRIG data was recorded
            irig_time = curr_time;
        }
        if(*error_ready != 0) {
            offset = *error_ready - 1;
            error_to_send[err_ind] = error_packets[offset];
            err_ind += 1;
            *error_ready = 0;
        }
        // Send encoder data if the buffer is full
        if(encd_ind == ENCODER_PACKETS_TO_SEND) {
            sendto(sockfd, (struct EncoderInfo *) &encoder_to_send, sizeof(*encoder_to_send), 
                   MSG_CONFIRM, (const struct sockaddr *) &servaddr, sizeof(servaddr));
            encd_ind = 0;
        }
        if(irig_ind == IRIG_PACKETS_TO_SEND) {
            sendto(sockfd, (struct IRIGInfo *) &irig_to_send, sizeof(*irig_to_send),
                   MSG_CONFIRM, (const struct sockaddr *) &servaddr, sizeof(servaddr));
            irig_ind = 0;
        }
        if(err_ind == ERROR_PACKETS_TO_SEND) {
            sendto(sockfd, (struct ErrorInfo *) &error_to_send, sizeof(*error_to_send), MSG_CONFIRM,
                   (const struct sockaddr *) &servaddr, sizeof(servaddr));
            err_ind = 0;
        }
        // Send timeout packets if no packets have been picked up in a while
        if(((double) (curr_time - encd_time))/CLOCKS_PER_SEC > ENCODER_TIMEOUT) {
            timeout_packet->type = ENCODER_TIMEOUT_FLAG
            sendto(sockfd, (struct TimeoutInfo *) &timeout_packet, sizeof(*timeout_packet),
                   MSG_CONFIRM, (const struct sockaddr *) &servaddr, sizeof(servaddr));
        }
        if(((double) (curr_time - irig_time))/CLOCKS_PER_SEC > IRIG_TIMEOUT) {
            timeout_packet->type = IRIG_TIMEOUT_FLAG
            sendto(sockfd, (struct TimeoutInfo *) &timeout_packet, sizeof(*timeout_packet),
                   MSG_CONFIRM, (const struct sockaddr *) &servaddr, sizeof(servaddr));
        }
    }

    // Disable PRUs when finished
    if(*on == 1) {
        prussdrv_pru_wait_event(PRU_EVTOUT_1);
        printf("All done\n");
        prussdrv_pru_disable(1);
        prussdrv_pru_disable(0);
        prussdrv_exit();
    }

    return 0;
}
