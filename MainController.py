# sudo xboxdrv --silent & sudo python MainController.py &

# lsusb
# add this to sudo nano /etc/rc.local and ctrl-o, enter, ctrl-x to save:
# xboxdrv --daemon --silent &
# sudo python MainController.py

# to terminate xboxdrv
# ps aux | grep xboxdrv
# sudo kill -TERM [put-your-pid-here]
# sudo kill -KILL [put-your-pid-here]

# to output sound to the 3mm audio jack:
# sudo amixer cset numid=3 1

# to output sound to the HDMI audio
# sudo amixer cset numid=3 2

# import modules
import sys
# import motorControl
import RPi.GPIO as GPIO
import math
import XboxController
import time
import pygame.mixer


class MainController:
    sabertoothS1 = 0
    sabertoothS2 = 0
    syren10 = 0

    def __init__(self):
        global sabertoothS1
        global sabertoothS2
        global syren10
        # setup gpio
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(3, GPIO.OUT)
        # channel=3 frequency=50Hz
        sabertoothS1 = GPIO.PWM(3, 50)
        sabertoothS1.start(7.5)

        GPIO.setup(5, GPIO.OUT)
        # channel=5 frequency=50Hz
        sabertoothS2 = GPIO.PWM(5, 50)
        sabertoothS2.start(7.5)

        GPIO.setup(7, GPIO.OUT)
        # channel=7 frequency=50Hz
        syren10 = GPIO.PWM(7, 50)
        syren10.start(7.5)

        # setup controller values
        self.xValueLeft = 0
        self.yValueLeft = 0
        self.xValueRight = 0
        self.yValueRight = 0

        pygame.mixer.pre_init()
        self.xboxCont = XboxController.XboxController(deadzone=0.2,
                                                      scale=1,
                                                      invertYAxis=True)

        # setup call backs
        self.xboxCont.setupControlCallback(self.xboxCont.XboxControls.LTHUMBX, self.leftThumbX)
        self.xboxCont.setupControlCallback(self.xboxCont.XboxControls.LTHUMBY, self.leftThumbY)
        self.xboxCont.setupControlCallback(self.xboxCont.XboxControls.RTHUMBX, self.rightThumbX)
        self.xboxCont.setupControlCallback(self.xboxCont.XboxControls.RTHUMBY, self.rightThumbY)
        self.xboxCont.setupControlCallback(self.xboxCont.XboxControls.BACK, self.backButton)
        self.xboxCont.setupControlCallback(self.xboxCont.XboxControls.A, self.aButton)

        # start the controller
        self.xboxCont.start()
        pygame.mixer.init()
        # load all the sounds
        # TODO: enum the names for ordinal
        pygame.mixer.music.load("./sounds/8ANNOYED.mp3")
        self.running = True

    def steering(self, x, y):
        # assumes the initial (x,y) coordinates are in the -1.0/+1.0 range
        print "x = {}".format(x)
        print "y = {}".format(y)

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

        print "left = {}".format(left)
        print "right = {}".format(right)

        # rotate 90 degrees counterclockwise back
        returnLeft = right * -1
        returnRight = left

        print "returnLeft = {}".format(returnLeft)
        print "returnRight = {}".format(returnRight)

        return returnLeft, returnRight

    def translate(self, value, leftMin, leftMax, rightMin, rightMax):
        # figure out how 'wide' each range is
        leftSpan = leftMax - leftMin
        rightSpan = rightMax - rightMin

        # convert the left range into a 0-1 range (float)
        valueScaled = float(value - leftMin) / float(leftSpan)

        # convert the 0-1 range into a value in the right range.
        return rightMin + (valueScaled * rightSpan)

    # call back funtions for left thumb stick
    def leftThumbX(self, xValue):
        self.xValueLeft = xValue
        self.updateFeet()

    def leftThumbY(self, yValue):
        self.yValueLeft = yValue
        self.updateFeet()

    # call back funtions for right thumb stick
    def rightThumbX(self, xValue):
        self.xValueRight = xValue
        self.updateDome()

    def rightThumbY(self, yValue):
        self.yValueRight = yValue
        self.updateDome()

    def backButton(self, value):
        self.stop()

    def aButton(self, value):
        if value == 1:
            pygame.mixer.music.play(0)
            print "sound annoyed"

    def updateDome(self):
        global syren10

        # debug
        print "xValueRight {}".format(self.xValueRight)
        print "yValueRight {}".format(self.yValueRight)

        # x,y values coming from XboxController are rotated 90 degrees
        # so rotate 90 degrees counterclockwise back (x,y) = (-y, x)
        x1 = self.yValueRight * -1
        y1 = self.xValueRight

        # debug
        print "x1 {}".format(x1)
        print "y1 {}".format(x1)

        # i.e. if i push left, motor should be spinning left
        #      if i push right, motor should be spinning right

        dutyCycleSyren10 = self.translate(x1, -1, 1, 5, 10)

        # debug
        print "dutyCycleSyren10 {}".format(dutyCycleSyren10)
        print ""

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
        syren10.ChangeDutyCycle(dutyCycleSyren10)
        # time.sleep(0.1)

    def updateFeet(self):
        global sabertoothS1
        global sabertoothS2

        # debug
        print "xValueLeft {}".format(self.xValueLeft)
        print "yValueLeft {}".format(self.yValueLeft)

        # i.e. if i push left, left motor should be spinning backwards, right motor forwards
        #      if i push right, left motor should be spinning forwards, right motor backwards

        left, right = self.steering(self.xValueLeft, self.yValueLeft)

        dutyCycleS1 = self.translate(left, -1, 1, 5, 10)
        dutyCycleS2 = self.translate(right, -1, 1, 5, 10)

        # debug
        print "dutyCycleS1 {}".format(dutyCycleS1)
        print "dutyCycleS2 {}".format(dutyCycleS2)
        print ""

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
        sabertoothS1.ChangeDutyCycle(dutyCycleS1)
        sabertoothS2.ChangeDutyCycle(dutyCycleS2)
        # time.sleep(0.1)

    def stop(self):
        GPIO.cleanup()
        self.xboxCont.stop()
        self.running = False


if __name__ == '__main__':

    print ("MainController started")
    controller = 0
    try:
        print "creating MainController"
        controller = MainController()
        print "MainController instantiated"
        while controller.running:
            time.sleep(0.1)

    # Ctrl C
    except KeyboardInterrupt:
        print "User cancelled"

    # Error
    except:
        print "Unexpected error:", sys.exc_info()[0]
        raise

    finally:
        print
        print ("stop")
        # if its still running (probably because an error occured, stop it
        if controller.running: controller.stop()
