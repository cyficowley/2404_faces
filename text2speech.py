from os import system

class Text2Speech:

    def say(self, msg):
        message = 'say ' + msg
        system(message)


boi = Text2Speech()
boi.say("paint me like one of your french girls")