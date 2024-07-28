# Needed for MicListener
import sounddevice as sd # needed to control the microphone
import soundfile as sf # needed to create the audio files
#import numpy # needed to create the numpy array of the wav files
import queue # needed for making the queue that handles real time audio
import sys # needed for file status
from openai import OpenAI # needed for calling OpenAI Audio API
import yaml # needed for config
import pika # needed to send messages out via RabbitMQ
import threading # needed for multi threads
from gpiozero import Button # needed for button control

import pygame # needed for audio
pygame.init()

from motorController import MotorController

import time


class MicListener:
    """
    Class that handles streaming the audio from a microphone
    """

    def __init__(self):
        """
        Initialization method
        """
        
        self.motorController = MotorController()
        
        self.recordStatus = False
        self.button = Button(1)

        self.detectedObjects = []

        self.queue = queue.Queue()
        self.deviceInfo = sd.query_devices(kind='input')
        #print(str(self.deviceInfo))

        # load config settings
        CFG = None  # global CFG settings
        with open("./configs/config.yml", "r") as ymlfile:
            CFG = yaml.safe_load(ymlfile)

        # load openAI keys into client
        self.client = OpenAI(api_key=CFG["openai"]["API_KEY"])

        # setup RabbitMQ connection
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.channel = connection.channel()
        self.channel.queue_declare(queue='mtr')

        #creates exchanges if they don't already exist
        self.channel.exchange_declare(exchange='cv', exchange_type='fanout')
        #self.channel.exchange_declare(exchange='rsp', exchange_type='fanout')
        #self.channel.exchange_declare(exchange='imu', exchange_type='fanout')


        self.channel.basic_consume(queue='cv', on_message_callback=self.cvCallback, auto_ack=True)
        #self.channel.basic_consume(queue='rsp', on_message_callback=self.rspCallback, auto_ack=True)
        #self.channel.basic_consume(queue='imu', on_message_callback=self.imuCallback, auto_ack=True)
        self.rabbitThread = threading.Thread(target=self.channel.start_consuming, daemon=True)
        self.rabbitThread.start()
        
        self.motorThread = threading.Thread(target=self.motorController.moveIt, daemon=True)
        self.motorThread.start()


    def cvCallback(self, ch, method, properties, body):
        """
        Callback method for object detection

        Args:
            ch (_type_): _description_
            method (_type_): _description_
            properties (_type_): _description_
            body (_type_): _description_
        """
        
        self.detectedObjects = body.decode()
        

    def rspCallback(self, ch, method, properties, body):
        """
        Callback method to push text to speech from other programs
        """
        request = body.decode()
        print(request)

    def imuCallback(self, ch, method, properties, body):
        """
        Callback method to push IMU data
        """
        request = body.decode()
        print(request)

    def publishText(self, text):
        """
        Publishes the given text to the motor message queue

        Args:
            text (str): the text that represents the audio transcription
        """
        
        print(text)

        self.channel.basic_publish(exchange='', routing_key='mtr', body=str(text))

    def transcribeAudio(self):
        """
        Transcribes the recorded audio into a text string and returns it

        Returns:
            str: The text representing all speech recorded by the audio file
        """
        audio_file = open("request.wav", "rb")
        transcript = self.client.audio.transcriptions.create(model="whisper-1", file=audio_file, response_format="text")

        return str(transcript)
    
    def callLLM(self, question):
        """
        passes the given question to the LLM

        Args:
            question (str): The string representing the user question
        """
        
        movementString = ""

        completion = self.client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are ComBee, a robot connected to multiple sensors and motors that is able to talk to users."},
            {"role": "system", "content": "You are connected to a wheeled motorized chassis that is capable of moving forwards, backwards, left, and right."},
            {"role": "system", "content": f"You are connected to an IMU sensor that currently has no readings"},
            {"role": "system", "content": f"You are connected to a Web Cam capable of object detection that sees the current objects: {str(self.detectedObjects)}"},
            {"role": "system", "content": "If the user wants you to move or navigate, return all movement commands in the format of [Forward/Reverse/Turn, angle (in degrees), time (in seconds)] Only return data in this format and always use the brackets with each command on a new line.  For example a command to turn left would look like [Turn, -90, 0] "},
            {"role": "system", "content": "If the user wants you to respond back to them with either an answer or comment, return that command in the format of [Text, Response] for example if the user asked you the prompt of what is your name, you would reply with [Text, My name is ComBee]."},
            {"role": "system", "content": "You may combine and respond with both movement and response commands, but each must be on a new line."},
            {"role": "system", "content": "Using this sensor data and formatting instructions, try to answer the following question from the user."},
            {"role": "user", "content": f"{str(question)}"}
        ]
        )

        output = str(completion.choices[0].message.content)
        print(output)
        
        lines = output.split("]")

        for i in range(len(lines) - 1):

            message = lines[i].replace("[","").replace("]","")
            print(message)
            if "Text" in message:
                transcript = message.split(',', 1)[1]
                #print(transcript)

                # generate audio
                response = self.client.audio.speech.create(model="tts-1", voice="onyx", input=f"{str(transcript)}",)
                response.stream_to_file("response.mp3")
                #time.sleep(1)

                # plays the response
                pygame.mixer.Sound('response.mp3').play()
            elif "Forward" in message:
                print("Forward command")
                message = message.replace(",", "")
                self.motorController.processMessage(message)
            elif "Reverse" in message:
                print("Reverse command")
                message = message.replace(",", "")
                self.motorController.processMessage(message)
            elif "Turn" in message:
                print("Turn command")
                message = message.replace(",", "")
                self.motorController.processMessage(message)
            else:
                print("catch all")



    def callback(self, indata, frames, time, status):
        """This is called (from a separate thread) for each audio block."""
        if status:
            print(status, file=sys.stderr)
        self.queue.put(indata.copy())

    def computerListener(self):
        """
        records the microphone, and ends when the user presses CTRL + C
        """
        try:
            sampleRate = int(self.deviceInfo['default_samplerate'])
            with sf.SoundFile(file="request.wav", mode='w', samplerate=sampleRate, channels=1, subtype='PCM_16') as file:
                with sd.InputStream(samplerate=sampleRate, channels=1, callback=self.callback):
                    print("Press CTRL + C to stop recording")
                    while True:
                        file.write(self.queue.get())
        except KeyboardInterrupt:
            print("Recording finished")
    
    def piListener(self):
        """
        records mic while button is pressed, and stops while released
        """
        
        print("press button to record")
        
        """
        
        try:
            sampleRate = int(self.deviceInfo['default_samplerate'])
            with sf.SoundFile(file="request.wav", mode='w', samplerate=sampleRate, channels=1, subtype='PCM_16') as file:
                with sd.InputStream(samplerate=sampleRate, channels=1, callback=self.callback):
                    while True:
                        if self.button.is_pressed:
                            self.recordStatus = True
                            file.write(self.queue.get())
                        elif not self.button.is_pressed and self.recordStatus:
                            self.recordStatus = False
                            print("Finished recording")
                            raise KeyboardInterrupt
                        elif not self.queue.empty():
                            #print("clearing queue")
                            self.queue.get()
                            
                            
        except KeyboardInterrupt:
            print("Recording finished")
        
        """
        
        
        sampleRate = int(self.deviceInfo['default_samplerate'])
        with sf.SoundFile(file="request.wav", mode='w', samplerate=sampleRate, channels=1, subtype='PCM_16') as file:
            with sd.InputStream(samplerate=sampleRate, channels=1, callback=self.callback):
                while True:
                    if self.button.is_pressed:
                        self.recordStatus = True
                        file.write(self.queue.get())
                    elif not self.button.is_pressed and self.recordStatus:
                        self.recordStatus = False
                        print("Finished recording")
                        file.close()
                        break
                    elif not self.queue.empty():
                            #print("clearing queue")
                            self.queue.get()
        

if __name__ == "__main__":
    print("Running Mic Listener")

    micListener = MicListener()

    while True:

        #input("Press any key to start transcribing: ")
        #micListener.computerListener()
        micListener.piListener()
        text = micListener.transcribeAudio()
        #micListener.publishText(text=text)
        print(text)
        micListener.callLLM(text)
