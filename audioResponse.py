import wave
import pika # needed to send messages out via RabbitMQ
from piper.voice import PiperVoice

import pygame # needed for audio
pygame.init()

class AudioResponse:
    """
    Class that handles generating and streaming audio messages made from text input
    """

    def __init__(self):
        """
        Initialization method
        """

        # load Piper TTS voice model
        self.voice = PiperVoice.load("en_US-amy-medium.onnx")

        # set up RabbitMQ
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel()

        self.channel.queue_declare(queue='audioInput')
        self.channel.basic_consume(queue='audioInput', on_message_callback=self.audioCallback, auto_ack=True)

    def startListening(self):
        """
        starts the listener thread
        """
        print("Beginning RabbitMQ listener")
        self.channel.start_consuming()
       

    def audioCallback(self, ch, method, properties, body):
        """
        Callback method for audio out queue, turning text into speech

        Args:
            ch (_type_): _description_
            method (_type_): _description_
            properties (_type_): _description_
            body (str): message from the llm
        """

        text = body.decode()
        self.textToSpeech(text=text)


    def textToSpeech(self, text):
        """
        Turns the provided text into audio and plays it

        Args:
            text (str): The text to turn to audio
        """

        # generate audio via Piper TTS
        with wave.open("response.wav", "wb") as wav_file:
            self.voice.synthesize(str(text), wav_file)

        # plays the response
        channel = pygame.mixer.Sound('response.wav').play()

        # wait for file to finish playing
        while channel.get_busy():
            pygame.time.wait(100) # wait 100 ms

if __name__ == '__main__':
    audioResp = AudioResponse()
    audioResp.startListening()