from ultralytics import YOLO # needed for YOLO model
import cv2 # needed for computer vision processes
import math # needed for math functions
import time # needed for sleep
import pika # needed for RabbitMQ 
import threading # needed for multi threads

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

        self.channel.queue_declare(queue='cameraOutput')
        self.channel.queue_declare(queue='cameraInput') 

        self.channel.basic_consume(queue='cameraInput', on_message_callback=self.cameraCallback, auto_ack=True)

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

    def cameraCallback(self, ch, method, properties, body):
        """
        Callback method for camera input queue, passes question to camera motor controller

        Args:
            ch (_type_): _description_
            method (_type_): _description_
            properties (_type_): _description_
            body (str): message from the user
        """
        
        command = body.decode()
        print(command)

if __name__ == "__main__":
    print("Running Computer Vision system")

    cameraAI = CameraAI(cameraSelect=0)
    cameraAI.comptuerVisionThread()