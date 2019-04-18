# R2PY  
## Raspberry Pi 3, Python, and Arduino code for Controlling a Three Legged Droid  

This control system for a three legged droid runs on a Raspbery Pi 3 and is written in Python 3.6.  

The R2PY system includes Xbox360 joystick controller support for driving the foot motors, turning the dome head, generating onboard sounds, and mixing sounds from other sources (such as Marcduino).  

R2PY also has a "peekaboo" system that uses machine learning to see through a USB camera or PiCamera and detects human faces.  If the droid doesn't see anyone, it coos worriedly a couple times, and when it spots someone it whistles excitedly.  Output from the camera is shown on a HDMI connected touchscreen with bounding boxes around the detected face.  

Optionally if you want a 2-3-2 transition system, included is the Arduino Nano code and hardware setup needed. 

## Running R2.PY
NOTE: you'll need to turn on your Xbox controller and make sure it binds to the XboxController running on your Raspberry Pi before you run R2.py

To start:  press "Activate R2-D2" in Raspberry Pi menu

## Control with Xbox controller
Use left stick for controlling driving around
Use right stick for looking around (i.e. turning his dome left and right)

## Hardware Requirements  

Raspberry Pi 3  

12v DC 5v Micro-USB power regulator to power your Raspberry Pi from 12v DC battery system - something like this: https://www.amazon.com/gp/product/B00U2DGJD2 

Foot motor controllers: Sabertooth 2x32 with USB control (for controlling the foot motors)  

Dome motor controller:  Syren 10 (for controlling the dome motor)  

Xbox 360 Joystick/Controller (the Microsoft brand only costs a little more than the knockoff and never has any problems)  

Xbox 360 Wireless Receiver (the Microsoft brand only costs a little more than the knockoff and never has any problems) 

Marcduino system for controlling the lights, holos, and servos in R2's head (instructions are on curiousmarc.com)

## Optional  
### 2-3-2 Transition  
(2) Pololu Jrk Motor Controllers (for controlling the leg actuators)  

Arduino Nano (for sending signals from the Raspberry Pi to the Nano to the Pololu Jrk to the leg actuators)  

### Sound  
15watt (or bigger) Amp - something like this: https://www.amazon.com/gp/product/B00C4MT274 or this: https://www.amazon.com/gp/product/B0181Z4M4A  

3.5" (or bigger) Speakers - something like this: https://www.amazon.com/gp/product/B0007L8BT4  

Sound Mixer - if you have an additional sound source like Marcduino - something like this: https://www.amazon.com/gp/product/B0002BG2S6  

### Camera  
USB Web Camera - something like this: https://www.amazon.com/gp/product/B01N8YH5VY  

### Video Output  
HDMI Touch Screen - 7" or so, something like this:  https://www.amazon.com/gp/product/B01ID5BQTC  

### Miscellaneous  
Utility Stool - slaving over a hot robot all day is back breaking work, you'll want something like this: https://www.amazon.com/gp/product/B072Y2MRY2   :-)  

## Setup & Connection  

Additional setup instructions are in each of the code files.  

### Connecting the Raspberry Pi to the Syren 10 and dome motor  

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

### Connecting the Raspberry Pi to the Sabertooth 2x32 (USB) and foot motors
Connect the USB cable from the Raspberry Pi to the Sabertooth 2x32

|Sabertooth (2x32)	|Battery|
| --- | --- |  
|B+	|Positive|
|B-	|Negative|

|Sabertooth (2x32)	|Foot Motors|
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

## Configuration, Installation, and Setup notes

Copy all files and folders (and unzip sounds) to /home/pi

Be sure to run "chmod +x run_r2.sh" to make run_r2.sh executable
If you edit run_r2.sh in the text editor, be sure to run "dos2unix run_r2.sh" to fix the carriage returns

In Main Menu Editor, create a new menu named ActivateR2D2.desktop in the Applications folder on the Raspberry Pi so you have a clickable icon to start R2:
and copy/paste the contents of ActivateR2D2.desktop into this and save
you will see the icon in the Applications menu

### Xbox controller setup
If running this inside a python virtual environment,
you'll need to run this to get the version of pygame that goes with the version of python in the environ
```
pip install pygame
```

Install xboxdrv driver on raspi with  
```
sudo apt-get install xboxdrv
```

Add this to sudo nano /etc/rc.local and ctrl-o, enter, ctrl-x to save  
```
xboxdrv --daemon --silent &
```

If you need to terminate xboxdrv  
```
ps aux | grep xboxdrv (to get its pid)
sudo kill -TERM [put-your-pid-here]
sudo kill -KILL [put-your-pid-here]
```
### Sound setup
To output sound to the 3mm audio jack  
```
sudo amixer cset numid=3 1
```

To output sound to the HDMI audio  
```
sudo amixer cset numid=3 2
```

### Touchscreen monitor setup
(from https://www.waveshare.com/w/upload/1/19/7inch_HDMI_LCD_%28B%29_User_Manual.pdf):
To configure 7 inch LCD monitor, run "sudo nano /boot/config.txt" and add this to the bottom:  
```
max_usb_current=1
hdmi_group=2
hdmi_mode=87
hdmi_cvt 800 480 60 6 0 0 0
hdmi_drive=1
```

(and if you need to rotate the screen to vertical, add this too:  
```
display_rotate=1
```
These are the options: display_rotate=1 #1: 90; 2: 180; 3: 270  

If you need to rotate the touchscreen to vertical, then:  
```
sudo apt-get install xserver-xorg-input-libinput
sudo mkdir /etc/X11/xorg.conf.d
sudo cp /usr/share/X11/xorg.conf.d/40-libinput.conf /etc/X11/xorg.conf.d/
sudo nano /etc/X11/xorg.conf.d/40-libinput.conf
```

And change this section:  
```
Section "InputClass"
         Identifier "libinput touchscreen catchall"
         MatchIsTouchscreen "on"
         Option "CalibrationMatrix" "0 1 0 -1 0 1 0 0 1"
         MatchDevicePath "/dev/input/event*"
         Driver "libinput"
 EndSection
```

These are the options for rotation:
90 degree: Option "CalibrationMatrix" "0 1 0 -1 0 1 0 0 1"
180 degree: Option "CalibrationMatrix" "-1 0 1 0 -1 1 0 0 1"
270 degree: Option "CalibrationMatrix" "0 -1 1 1 0 0 0 0 1"


### Wiring
The Raspberry Pi GPIO are all set as INPUTS at power-up.
GPIO 0-8 have pull-ups to 3V3 applied as a default.
GPIO 9-27 have pull-downs to ground applied as a default.
This means that GPIO 0-8 will probably be seen as high and GPIO 9-27 will probably be seen as low.
You want to use GPIO > 8 or else your Arduino will be triggered when you power on the RPi
because any GPIO < 9 will be set to high until you run R2PY
but check the schematics for your version of Raspberry Pi

Run this for motor control  
```
pip install pysabertooth
```

The Syren10 dip switches should be (0 is off, 1 is on): 0 1 1 1 1 1
The USB Control Sabertooth2x32 dip switches should be (0 is off, 1 is on):  1 0 1 1 1 1

### Setup pigpio
If virtual environment, need to copy your pigpio.py and pigpio-1.42.dist-info folder
from /usr/local/lib/python3.5/dist-packages
to /home/pi/.virtualenvs/py3cv3/lib/python3.5/site-packages
then while running virtual environment:  
```
sudo apt-get install pigpio
```
then to start the pigpiod daemon on system boot run this:  
```
sudo systemctl enable pigpiod
sudo systemctl start pigpiod
```
### Miscellaneous  
To remote into raspberry pi
```sudo apt-get install xrdp```

TODO: I was trying to get it to start at system boot with this, but not working maybe because of imshow?  
``` 
sudo crontab -e
```
and this line  
```
@reboot /home/pi/run_r2.sh
```

## Acknowledgements
Many thanks for the Sabertooth and Syren hardware configuration adapted from Padawan/Padawan360 developed by DanK, DanF, et al., detailed on Astromech.net; the XboxController code adapted from martinohanlon (which I upgraded to Python 3 and made some modifications to how threading and starting/stopping works); the OpenCV and camera setup adapted from jrosebr (which I made several modifications).   

Unending thanks to everyone who contributed to all the open source libraries used in this project!

Let me know if you have any trouble with this system or if you have trouble submitting pull requests.  

Enjoy!
