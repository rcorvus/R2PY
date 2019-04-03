import cv2

class FaceDetector:
    def __init__(self, faceCascadePath):
        # load the face detector
        try:
            self.faceCascade = cv2.CascadeClassifier(faceCascadePath)
        except:
            print("CascadeClassifier failed to load")

    def detect(self, image, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)):
        # detect faces in the image
        try:
            rects = self.faceCascade.detectMultiScale(image,
                                                  scaleFactor=scaleFactor, minNeighbors=minNeighbors,
                                                  minSize=minSize, flags=cv2.CASCADE_SCALE_IMAGE)
        except:
            print("failure while trying to detect face in image")

        # return the rectangles representing boundinb
        # boxes around the faces
        return rects
