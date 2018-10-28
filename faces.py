import face_recognition
import cv2
import os
import operator

# Get a reference to webcam #0 (the default one)
video_capture = cv2.VideoCapture(0)

people = {
  "cyrus":[],
  "nick":[],
  "surya":[]
}


for root, dirs, files in os.walk("faces"):
  for person in dirs:
    for root, dirs, files in os.walk(os.path.join("faces", person)):
      for image in files:
        if image.endswith(".jpg"):
          path = os.path.join("faces", person, image)
          encoding = face_recognition.face_encodings(face_recognition.load_image_file(path))[0]
          if(person in people):
            people[person].append(encoding)
          else:
            people[person] = [encoding]


known_encodings = []
names = []

for name, encodings_list in people.items():
  names += [name] * len(encodings_list)
  print(encodings_list)
  known_encodings += encodings_list



while True:
  ret, frame = video_capture.read()

  # Resize frame of video to 1/4 size for faster face recognition processing
  small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

  # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
  rgb_small_frame = small_frame[:, :, ::-1]

  face_locations = face_recognition.face_locations(rgb_small_frame)
  face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

  face_names = []

  all_matches = []
  for face_encoding in face_encodings:
    # See if the face is a match for the known face(s)
    matches = face_recognition.compare_faces(known_encodings, face_encoding)
    
    totals = {name:0 for name in people.keys()}

    # print(matches)

    for i in range(len(matches)):
      if(matches[i]):
        totals[names[i]] += 1

    max_person = max(totals.items(), key=operator.itemgetter(1))
    if(max_person[1] != 0):
      all_matches.append(max_person[0])
    else:
      print("unknown face")
      
  
  if(face_locations):
    print(all_matches)

# Release handle to the webcam
video_capture.release()
cv2.destroyAllWindows()
