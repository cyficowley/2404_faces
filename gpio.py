import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(4, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.setup(24, GPIO.OUT)

#Turns off the light initially
GPIO.output(24, 1)

def turn_on_light():
    GPIO.output(24,0)

def turn_off_light():
    GPIO.output(24,1)

def deal_with_change(input_pin):
    if(GPIO.input(4)):
        turn_on_light()
    else:
        turn_off_light()

#bouncetime is so that when it turns off the light it doesn't just reactivate
GPIO.add_event_detect(4, GPIO.BOTH, callback=deal_with_change, bouncetime=2000)
