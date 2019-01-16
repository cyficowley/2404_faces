from os import system

class Text2Speech:
    def __init__(self):
        self.bluetooth_device = 'FC:58:FA:2A:15:98'

    def say(self, msg):
        create_wave = 'flite -o neat.wav -voice slt -t "{}"'.format(msg)
        system(create_wave)
        say_wave = 'aplay -D bluealsa:HCI=hci0,DEV={},PROFILE=a2dp neat.wav'.format(self.bluetooth_device)
        system(say_wave)
        
