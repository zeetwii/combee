from adafruit_servokit import ServoKit # needed for servo movements

class PanTiltSystem:
    """
    Moving this to a seperate class because neither ultralytics or pkia like to multithread
    """

    def __init__(self):
        """
        Initialization method
        """

        # setup servos
        self.kit = ServoKit(channels=16)
        self.panServo = self.kit.servo[0] # servo 0 is the one that pans
        self.tiltServo = self.kit.servo[1] # servo 1 handles tilt

        self.panServo.actuation_range = 270
        self.panServo.set_pulse_width_range(500, 2500)
        self.tiltServo.set_pulse_width_range(500, 2500)
        self.panServo.angle = 90
        self.tiltServo.angle = 90

        # min and max tilt angle to stop camera hitting stuff
        self.minTiltAngle = 30
        self.maxTiltAngle = 140

        self.channel.queue_declare(queue='cameraInput') 
        self.channel.queue_declare(queue='audioInput')

        self.channel.basic_consume(queue='cameraInput', on_message_callback=self.cameraCallback, auto_ack=True)


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

        #self.panServo.angle = actualPanAngle
        #self.tiltServo.angle = actualTiltAngle


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



    def startListening(self):
        """
        Begin processing RabbitMQ messages.  
        """

        print("Beginning RabbitMQ listener")
        self.channel.start_consuming()

if __name__ == "__main__":
    print("Running Pan Tilt system")

    panTilt = PanTiltSystem()

    panTilt.startListening()