# python R2.py

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

# import modules
import sys
import RPi.GPIO as GPIO
import math
from time import sleep
import pygame
from XboxController import XboxController
from SoundController import SoundController
from PeekabooController import PeekabooController

class R2PY:

    def __init__(self):
        self.sabertoothS1 = 0
        self.sabertoothS2 = 0
        self.syren10 = 0
        self.gpioPin_SabertoothS1 = 3
        self.gpioPin_SabertoothS2 = 5
        self.gpioPin_Syren10 = 7
        self.gpioPin_2_leg_mode = 16
        self.gpioPin_3_leg_mode = 18

        # setup gpio
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)

        GPIO.setup(self.gpioPin_2_leg_mode, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self.gpioPin_3_leg_mode, GPIO.OUT, initial=GPIO.LOW)

        GPIO.setup(self.gpioPin_SabertoothS1, GPIO.OUT)
        # channel=3 frequency=50Hz
        self.sabertoothS1 = GPIO.PWM(self.gpioPin_SabertoothS1, 50)
        self.sabertoothS1.start(7.5)

        GPIO.setup(self.gpioPin_SabertoothS2, GPIO.OUT)
        # channel=5 frequency=50Hz
        self.sabertoothS2 = GPIO.PWM(self.gpioPin_SabertoothS2, 50)
        self.sabertoothS2.start(7.5)

        GPIO.setup(self.gpioPin_Syren10, GPIO.OUT)
        # channel=7 frequency=50Hz
        self.syren10 = GPIO.PWM(self.gpioPin_Syren10, 50)
        self.syren10.start(7.5)


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
        # setup controller values
        self.xValueLeft = 0
        self.yValueLeft = 0
        self.xValueRight = 0
        self.yValueRight = 0
        self.dpadValue = (0,0)
        self.lbValue = 0

        self.xboxCtrlr = XboxController(deadzone=0.2,
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
                self.peekabooCtrlr.running = True


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
            GPIO.output(self.gpioPin_3_leg_mode, GPIO.HIGH)
            sleep(0.1)
            GPIO.output(self.gpioPin_3_leg_mode, GPIO.LOW)
        # down
        elif((self.dpadValue == (0,1)) & (self.lbValue == 1)):
            print("2 legged mode started")
            GPIO.output(self.gpioPin_2_leg_mode, GPIO.HIGH)
            sleep(0.1)
            GPIO.output(self.gpioPin_2_leg_mode, GPIO.LOW)

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

        dutyCycleSyren10 = self.translate(x1, -1, 1, 5, 10)

        # debug
        print("dutyCycleSyren10 {}".format(dutyCycleSyren10))
        print("")

        # assuming RC, then you need to generate pulses about 50 times per second
        # where the actual width of the pulse controls the speed of the motors,
        # with a pulse width of about 1500 is stopped
        # and somewhere around 1000 is full reverse and 2000 is full forward.

        # if the power is 0 stop the motors
        # if powerA == 0 and powerB == 0:
        #    sabertoothS1.stop()
        #    sabertoothS2.stop()
        # otherwise start them up
        # else:
        self.syren10.ChangeDutyCycle(dutyCycleSyren10)
        # sleep(0.1)

    def updateFeet(self):
        # debug
        print("xValueLeft {}".format(self.xValueLeft))
        print("yValueLeft {}".format(self.yValueLeft))

        # i.e. if i push left, left motor should be spinning backwards, right motor forwards
        #      if i push right, left motor should be spinning forwards, right motor backwards

        left, right = self.steering(self.xValueLeft, self.yValueLeft)

        self.dutyCycleS1 = self.translate(left, -1, 1, 5, 10)
        self.dutyCycleS2 = self.translate(right, -1, 1, 5, 10)

        # debug
        print("dutyCycleS1 {}".format(self.dutyCycleS1))
        print("dutyCycleS2 {}".format(self.dutyCycleS2))
        print("")

        # assuming RC, then you need to generate pulses about 50 times per second
        # where the actual width of the pulse controls the speed of the motors,
        # with a pulse width of about 1500 is stopped
        # and somewhere around 1000 is full reverse and 2000 is full forward.

        # if the power is 0 stop the motors
        # if powerA == 0 and powerB == 0:
        #    sabertoothS1.stop()
        #    sabertoothS2.stop()
        # otherwise start them up
        # else:
        self.sabertoothS1.ChangeDutyCycle(self.dutyCycleS1)
        self.sabertoothS2.ChangeDutyCycle(self.dutyCycleS2)
        # sleep(0.1)

    def stop(self):
        GPIO.cleanup()
        self.xboxCtrlr.stop()
        self.peekabooCtrlr.stop()
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
