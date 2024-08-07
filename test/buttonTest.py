from gpiozero import Button, LED

led = LED("BOARD8")
led.off()
button = Button("BOARD10")

while True:
    if button.is_pressed:
        print("Button is pressed")
    else:
        print("Button is not pressed")
