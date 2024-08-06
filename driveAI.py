import pika # needed to read messages out via RabbitMQ
#import threading # needed for multi threads
#import gpiozero # needed for motor control
import time # needed for sleep

class DriveAI:
    """
    Class that controls the motors and navigation for the rover

    Note: currently doesn't navigate
    """

    def __init__(self, maxSpeed=1):
        """
        Initialization method

        Args:
            maxSpeed (int, optional): The max speed to use for the motors, should be between 0 and 1. Defaults to 1.
        """

        # fix max speed if entered wrong
        while abs(maxSpeed) > 1:
            maxSpeed = abs(maxSpeed) / 10
        
        print(f"DriveAI started, motors have a max speed of: {str(maxSpeed)}")
        self.maxSpeed = maxSpeed

        #TODO Change these to pull from a yaml config
        self.turnRate = 120.0 # turn 120 degrees a second
        self.moveRate = 1.0 # move 1 foot a second

        # set up RabbitMQ
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel()

        self.channel.queue_declare(queue='moveInput')
        self.channel.queue_declare(queue='audioInput')
        self.channel.basic_consume(queue='moveInput', on_message_callback=self.driveCallback, auto_ack=True)

    def startListening(self):
        """
        Starts listening to the message queues
        """

        print("Beginning RabbitMQ listener")
        self.channel.start_consuming()

    def driveCallback(self, ch, method, properties, body):
        """
        Callback method for drive input queue

        Args:
            ch (_type_): _description_
            method (_type_): _description_
            properties (_type_): _description_
            body (str): message from the user
        """
        message = body.decode()
        #print(message)

        command = str(message).split(', ')

        if command[0].startswith("TURN"):
            if len(command) == 2: # correct length
                try:
                    self.turn(float(command[1]))
                except ValueError:
                    print("Error, expected angle value could not turn into a float")
                    #TODO: make audio message
            else:
                print("Error, unexpected number of of commands")
                    #TODO: make audio message
        elif command[0].startswith("MOVED"):
            if len(command) == 3:
                try:
                    self.moveD(float(command[1]), float(command[2]))
                except ValueError:
                    print("Error, expected values could not turn into a float")
                    #TODO: make audio message
            else:
                print("Error, unexpected number of of commands")
                    #TODO: make audio message
        elif command[0].startswith("MOVET"):
            if len(command) == 3:
                try:
                    self.moveT(float(command[1]), float(command[2]))
                except ValueError:
                    print("Error, expected values could not turn into a float")
                    #TODO: make audio message
            else:
                print("Error, unexpected number of of commands")
                    #TODO: make audio message
        else:
             print("Error, unexpected command")   


    def turn(self, angle):
        """
        Handles turn movements

        Args:
            angle (float): the angle to turn to in degrees
        """

        turnTime = abs(float(angle)) / self.turnRate # calc how long to turn

        if angle > 0: # turn right
            # Left motors forward, right motors reverse
            frontRight = self.maxSpeed
            rearLeft = self.maxSpeed
            frontLeft = self.maxSpeed
            rearRight = self.maxSpeed

            time.sleep(turnTime)
            print(f"Turn right for {str(turnTime)} seconds")
        else: # turn left
            # Left motors reverse, right motors forward
            frontRight = self.maxSpeed
            rearLeft = self.maxSpeed
            frontLeft = self.maxSpeed
            rearRight = self.maxSpeed

            time.sleep(turnTime)
            print(f"Turn left for {str(turnTime)} seconds")


    def moveD(self, angle, distance):
        """
        Handles moving a given distance

        Args:
            angle (float): the angle to move at (0 for forward, 180 for reverse, anywhere in between)
            distance (float): the distance to travel in feet
        """

        # translate distance into time
        moveTime = distance / self.moveRate

        if -90 <= float(angle) <= 90:
            self.moveForward(float(angle), moveTime)
        else:
            self.moveReverse(float(angle), moveTime)


    def moveT(self, angle, moveTime):
        """
        Handles moving a given time

        Args:
            angle (float): the angle to move at (0 for forward, 180 for reverse, anywhere in between)
            moveTime (float): the time to travel in seconds
        """

        if -90 <= float(angle) <= 90:
            self.moveForward(float(angle), moveTime)
        else:
            self.moveReverse(float(angle), moveTime)

    
    def moveReverse(self, angle, runtime):
        """
        Handles moving the robot backwards at a given angle for a given time

        Args:
            angle (float): The angle to move at
            runtime (float): the time to run
        """

        # because of mecanum wheel design all movements are done in movement pairs across the four wheels
        primary = self.maxSpeed
        secondary = self.maxSpeed

        angle = float(angle) # cast to float for math

        # check to make sure angle is within valid range:

        # check to make sure its not larger than 180 degrees
        while angle > 180:
            angle = angle - 360
        
        while angle < -180: 
            angle = angle + 360

        if -90 <= angle <= 90: # actually moving forward
            self.moveForward(angle, runtime)

        if angle > 0: # moving backwards in a right leaning angle
            # motors frontLeft and rearRight move with secondary
            # motors frontRight and rearLeft move with primary
            if angle <= 135: # secondary motors move forward
                secondary = secondary - (secondary * ((angle - 90) / 45))
                
                # catch edge cases
                if secondary > 1:
                    secondary = 1
                if secondary < 0:
                    secondary = 0
                
                # Reverse
                frontRight = primary
                rearLeft = primary

                # Forward
                frontLeft = secondary
                rearRight = secondary

                time.sleep(float(runtime))

                # turn all motors off
                frontLeft = 0
                rearRight = 0
                frontRight = 0
                rearLeft = 0 

                print(f"Move Reverse, 90 to 135: P: {str(primary)} S: {str(secondary)}")

            else: # secondary motors move in reverse
                secondary = (secondary * ((angle - 135) / 45))
                
                # catch edge cases
                if secondary > 1:
                    secondary = 1
                if secondary < 0:
                    secondary = 0
                
                # Reverse
                frontRight = primary
                rearLeft = primary
                frontLeft = secondary
                rearRight = secondary

                time.sleep(float(runtime))

                # turn all motors off
                frontLeft = 0
                rearRight = 0
                frontRight = 0
                rearLeft = 0 

                print(f"Move Reverse, 135 to 180: P: {str(primary)} S: {str(secondary)}")

        else: # moving backward in a left leaning direction
            # motors frontLeft and rearRight move with primary
            # motors frontRight and rearLeft move with secondary

            if abs(angle) <= 135: # secondary motors move forward
                secondary = secondary - (secondary * ((abs(angle) - 90) / 45))
                
                # catch edge cases
                if secondary > 1:
                    secondary = 1
                if secondary < 0:
                    secondary = 0
                
                # Forward
                frontRight = secondary
                rearLeft = secondary

                # Reverse
                frontLeft = primary
                rearRight = primary

                time.sleep(float(runtime))

                # turn all motors off
                frontLeft = 0
                rearRight = 0
                frontRight = 0
                rearLeft = 0 

                print(f"Move Reverse, -90 to -135: P: {str(primary)} S: {str(secondary)}")

            else: # secondary motors move in reverse
                secondary = (secondary * ((abs(angle) - 135) / 45))
                
                # catch edge cases
                if secondary > 1:
                    secondary = 1
                if secondary < 0:
                    secondary = 0
                
                # Reverse
                frontRight = secondary
                rearLeft = secondary
                frontLeft = primary
                rearRight = primary

                time.sleep(float(runtime))

                # turn all motors off
                frontLeft = 0
                rearRight = 0
                frontRight = 0
                rearLeft = 0 

                print(f"Move Reverse, -135 to -180: P: {str(primary)} S: {str(secondary)}")


    def moveForward(self, angle, runtime):
        """
        Handles moving the robot forward at a given angle for a given time

        Args:
            angle (float): The angle to move at
            runtime (float): the time to run
        """

        # because of mecanum wheel design all movements are done in movement pairs across the four wheels
        primary = self.maxSpeed
        secondary = self.maxSpeed

        angle = float(angle) # cast to float for math

        if angle >= 0: # move forward in a right leaning angle
            # motors frontLeft and rearRight move with primary
            # motors frontRight and rearLeft move with secondary
            if angle <= 45: # secondary motors moving forward
                secondary = secondary - (secondary * (angle / 45))
                # catch edge cases
                if secondary > 1:
                    secondary = 1
                if secondary < 0:
                    secondary = 0

                # all forward
                frontLeft = primary
                rearRight = primary
                frontRight = secondary
                rearLeft = secondary    

                time.sleep(float(runtime))

                # turn all motors off
                frontLeft = 0
                rearRight = 0
                frontRight = 0
                rearLeft = 0 

                print(f"Move Forward, 0 to 45: P: {str(primary)} S: {str(secondary)}")

            elif angle <= 90: # secondary motors moving in reverse
                secondary = (secondary * ((angle - 45) / 45))
                # catch edge cases
                if secondary > 1:
                    secondary = 1
                if secondary < 0:
                    secondary = 0

                # primary forward
                frontLeft = primary
                rearRight = primary

                # secondary reverse
                frontRight = secondary
                rearLeft = secondary    

                time.sleep(float(runtime))

                # turn all motors off
                frontLeft = 0
                rearRight = 0
                frontRight = 0
                rearLeft = 0 

                print(f"Move Forward, 45 to 90: P: {str(primary)} S: {str(secondary)}")
            else:
                # angle is greater than 90 degrees which means we're actually going in reverse
                self.moveReverse(angle, runtime)
        else: # move forward in a left leaning direction
            # motors frontRight and rearLeft move with primary
            # motors frontLeft and rearRight move with secondary
            if angle >= -45: # secondary motors moving forward
                secondary = secondary - (secondary * (abs(angle) / 45))
                # catch edge cases
                if secondary > 1:
                    secondary = 1
                if secondary < 0:
                    secondary = 0

                # all forward
                frontRight = primary
                rearLeft = primary
                frontLeft = secondary
                rearRight = secondary    

                time.sleep(float(runtime))

                # turn all motors off
                frontLeft = 0
                rearRight = 0
                frontRight = 0
                rearLeft = 0 

                print(f"Move Forward, -0 to -45: P: {str(primary)} S: {str(secondary)}")

            elif angle >= -90: # secondary motors moving in reverse
                secondary = (secondary * ((abs(angle) - 45) / 45))
                # catch edge cases
                if secondary > 1:
                    secondary = 1
                if secondary < 0:
                    secondary = 0

                # primary forward
                frontRight = primary
                rearLeft = primary

                # secondary reverse
                frontRight = secondary
                rearLeft = secondary    

                time.sleep(float(runtime))

                # turn all motors off
                frontLeft = 0
                rearRight = 0
                frontRight = 0
                rearLeft = 0 

                print(f"Move Forward, -45 to -90: P: {str(primary)} S: {str(secondary)}")
            else:
                # angle is greater than 90 degrees which means we're actually going in reverse
                self.moveReverse(angle, runtime)





if __name__ == "__main__":
    print("Running DriveAI")

    driveAI = DriveAI(1)
    driveAI.startListening()