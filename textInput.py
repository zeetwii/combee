# Backup program for allowing to control combee via typed commands incase audio goes down

import pika # needed to send messages out via RabbitMQ


connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.queue_declare(queue='userInput')

print("Running text input script.  Type out commands as if they had been parsed by audio.  ")

while True:

    try:

        userText = input("\nEnter what you want to say to the robot: \n")

        channel.basic_publish(exchange='', routing_key='userInput', body=userText)


    except KeyboardInterrupt:
        print("\nInterrupt detected, closing down")
        connection.close() # close RabbitMQ socket

        break