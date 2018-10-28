import face_recognition
import cv2
import os
import operator
from text2speech import Text2Speech
import audio
# Get a reference to webcam #0 (the default one)

wait_loops = 60


class faces:

  def __init__(self):
    self.people = {}
    self.speech = Text2Speech()

    self.seen_people = {}

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


    self.known_encodings = []
    self.names = []

    for name, encodings_list in self.people.items():
      self.names += [name] * len(encodings_list)
      self.known_encodings += encodings_list


  def main_loop(self):
    video_capture = cv2.VideoCapture(0)

    frames_new_face = 0

    while True:

      for name in self.seen_people.keys():
        self.seen_people[name] -= 1
    
      ret, frame = video_capture.read()

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
            frames_new_face = 0
            if(len(face_encodings) == 1):
              self._add_new_face("surya", frame)
          
      
      if(face_locations is not None):
        for each in all_matches:
          if(each not in self.seen_people):
            self.speech.say("Good to see you {}".format(each))
          self.seen_people[each] = wait_loops


    # Release handle to the webcam
    video_capture.release()
    cv2.destroyAllWindows()



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