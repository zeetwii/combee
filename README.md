# Combee

Combee is a proof of concept framework for safely integrating Large Language Models (LLMs) into physical systems.  It's also a fun little robot you can talk to, and yes it is named after the pokemon.  

**Table of Contents**
- [Background](#background)

## Background

Human controlled robotics, and indeed human controlled physical systems in general have always struggled when it comes to how are they actually controlled.  Your controller ends up being the language that the operator uses to communicate with your machine, with things like button presses and joystick movements acting like words and sentences.  There are two glaring issues with this: first this is a language the operator needs to learn since humans communicate with words and not joysticks, and second that the more complex the interactions you wish to allow between machine and operator, the more complex of a controller you must design.  

LLMs present an elegant solution to these two problems.  By using an LLM as an human-machine interface the human operator is able to interact and communicate to the machine in their natural language, no training or tutorials required.  At the same time, human languages are very good at conveying both complex and simple topics.  So if the operator wants the robot to do a funny dance, they can just say "Do a funny dance", if they want it to move forward X meters and turn Y degrees, they can again just tell it so, without requiring a new interface or special steps.  

This isn't to say that LLMs are perfect in this role.  Any generative AI system is going to be vulnerable to hallucinations, or generating unwanted or invalid data from user input.  This problem becomes worse when you look at multimodal systems, where the generative AI model is performing multiple tasks such as vision recognition and text analysis, because it quickly becomes impossible to both tell what part of the system created the hallucination, and what is a hallucination versus normal input.  To confront this problem, Combee is a multi-model framework, where you the engineer are able to separate and bind different generative AI models so that you can still use these systems as an interface, but are able to limit the ability of false or bad data from them to affect the rest of the system.  