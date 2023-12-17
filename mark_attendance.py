import face_recognition.api as face_recognition
import cv2, pickle, os, csv
import numpy as np
from datetime import datetime
import matplotlib as mpl
import sys
import dlib
cascPath = sys.argv[0]
from gtts import gTTS
import pygame
import os
from cvzone.HandTrackingModule import HandDetector



def text_to_speech(text, language='en', filename='output.mp3'):
    tts = gTTS(text=text, lang=language, slow=False)
    tts.save(filename)
    pygame.mixer.init()
    pygame.mixer.music.load(filename,"mp3")
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    
    pygame.quit()
    
    os.remove('output.mp3')

p = r"shape_predictor_68_face_landmarks.dat"
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(p)

def trackFace( info, w, pid, pError, fbRange):

    area = info[1]

    x, y = info[0]

    fb = 0

    error = x - w // 2

    speed = pid[0] * error + pid[1] * (error - pError)

    speed = int(np.clip(speed, -100, 100))
    #print('speed is',speed)

    if area > fbRange[0] and area < fbRange[1]:

        fb = 0

    elif area > fbRange[1]:

        fb = -20

    elif area < fbRange[0] and area != 0:

        fb = 20

    if x == 0:

        speed = 0

        error = 0

    print(speed, fb)

    # me.send_rc_control(0, fb, 0, speed)

    return error

def mark_your_attendance():
    Hdetector = HandDetector(detectionCon=0.8, maxHands=2)
    mpl.rcParams['toolbar'] = 'None'
    STORAGE_PATH = "storage"

    try:
        with open( os.path.join(STORAGE_PATH, "known_face_ids.pickle"),"rb") as fp:
            known_face_ids = pickle.load(fp)
        with open( os.path.join(STORAGE_PATH, "known_face_encodings.pickle"),"rb") as fp:
            known_face_encodings = pickle.load(fp)
    except:
        known_face_encodings = []
        known_face_ids = []

    CSV_PATH = "facedata/attendance.csv"

    if(os.path.exists(CSV_PATH)):
        csv_file = open(CSV_PATH, "a+")
        writer = csv.writer(csv_file)

    else:
        # os.mknod(CSV_PATH)
        csv_file = open(CSV_PATH, "w+")
        writer = csv.writer(csv_file)
        writer.writerow(["Student ID", "Date", "Time of Entry"])

    name = "Unknown"
    face_locations = []
    face_encodings = []
    face_names = []
    process_this_frame = True
    sanity_count = 0
    unknown_count = 0
    marked = True

    video_capture = cv2.VideoCapture(0)
    ret, frame = video_capture.read()

    studentname=''
    while True:
        # Grab a single frame of video
        ret, frame = video_capture.read()
        hands, img = Hdetector.findHands(frame)
        if hands:
            hand1 = hands[0]
            lmList1 = hand1["lmList"]  # List of 21 Landmarks points
            bbox1 = hand1["bbox"]  # Bounding Box info x,y,w,h
            centerPoint1 = hand1["center"]  # center of the hand cx,cy
            handType1 = hand1["type"]  # hand type Left or Right


            fingers1 = Hdetector.fingersUp(hand1)
            cnt = fingers1[0]+fingers1[1]+fingers1[2]+fingers1[3]+fingers1[4]

            if cnt==0 or cnt==5:
                break
        else:
            # Only process every other frame of video to save time
            if process_this_frame:
                # Find all the faces and face encodings in the current frame of video
                
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  

                face_locations = face_recognition.face_locations(frame)
                face_encodings = face_recognition.face_encodings(frame, face_locations)

                face_names = []
                for face_encoding in face_encodings:
                    # See if the face is a match for the known face(s)
                    matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance = 0.35)
                    name = "Unknown"

                    face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                    # print(face_distances)
                    try:
                        best_match_index = np.argmin(face_distances)
                    except:
                        # print("No students have been marked")
                        video_capture.release()
                        cv2.destroyAllWindows()
                        marked = False
                        return marked
                    if matches[best_match_index]:
                        name = known_face_ids[best_match_index]

                    face_names.append(name)
            if(name == "Unknown"):
                unknown_count += 1
            else:
                unknown_count = 0

            if(unknown_count == 600):
                marked = False
                unknown_count = 0
                break

            process_this_frame = not process_this_frame


            for (top, right, bottom, left), name in zip(face_locations, face_names):
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4

                cv2.rectangle(frame, (left, bottom), (right, bottom), (0,0,255), 1)
                font=cv2.FONT_HERSHEY_SIMPLEX
                fontScale=2
                fontColor=(0,0,255)
                org=(50, 100)
                # print(name)
                cv2.putText(frame, str(name),org,font,fontScale,fontColor)


            cv2.imshow('Video', frame)
            if cv2.waitKey(20) == 27:
                break

            
            if(sanity_count == 0):
                prev_name = name
                sanity_count += 1
                print("prev_name: ",prev_name+" "+str(unknown_count))
                if unknown_count % 15 == 0 and prev_name == "Unknown": 
                    text = "You are not registered yet"
                    text_to_speech(text, language='en')
                    unknown_count = 0

            elif(sanity_count < 200):
                if(prev_name == name and name != "Unknown"):
                    sanity_count += 1
                    prev_name = name
                    if sanity_count % 8 == 0 and name != "Unknown": 
                        text = "Hello "+name
                        text_to_speech(text, language='en')
                else:
                    sanity_count = 0

            elif(sanity_count == 200):
                sanity_count = 0
                now = datetime.now()
                dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
                date = dt_string.split(" ")[0]
                time = dt_string.split(" ")[1]
                studentname=str(name)+" at "+str(date)
                writer.writerow([name, date, time])
                # print(name + date + time)
                break

    # Release handle to the webcam

    # plt.close()
    video_capture.release()
    cv2.destroyAllWindows()
    studentname = face_names[0]

    return marked,studentname


# mark_your_attendance()
