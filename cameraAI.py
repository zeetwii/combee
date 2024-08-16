from ultralytics import YOLO # needed for YOLO model
import cv2 # needed for computer vision processes
import math # needed for math functions
import time # needed for sleep
import pika # needed for RabbitMQ 
from threading import Thread # needed for multithreading

class CameraAI:
    """
    Class to handle all the camera functions
    """

    def __init__(self, cameraSelect=0):
        """
        Initialization method

        Args:
            cameraSelect (int, optional): Select which camera to use. Defaults to 0.
        """

        # set up RabbitMQ
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel()

        self.channel.queue_declare(queue='cameraInput') 

        # model stuff
        self.model = YOLO("./models/yolov10n.pt", verbose=False)
        self.detectedObjects = []

        self.cameraSelect = cameraSelect

        # start webcam
        self.webCam = cv2.VideoCapture(cameraSelect)
        #self.webCam.set(3, 640)
        #self.webCam.set(4, 480)

        self.cameraWidth = 640
        self.cameraHeight = 480
        self.viewAngle = 90


    def comptuerVisionThread(self):
        """
        Begins looking for objects in webcam - blocking thread
        """

        print("starting computer vision thread")

        while True:
            #print("test")

            self.channel.basic_publish(exchange='', routing_key='cameraOutput', body=str(self.detectedObjects))
            self.detectedObjects.clear()

            success, img = self.webCam.read()
            results = self.model(img, stream=True, conf=0.15, verbose = False)
            #test = self.model.predict(self.cameraSelect, save=False, show=True, stream=True, conf=0.15)

            for r in results:

                #print(f"Detected {len(r)} objects in image")

                for box in r.boxes:

                    # bounding box
                    x1, y1, x2, y2 = box.xyxy[0]
                    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2) # convert to int values

                    # find the center of the box
                    xCenter = float(x2 - x1) + x1
                    yCenter = float(y2 - y1) + y1

                    #print(str(xCenter))

                    xAngle = ((xCenter / self.cameraWidth) * self.viewAngle) - (self.viewAngle / 2.0)
                    xAngle = round(xAngle)
                    #print(f"Name: {str(r.names[int(box.cls[0])])} Angle: {str(xAngle)}")
                    self.detectedObjects.append(f"{str(r.names[int(box.cls[0])])}")

            #print("")
            time.sleep(1) # done to slow things down so as not to bog down the rest of the system.
 

if __name__ == "__main__":
    print("Running Computer Vision system")

    cameraAI = CameraAI(cameraSelect=0)
    #cameraAI.startListening()
    cameraAI.comptuerVisionThread()
