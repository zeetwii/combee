# Combee

![combee](./pictures/combee.png)

Combee is a proof of concept framework for safely integrating Large Language Models (LLMs) into physical systems.  It's also a fun little robot you can talk to, and yes it is named after the pokemon.  

It's designed to show how you can securely use multiple AI models together to add multimodal capabilities to otherwise dumb systems.  If you want to build your own, check out [the build guide here](./buildGuide.md).  

## Background and Terms

In AI terms, a modal model is a model that is able to process a single type of data.  The classic example of this is a computer vision model, like YOLO.  These models can process images and videos, and do things like object recognition, but they can only process visual data, nothing else.  Thus, a multimodal model is a model that can process and respond to multiple types of data.  One of the most well known multimodal is OpenAIs ChatGPT 4.o models, which are combined text and vision models.  

Hallucinations are a thing that all generative AI models do, it's the short hand name for any and all unwanted creativity from the system.  Because LLMs and other generative AI systems can be simplified down as probability engines, they don't have any concept of truth or correctness.  This can be seen in examples like you ask an LLM to write a poem about birds, but the one it generates is for bees.  

You would be forgiven for thinking that if you have a model that can process all the data sets you want to use at once, that it must be the best model to use.  And it is by far the simplest and most optimized from a design perspective, just make the multimodal model the core of your program, pass everything to it, and let it figure things out on its own.  However this simple design has a major problem: If any part of the model hallucinates or messes up for any reason, you have no easy way to detect, contain, or fix this since the problem is literally at the core of your program.  

An alterative design is to do a multi-model design, where you have multiple individual AI models that each do their own thing independently of each other, but are able to pass data back and forth.  These multi-model systems are much more complicated to design, but since each model is stand  alone, you can check the input and data going in and out of each one, allowing you to detect and react to hallucinations and other unwanted creativity.  

This is all a lot of text, so lets use a flow diagram to visualize what we are talking about.  Lets assume you have a physical system, maybe a robot of some kind.  This system has two sensors on it, one of which changes values based on the status of the control surfaces of the system, while the other is completely independent.  We're going to make two versions of adding an AI to this system.  One with a multimodal model, and one with a multi-model implementation.  Lets look at what these look like:

| Multimodal vs Multi-Model |
| --- |
| ![True multimodal solution](./pictures/multimodal.png) |
| This is what the solution looks like when tying everything directly to a multimodal AI.  You can see it's very simple and optimized from a design perspective.  However if and when the AI does something you don't want, your very limited in both becoming aware of the problem or reacting to it, since if the multimodal AI goes bad, there's no real way for the system to become aware of this.  |
| ![Mult-Model solution](./pictures/multi-model.png) |
| This is the same system, but using several standalone AI models to mimic a single multimodal one.  Notice how none of the AIs connect to any of the systems directly, they're all going through an interface of some kind for each sensor and system, including each other.  These interfaces are acting as API calls for the underlying sensor or system.  This has the advantage of black boxing each of the AIs, allowing you to change them out without having to retrain the system.  Additionally it means that you can detect things like hallucinations by using the same methods you would use for any normal input validation from a user.  This method has a lot of long term advantages for the system, but as the image shows is far more complicated to initially code.  |