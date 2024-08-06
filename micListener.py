import sounddevice as sd # needed to control the microphone
import soundfile as sf # needed to create the audio files
#import numpy # needed to create the numpy array of the wav files
import queue # needed for making the queue that handles real time audio
import sys # needed for file status
from openai import OpenAI # needed for calling OpenAI Audio API
import yaml # needed for config
import pika # needed to send messages out via RabbitMQ
import threading # needed for multi threads
from gpiozero import Button, LED # needed for button control

import time # needed for sleep

class MicListener:
    """
    Class that handles listening to the microphone and generating 
    """

    def __init__(self):
        """
        Initialization method
        """

        self.recordStatus = False # boolean for if the audio is being saved

        self.led = LED("BOARD8")
        self.led.off() # just using this to turn the pin into a ground
        self.button = Button("BOARD10") # the actual button pin

        self.queue = queue.Queue()

        # setup microphone
        self.deviceInfo = sd.query_devices(kind='input')
        #print(str(self.deviceInfo))

        # load config settings
        with open("./configs/billing.yaml", "r") as ymlfile:
            config = yaml.safe_load(ymlfile)

        # load openAI keys into client
        self.client = OpenAI(api_key=config["openai"]["API_KEY"])

        # set up RabbitMQ
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel()

        self.channel.queue_declare(queue='userOutput') 
    
    def callback(self, indata, frames, time, status):
        """This is called (from a separate thread) for each audio block."""
        if status:
            print(status, file=sys.stderr)
        self.queue.put(indata.copy())

    def transcribeAudio(self):
        """
        Transcribes the recorded audio into a text string and returns it

        Returns:
            str: The text representing all speech recorded by the audio file
        """
        audio_file = open("request.wav", "rb")
        transcript = self.client.audio.transcriptions.create(model="whisper-1", file=audio_file, response_format="text")

        return str(transcript)
    
    def piListener(self):
        """
        records mic while button is pressed, and stops while released
        """
        
        print("press button to record")
        
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
    
    def publishText(self, text):
        """
        pushes text out to the message queue

        Args:
            text (str): the text to add to the message queue
        """

        self.channel.basic_publish(exchange='', routing_key='userOutput', body=text)
        
if __name__ == "__main__":
    print("Running Mic Listener")

    micListener = MicListener()

    while True:

        micListener.piListener()
        text = micListener.transcribeAudio()
        micListener.publishText(text=text)
        #print(text)
        #micListener.callLLM(text)