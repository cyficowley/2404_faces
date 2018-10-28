import speech_recognition as sr

class InterpretAudio:
  def __init__(self):
    self.r = sr.Recognizer()
    self.mic = sr.Microphone()
    self.r.adjust_for_ambient_noise(source)

  def listen_for_response(self):
    with self.mic as source:
      audio = self.r.listen(source)
      try:
        return self.r.recognize_google(audio))
      except:
        print("failed to recognize speech")
        return None

