# R2PY  
## Raspberry Pi 3, Python, and Arduino code for Controlling a Three Legged Droid  

This control system for a three legged droid runs on a Raspbery Pi 3 and is written in Python 3.6.  Optionally if you want a 2-3-2 transition system, included is the Arduino Nano code and hardware setup.

R2PY includes Xbox360 joystick controller support, onboard sounds, and mixing sounds from other sources (such as Marcduino).  

R2PY also has a "peekaboo" system that uses OpenCV and machine learning to see through a USB camera or PiCamera and detects human faces.  If it doesn't see anyone it coos worriedly a couple times and when it spots someone it whistles excitedly.  Output from the camera is shown on a HDMI connected touchscreen with bounding boxes around the detected face.  

## Hardware Requirements

Raspberry Pi 3  
12v DC 5v Micro-USB power regulator to power your Raspberry Pi from 12v DC battery system - something like this: https://www.amazon.com/gp/product/B00U2DGJD2 

Foot motor controllers: Sabertooth 2x25 (or 2x12 if styrene or 3D printed body) (for controlling the foot motors)  

Dome motor controller:  Syren 10 (for controlling the dome motor)  

Xbox 360 Joystick/Controller (the Microsoft brand only costs a little more than the knockoff and never has any problems)  

Xbox 360 Wireless Receiver (the Microsoft brand only costs a little more than the knockoff and never has any problems)  

## Optional  
### 2-3-2 Transition  
(2) Pololu Jrk Motor Controllers (for controlling the leg actuators)  

Arduino Nano (for sending signals from the Raspberry Pi to the Nano to the Pololu Jrk to the leg actuators)  

## Sound  
15watt (or bigger) Amp - something like this: https://www.amazon.com/gp/product/B00C4MT274 or this: https://www.amazon.com/gp/product/B0181Z4M4A  

3.5" (or bigger) Speakers - something like this: https://www.amazon.com/gp/product/B0007L8BT4  

Sound Mixer - if you have an additional sound source like Marcduino - something like this: https://www.amazon.com/gp/product/B0002BG2S6  

## Camera  
USB Web Camera - something like this: https://www.amazon.com/gp/product/B01N8YH5VY  

## Video Output  
HDMI Touch Screen - 7" or so, something like this:  https://www.amazon.com/gp/product/B01ID5BQTC  

## Miscellaneous  
Utility Stool - slaving over a hot robot all day is back breaking work, you'll want something like this: https://www.amazon.com/gp/product/B072Y2MRY2   :-)  

## Connecting the Raspberry Pi to the Syren 10 and dome motor  

|Syren10	| RaspberryPi3 |  
| --- | --- |  
| S1 |	12 |
|0v |	GND |

|Syren10	|Battery|
| --- | --- |  
|B+	|Positive|
|B-	|Negative|

|Syren10	|Dome Motor|
| --- | --- |  
|M1	|1 (Positive)|
|M2	|2 (Negative)|

### Connecting the Raspberry Pi to the Sabertooth 2x25 (2x12) and foot motors
|Sabertooth (2x25 or 2x12)	|RaspberryPi3|
| --- | --- |  
|S1	|3|
|S2	|5|
|0v	|GND|

|Sabertooth (2x25 or 2x12)	|Battery|
| --- | --- |  
|B+	|Positive|
|B-	|Negative|

|Sabertooth (2x25 or 2x12)	|Foot Motors|
| --- | --- |  
|M1A	Right Motor Terminal    |1|
|M1B	Right Motor Terminal    |2|
|M2A	Left Motor Terminal     |1|
|M2B	Left Motor Terminal     |2|

### Optional for 2-3-2 transition
#### Connecting the Raspberry Pi 3 to the Arduino Nano 
|RaspberryPi3   | ArduinoNano|
| --- | --- |  
|16      |D11|
|18      |D12|

#### Connecting the Arduino Nano to the Pololu Jrk 21v3 and leg actuators  
https://www.pololu.com/docs/0J38/all
|PololuJrk21v3   |ArduinoNano|
| --- | --- |  
|Left Leg Controller TX | D5|
|Left Leg Controller RX | D6|
|Right Leg Controller TX| D7|
|Right Leg Controller RX| D8|

In order to get the Peekaboo system working, you'll need to configure OpenCV on your Raspberry Pi.  Here are [extremely good instructions](https://www.pyimagesearch.com/2018/05/28/ubuntu-18-04-how-to-install-opencv/) on how to install everything you need, but even better if you buy his [Practical Python And OpenCV QuickStart bundle](https://www.pyimagesearch.com/practical-python-opencv/), he gives you a Raspberry Pi image file preconfigured with everything you need.  To me, that was worth $100 in time savings right there, and his tutorials are great too.  

Many thanks for the Sabertooth and Syren hardware configuration from Padawan/Padawan360 developed by DanK, DanF, et al., detailed on Astromech.net; the XboxController code developed by Martin O'Hanlon (which I upgraded to Python 3 and made some modifications to how threading and starting/stopping works); the OpenCV and camera setup from jrosebr (which I made several modifications).

Let me know if you have any trouble with this system or if you have trouble submitting pull requests.  

Enjoy!
