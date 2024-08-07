import time # needed for sleep
import datetime # needed for timestamps
import random # needed for random number generation
from adafruit_servokit import ServoKit # needed for servo movements
# setup servo kit
kit = ServoKit(channels=16)
kit.servo[0].actuation_range = 270
kit.servo[0].set_pulse_width_range(500, 2500)
kit.servo[1].set_pulse_width_range(500, 2500)
print("init servos")
kit.servo[0].angle = 90
kit.servo[1].angle = 90
time.sleep(5)
print("Initalization finished")
while True:
	yawAngle = random.randint(5, 175)
	pitchAngle = random.randint(5, 175)
	
	#print(f"Setting angles to {str(yawAngle)} and {str(pitchAngle)}")
	kit.servo[0].angle = yawAngle
	kit.servo[1].angle = pitchAngle
	time.sleep(5) # give time for everything to move and stabalize
	
