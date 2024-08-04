from openai import OpenAI # needed for calling OpenAI Audio API
import yaml # needed for config
import pika # needed to send messages out via RabbitMQ
import time # needed for sleep

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

        # load config settings
        with open("./configs/billing.yaml", "r") as ymlfile:
            config = yaml.safe_load(ymlfile)

        # load openAI keys into client
        self.client = OpenAI(api_key=config["openai"]["API_KEY"])

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

        # generate audio
        response = self.client.audio.speech.create(model="tts-1", voice="onyx", input=f"{str(text)}",)
        response.stream_to_file("response.mp3")
        #time.sleep(1)

        # plays the response
        channel = pygame.mixer.Sound('response.mp3').play()

        # wait for file to finish playing
        while channel.get_busy():
            pygame.time.wait(100) # wait 100 ms

if __name__ == '__main__':
    audioResp = AudioResponse()
    audioResp.startListening()