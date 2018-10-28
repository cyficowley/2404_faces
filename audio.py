import speech_recognition as sr

r = sr.Recognizer()
mic = sr.Microphone()

with mic as source:
  print("about to adjust")
  r.adjust_for_ambient_noise(source)
  print("adjusted to noise")
  audio = r.listen(source)
  
  print("sending to google")
  try:
    print("you said {}".format(r.recognize_google(audio)))
  except:
    print("it tried and fail to recognize")


