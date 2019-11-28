#include <stdlib.h>
#include <stdint.h>

// ********** CONSTANTS **********

// Shared addresses between counter and IRIG
// Address for shared variable 'on' to tell ARM when the PRU is still sampling
#define ON_ADDRESS 0x00010000
// Address for shared variable between PRUs to count clock overflows
// Needed since both PRUs share the same clock
#define OVERFLOW_ADDRESS 0x00010002

// IRIG-specific addresses
// IRIG packet identifier
#define IRIG_READY_ADDRESS 0x00012000
#define IRIG_ADDRESS 0x00012002

// Error-specific addresses (not currently used)
// *** This might break something ***
#define ERROR_READY_ADDRESS 0x00012300
#define ERROR_ADDRESS 0x00012302

// ~75% of max counter value (not used)
#define MAX_LOOP_TIME 0x5FFFFFFF

// IEP (Industrial Ethernet Peripheral) Registers
// IEP base address
#define IEP 0x0002e000
// Register IEP Timer configuration
#define IEP_TMR_GLB_CFG ((volatile unsigned long int *)(IEP + 0x00))
// Register to check for counter overflows
#define IEP_TMR_GLB_STS ((volatile unsigned long int *)(IEP + 0x04))
// Register to configure compensation counter
#define IEP_TMR_COMPEN ((volatile unsigned long int *)(IEP + 0x08))
// Register for the IEP counter (32-bit, 200MHz)
#define IEP_TMR_CNT ((volatile unsigned long int *)(IEP + 0x0c))

// IRIG bit types
#define IRIG_0 0 // 2 ms
#define IRIG_1 1 // 5 ms
#define IRIG_PI 2  // 8 ms
#define IRIG_ERR 3 // Error

// Error bits
#define ERR_NONE 0
#define ERR_DESYNC 1

// IRIG delta_clock values
#define IRIG_TIMER_0 700000
#define IRIG_TIMER_1 1300000
#define IRIG_TIMER_PI 2457600

// Number of seconds to gather data for
#define DAQ_TIME 0x10000000  // ~10 years

// ********** STRUCTS **********

// Structure to sample PRU input and determine edges
struct ECAP {
    // Previous sample of the input register __R31
    unsigned long int p_sample;
    // Time stamp of edge seen
    unsigned long int ts;
    // ID rising vs falling edge (not used)
    unsigned long int trigger;
};

// Structure for IRIG
struct IrigInfo {
    // IRIG header
    unsigned short int header;
    // Rising edge time
    unsigned long int clock;
    // Number of overflows that have occurred
    // when the first rising edge is seen
    unsigned long int clock_overflow;
    // Info pointer
    unsigned long int info[10];
    // Synchronization pulse pointer
    unsigned long int synch[10];
    // Number of overflows that have occurred
    // at each synchronization pulse
    unsigned long int synch_overflow[10];
};

// Structure for Errors
struct ErrorInfo {
    // Error header
    unsigned short int header;
    // 0 if all is good, 1 if an error exists
    unsigned short int err_code;
};

// ********** POINTERS **********

// *** Shared Pointers ***
// Pointer to the 'on' variable
// 0 if PRUs are still sampling, 1 if they are done
volatile unsigned short int* on =
(volatile unsigned short int *) ON_ADDRESS;
// Identifies when and which clock_overflow struct is ready
// to be read out
volatile unsigned long int* clock_overflow =
(volatile unsigned long int *) OVERFLOW_ADDRESS;

// *** IRIG-only pointers ***
// Identifies when and which IRIG struct is ready
// to be read from shared memory
volatile unsigned short int* irig_ready = 
(volatile unsigned short int *) IRIG_READY_ADDRESS;
// Pointer to shared memory for IRIG structs
volatile struct IrigInfo* irig_packets =
(volatile struct IrigInfo *) (IRIG_ADDRESS);

// Identifies when and which Error struct is ready
// to be ready from shared memory
volatile unsigned short int* error_ready =
(volatile unsigned short int *) ERROR_READY_ADDRESS;
// Pointer to shared memory for Error structs
volatile struct ErrorInfo* error_state =
(volatile struct ErrorInfo *) (ERROR_ADDRESS);

// ********** LOCAL VARIABLES **********

// Rising edge clock value (accounting for overflows)
unsigned long long int rising_edge_clock;
// Falling edge clock value (accounting for overflows)
unsigned long long int falling_edge_clock;
// Time between rising and falling edges
unsigned long long int delta_clock;
// Rising edge clock value (without accounting for overflows)
unsigned long int short_rising_edge_clock;

// Bit location within IRIG frame (0 - 100)
unsigned char bit_position;
// Whether or not the IRIG is synced
unsigned char irig_parser_is_synched;
// Current IRIG bit type
unsigned char irig_bit_type;
// Previous IRIG bit type
unsigned char prev_bit_type;

// Number of overflows
unsigned int overflow_bits;
// Cached overflows
unsigned int overflow_cached;
// Total overflows = overflow bits + cached overflows
unsigned int overflow_total;
// Overflow time = overflow_total << 32;
unsigned long long int overflow_time;

// Value of sampled digital inputs
unsigned long int sample;

// Variable used to write to two different blocks of memory allocated
// to an individual instantiation of IRIG struct
int i;
// Number of DAQ seconds
long int x;
// Index to track synch and info pulses
unsigned char ind;
// Info offset when writing each info bit
unsigned char info_offset;

// Struct for storing captures
// Initialize ECAP struct to determine edges
volatile struct ECAP ECAP;

// **************************
// ********** MAIN **********
// **************************

int main(void) {
    // Registers to use for PRU input/output, __R31 is input, __R30 is output
    volatile register unsigned int __R31, __R30;

    // IEP configuration taken care of by the encoder code 
    // running on the other PRU
    // Clears Overflow Flags
    *IEP_TMR_GLB_STS = 1;
    // Enables IEP counter to increment by 1 every cycle
    *IEP_TMR_GLB_CFG = 0x11;
    // Disables compensation counter
    *IEP_TMR_COMPEN = 0;

    // Initialize ECAP struct
    // Previous sample
    ECAP.p_sample = 0;
    // Current time
    ECAP.ts = *IEP_TMR_CNT;
    // Whether rising or falling edge
    ECAP.trigger = 1 << 14;

    // initial state: no IRIG struct is ready to be read out
    *irig_ready = 0;
    // Initial state: no Error struct is ready to be read out
    *error_ready = 0;

    // Start with no counter overflows
    *clock_overflow = 0;
    overflow_cached = 0;

    // Initial IRIG bit position
    bit_position = 0;

    // Don't start with IRIG synchronization pulse
    irig_parser_is_synched = 0;

    // Assume an IRIG error state to start
    prev_bit_type = IRIG_ERR;

    // Initialize one error packet
    // Initial state: no error
    error_state->header = 0xe12a;
    error_state->err_code = ERR_NONE;

    // Initialize two IRIG packets
    // Set IRIG headers for both IRIG packets
    irig_packets[0].header = 0xcafe;
    irig_packets[1].header = 0xcafe;

    // Sample for DAQ_HOURS number of hours
    x = 0;
    // Signal that data collection is beginning
    *on = 0;
    while(x < (DAQ_TIME / 2)) {
        // Fill each IRIG packet in the queue
        i = 0;
        while(i < 2) {
            // Check for the counter overflow register
            // and reset it by writing a 1
            if ((*IEP_TMR_GLB_STS & 1) == 1){
                *clock_overflow += 1;
                *IEP_TMR_GLB_STS = 1;
            }

            // Sample the inputs
            sample = (__R31 & (1 << 14));
            // If the input has changed, store the timer value
            if(sample ^ ECAP.p_sample) {
                // Store the clock value
                ECAP.ts = *IEP_TMR_CNT;
                // Store this sample as the new previous sample
                ECAP.p_sample = sample;

                // Checks again for an overflow that has occurred since the last check
                overflow_bits = (*IEP_TMR_GLB_STS & 1);
                // Cache the current overflow counter value
                overflow_cached = *clock_overflow;
                // Total overflows
                overflow_total = overflow_bits + overflow_cached;
                // Total overflow time
                overflow_time = overflow_total << 32;
                // Assume an IRIG error until proven otherwise
                irig_bit_type = IRIG_ERR;
                // If a rising edge, simply store the clock value
                if ((sample & 1 << 14) == 1) {
                    // Store rising edge time (accounting for overflows)
                    rising_edge_clock = ECAP.ts + overflow_time;
                    // Store rising edge time (not accounting for overflows)
                    short_rising_edge_clock = ECAP.ts;
                }
                // If a falling edge, process IRIG PWM input
                else {
                    // Store the falling edge time (accounting for overflows)
                    falling_edge_clock = ECAP.ts + overflow_time;
                    // Store the time between rising and falling edges
                    delta_clock = falling_edge_clock - rising_edge_clock;

                    // Assess the IRIG bit type
                    if ((delta_clock > 0) && (delta_clock < IRIG_TIMER_0)) {
                        irig_bit_type = IRIG_0;
                    }
                    else if ((delta_clock > IRIG_TIMER_0) &&
                             (delta_clock < IRIG_TIMER_1)) {
                        irig_bit_type = IRIG_1;
                    }
                    else if ((delta_clock > IRIG_TIMER_1) && 
                             (delta_clock < IRIG_TIMER_PI)) {
                        irig_bit_type = IRIG_PI;
                    }
                    else {
                        irig_bit_type = IRIG_ERR;
                    }

                    // Process IRIG synchronization and info pulses
                    if (irig_parser_is_synched) {

                        // Every 100th bit signals the end of the IRIG PWM waveform
                        if (bit_position == 100) {
                            // Switches which packet is being written to
                            *irig_ready = (i+1);
                            if (i == 0) {
                                irig_packets[1].clock = short_rising_edge_clock;
                                irig_packets[1].clock_overflow =
                                overflow_bits + overflow_cached;
                            }
                            else if (i == 1) {
                                irig_packets[0].clock = short_rising_edge_clock;
                                irig_packets[0].clock_overflow =
                                overflow_bits + overflow_cached;
                            }
                            // Reset the bit position
                            bit_position = 1;
                            i += 1;
                        }
                        // Every 9th bit is a synchronization pulse
                        else if (bit_position % 10 == 9) {
                            if (irig_bit_type != IRIG_PI){
                                irig_parser_is_synched = 0;
                                *irig_ready = 0;
                                error_state->err_code = ERR_DESYNC;
                                *error_ready = 1;
                            }
                            ind = bit_position/10;
                            irig_packets[i].synch[ind] = short_rising_edge_clock;
                            irig_packets[i].synch_overflow[ind] = overflow_total;
                            bit_position += 1;
                        }
                        // All other bits are INFO bits
                        else {
                            // INFO bit either a 1 or 0
                            ind = bit_position/10;
                            info_offset = bit_position % 10;
                            irig_packets[i].info[ind] &= ~(1 << info_offset);
                            irig_packets[i].info[ind] |= irig_bit_type << (info_offset);
                            bit_position += 1;
                        }
                    }
                    else {
                        // 2 synch pulses in a row means a new irig packet is starting
                        if ((irig_bit_type == IRIG_PI) && (prev_bit_type == IRIG_PI)) {
                            // Reset the bit position
                            bit_position = 1;
                            // Reset the synchronization
                            irig_parser_is_synched = 1;
                            irig_packets[i].clock = short_rising_edge_clock;
                        }
                    }
                    prev_bit_type = irig_bit_type;
                }
            }
        }
        x += 1;
    }
    // Signal that the data collection is finished
    *on = 1;
    // Interrupt ARM when finished
    __R31 = 0x28;
    // Halt the PRU
    __halt();
}
