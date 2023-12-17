import cv2
import numpy as np
import time
from cvzone.HandTrackingModule import HandDetector
import torch
from gtts import gTTS
import pygame
import os


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

def detect_objects():
    obcount = 0
    prev_lable = ""
    model = torch.hub.load('ultralytics/yolov5', 'yolov5s', force_reload=False, trust_repo=True)
    # define a video capture object
    vid = cv2.VideoCapture(0)
    while(True):
        ret, frame = vid.read()
        detector = HandDetector(detectionCon=0.8, maxHands=2)
        hands, img = detector.findHands(frame)
        
        if hands:
            hand1 = hands[0]
            lmList1 = hand1["lmList"]  # List of 21 Landmarks points
            bbox1 = hand1["bbox"]  # Bounding Box info x,y,w,h
            centerPoint1 = hand1["center"]  # center of the hand cx,cy
            handType1 = hand1["type"]  # hand type Left or Right


            fingers1 = detector.fingersUp(hand1)
            cnt = fingers1[0]+fingers1[1]+fingers1[2]+fingers1[3]+fingers1[4]

            if cnt==0 or cnt==5:
                break
        else:
            if frame is None:
                continue
            img =frame# cv2.imread("room_ser.jpg")
            result = model(img)
            df = result.pandas().xyxy[0]
            for ind in df.index:
                x1, y1 = int(df['xmin'][ind]), int(df['ymin'][ind])
                x2, y2 = int(df['xmax'][ind]), int(df['ymax'][ind])
                label = df['name'][ind]
                conf = df['confidence'][ind]
                text = label + ' ' + str(conf.round(decimals= 2))

                cv2.rectangle(img, (x1, y1), (x2, y2), (255, 255, 0), 2)
                cv2.putText(img, text, (x1, y1 - 5), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 0), 2)

                prev_lable = label
                if prev_lable == label:
                    obcount+=1
                
                if obcount % 15 == 0:
                    textss = prev_lable+" Detected"
                    text_to_speech(textss, language='en')

            # cv2.putText(img, "Number of people at this time ", (30, 30), font, 1, color, 3)
        cv2.imshow("ObjectDetect", img)
        #time.sleep(5)
        
        # the 'q' button is set as the
        # quitting button you may use any
        # desired button of your choice
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # After the loop release the cap object
    vid.release()
    # Destroy all the windows
    cv2.destroyWindow("ObjectDetect")


# detect_objects()