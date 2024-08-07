from gpiozero import Motor
from time import sleep

motor = Motor(forward="BOARD36", backward="BOARD32")

while True:
    motor.forward()
    print("forward")
    sleep(5)
    motor.backward()
    print("backward")
    sleep(5)
