# USAGE (test)
# python Peekaboo.py --face cascades/haarcascade_frontalface_default.xml

# press 'q' to stop

# enable camera on RaspberryPi by running "sudo raspi-config" and choose "Enable Camera"

# import the necessary packages
from FaceDetector import FaceDetector
from picamera.array import PiRGBArray
from picamera import PiCamera
import numpy as np
import time
import cv2
from SoundController import SoundController
import threading

class PeekabooController(threading.Thread):

    def __init__(self):
        # setup threading
        threading.Thread.__init__(self)

        self.running = False

        face = "cascades/haarcascade_frontalface_default.xml"

        self.soundCtrlr = SoundController()

        # initialize the camera and grab a reference to the raw camera capture
        self.camera = PiCamera()
        self.camera.resolution = (640, 480)
        self.camera.framerate = 32
        self.rawCapture = PiRGBArray(self.camera, size=(640, 480))

        # construct the face detector and allow the camera to warm up
        self.faceDetector = FaceDetector(face)
        time.sleep(0.1)

        # choose xvid codec
        self.fourcc = cv2.VideoWriter_fourcc(*'XVID')

        self.whereIsEveryoneFlag = False
        self.iSeeSomeoneFlag = False

    #called by the thread
    def run(self):
        self._start()


    # start looking
    def _start(self):
        self.running = True

        zeros = None

        previousX = 0
        direction = "NONE"

        self.writer = None
        (h, w) = (None, None)

        # run until the controller is stopped
        while (True):
            if(self.running):
                # capture frames from the camera
                for f in self.camera.capture_continuous(self.rawCapture, format="bgr", use_video_port=True):
                    # grab the raw NumPy array representing the image
                    frame = f.array

                    # resize the frame and convert it to grayscale
                    frame = self.resize(frame, width=300)
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                    # detect faces in the image and then clone the frame
                    # so that we can draw on it
                    faceRects = self.faceDetector.detect(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
                    frameClone = frame.copy()

                    # where is everyone?
                    if len(faceRects) <= 0:
                        cv2.putText(frameClone, "WHERE IS EVERYONE?", (20, 20),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 0), 2)
                        self.whereIsEveryone()
                    else:
                        # peekaboo!
                        # R2 is happy to see someone
                        self.iSeeSomeone()

                    # loop over the face bounding boxes and draw them
                    for (fX, fY, fW, fH) in faceRects:
                        cv2.rectangle(frameClone, (fX, fY), (fX + fW, fY + fH), (255, 0, 0), 2)

                        # only turn head if face gets far out of center
                        if ((previousX - 10) < fX < (previousX + 10)):
                            direction = "NONE"
                        elif fX < (previousX + 10):
                            direction = "LEFT"
                        elif fX > (previousX - 10):
                            direction = "RIGHT"

                        # turn R2's head to keep face centered
                        # if direction == "LEFT":
                            # self.mainCtrlr.rightThumbX(self.mainCntlr, self.mainCtrlr.xValueRight - 10)
                        # elif direction == "RIGHT":
                            # self.mainCtrlr.rightThumbX(self.mainCntlr, self.mainCtrlr.xValueRight + 10)

                        cv2.putText(frameClone, "PEEKABOO!".format(direction), (fX, fY - 10), cv2.FONT_HERSHEY_SIMPLEX,
                                    0.55, (0, 255, 0), 2)

                        if direction != "NONE":
                            cv2.putText(frameClone, "<Turn {}>".format(direction), (fX, fY - 0), cv2.FONT_HERSHEY_SIMPLEX,
                                        0.55, (0, 255, 0), 2)

                        previousX = fX

                    # show our detected faces, then clear the frame in preparation for the next frame
                    # NOTE:this is commented out for now because can't turn off without keyboard
                    # cv2.imshow("Face", frameClone)

                    # write video to file
                    if self.writer is None:
                        # store the image dimensions, initialize the video writer,
                        # and construct the zeros array
                        (h, w) = frameClone.shape[:2]
                        self.writer = cv2.VideoWriter("test.avi", self.fourcc, 4,
                                                      (w, h), True)
                    output = np.zeros((h, w, 3), dtype="uint8")
                    output[0:h, 0:w] = frameClone
                    self.writer.write(output)

                    self.rawCapture.truncate(0)


                    if(self.running == False):
                        print("running = false, stopping Peekaboo")
                        self.stop()
                        break

                    # NOTE:this is commented out for now because can't turn off without keyboard
                    # # if the 'q' key is pressed, stop the loop
                    # if cv2.waitKey(1) & 0xFF == ord("q"):
                    #     print("keypress 'q', stopping Peekaboo")
                    #     self.stop()
                    #     break

    def stop(self):
        self.running = False
        print("stopping PeekabooController")
        cv2.destroyAllWindows()
        self.writer.release()

    def whereIsEveryone(self):
        if(self.whereIsEveryoneFlag == False):
            SoundController.worried(self.soundCtrlr)
            self.whereIsEveryoneFlag = True
            self.iSeeSomeoneFlag = False

    def iSeeSomeone(self):
        if(self.iSeeSomeoneFlag == False):
            SoundController.whistle(self.soundCtrlr)
            self.whereIsEveryoneFlag = False
            self.iSeeSomeoneFlag = True

    def resize(self, image, width = None, height = None, inter = cv2.INTER_AREA):
        # initialize the dimensions of the image to be resized and
        # grab the image size
        dim = None
        (h, w) = image.shape[:2]

        # if both the width and height are None, then return the
        # original image
        if width is None and height is None:
            return image

        # check to see if the width is None
        if width is None:
            # calculate the ratio of the height and construct the
            # dimensions
            r = height / float(h)
            dim = (int(w * r), height)

        # otherwise, the height is None
        else:
            # calculate the ratio of the width and construct the
            # dimensions
            r = width / float(w)
            dim = (width, int(h * r))

        # resize the image
        resized = cv2.resize(image, dim, interpolation = inter)

        # return the resized image
        return resized

if __name__ == '__main__':

    print ("PeekabooController started")
    print("creating Peekaboo")
    controller = PeekabooController()
    print("Peekaboo instantiated")
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
