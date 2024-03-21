# Combee

Combee is a proof of concept framework for safely integrating Large Language Models (LLMs) into physical systems.  It's also a fun little robot you can talk to, and yes it is named after the pokemon.  

**Table of Contents**
- [Background](#background)
- [Framework Description](#framework-description)

## Background

Human controlled robotics, and indeed human controlled physical systems in general have always struggled when it comes to how are they actually controlled.  Your controller ends up being the language that the operator uses to communicate with your machine, with things like button presses and joystick movements acting like words and sentences.  There are two glaring issues with this: first this is a language the operator needs to learn since humans communicate with words and not joysticks, and second that the more complex the interactions you wish to allow between machine and operator, the more complex of a controller you must design.  

LLMs present an elegant solution to these two problems.  By using an LLM as an human-machine interface the human operator is able to interact and communicate to the machine in their natural language, no training or tutorials required.  At the same time, human languages are very good at conveying both complex and simple topics.  So if the operator wants the robot to do a funny dance, they can just say "Do a funny dance", if they want it to move forward X meters and turn Y degrees, they can again just tell it so, without requiring a new interface or special steps.  

This isn't to say that LLMs are perfect in this role.  Any generative AI system is going to be vulnerable to hallucinations, or generating unwanted or invalid data from user input.  This problem becomes worse when you look at multimodal systems, where the generative AI model is performing multiple tasks such as vision recognition and text analysis, because it quickly becomes impossible to both tell what part of the system created the hallucination, and what is a hallucination versus normal input.  To confront this problem, Combee is a multi-model framework, where you the engineer are able to separate and bind different generative AI models so that you can still use these systems as an interface, but are able to limit the ability of false or bad data from them to affect the rest of the system.  

## Framework Description

The combee framework is a multi-model framework that allows multiple AI models to interface and communicate with physical sensors in an abstracted manner without the need for retraining.  In english, this means we created a framework where you the user can plug in any LLM or other model of your choosing and have that model instantly begin interpreting and interfacing with other connected systems and sensors in a secure way via a user controlled API.  It sounds complicated, but it will make sense once we break it down.  

### Multimodal vs Multi-Model

The first unique part of this framework is that we support a multi-model environment instead of a multimodal one.  Multimodal models are AI models that are designed to process and interpret multiple types of the data at the same time, such as text and video.  They are very simple to implement, since you only need to call one model for everything, but can get very large in size, and difficult to analyze if something goes wrong, since its hard to tell what part of the model is causing the problem.  Multi-model systems are systems where multiple independent AI models are sharing data with each other.  These systems are more complicated to implement than a multimodal one, but allow for the isolation of individual models, so that an error in one can stop before affecting the other.  Additionally because each model is only doing a single task, smaller more light-weight models can be used, which makes for easier deployment on hardware like Raspberry Pis.  

### API Abstraction

The second big part of the framework is having each of the models interact with the other sensors and systems via API.  This does two main things: First it allows multiple models to communicate and listen to the same sensor or system, and two it allows hallucination problems to become bounded into more general invalid input problems.  This is because rather than checking if the open-ended question of did the model generate what the user wanted correctly, we instead just have to check and validate if the model generated the API call correctly.  In other words, we are turn what would normally be an open ended write your own answer question into a multiple choice one.  
