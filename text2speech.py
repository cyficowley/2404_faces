from os import system

class Text2Speech:

    def say(self, msg):
        message = 'say ' + msg
        system(message)