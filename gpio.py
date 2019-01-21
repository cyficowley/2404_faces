import RPi.GPIO as GPIO
import time
from threading import Timer

GPIO.setmode(GPIO.BCM)
GPIO.setup(4, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.setup(24, GPIO.OUT)

#Turns off the light initially
GPIO.output(24, 1)



class needs_to_be_class():
    def __init__(self, turn_camera_on, turn_camera_off):
        self.turn_camera_on = turn_camera_on
        self.turn_camera_off = turn_camera_off
        GPIO.add_event_detect(4, GPIO.BOTH, callback=self.switch_changed)
        self.activated = False
        self.waiting_thread = None
        #bouncetime is so that when it turns off the light it doesn't just reactivate
    
    def turn_on_light(self):
        self.turn_camera_on()
        GPIO.output(24,0)
        self.activated = True

    def turn_off_light(self):
        self.turn_camera_off()
        GPIO.output(24,1)
        self.activated = False

    def detected_motion(self):
        if(not self.activated):
            self.turn_on_light()
        if(self.waiting_thread is not None):
            self.waiting_thread.cancel()

    #makes it only turn off after 10 seconds of no motion, and can never get stuck in a state like before
    def no_motion(self):
        self.waiting_thread = Timer(10, self.delayed_turn_off)
        self.waiting_thread.start()

    def delayed_turn_off(self):
        self.turn_off_light() 
        self.waiting_thread = None

    def switch_changed(self, input_pin):
        if(GPIO.input(4)):
            self.detected_motion()
        else:
            self.no_motion()
