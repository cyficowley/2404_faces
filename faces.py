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
import socket
import numpy as np
from gpio import needs_to_be_class 
from sql import database
# Get a reference to webcam #0 (the default one)

wait_loops = 20



class faces:

  def __init__(self):
    self.dictionary = enchant.Dict("en_US")
    self.people = {}
    self.speech = Text2Speech()
    
    self.camera_on = False #tells the camera to actually process frames or not
                           #its actually always on, not sure how bad that is

    self.seen_people = {}
    print("loading all faces")
    for root, dirs, files in os.walk("faces"):
      for person in dirs:
        for root, dirs, files in os.walk(os.path.join("faces", person)):
          for image in files:
            if image.endswith(".jpg"):
              path = os.path.join("faces", person, image)
              print(path)
              encoding = face_recognition.face_encodings(face_recognition.load_image_file(path))[0]
              if(person in self.people):
                self.people[person].append(encoding)
              else:
                self.people[person] = [encoding]
    print("finished loading all faces")

    #associating gpio functions with this classes fucntions
    needs_to_be_class(self._turn_on_camera, self._turn_off_camera)


    self.known_encodings = []
    self.names = []

    for name, encodings_list in self.people.items():
      self.names += [name] * len(encodings_list)
      self.known_encodings += encodings_list


  def main_loop(self):
    print("initializing camera")
    frames_new_face = 0
    camera = PiCamera()
    camera.resolution = (320,192)
    camera.framerate = 30 
    rawCapture = PiRGBArray(camera, size=(320,192))
    
    time.sleep(.1)

    for image in camera.capture_continuous(rawCapture, format='bgr', use_video_port=True):


      frame = image.array
      rawCapture.truncate(0)

      names_to_remove = []
      for name in self.seen_people.keys():
        self.seen_people[name] -= 1
        if(self.seen_people[name] < 0):
          names_to_remove.append(name)

      for each in names_to_remove:
        del self.seen_people[each] 
      
      
      if(not self.camera_on): #no motion detected so camera not needed
        time.sleep(.1)
        continue

      # Resize frame of video to 1/4 size for faster face recognition processing
      small_frame = frame

      # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
      rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

      face_locations = face_recognition.face_locations(rgb_small_frame)
      face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

      face_names = []

      all_matches = []
      if(len(face_encodings) > 0):
        print(len(face_encodings))
      for face_encoding in face_encodings:
        # See if the face is a match for the known face(s)
        matches = face_recognition.compare_faces(self.known_encodings, face_encoding)
        
        
        encodings_to_check = []
        names_to_check = []
        for i in range(len(matches)):
          if(matches[i]):
            encodings_to_check.append(self.known_encodings[i])
            names_to_check.append(self.names[i])
        
        closest_person = None
        min_distance = None
        difference = -1
        if(len(encodings_to_check) != 0):
          distances = face_recognition.face_distance(encodings_to_check,face_encoding)
          min_distance = min(distances)
          closest_person = names_to_check[np.argmin(distances)]
          if(len(distances) > 1):
            difference = min([each - min_distance for each in distances if each - min_distance != 0])
        
        if(closest_person is not None):
          frames_new_face = 0
          all_matches.append((closest_person, min_distance, difference))
        else:
          frames_new_face += 1
          # Has to see 3 frames of new person in a row to try to add them
          if(frames_new_face == 2):
            if(len(face_encodings) == 1):
              frames_new_face = 0
              self.speech.say("Please say your first name after the reeee")
              self.audio_input = InterpretAudio()
              self.speech.say("rrrrrrreeeeeeee")
              response = self.audio_input.listen_for_response()
              name = self._return_name(response)
              if(name is not None and len(name) != 0):
                self._add_new_face(name, frame)
                self.speech.say("nice to meet you {}".format(name))
          
      
      if(face_locations is not None):
        db = database()
        for each in all_matches:
          person, surity, difference = each
          if(person not in self.seen_people):
            self.speech.say("hey good to see you {}".format(person))
            db.add_row(person, surity, difference)
          self.seen_people[person] = wait_loops
        db.shutdown()


  def _return_name(self, text):
    if(text is None):
        return None
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
    
  def _get_ip_address(self):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    addr = s.getsockname()[0]
    s.close()
    
    #making the ip address easier to hear
    sub_addr = addr.split(".")
    vocal_addr = ""
    for bit in sub_addr:
        vocal_addr += bit + " point "
    vocal_addr = vocal_addr[:-7]
    self.speech.say("I P address is {}, again that is {}".format(vocal_addr, vocal_addr))


  def _turn_on_camera(self):
    self.camera_on = True

  def _turn_off_camera(self):
    self.camera_on = False

if(__name__=="__main__"):
  face = faces()
  face._get_ip_address()
  face.main_loop()
