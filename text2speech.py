from os import system
# system('say hello world)
# system('say -v Alex hello world)

class Text2Speech:

    def say(self, msg):
        message = 'say ' + msg
        system(message)


boi = Text2Speech()
boi.say("paint me like one of your french girls")