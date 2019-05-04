# USAGE (test)
# python Peekaboo.py --face cascades/haarcascade_frontalface_default.xml

# press 'q' to stop

# enable camera on RaspberryPi by running "sudo raspi-config" and choose "Enable Camera"

from FaceDetector import FaceDetector
from videostream import VideoStream
import numpy as np
from time import sleep
import cv2
from SoundController import SoundController
import threading

class PeekabooController(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

        self.running = False

        self.soundCtrlr = SoundController()

        self.initVideo()

        self.whereIsEveryoneFlag = False
        self.iSeeSomeoneFlag = False
        self.failure = False
        self.record = False

    def initVideo(self):
        try:
            self.video = VideoStream(src=0)
        except:
            print("video stream not found")
        if(self.video is None):
            print("video stream was not initialized")
            return

        try:
            self.video.start()
        except:
            print("video failed to start")

        # construct the face detector and allow the camera to warm up
        try:
            face = "cascades/haarcascade_frontalface_default.xml"
            self.faceDetector = FaceDetector(face)
            sleep(0.1)
        except:
            print("face detector init failed")

        # choose xvid codec
        try:
            self.fourcc = cv2.VideoWriter_fourcc(*'XVID')
        except:
            print("video writer not found")

        sleep(0.1)

    #called by the thread
    def run(self):
        self._start()

    def toggleRecord(self):
        if(self.record == True):
            self.record = False
            print("video recording stopped")
        else:
            self.record = True
            print("video recording started")

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
            # capture frames from the camera
            if(self.running == True):
                frame = self.video.read()
                if(frame is None):
                    print("ERROR: cannot read frame from video, stopping Peekaboo. If you want Peekaboo to work, connect camera and restart R2.py")
                    self.failure = True
                    self.stop()
                    break

                # resize the frame and convert it to grayscale
                frame = self.resizeImage(frame, width=500)

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
                # NOTE: comment this out if you don't want the video stream window to show in terminal
                cv2.imshow("Face", frameClone)

                # write video to file
                if self.record == True:
                    if self.writer is None:
                        # store the image dimensions, initialize the video writer,
                        # and construct the zeros array
                        (h, w) = frameClone.shape[:2]
                        self.writer = cv2.VideoWriter("r2_recording.avi", self.fourcc, 4,
                                                      (w, h), True)
                    output = np.zeros((h, w, 3), dtype="uint8")
                    output[0:h, 0:w] = frameClone
                    self.writer.write(output)

                # NOTE: comment this out if you don't want the video stream window to show in terminal
                # if the 'q' key is pressed, stop the loop
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    print("keypress 'q', stopping Peekaboo")
                    self.stop()
                    break

    def resume(self):
        print("starting PeekabooController")
        if(self.failure == True):
            print("ERROR: the video had failed to load.  If you want Peekaboo to work, you will need to connect the camera and restart R2.py")
            return
        self.running = True

    def stop(self):
        print("stopping PeekabooController")
        self.running = False
        if self.writer is not None:
            self.writer.release()

    def stopVideo(self):
        if(self.video is not None):
            self.video.stop()

        try:
            cv2.destroyAllWindows()
        except:
            print("")

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

    def resizeImage(self, image, width=None, height=None, inter=cv2.INTER_AREA):
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
        resized = cv2.resize(image, dim, interpolation=inter)

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
