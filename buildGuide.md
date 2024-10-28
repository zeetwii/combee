# Combee Build Guide

This is a quick guide for building Combee as is.  I've broken the guide up into the different subsystems to keep things easy to follow.  Everything I used to make Combee is from Amazon and similar websites, and I included links to everything.

## Parts List

Here is the breakout of all the parts and their costs when it comes to building Combee.  The total cost for everything as I built it is roughly $746 if buying off Amazon and aliexpress.  

### Computer

- [Raspberry Pi 5 - 8GB version](https://www.adafruit.com/product/5813)
  - $80 at most official resellers
- [Raspberry Pi 5 Active cooler](https://www.adafruit.com/product/5815)
  - $5 at most official resellers
  - Running any AI models on the Pi will get it very hot, so I strongly recommend some form of active cooling, and the official cooler works really well for this.  
- [5V5A PD power module](https://www.aliexpress.us/item/3256806175607588.html)
  - $14 after shipping
  - The Pi 5 will throttle itself unless it gets 5V5A directly from a power source.  This is a really weird combo from a power delivery stand point, combining the lowest voltage with the highest current supported by the spec.  As such, most battery packs do not natively support this power combination.  By using this power converter, we ensure that regardless of the battery pack being used, we're giving the pi a voltage and current level that will let it run at max speed.  
- [3d printed protective case](https://www.printables.com/model/187691-raspberry-pi-mount-for-ikea-skadis)
  - Because the chassis of Combee is metal, if you don't have some case on the bottom of the pi, you risk the system shorting out during operation.  

Total: ~$100, possibly more if you buy a case instead of printing one.  

### Frame

- [Yahboom Large Mechanum Wheel Chassis](https://www.amazon.com/gp/product/B0BR9Q58GL/)
  - $150
- [Yahboom Pan and Tilt servo kit](https://www.amazon.com/gp/product/B0BRXVFCKX/)
  - $50
- [PCA9685 servo driver](https://www.adafruit.com/product/815)
  - $15
  - There is a pre soldered version from HiLetgo on amazon if you are nervous about your solder skills.  It's [here](https://www.amazon.com/dp/B07BRS249H)
- [L298N motor drivers](https://www.amazon.com/gp/product/B07BK1QL5T/)
  - $12
  - These come in a four pack, but we only need two

Total: $227

### Power

- 2x [Anker 737 Power Bank](https://www.amazon.com/gp/product/B09VPHVT2Z/)
  - $109 each, so $218 for both
  - These give Combee around seven hours of battery life
  - Combee needs four USB C  ports for power, which is why you need two of the power banks:
    - 1x for the Pi 5 itself
    - 1x for the servo controller
    - 2x for the motor drivers
- [Short USB C cables 5 pack](https://www.amazon.com/gp/product/B0BXX2KCT2/)
  - $30
  - You need five USB C cables for Combee, so its easier just to get them as one big pack
- [USB C Power Delivery breakout boards](https://www.amazon.com/dp/B0C6KCP592)
  - $14 for a four pack
  - These are used to power the motor drivers and servo controller over USB C.  Only three are needed, but it doesn't hurt to have a spare.  
- [Terminal Block connectors](https://www.amazon.com/dp/B07CZYGQQ3)
  - $9 for a 50 pack
  - The PD breakout boards don't ship with terminal connectors, so you have to manually solder these on.  

Total: $271

### Audio and Video

  - Generic Webcam
    - ~$30
    - Any webcam with a 1/4" mounting hole will work, but I've tested two:
      - [ROCWARE camera, mic, speaker combo](https://www.amazon.com/gp/product/B09TKCNP96/)
        - This one worked well if you are wanting to cut costs, since you can use it as a speaker and microphone as well.  However everyone that I bought would eventually die after a few months, with either the mic or speaker just deciding to die.  
      - [Tewiky Webcam](https://www.amazon.com/gp/product/B08VJ25PL1/)
        - This is the one I currently used, and it has held up well.  It does also have a mic, but I find that one too weak to use in most situations.  
  - [1/4" Threaded tripod screw adapter](https://www.amazon.com/gp/product/B079BNWB6K/)
    - $7
    - These just make it easier to connect the webcam to the pan and tilt system.  You could also just use tape or something.  
  - [TONOR Conference Microphone](https://www.amazon.com/gp/product/B07GVGMW59/)
    - $24
    - Any conference microphone will work, this is just the one that I used.  
  - [USB Speaker](https://www.amazon.com/gp/product/B086JXJ1LF/)
    - $16
    - Having a dedicated speaker is needed if your in loud spaces, and this model is easy to tape to the slot in the front of the chassis to stay in place.  
  - [Momentary switch pushbutton](https://www.adafruit.com/product/560)
    - $5
    - This is just the push to talk switch.  Could technically be any momentary switch, but I think the led ring is cool.  
  - [3/4in PVC pipe](https://www.amazon.com/gp/product/B085B4Y5V6/)
    - $25 from amazon
    - $5 from a hardware store
    - This is just to give hight to the microphone and push to talk button.  You only need about two feet worth of pipe to make something thats tall enough to be easily interacted with.  

Total: $107

### Optionals

None of these are needed, but I used them in my build to make things easier to take apart and disassemble / repair.  

  - [Gorilla Tape](https://www.amazon.com/gp/product/B082TQ3KB5/)
    - $12
    - This is great for attaching stuff quickly
  - [Dupont cables](https://www.amazon.com/gp/product/B01EV70C78/)
    - $7
    - These are technically essential, since this is the connector style the pi pins use, but you can always just crimp your own wires.  
  - [Multi to one splicing connectors](https://www.amazon.com/gp/product/B09VSF5TV2/)
    - $15
    - The two to one connectors in this kit are great for the motor drivers.  To make those work, you need to combine the ground line from the USB C breakout boards with the ground on the pi in order for the signals to be read correctly.  These are a super easy way to do that.  
  - [Inline splicing connector](https://www.amazon.com/gp/product/B0BM4B3D6T/)
    - $7
    - These are great for the push to talk button, since they can create an easy disconnect point between the pi and the cable harness for the button.  

Total: $41