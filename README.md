# 2404_faces

This was a project I built to recognize the faces of all the people that live in and visit my apartment.  Basically someone walks in, it recognizes their face, and says hey good to see you Cyrus or whoever it was.

### HARDWARE

* Raspberry Pi
* IR camera (has night vision)
* Passive IR Sensor
* Bluetooth Speaker (not necessary, just the only speaker that I had)
* Playstation eye (again not necessary, just the only usb mic I had)
* Solid State Relay

![The hardware](https://i.imgur.com/efTLwTh.jpg)
 
(the IR lights aren't visible to the eye, it just shows up in the camera)  
(Also there is a speaker and a microphone off to the left)

### HOW IT WORKS

When the door opens or someone walks by the passive IR sensor detects a change in the IR levels and tells the Raspberry Pi.  
This turns on the solid state relay which the power for the IR leds is wired through.  
* This I had to do because by defualt the IR leds are always on and are connected straight to the rasperry pis power pins, so there is no way to turn them off without turning off the Raspberry Pi.  
* This would be fine but they get really hot if you leave them on for 10 or more minutes so I couldn't leave them on constantly for a long amount of time.   

With the IR lighting on the Raspberry Pi starts looking for faces.  If it sees one it:
* Compares it to all already registered faces using a face vector computer for each distinct face
* If the face is similar to an already known face vector past a certain threshold it says "Good to see you (name of person)"
  * It then adds a row to an online mysql database saying it saw this person at this time and the surity (good for debugging look alike faces and might be able to do cool data analysis)
* If it is not similar, it waits for there to be 3 frames of new person (so it doesn't start yelling at the wall sometimes) and then asks them what theyre name is.
  * They answer and their face is saved so that it will always be able to recognize them in the future. 
  
  
### Problems and possible upgrades

It mixes up people a fair amount.  I'd say around 20% of the time it says the wrong person, usually of the same race.  I could possibly solve this by using a different library for the face recognition or being more picky about what picture to save for their face vector.  It also every once in a while misses a face of someone coming in, i could possibly look into using a better hog detector or actually using this intel neural processing chip I have and using a cnn.

I definitly will have to continue doing something like a face vector for face comparisons though becuase I want to be able to recognize a face after only a single image of it, so theres non way to train a net on each face.  

### What was hard

Bluetooth sucks, I should have just bought a real speaker

### What was easy

I just took this neural networks course and was already to make this awesome cnn to recognize everyone then I realized that there wasn't enough power on a rasperry pi and I would only have one image and I could just import face_recognition instead.  So I did that.
