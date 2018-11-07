import face_recognition
import cv2
import os
import operator
import time
import enchant
from text2speech import Text2Speech
from picamera.array import PiRGBArray
from picamera import PiCamera, PiCameraValueError
from audio import InterpretAudio
# Get a reference to webcam #0 (the default one)

wait_loops = 60



class faces:

  def __init__(self):
    self.dictionary = enchant.Dict("en_US")
    self.people = {}
    self.speech = Text2Speech()

    self.seen_people = {}
    print("loading all faces")
    for root, dirs, files in os.walk("faces"):
      for person in dirs:
        for root, dirs, files in os.walk(os.path.join("faces", person)):
          for image in files:
            if image.endswith(".jpg"):
              path = os.path.join("faces", person, image)
              encoding = face_recognition.face_encodings(face_recognition.load_image_file(path))[0]
              if(person in self.people):
                self.people[person].append(encoding)
              else:
                self.people[person] = [encoding]
    print("finished loading all faces")


    self.known_encodings = []
    self.names = []

    for name, encodings_list in self.people.items():
      self.names += [name] * len(encodings_list)
      self.known_encodings += encodings_list


  def main_loop(self):
    print("initializing camera")
    frames_new_face = 2
    camera = PiCamera()
    camera.resolution = (1280,720)
    camera.framerate = 6 
    rawCapture = PiRGBArray(camera, size=(1280,720))
    
    time.sleep(.1)

    for image in camera.capture_continuous(rawCapture, format='bgr', use_video_port=True):
      frame = image.array
      rawCapture.truncate(0)
      print("new frame")
      names_to_remove = []
      for name in self.seen_people.keys():
        self.seen_people[name] -= 1
        if(self.seen_people[name] < 0):
          names_to_remove.append(name)

      for each in names_to_remove:
          del self.seen_people[name]      
    
      # Resize frame of video to 1/4 size for faster face recognition processing

      small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

      # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
      rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

      face_locations = face_recognition.face_locations(rgb_small_frame)
      face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

      face_names = []

      all_matches = []
      for face_encoding in face_encodings:
        # See if the face is a match for the known face(s)
        matches = face_recognition.compare_faces(self.known_encodings, face_encoding)
        
        totals = {name:0 for name in self.people.keys()}

        for i in range(len(matches)):
          if(matches[i]):
            totals[self.names[i]] += 1

        max_person = max(totals.items(), key=operator.itemgetter(1))
        if(max_person[1] != 0):
          frames_new_face = 0
          all_matches.append(max_person[0])
        else:
          frames_new_face += 1
          # Has to see 3 frames of new person in a row to try to add them
          if(frames_new_face == 3):
            if(len(face_encodings) == 1):
              frames_new_face = 0
              self.speech.say("Please say your first name after the reeee")
              self.audio_input = InterpretAudio()
              self.speech.say("reeee")
              response = self.audio_input.listen_for_response()
              name = self._return_name(response)
              if(len(name) != 0):
                self._add_new_face(name, frame)
          
      
      if(face_locations is not None):
        for each in all_matches:
          if(each not in self.seen_people):
            self.speech.say("Good to see you {}".format(each))
          self.seen_people[each] = wait_loops


    # Release handle to the webcam
    video_capture.release()
    cv2.destroyAllWindows()


  def _return_name(self, text):
    words = text.split(" ")
    if(len(words) == 1):
      return words[0]
    non_words = []
    for each in words:
      if(not self.dictionary.check(each)):
        non_words.append(each)
    if(len(non_words) == 1):
      return non_words[0]
    
    words.reverse()

    for each in words:
      if(each.lower() != each):
        return each
    return words[0]


  def _add_new_face(self, name, face_image):
    print("ADDING NAME {}".format(name))
    if(not os.path.isdir(os.path.join("faces", name))):
      os.mkdir(os.path.join("faces", name))
    
    total_files = 0
    for each in os.listdir(os.path.join("faces", name)):
      total_files += 1
    cv2.imwrite(os.path.join("faces", name,"img_{}.jpg".format(total_files)), face_image)
    
    encoding = face_recognition.face_encodings(face_image)[0]
    
    self.known_encodings.append(encoding)
    self.names.append(name)
    if(name in self.people):
      self.people[name].append(encoding)
    else:
      self.people[name] = [encoding]



if(__name__=="__main__"):
  face = faces()
  face.main_loop()
