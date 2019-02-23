/*
v1.0
by Robert Corvus

Hardware:
Arduino UNO
Microsoft Xbox 360 Controller
Xbox 360 USB Wireless Reciver
Sabertooth2x25 Motor Controller
Syren10 Motor Controller
Sparkfun MP3 Trigger

Set Sabertooth 2x25/2x12 Dip Switches 1 and 2 Down, All Others Up
For SyRen Simple Serial Set Switches 1 and 2 Down, All Others Up
For SyRen Simple Serial Set Switchs 2 & 4 Down, All Others Up
Placed a 10K ohm resistor between S1 & GND on the SyRen 10 itself

*/

#include <Servo.h>
#include <MP3Trigger.h>
#include <Wire.h>
#include <SoftwareSerial.h>

const int pin_2_legged_mode = 11;
const int pin_3_legged_mode = 12;

// UNO Pins:
//const int pin_left_controller_TX = 8;
//const int pin_left_controller_RX = 9;
//const int pin_right_controller_TX = 10;
//const int pin_right_controller_RX = 11;

// NANO Pins:
// PWM Pins 6, 8, 9, 12, 13, 14
const int pin_left_controller_TX = 6;
const int pin_left_controller_RX = 8;
const int pin_right_controller_TX = 13;
const int pin_right_controller_RX = 14;

int two_legged_state = 0;
int three_legged_state = 0;


// *** 2-3-2 transition BEGIN ***

/*
 In the Pololu Jrk Configuration Utility:
 on Input tab, set Serial Interface to "UART, fixed baud rate 9600"
 on Input tab, set Device Number as below for LEG_RIGHT, LEG_LEFT, and FOOT
 on PID tab, set Proportional Coefficient top number to 10 (leave bottom number 0)

 In the arduino Serial Monitor (Tools --> Serial Monitor):
 set the baud rate to 115200
*/

// on UNO, the larger-number pin goes to the RX jack and smaller-number pin goes to the TX jack (on some arduino boards this is reversed)
SoftwareSerial jrkLEFT(pin_left_controller_TX, pin_left_controller_RX);
SoftwareSerial jrkRIGHT(pin_right_controller_TX, pin_right_controller_RX);
//SoftwareSerial jrkFOOT(12, 13);

// Device Number ID of jrk
// (the Device Number is set in the Serial Interface box in the Input tab of your jrk config utility in directions above)
// by default all are 0x0B, so if you have not changed the ID, then put 0x0B for each here
#define LEG_LEFT 0x0A // 10
#define LEG_RIGHT 0x0B // 11
//#define FOOT 0x0C // 12

// min and max position for the legs
// this is callibrated in your jrk config utility by checking the "Automatically set target" 
// then for the min, slide the target bar down until the actuator stops, then clicking up until the yellow light on the jrk stops flashing (reversed for max)
// you may have to adjust calibration after installing to get true min/max positions
#define LEG_POSITION_2 1430

#define LEG_POSITION_3 2560 //2560 is max
// middle is (LEG_POSITION_2 + LEG_POSITION_3) / 2
#define LEG_POSITION_MIDDLE 1985

// min and max position for the central foot
//#define FOOT_POSITION_2 860
//#define FOOT_POSITION_3 2810
// middle is (FOOT_POSITION_2 + FOOT_POSITION_3) / 2
// however, need to set this to safe position for tilt  
//TODO: calibrate this
//#define FOOT_POSITION_MIDDLE 1800

void legsInit() {
  jrkLEFT.begin(9600);
  Serial.println("Init jrkLEFT");
  jrkRIGHT.begin(9600);
  Serial.println("Init jrkRIGHT");
  //jrkFOOT.begin(9600);
  //Serial.println("Init jrkFOOT");
}

void moveLegsTo(uint16_t value) {
  uint16_t target = value;
  Serial.print("Move legs to: ");
  Serial.println(target);

  //wait for both legs to become available
  while (jrkLEFT.available() < 2);
  while (jrkRIGHT.available() < 2);
  
  jrkLEFT.write(0xAA);
  jrkLEFT.write(LEG_LEFT);
  jrkLEFT.write(0x40 + (target & 0x1F));
  jrkLEFT.write((target >> 5) & 0x7F);
  
  jrkRIGHT.write(0xAA);
  jrkRIGHT.write(LEG_RIGHT);
  jrkRIGHT.write(0x40 + (target & 0x1F));
  jrkRIGHT.write((target >> 5) & 0x7F);

  Serial.print("Finished telling legs to move to: ");
  Serial.println(target);
}

void transition_to_2_legged_mode(){
  Serial.println("BEGIN 2-LEGGED MODE");
  
  moveLegsTo(LEG_POSITION_2);
  //while(GetLegPosition(0xA5) > LEG_POSITION_MIDDLE);//TODO: calibrate this
  //moveFootTo(FOOT_POSITION_2);
  Serial.println("END 2-LEGGED MODE");
}

void transition_to_3_legged_mode(){

  //moveFootTo(FOOT_POSITION_3);
  //while(GetFootPosition(0xA5) < FOOT_POSITION_MIDDLE);//TODO: calibrate this
  moveLegsTo(LEG_POSITION_3);
  Serial.println("END 3-LEGGED MODE");
}


//void moveFootTo(uint16_t value) {
//  uint16_t target = value;
//  Serial.print("Move foot to: ");
//  Serial.println(target);
//  jrkFOOT.write(0xAA);
//  jrkFOOT.write(FOOT);
//  jrkFOOT.write(0x40 + (target & 0x1F));
//  jrkFOOT.write((target >> 5) & 0x7F);
//  Serial.print("Finished telling foot to move to: ");
//  Serial.println(target);
//}

/* 
FUNCTIONS FOR TROUBLESHOOTING (uncomment to use):
int GetLeftLegPosition(byte command)
{
  char response[2];
  jrkLEFT.listen();
  jrkLEFT.write(0xAA);
  jrkLEFT.write(LEG_LEFT);
  jrkLEFT.write(command);
  while (jrkLEFT.available() < 2);//wait for it to become available
  jrkLEFT.readBytes(response,2);
  return word(response[1],response[0]);
}
int GetRightLegPosition(byte command)
{
  char response[2];
  jrkRIGHT.listen();
  jrkRIGHT.write(0xAA);
  jrkRIGHT.write(LEG_RIGHT);
  jrkRIGHT.write(command);
  while (jrkRIGHT.available() < 2);//wait for it to become available
  jrkRIGHT.readBytes(response,2);
  return word(response[1],response[0]);
}
int GetFootPosition(byte command)
{
  char response[2];
  jrkFOOT.listen();
  jrkFOOT.write(0xAA);
  jrkFOOT.write(FOOT);
  jrkFOOT.write(command);
  while (jrkFOOT.available() < 2);//wait for it to become available
  jrkFOOT.readBytes(response,2);
  return word(response[1],response[0]);
}
void ShowCurrentLegAndFootPositions()
{
  // feedback command is 0xA5
  // scaled feedback command is 0xA7
//  word feedbackPositionFoot = GetFootPosition(0xA5);
//  Serial.print("GetFootPosition: ");
//  Serial.println(feedbackPositionFoot);
  word feedbackPositionLeft = GetLeftLegPosition(0xA5);
  Serial.print("Left Leg Position: ");
  Serial.println(feedbackPositionLeft);
  word feedbackPositionRight = GetRightLegPosition(0xA5);
  Serial.print("Right Leg Position: ");
  Serial.println(feedbackPositionRight);
}
*/

// *** 2-3-2 transition END ***


void setup(){ 
//  To monitor output with the arduino Serial Monitor for PC/Mac, set the baud rate to 115200
//  Serial.begin(115200);
//  delay(20);

  // init JRK controllers
  legsInit();
  
  pinMode(pin_2_legged_mode, INPUT);
  pinMode(pin_3_legged_mode, INPUT);
  pinMode(LED_BUILTIN, OUTPUT);

//  attachInterrupt(digitalPinToInterrupt(pin_2_legged_mode), transition_to_2_legged_mode, RISING);
//  attachInterrupt(digitalPinToInterrupt(pin_3_legged_mode), transition_to_3_legged_mode, RISING);
}

void loop(){

//  digitalWrite(LED_BUILTIN, HIGH);
//  delay(1000);
//  digitalWrite(LED_BUILTIN, LOW);
//  delay(1000); 

  two_legged_state = digitalRead(pin_2_legged_mode);
  if(two_legged_state == HIGH){
    digitalWrite(LED_BUILTIN, LOW);
    transition_to_2_legged_mode();
  }
  three_legged_state = digitalRead(pin_3_legged_mode);
  if(three_legged_state == HIGH){
    digitalWrite(LED_BUILTIN, HIGH);
    transition_to_3_legged_mode();
  }

  // 2-3-2 Transition
  // Hold L1 and press up/down on dpad to change 2/3 leg
  // UP = 2 leg mode

 
//  if(Xbox.getButtonClick(UP, 0)){
//    if(Xbox.getButtonPress(L1, 0)){
//        Serial.println("BEGIN UP");
//        // 2 leg mode
//        moveLegsTo(LEG_POSITION_2);
//        //while(GetLegPosition(0xA5) > LEG_POSITION_MIDDLE);//TODO: calibrate this
//        //moveFootTo(FOOT_POSITION_2);
//        Serial.println("END UP");
//    }
//  }
//  // DOWN = 3 leg mode
//  if(Xbox.getButtonClick(DOWN, 0)){
//    if(Xbox.getButtonPress(L1, 0)){
//        Serial.println("BEGIN DOWN");
//        // 3 leg mode
//        //moveFootTo(FOOT_POSITION_3);
//  //      while(GetFootPosition(0xA5) < FOOT_POSITION_MIDDLE);//TODO: calibrate this
//        moveLegsTo(LEG_POSITION_3);
//        Serial.println("END DOWN");
//    }
//  }
//  // RIGHT = + Move up a little
//  if(Xbox.getButtonClick(RIGHT, 0)){
//    if(Xbox.getButtonPress(L1, 0)){
//        int currentFootPosition = GetFootPosition(0xA5); 
//        moveFootTo(currentFootPosition + 100);
//
//        int currentLeftLegPosition = GetLeftLegPosition(0xA5); 
//        moveLegsTo(currentLeftLegPosition + 100);
//    }
//  }
//  // LEFT = - Move down a little
//  if(Xbox.getButtonClick(LEFT, 0)){
//    if(Xbox.getButtonPress(L1, 0)){
//        int currentFootPosition = GetFootPosition(0xA5); 
//        moveFootTo(currentFootPosition - 100);
//
//        int currentLeftLegPosition = GetLeftLegPosition(0xA5); 
//        moveLegsTo(currentLeftLegPosition - 100);
//    }
//  }


} // END loop()
