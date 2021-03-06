# R2.py
# version 1.0
# by Robert Corvus


# TODO:
# - Change `source /home/pi/.virtualenvs` -> `source ~/virtualenvwrapper.sh`
# - Change `workon start_py3cv3` -> `workon py3cv3` (since py3cv3 is the actual name of the environment while `start_py3cv3 is just a script used to activate the environment)
#
# Regarding your 2nd e-mail, did you update contrab properly as shown in the blog post? If yes, then can you double check if the path provided for the `on_reboot.sh` script is correct? Additionally, have you removed the lines that output the frame to the display (lines that use the cv2.imshow method)? If not, please do this since the contrab method runs in the background and it's not possible to use cv2.imshow in this case.
#
# Also, if you want to use `cv2.imshow` in your python script then you can check this comment by one of our reader who was able to get it working:
# - https://www.pyimagesearch.com/2016/05/16/running-a-python-opencv-script-on-reboot/#comment-490202




import sys
import pigpio
from pysabertooth import Sabertooth
import math
from time import sleep
import pygame
from XboxController import XboxController
from SoundController import SoundController
from PeekabooController import PeekabooController

class R2PY:

    def __init__(self):
        # if you want to switch to hardware PWM, remember:
        # GPIO12(Board 32) & GPIO18(Board 12) share a setting as do GPIO13(Board 33) & GPIO19(Board 35)

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
        self.pi.set_PWM_frequency(self.gpioPin_Syren10, 50)
        self.pi.set_servo_pulsewidth(self.gpioPin_Syren10, 0)

        # to find the usb port of the sabertooth run this: cd /dev
        # and ls to see the list of usb ports, then plug in your usb to the sabertooth and ls again to see the new port
        self.saber = Sabertooth('/dev/ttyACM0', baudrate=115200, address=128, timeout=0.1)

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
        if ((value == 1) & (self.lbValue == 1)):
            PeekabooController.toggleRecord()
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

        dutyCycleS1 = self.translate(left, -1, 1, -100, 100)
        dutyCycleS2 = self.translate(right, -1, 1, -100, 100)

        # debug
        print("---------------------")
        print("dutyCycleS1 {}".format(dutyCycleS1))
        print("dutyCycleS2 {}".format(dutyCycleS2))
        print("---------------------")

        # drive(number, speed)
        # number: 1-2
        # speed: -100 - 100
        self.saber.drive(1, dutyCycleS1)
        self.saber.drive(2, dutyCycleS2)

    def stop(self):
        self.pi.set_servo_pulsewidth(self.gpioPin_Syren10, 0)
        saber.stop()
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
