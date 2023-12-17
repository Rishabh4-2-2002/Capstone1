import cv2 
from cvzone.HandTrackingModule import HandDetector
import time
from gtts import gTTS
import pygame
import os
import easyocr

detector = HandDetector(detectionCon=0.8, maxHands=2)

# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
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

def extract_text_from_image(image_path):
    # Create an EasyOCR reader
    reader = easyocr.Reader(['en'], gpu=False)  # 'en' for English

    # Read text from the image
    result = reader.readtext(image_path)

    # Extract and return the text
    text = ' '.join([item[1] for item in result])
    return text

def Detect_OCR():
    interval = 20
    start_time = time.time()
    vid = cv2.VideoCapture(0) 
    while(True): 
        ret, frame = vid.read() 
        hands, img = detector.findHands(frame)
        
        if hands:
            hand1 = hands[0]
            lmList1 = hand1["lmList"]  # List of 21 Landmarks points
            bbox1 = hand1["bbox"]  # Bounding Box info x,y,w,h
            centerPoint1 = hand1["center"]  # center of the hand cx,cy
            handType1 = hand1["type"]  # hand type Left or Right


            fingers1 = detector.fingersUp(hand1)
            cnt = fingers1[0]+fingers1[1]+fingers1[2]+fingers1[3]+fingers1[4]

            if cnt==1 or cnt==5:
                break
        else:

            textss = extract_text_from_image(frame)
            print()
            print("Extracted Text: ",textss)
            print()
            if len(textss)>2:
                current_time = time.time()
                if current_time - start_time >= interval:
                    text_to_speech(textss, language='en')
                    start_time = current_time

        cv2.imshow("OCR", frame)     
        k = cv2.waitKey(1) & 0xff
        if k == 27:
            break

    vid.release() 
    cv2.destroyWindow("OCR") 


# Detect_OCR()