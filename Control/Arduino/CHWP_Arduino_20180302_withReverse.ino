#include <SPI.h>
#include <Ethernet2.h>
#include <EthernetUdp2.h>   

/**u
Using IRIG standard 'B'
- 100 Hz pulse frequency --> 10 ms pulse period
- 100 bits per frame --> 1 Hz frame rate
- Position idenfiers: reference pulse 'Pr' comes every 100 bits and position idenfiers 'Pn' come every 10 bits on the 9's (i.e. 9 for n = 1, 19 for n = 2, 29 for n = 3, etc.)
- Binary encodings:
  - '0' for 0.2*(10 ms) = 2 ms
  - '1' for 0.5*(10 ms) = 5 ms
  - '2' for 0.8*(10 ms) = 8 ms (marker bit)
**/

//Set this to be 75% of the max counter value (which is 16 bits)
#define MAX_LOOP_TIME 0xC000 //49,152 = 3.072 ms
//Encoder packet size is 150 counter packets
#define ENCODER_COUNTER_SIZE 150

/**
Generic Notes:
- We are using IRIG standard 'B'
- Arduino clock is 16 MHz, so time reference is 62.5 ns
- We are using counter 1 for the encoder TTL
- We are using counter 3 on the microcontroller
- No double buffering
- Some of the registers here can't be found in the Arduino Leonardo ETH documentation - you may have to
  go to the datasheet for the ATmega32U4 8-bit microcontroller on the board
- pin 13 is the input capture pin (ICPn) for counter 3, which is 16 bits and we use for the CPU clock (this is the IRIG input pin)
- pin 4 is the input for counter 1, which we use for the encoder TTL output (this is the TTL input pin)
- in the above, 'pin' refers to the input pins physically on the Arduino connector
**/


/**
Ethernet communication setup
**/

//Check for this on the Arduino sticker
byte mac[] = { 0xCA, 0xFE, 0xCA, 0xFE, 0xFE, 0xED };
//IP address assigned to the Arduino
IPAddress ip(192, 168, 1, 2); // must share 2nd to last number
//IP address assigned to the receiving computer
// This IP will need to be hard-programmed into the receivng laptop
IPAddress remote_ip(192, 168, 1, 1);
//Arbitrary port number > 1024
unsigned int localPort = 8888;
//Establish UDP protocol
EthernetUDP Udp;

/**
Arduino pin definitions
**/

//Pins which the quadrature will be attached to
//#define encoder_pin_1 4
#define encoder_pin_2 8
#define encoder_pin_3 9
#define encoder_pin_4 11

//Pins which the motor stop will be attached to
#define brake_pin_digital 0 
#define brake_pin_analog A0

/**
Info we will be sending back to the computer from the Arduino
**/

//Structure to hold the readout values of the quadrature
struct QuadEncoder{
  unsigned int encoder_value_2;
  unsigned int encoder_value_3;
  unsigned int encoder_value_4;
};

volatile struct QuadEncoder quad;

//Structure to hold clock values and mesure the difference between the two clocks
struct SynchClocks {
  //These values are recorded immediately after eachother
  unsigned int clk_1_start;
  unsigned int clk_3;
  unsigned int clk_1_end;
};

volatile struct SynchClocks synch;


//Structure which holds information from the encoder
struct CounterInfo{
  //Clock count of a datapoint
  unsigned int clock_cnt[ENCODER_COUNTER_SIZE];
  //Overflow amount of a data point
  unsigned int counter_ovflow[ENCODER_COUNTER_SIZE];
  //Counter of total rising/falling edges
  unsigned int encoder_cnt[ENCODER_COUNTER_SIZE];
};

//Structure which holds information from the IRIG
struct IrigInfo{
  unsigned int random_header = 0xCAFE; //I need my coffee
  //Rising edge of Pr pulse, beginning of IRIG packet
  unsigned long int rising_edge_time;
  //Bit information for each packet position
  unsigned int info[10]; 
  //Rising edge location for each packet position
  unsigned long int re_count[10]; 
};

/**
Info we will be receiving from the computer
**/

//Structure which holds information from the motor stop command
struct MotorStop {
  unsigned int header = 0xBEEF; //I need my beef
  unsigned int killFlag = 0 //Tells the host computer to cut the motor power supply
};

volatile struct MotorStop stop;

/**
Interrupt for controlling the overflow of counter 3, which is handling the clock
Just keep track of the number of times it's overflowed (overflown?) so that we can
account for that and keep counting time linearly
**/

//Counter which keeps track of the number of times the CPU counter overflows
volatile unsigned int counter_3_overflow = 0;

//*** Interrupt #1***
//Interrupt service routine to increment the overflow counter
ISR(TIMER3_OVF_vect){
  counter_3_overflow++;
}
//*******************

/**
Error reporting
**/

//Variables to define whether or not we have desynced
#define ERR_NONE 0
#define ERR_DESYNC 1

struct ErrorInfo {
  unsigned int header = 0xE12A; 
  //0 if all is good, 1 if an error exists
  unsigned int err_code = ERR_NONE;  
};

//Create one ErrorInfo object that will keep track of the error state
volatile struct ErrorInfo error_state;


/**
Generic IRIG Routines
**/

// Define the possible PWM irig bits: 0, 1, PI (the synchronization pulse), ERR (an error)
#define IRIG_0 0 //2 ms
#define IRIG_1 1 //5 ms
#define IRIG_PI 2  //8 ms
#define IRIG_ERR 3 //Error

//Instantiate two IrigInfo objects
struct IrigInfo irig_packet_0;
struct IrigInfo irig_packet_1;

//Instantiate two IrigInfo pointers that point to the address of the above two IrigInfo objects
volatile struct IrigInfo * the_irig_packet = &irig_packet_0;
volatile struct IrigInfo * to_send_irig_packet = &irig_packet_1;

//Boolean to swap addresses of the above two pointers
bool irig_packet_pointer_coord = false;

/**
Variables and procedures for the irig interrupt
**/

//Time coordinate of the rising edge
unsigned long int rising_edge_t;
//Time coordinate of the falling edge
unsigned long int falling_edge_t;

//By default, assume bit type is an error
unsigned char prev_bit_type = IRIG_ERR; //bit '3'
//By default, assume IRIG parser is not synched
unsigned char irig_parser_is_synched = 0;

//Bit position '0' marks the beginning of an IRIG frame
unsigned char bit_position = 0;

//Character that triggers whether or not to book the IRIG packet
volatile unsigned char book_the_irig_packet = 0;

void irig_interrupt(){
  //Grab the clock before doing anything else
  //'TIFR' is 'Timer Interrupt Flag Register'
  unsigned char overflow_bits = TIFR3;
  //'ICR' is the 'Input Capture Register', which fires at 16 MHz
  unsigned long int clock_cnt = ICR3;
  
  //Cache previous overflow value
  unsigned int counter_3_overflow_cached = counter_3_overflow;
  
  //Allow interrupts on the AVI chip
  //sei();
  
  //(overflow_bits & 1) checks 'TOV', which is the timer overflow flag
  //Don't double-count overflows, so make sure clock_cnt is far from MAX_LOOP_TIME
  overflow_bits = (overflow_bits & 1) && (clock_cnt < MAX_LOOP_TIME);
  //Default current IRIG bit type is an error
  unsigned char irig_bit_type = IRIG_ERR; //bit '3'
  
  //'TCCR' is 'Timer Counter Control Register'
  //Toggle the 'Input Capture Edge Select' bit, which is '1' for rising edge and '0' for falling edge
  TCCR3B ^= 1 << 6;
  
  //64 = 1 << 6
  //If rising edge bit set (toggled above, so this is actually a falling edge), store falling edge time and check pulse type
  if (TCCR3B & 64) {
     #ifdef DEBUG_SERIAL
     Serial.println("At falling edge:");
     #endif
     
     //Record the falling edge time
     falling_edge_t = clock_cnt + (((unsigned long int)(overflow_bits + counter_3_overflow_cached)) << 16);

     //Check pulse width. Recall that the Arduino clock delta(t) = 16 MHz
     unsigned long int delta = falling_edge_t - rising_edge_t; 
     
     //'0' if delta < 3.5 ms (2 ms target)
     if (delta < 56000) irig_bit_type = IRIG_0;
     //'3' if delta > 12.3 ms = 4 x MAX_LOOP_TIME
     else if ( delta > 196608) irig_bit_type = IRIG_ERR;
     //'2' if 6.5 ms < delta < 12.3 ms (8 ms target)
     else if ( delta > 104000 ) irig_bit_type = IRIG_PI;
     //'1' if 3.5 ms < delta < 6.5 ms (5 ms target)
     else irig_bit_type = IRIG_1;

     //Check synchronization. By default, 'irig_parser_is_synched' is set to '0'
     //If synched, parse and store IRIG information
     if (irig_parser_is_synched) {
       #ifdef DEBUG_SERIAL
       Serial.println("synched falling edge");
       #endif 
       
       //If the frame is complete, send IRIG packet  
       if ( bit_position == 100 ) {
         //Toggle the point coordinate boolean
         //Default value of 'irig_packet_pointer_coord' is FALSE
         irig_packet_pointer_coord = !irig_packet_pointer_coord;
         //Swap irig packet pointers to refresh the IrigInfo object
         if (irig_packet_pointer_coord) {
           the_irig_packet = &irig_packet_1;
           to_send_irig_packet = &irig_packet_0;
         } else {
           the_irig_packet = &irig_packet_0;
           to_send_irig_packet = &irig_packet_1;
         } 
         //Indicate the packet is ready to be sent     
         book_the_irig_packet = 1;
         //Reset bit position
         bit_position = 1;
         //Bit 100 is the rising-edge Bit 0 of the next packet
         the_irig_packet->rising_edge_time = rising_edge_t;
       
       //Expect a position identifier pulse on bit 9, 19, 29, etc.
       } else if ( bit_position % 10 == 9) {
         //Throw an error if this is not a synchronization pulse
         if (irig_bit_type != IRIG_PI) {
           irig_parser_is_synched = 0;
           book_the_irig_packet = 0;
           error_state.err_code = ERR_DESYNC;
         }
         //Increment P_n index
         unsigned char ind = bit_position/10;
         the_irig_packet->re_count[ind] = rising_edge_t;
         bit_position++;
       
       //Expect a typical '1' or '0' on all other bits
       } else {
         //Store IRIG bit for this position, either a '1' or a '0'
         unsigned char offset = bit_position % 10;
         the_irig_packet->info[bit_position/10] &= ~(1 << offset);
         the_irig_packet->info[bit_position/10] |= irig_bit_type << (offset);   
         bit_position++;
       }
     
     //If not synchronized, wait for the start of a new frame   
     } else {
       #ifdef DEBUG_SERIAL
       Serial.println("not synched falling edge");
       #endif

       if ( irig_bit_type == IRIG_PI && prev_bit_type == IRIG_PI) {
         bit_position = 1;
         irig_parser_is_synched = 1;
         the_irig_packet->rising_edge_time = rising_edge_t;
       }
     }
     
     //Done with this bit. Store it as the previous bit.
     prev_bit_type = irig_bit_type;
   
   //If falling edge bit is set (toggled above, so this is actually a rising edge), store rising edge time
   } else {
     rising_edge_t = clock_cnt + (((unsigned long int)(overflow_bits + counter_3_overflow_cached)) << 16);
   } 
}

//*** Interrupt #2***
//Function that interrupts to do IRIG synchronization
//Timer 3 capture vector: runs whenever there is a rising/falling edge on pin 13
ISR(TIMER3_CAPT_vect){
  irig_interrupt();
}
//*******************

/**
Variables and procedures for the counter interrupt
**/

//Index over stored counter objects
unsigned int counter_index = 0;
unsigned char send_counter_data = 0;

//Counter of encoder capture count
unsigned int input_capture_cnt = 1;

//Header for encoder packet
unsigned int counter_info_header = 0x1eaf;

//Instantiate two CounterInfo objects
struct CounterInfo counter_packet_0;
struct CounterInfo counter_packet_1;

//Instantiate two CounterInfo pointers that point to the address of the above two CounterInfo objects
volatile struct CounterInfo * the_counter_packet = &counter_packet_0;
volatile struct CounterInfo * to_send_counter_packet = &counter_packet_1;

bool counter_packet_pointer_coord = false;

//Counter interrupt routine
void counter_interrupt(){
  //Record the clock count at which a rising/falling edge occured
  the_counter_packet->clock_cnt[counter_index] = ICR1;
  //Record the overflow count
  unsigned char overflow_bits = TIFR3;
  the_counter_packet->counter_ovflow[counter_index] = counter_3_overflow +
    ((overflow_bits & 1) && (the_counter_packet->clock_cnt[counter_index] < MAX_LOOP_TIME));
  //64 for rising edge and 0 for falling edge
  the_counter_packet->encoder_cnt[counter_index] = input_capture_cnt;
  counter_index++;

  //Switch between rising/falling edge
  TCCR1B ^= 1 << 6;

  //If the packet is full begin filling a different packet and send the current packet
  if (counter_index == ENCODER_COUNTER_SIZE){
    counter_packet_pointer_coord = !counter_packet_pointer_coord;

    if (counter_packet_pointer_coord) {
      the_counter_packet = &counter_packet_1;
      to_send_counter_packet = &counter_packet_0;
    }
    else {
      the_counter_packet = &counter_packet_0;
      to_send_counter_packet = &counter_packet_1;
    }
    counter_index = 0;
    send_counter_data = 1;

    //Read and record the quadrature
    quad.encoder_value_2 = digitalRead(encoder_pin_2);
    quad.encoder_value_3 = digitalRead(encoder_pin_3);
    quad.encoder_value_4 = digitalRead(encoder_pin_4);

    //Record the desynch of the two clocks
    synch.clk_1_start = TCNT1;
    synch.clk_3 = TCNT3;
    synch.clk_1_end = TCNT1;
  }
}


////*** Interrupt #3***
//Timer 1 capture vector: runs whenever there is a rising/falling edge on pin 4
ISR(TIMER1_CAPT_vect){
  counter_interrupt();
  input_capture_cnt++;
}
//*********************

/**
Variables and procedures for the motor stop
**/
void motorStop_interrupt() {
  //Monitor the frequency of the waveplate until it is sufficiently low to grab
  while True {
    //Check the analog input to the frequency monitor pin
    unsigned int freqVoltage = analogRead(brake_pin_analog);
    if (freqVoltage > 20) {
      continue;
    }
    else { //Tell the host computer to turn off the motor
      stop.killFlag = 1 //Tell the host computer to stop the motor
      UDP.beginPacket(remote_ip, localport)
      UDP.write((char*)&stop, sizeof(struct motorStop))
      UDP.endPacket() 
    }
  } 
}

////*** Interrupt #4***
attachInterrupt(digitalPinToInterrupt(brake_pin_digital), motorStop_interrupt)
//*********************

/**
Runs once after programming
**/
void setup() {  
  //Setup up UDP over Ethernet
  Ethernet.begin(mac, ip);
  Udp.begin(localPort);
  
  #ifdef DEBUG_SERIAL
  Serial.begin(9600);
  #endif
  
  //Setup Counter 1
  TCCR1A = 0; // set counter 1 to not use fancy decimating
  TCCR1B = 0b01000001; // set counter 1 to use the clock as it's source and use rising edge to trigger input capture
  TIMSK1 = 0b00100000; // set counter 1 to send an interrupt on input capture
 
  //Setup Counter 3
  TCCR3A = 0;  // set counter 3 to not use any fancy decimating of input
  TCCR3B = 0b01000001; // set counter 3 to use the clock as it's source and use rising edge to trigger input capture
  TIMSK3 = 0b00100001; // set counter 3 to send an interrupt on overflow and interrupt on input capture  

  //Set the quadrature pins read the incoming signal
  pinMode(encoder_pin_2, INPUT);
  pinMode(encoder_pin_3, INPUT);
  pinMode(encoder_pin_4, INPUT);
  
  //Clean the IRIG packet
  for (int i=0; i < 10; i++) the_irig_packet->info[i] = 0;
  
  //Motor stop pins
  pinMode(brake_pin_1, OUTPUT);
  pinMode(brake_pin_2, INPUT);
}



/**
Runs continuously after setup() is completed
**/
void loop() {

  //Construct an IRIG packeet when the 'book' flag is set
  if (book_the_irig_packet) {
    Udp.beginPacket(remote_ip, localPort);
    Udp.write(((char*)to_send_irig_packet), sizeof(struct IrigInfo));
    Udp.endPacket();
    //Reset book flag
    book_the_irig_packet = 0;
  }

  //Send the counter data when the 'send_counter' flag is set
  if (send_counter_data) {
    Udp.beginPacket(remote_ip, localPort);
    Udp.write((char*)&counter_info_header, sizeof(unsigned int));
    Udp.write(((char*)to_send_counter_packet), sizeof(struct CounterInfo));
    Udp.write((char*)&quad, sizeof(struct QuadEncoder));
    Udp.write((char*)&synch, sizeof(struct SynchClocks));
    Udp.endPacket();

    send_counter_data = 0;
  }  

  //Sent an error packet
  if (error_state.err_code) {
    Udp.beginPacket(remote_ip, localPort);
    Udp.write(((char*)&error_state), sizeof(struct ErrorInfo));
    Udp.endPacket();  
    //Reset error code
    error_state.err_code = ERR_NONE;
  }

  //Stopping the rotor
  int packetSize = Udp.parsePacket();
  if (packetSize == sizeof(struct MotorStop)) {
    UDP.read(read_packet_buffer, sizeof(struct MotorStop));
    int state;
    char header[2];
    char stopFlag[1];
    for (int i = 0; i < 2; i++) { header[i] = read_packet_buffer[i]; }
    for (int i = 0; i < 1; i++) { stopFlag[i] = read_packet_buffer[i]; }
    //Toggle the digital output pin to the inverter
    if (header == stop.header) {
      if (digitalRead(stop_pin_digital) == HIGH) { state = LOW; }
      else { state = HIGH; }
      digitalWrite(stop_pin_digital, state);
  }
    
}
