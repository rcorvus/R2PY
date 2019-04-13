# ./run_r2.sh

# be sure to run "chmod +x run_r2.sh" to make it executable
# if you edit run_r2.sh in the text editor, be sure to run "dos2unix run_r2.sh" to fix the carriage returns

# in Main Menu Editor, create a new menu named ActivateR2D2.desktop in the Applications folder on the Raspberry Pi so you have a clickable icon to start R2:
# and copy/paste the contents of ActivateR2D2.desktop into this and save
# you will see the icon in the Applications menu

# NOTE: you'll need to turn on your Xbox controller and make sure it binds to the XboxController running on your Raspberry Pi before you run R2.py

# if running this inside a python virtual environment,
# you'll need to run "pip install pygame" to get the version of pygame that goes with the version of python in the environ

# install xboxdrv driver on raspi with:
# sudo apt-get install xboxdrv

# add this to sudo nano /etc/rc.local and ctrl-o, enter, ctrl-x to save:
# xboxdrv --daemon --silent &

# if you need to terminate xboxdrv:
# ps aux | grep xboxdrv (to get its pid)
# sudo kill -TERM [put-your-pid-here]
# sudo kill -KILL [put-your-pid-here]

# to output sound to the 3mm audio jack:
# sudo amixer cset numid=3 1

# to output sound to the HDMI audio
# sudo amixer cset numid=3 2

# (from https://www.waveshare.com/w/upload/1/19/7inch_HDMI_LCD_%28B%29_User_Manual.pdf):
# To configure 7 inch LCD monitor, run "sudo nano /boot/config.txt" and add this to the bottom:
# max_usb_current=1
# hdmi_group=2
# hdmi_mode=87
# hdmi_cvt 800 480 60 6 0 0 0
# hdmi_drive=1

# (and if you need to rotate the screen to vertical, add this too:
# display_rotate=1
# these are the options: display_rotate=1 #1: 90; 2: 180; 3: 270

# if you need to rotate the touchscreen to vertical, then:
# sudo apt-get install xserver-xorg-input-libinput
# sudo mkdir /etc/X11/xorg.conf.d
# sudo cp /usr/share/X11/xorg.conf.d/40-libinput.conf /etc/X11/xorg.conf.d/
# sudo nano /etc/X11/xorg.conf.d/40-libinput.conf

# and change this section:
# Section "InputClass"
#         Identifier "libinput touchscreen catchall"
#         MatchIsTouchscreen "on"
#         Option "CalibrationMatrix" "0 1 0 -1 0 1 0 0 1"
#         MatchDevicePath "/dev/input/event*"
#         Driver "libinput"
# EndSection

# these are the options for rotation:
# 90 degree: Option "CalibrationMatrix" "0 1 0 -1 0 1 0 0 1"
# 180 degree: Option "CalibrationMatrix" "-1 0 1 0 -1 1 0 0 1"
# 270 degree: Option "CalibrationMatrix" "0 -1 1 1 0 0 0 0 1"

# to remote into raspberry pi
# sudo apt-get install xrdp

# Control with Xbox controller:
# Use left stick for controlling driving around
# Use right stick for looking around (i.e. turning his dome left and right)

# Wiring:
# The Pi GPIO are all set as INPUTS at power-up.
# GPIO 0-8 have pull-ups to 3V3 applied as a default.
# GPIO 9-27 have pull-downs to ground applied as a default.
# This means that GPIO 0-8 will probably be seen as high and GPIO 9-27 will probably be seen as low.
# You want to use GPIO > 8 or else your Arduino will be triggered when you power on the RPi
# because any GPIO < 9 will be set to high until you run R2PY

# The Syren10 dip switches should be (0 is off, 1 is on): 0 1 1 1 1 1
# The Sabertooth2x25 dip switches should be (0 is off, 1 is on):  0 1 0 0 1 1

# setup pigpio:
# if virtual environment, need to copy your pigpio.py and pigpio-1.42.dist-info folder
# from /usr/local/lib/python3.5/dist-packages
# to /home/pi/.virtualenvs/py3cv3/lib/python3.5/site-packages
# then while running virtual environment:
# sudo apt-get install pigpio
# then to start the pigpiod daemon on system boot run this:
# sudo systemctl enable pigpiod
# sudo systemctl start pigpiod

# TODO: I was trying to get it to start at system boot with this, but not working maybe because of imshow?
# "sudo crontab -e" and this line:
# @reboot /home/pi/run_r2.sh

import sys
import pigpio
import math
from time import sleep
import pygame
from XboxController import XboxController
from SoundController import SoundController
from PeekabooController import PeekabooController

class R2PY:

    def __init__(self):
        # if you want to switch to hardware PWM, remember:
        # GPIO12(32) & GPIO18(12) share a setting as do GPIO13(33) & GPIO19(35)

        # NOTE: all gpio pin numbers are BCM
        self.gpioPin_SabertoothS1 = 18
        self.gpioPin_SabertoothS2 = 12
        self.gpioPin_Syren10 = 13
        # board pins 16 (BCM 23) and 18 (BCM 24) initialize to LOW at boot
        self.gpioPin_2_leg_mode = 23
        self.gpioPin_3_leg_mode = 24

        self.pi = pigpio.pi()

        self.pi.set_mode(self.gpioPin_2_leg_mode, pigpio.OUTPUT)
        self.pi.write(self.gpioPin_2_leg_mode, 0)
        self.pi.set_mode(self.gpioPin_3_leg_mode, pigpio.OUTPUT)
        self.pi.write(self.gpioPin_3_leg_mode, 0)

        self.pi.set_mode(self.gpioPin_Syren10, pigpio.OUTPUT)
        self.pi.set_servo_pulsewidth(self.gpioPin_Syren10, 0)

        self.pi.set_mode(self.gpioPin_SabertoothS1, pigpio.OUTPUT)
        self.pi.set_servo_pulsewidth(self.gpioPin_SabertoothS1, 0)

        self.pi.set_mode(self.gpioPin_SabertoothS2, pigpio.OUTPUT)
        self.pi.set_servo_pulsewidth(self.gpioPin_SabertoothS2, 0)

        self.initializeXboxController()
        self.initializeSoundController()
        self.initializePeekabooController()

        self.running = True

    def initializePeekabooController(self):
        self.peekabooCtrlr = PeekabooController()
        self.peekabooCtrlr.start()

    def initializeSoundController(self):
        self.soundCtrlr = SoundController()
        self.soundCtrlr.start()

    def initializeXboxController(self):
        try:
            # setup controller values
            self.xValueLeft = 0
            self.yValueLeft = 0
            self.xValueRight = 0
            self.yValueRight = 0
            self.dpadValue = (0,0)
            self.lbValue = 0

            self.xboxCtrlr = XboxController(deadzone=0.3,
                                            scale=1,
                                            invertYAxis=True)

            # setup call backs
            self.xboxCtrlr.setupControlCallback(self.xboxCtrlr.XboxControls.LTHUMBX, self.leftThumbX)
            self.xboxCtrlr.setupControlCallback(self.xboxCtrlr.XboxControls.LTHUMBY, self.leftThumbY)
            self.xboxCtrlr.setupControlCallback(self.xboxCtrlr.XboxControls.RTHUMBX, self.rightThumbX)
            self.xboxCtrlr.setupControlCallback(self.xboxCtrlr.XboxControls.RTHUMBY, self.rightThumbY)
            # self.xboxCtrlr.setupControlCallback(self.xboxCtrlr.XboxControls.LTRIGGER, self.leftTrigger) #triggers don't work
            # self.xboxCtrlr.setupControlCallback(self.xboxCtrlr.XboxControls.RTRIGGER, self.rightTrigger) #triggers don't work
            self.xboxCtrlr.setupControlCallback(self.xboxCtrlr.XboxControls.DPAD, self.dpadButton)
            self.xboxCtrlr.setupControlCallback(self.xboxCtrlr.XboxControls.BACK, self.backButton)
            self.xboxCtrlr.setupControlCallback(self.xboxCtrlr.XboxControls.A, self.aButton)
            self.xboxCtrlr.setupControlCallback(self.xboxCtrlr.XboxControls.B, self.bButton)
            self.xboxCtrlr.setupControlCallback(self.xboxCtrlr.XboxControls.X, self.xButton)
            self.xboxCtrlr.setupControlCallback(self.xboxCtrlr.XboxControls.Y, self.yButton)
            self.xboxCtrlr.setupControlCallback(self.xboxCtrlr.XboxControls.LB, self.lbButton)

            # start the controller
            self.xboxCtrlr.start()

        except:
            print("ERROR: could not connect to Xbox controller")

    def steering(self, x, y):
        # assumes the initial (x,y) coordinates are in the -1.0/+1.0 range
        print("x = {}".format(x))
        print("y = {}".format(y))

        # convert to polar
        r = math.hypot(x, y)
        t = math.atan2(y, x)

        # rotate by 45 degrees
        t += math.pi / 4

        # back to cartesian
        left = r * math.cos(t)
        right = r * math.sin(t)

        # rescale the new coords
        left = left * math.sqrt(2)
        right = right * math.sqrt(2)

        # clamp to -1/+1
        left = max(-1, min(left, 1))
        right = max(-1, min(right, 1))

        print("left = {}".format(left))
        print("right = {}".format(right))

        # rotate 90 degrees counterclockwise back
        returnLeft = right * -1
        returnRight = left

        print("returnLeft = {}".format(returnLeft))
        print("returnRight = {}".format(returnRight))

        return returnLeft, returnRight

    def translate(self, value, leftMin, leftMax, rightMin, rightMax):
        # figure out how 'wide' each range is
        leftSpan = leftMax - leftMin
        rightSpan = rightMax - rightMin

        # convert the left range into a 0-1 range (float)
        valueScaled = float(value - leftMin) / float(leftSpan)

        # convert the 0-1 range into a value in the right range.
        return rightMin + (valueScaled * rightSpan)

    # call back functions for left thumb stick
    def leftThumbX(self, xValue):
        self.xValueLeft = xValue
        self.updateFeet()

    def xValueLeftValue(self):
        return self.xValueLeft

    def leftThumbY(self, yValue):
        self.yValueLeft = yValue
        self.updateFeet()

    # call back functions for right thumb stick
    def rightThumbX(self, xValue):
        self.xValueRight = xValue
        self.updateDome()

    def xValueRightValue(self):
        return self.xValueRight

    def rightThumbY(self, yValue):
        self.yValueRight = yValue
        self.updateDome()

    def dpadButton(self, value):
        print("dpadButton = {}".format(value))
        self.dpadValue = value
        self.transitionLegs()

    def lbButton(self, value):
        print("lbButton = {}".format(value))
        self.lbValue = value

    def backButton(self, value):
        print("backButton = {}".format(value))
        self.stop()

    def aButton(self, value):
        print("aButton = {}".format(value))
        if value == 1:
            self.annoyed()


    def xButton(self, value):
        print("xButton = {}".format(value))
        if value == 1:
            self.worried()
            if(self.lbValue == 1):
                self.peekabooCtrlr.resume()


    def bButton(self, value):
        print("bButton = {}".format(value))
        if value == 1:
            self.whistle()
            if(self.lbValue == 1):
                self.peekabooCtrlr.stop()

    def yButton(self, value):
        print("yButton = {}".format(value))
        if value == 1:
            self.scream()


    # behavioral functions
    def annoyed(self):
        print("sound annoyed")
        SoundController.annoyed(self.soundCtrlr)

    def worried(self):
        print("sound worried")
        SoundController.worried(self.soundCtrlr)

    def whistle(self):
        print("sound whistle")
        SoundController.whistle(self.soundCtrlr)

    def scream(self):
        print("sound scream")
        SoundController.scream(self.soundCtrlr)


    def transitionLegs(self):
        # up
        if((self.dpadValue == (0,-1)) & (self.lbValue == 1)):
            print("3 legged mode started")
            self.pi.write(self.gpioPin_3_leg_mode, 1)
            sleep(0.1)
            self.pi.write(self.gpioPin_3_leg_mode, 0)
        # down
        elif((self.dpadValue == (0,1)) & (self.lbValue == 1)):
            print("2 legged mode started")
            self.pi.write(self.gpioPin_2_leg_mode, 1)
            sleep(0.1)
            self.pi.write(self.gpioPin_2_leg_mode, 0)

    def updateDome(self):
        # debug
        print("xValueRight {}".format(self.xValueRight))
        print("yValueRight {}".format(self.yValueRight))

        # x,y values coming from XboxController are rotated 90 degrees,
        # so rotate 90 degrees counterclockwise back (x,y) = (-y, x)
        x1 = self.yValueRight * -1
        y1 = self.xValueRight

        # debug
        print("x1 {}".format(x1))
        print("y1 {}".format(x1))

        # i.e. if i push left, motor should be spinning left
        #      if i push right, motor should be spinning right

        # assuming RC, then you need to generate pulses about 50 times per second
        # where the actual width of the pulse controls the speed of the motors,
        # with a pulse width of about 1500 is stopped
        # and somewhere around 1000 is full reverse and 2000 is full forward.
        dutyCycleSyren10 = self.translate(x1, -1, 1, 1000, 2000)

        # debug
        print("---------------------")
        print("dutyCycleSyren10 {}".format(dutyCycleSyren10))
        print("---------------------")

        self.pi.set_servo_pulsewidth(self.gpioPin_Syren10, dutyCycleSyren10)


    def updateFeet(self):
        # debug
        print("xValueLeft {}".format(self.xValueLeft))
        print("yValueLeft {}".format(self.yValueLeft))

        # i.e. if i push left, left motor should be spinning backwards, right motor forwards
        #      if i push right, left motor should be spinning forwards, right motor backwards

        left, right = self.steering(self.xValueLeft, self.yValueLeft)

        # assuming RC, then you need to generate pulses about 50 times per second
        # where the actual width of the pulse controls the speed of the motors,
        # with a pulse width of about 1500 is stopped
        # and somewhere around 1000 is full reverse and 2000 is full forward.
        dutyCycleS1 = self.translate(left, -1, 1, 1000, 2000)
        dutyCycleS2 = self.translate(right, -1, 1, 1000, 2000)

        # debug
        print("---------------------")
        print("dutyCycleS1 {}".format(dutyCycleS1))
        print("dutyCycleS2 {}".format(dutyCycleS2))
        print("---------------------")

        self.pi.set_servo_pulsewidth(self.gpioPin_SabertoothS1, dutyCycleS1)
        self.pi.set_servo_pulsewidth(self.gpioPin_SabertoothS2, dutyCycleS2)

    def stop(self):
        self.pi.set_servo_pulsewidth(self.gpioPin_Syren10, 0)
        self.pi.set_servo_pulsewidth(self.gpioPin_SabertoothS1, 0)
        self.pi.set_servo_pulsewidth(self.gpioPin_SabertoothS2, 0)
        self.xboxCtrlr.stop()
        self.peekabooCtrlr.stop()
        self.peekabooCtrlr.stopVideo()
        self.running = False


if __name__ == '__main__':

    print ("R2PY started")
    print("creating R2PY")
    controller = R2PY()
    print("R2PY instantiated")
    try:
        while controller.running:
            sleep(0.1)

    # Ctrl C
    except KeyboardInterrupt:
        print("User cancelled")

    # Error
    except:
        print("Unexpected error:", sys.exc_info()[0])
        raise

    finally:
        print ("stop")
        # if its still running (probably because an error occured, stop it
        if controller.running: controller.stop()
