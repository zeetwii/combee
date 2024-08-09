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


    def startListening(self):
        """
        Begin processing RabbitMQ messages.  
        """

        print("Beginning RabbitMQ listener")
        self.channel.start_consuming()


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
            #time.sleep(2)
    def panTilt(self, panAngle, tiltAngle):
        """
        method to adjust the pan and tilt system the camera is on

        Args:
            panAngle (int): the angle to look left or right relative to straight ahead
            tiltAngle (int): the angle to look up or down relative to straight ahead
        """

        actualPanAngle = 90 + int(panAngle) # 90 degrees is our center
        actualTiltAngle = 90 + int(tiltAngle)

        if actualPanAngle < 0: # if less than min angle 
            actualPanAngle = 0
        elif actualPanAngle > 180: # if greater than max angle
            actualPanAngle = 180

        if actualTiltAngle < self.minTiltAngle: # if less than min angle 
            actualTiltAngle = self.minTiltAngle
        elif actualTiltAngle > self.maxTiltAngle: # if greater than max angle
            actualTiltAngle = self.maxTiltAngle

        self.panServo.angle = actualPanAngle
        self.tiltServo.angle = actualTiltAngle

    def cameraCallback(self, ch, method, properties, body):
        """
        Callback method for camera input queue, passes question to camera motor controller

        Args:
            ch (_type_): _description_
            method (_type_): _description_
            properties (_type_): _description_
            body (str): message from the user
        """
        
        message = body.decode()
        print(message)
        command = str(message).split(', ')

        if command[0].startswith("PANTILT"):
            if len(command) == 3: # the expected length
                try:
                    self.moveD(int(command[1]), int(command[2]))
                except ValueError:
                    print("Error, expected values could not turn into a int")
                    self.channel.basic_publish(exchange='', routing_key='audioInput', body="Error from the Camera AI, expected angle value could not turn into an int")
            else:
                print("Error, unexpected number of of commands")
                self.channel.basic_publish(exchange='', routing_key='audioInput', body="Error from the Camera AI, unexpected number of commands")



if __name__ == "__main__":
    print("Running Computer Vision system")

    cameraAI = CameraAI(cameraSelect=0)
    #cameraAI.startListening()
    cameraAI.comptuerVisionThread()