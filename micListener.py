import sounddevice as sd # needed to record audio from the microphone
import soundfile as sf # needed to save the recorded audio to a wav file
import queue # needed to create a queue for recording audio from the microphone in real time
import sys # needed for printing errors to stderr
from pywhispercpp.model import Model # needed for speech to text
import pika # needed for RabbitMQ interactions
import threading # needed for multithreading
from gpiozero import Button, LED # needed for button and LED interactions
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

        self.model = Model('tiny.en')

        # set up RabbitMQ
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', heartbeat=3600)) # increase heartbeat to deal with weird dropouts
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

        # check the file size to make sure audio file is long enough
        f = sf.SoundFile("request.wav")

        #print(f"Runtime = {str(f.frames / f.samplerate)}")

        if (f.frames / f.samplerate) > 0.1:
            segments = self.model.transcribe("request.wav")
            return " ".join(s.text for s in segments).strip()
        else:
            return "Error, recording was too short"
    
    def piListener(self):
        """
        records mic while button is pressed, and stops while released
        """
        
        print("press button to record")
        
        sampleRate = 16000
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
        if not text.startswith("Error"):
            micListener.publishText(text=text)
        else:
            print(text)
        print(text)