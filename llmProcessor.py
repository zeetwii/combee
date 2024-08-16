from openai import OpenAI # needed for calling OpenAI Audio API
import yaml # needed for config
import pika # needed to send messages out via RabbitMQ
import time # needed for sleep


class LLMProcessor:
    """
    Class that handles sending messages to and from the LLM
    """

    def __init__(self):
        """
        Initialization method
        """

        # String that will contain all the detected objects and their positions relative to us
        self.detectedObjects = ""

        # load config settings
        with open("./configs/billing.yaml", "r") as ymlfile:
            config = yaml.safe_load(ymlfile)

        # load openAI keys into client
        self.client = OpenAI(api_key=config["openai"]["API_KEY"])

        # load context settings
        with open("./configs/context.yaml", "r") as ctxfile:
            context = yaml.safe_load(ctxfile)

        self.personality = context["llm"]["PERSONALITY"]
        self.moveDes = context["llm"]["MOVE_DESCRIPTION"]
        self.lookDes = context["llm"]["CAMERA_DESCRIPTION"]
        self.waitDes = context["llm"]["WAIT_DESCRIPTION"]
        self.textDes = context["llm"]["TEXT_DESCRIPTION"]
        self.llmDes = context["llm"]["LLM_DESCRIPTION"]


        # set up RabbitMQ
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel()

        # Declare all the queues we will listen to or use
        self.channel.queue_declare(queue='userOutput') 
        self.channel.queue_declare(queue='cameraOutput')
        self.channel.queue_declare(queue='cameraInput')
        self.channel.queue_declare(queue='audioInput')
        self.channel.queue_declare(queue='moveInput')

        self.channel.basic_consume(queue='userOutput', on_message_callback=self.userCallback, auto_ack=True)
        self.channel.basic_consume(queue='cameraOutput', on_message_callback=self.cameraCallback, auto_ack=True)

    def cameraCallback(self, ch, method, properties, body):
        """
        Callback method for object detection

        Args:
            ch (_type_): _description_
            method (_type_): _description_
            properties (_type_): _description_
            body (_type_): _description_
        """
        
        self.detectedObjects = body.decode()
        #print(self.detectedObjects)

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
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": f"{str(self.personality)}"},
            {"role": "system", "content": f"{str(self.moveDes)}"},
            {"role": "system", "content": f"{str(self.lookDes)}"},
            {"role": "system", "content": f"The webcam currently sees the following objects: {str(self.detectedObjects)}"},
            {"role": "system", "content": f"{str(self.waitDes)}"},
            {"role": "system", "content": f"{str(self.textDes)}"},
            #{"role": "system", "content": f"{str(self.llmDes)}"},
            {"role": "system", "content": "You may combine and chain commands together however each command must be on a new line, and only one command is allowed per line.  The command should be the only thing on the line, nothing else.  Do not respond with anything other than commands, and do not abbreviate or title the commands anything other than what has been provided to you.  "},
            {"role": "system", "content": "Using this sensor data and formatting instructions, try to answer the following question from the user."},
            {"role": "user", "content": f"{str(question)}"}
        ]
        )

        output = str(completion.choices[0].message.content)
        print("")
        print(output)
        
        lines = [line.strip() for line in output.split("\n")]

        for i in range(len(lines)):

            message = lines[i].replace("[","").replace("]","")
            #print(message)
            if len(message) > 0: # make sure line isn't empty
                if message.startswith("TEXT"):
                    #print("text")
                    message = message.split(',', 1)[1]
                    self.channel.basic_publish(exchange='', routing_key='audioInput', body=message)
                elif message.startswith("WAIT"):
                    #print("wait")
                    message = message.split(", ", 1)[1]
                    
                    try:
                        time.sleep(float(message))
                    except ValueError:
                        print("Sleep time unable to be turned into float")
                elif message.startswith("LLM"):
                    #print("llm")
                    message = message.split(", ", 1)[1]
                    print(message)
                    self.callLLM(message)
                elif message.startswith("PANTILT"):
                    #print("pan/tilt")
                    self.channel.basic_publish(exchange='', routing_key='cameraInput', body=message)
                elif message.startswith(('MOVET', 'MOVED', 'TURN')):
                    #print("move")
                    self.channel.basic_publish(exchange='', routing_key='moveInput', body=message)
                else:
                    print("Error, unknown message generated, possible hallucination.  ")
                    print(f"Message: {str(message)}")
                    self.channel.basic_publish(exchange='', routing_key='audioInput', body="Error, I think you made me generate an incorrect message type.  ")


if __name__ == '__main__':
    llmP = LLMProcessor()

    llmP.startListening()
