from os import system

class Text2Speech:

    def say(self, msg):
        message = 'flite -voice slt -t "{}"'.format(msg)
        system(message)
