from openai import OpenAI # needed for calling OpenAI Audio API
import yaml # needed for config
import pika # needed to send messages out via RabbitMQ


class LLMProcessor:
    """
    Class that handles sending messages to and from the LLM
    """

    def __init__(self):
        """
        Initialization method
        """

        # load config settings
        CFG = None  # global CFG settings
        with open("./configs/billing.yaml", "r") as ymlfile:
            CFG = yaml.safe_load(ymlfile)

        # load openAI keys into client
        self.client = OpenAI(api_key=CFG["openai"]["API_KEY"])

        # set up RabbitMQ
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel()

        # Declare all the queues we will listen to 
        self.channel.queue_declare(queue='userInput') 
        self.channel.queue_declare(queue='cvInput')
        self.channel.queue_declare(queue='imuInput')
        self.channel.queue_declare(queue='audioOut')

        self.channel.basic_consume(queue='userInput', on_message_callback=self.userCallback, auto_ack=True)


    def userCallback(self, ch, method, properties, body):
        """
        Callback method for user input queue, passes question to LLM

        Args:
            ch (_type_): _description_
            method (_type_): _description_
            properties (_type_): _description_
            body (str): message from the user
        """
        question = body.decode()
        self.callLLM(question=question)

    def startListening(self):
        """
        Starts listening to the message queues
        """

        print("Beginning RabbitMQ listener")
        self.channel.start_consuming()

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
            #{"role": "system", "content": f"You are connected to a Web Cam capable of object detection that sees the current objects: {str(self.detectedObjects)}"},
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

                print(transcript)

                # generate audio
                #response = self.client.audio.speech.create(model="tts-1", voice="onyx", input=f"{str(transcript)}",)
                #response.stream_to_file("response.mp3")
                #time.sleep(1)

                # plays the response
                #pygame.mixer.Sound('response.mp3').play()
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

if __name__ == '__main__':
    llmP = LLMProcessor()

    llmP.startListening()