# from dataclasses import replace
from flask import *
from werkzeug.utils import secure_filename
import warnings
warnings.filterwarnings("ignore")
import cv2
from cvzone.HandTrackingModule import HandDetector
from mark_attendance import mark_your_attendance
from ocr_detect import Detect_OCR
from Object_detection import detect_objects
from register import register_yourself
from gtts import gTTS
import pygame
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = set(['jpeg', 'jpg', 'png', 'gif'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'random string'

print("[info] Model loading....")
# test_model = load_model("birdClassify37.hp5")
image_size=224
print("model loaded successfully!!")

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
##########################################################################################################
#                                       Main Code
##########################################################################################################
text = '''1) Face Detection/nb)OCR/n 
           2) Object Detection\n 
           3) Face Registration\n 
           4) Exit
'''
org = (100, 200)
font = cv2.FONT_HERSHEY_COMPLEX
fontScale = 0.5
color = (0,0,255)  #(B, G, R)
thickness = 1

def allCodeHere():
    cap = cv2.VideoCapture(0)
    detector = HandDetector(detectionCon=0.8, maxHands=2)
    while True:
        success, img = cap.read()
        hands, img = detector.findHands(img)
        cv2.putText(img, "a) Face Detection", (50, 50),  font, 1,  color,  2,  cv2.LINE_4)
        cv2.putText(img, "b) OCR", (50, 100),  font, 1,  color,  2,  cv2.LINE_4)
        cv2.putText(img, "c) Object Detection", (50, 150),  font, 1,  color,  2,  cv2.LINE_4)
        cv2.putText(img, "d) Face Registration", (50, 200),  font, 1,  color,  2,  cv2.LINE_4)
        cv2.putText(img, "e) Exit", (50, 250),  font, 1,  color,  2,  cv2.LINE_4)

        if hands:
            # get Hand1
            hand1 = hands[0]
            lmList1 = hand1["lmList"]  # List of 21 Landmarks points
            bbox1 = hand1["bbox"]  # Bounding Box info x,y,w,h
            centerPoint1 = hand1["center"]  # center of the hand cx,cy
            handType1 = hand1["type"]  # hand type Left or Right

            fingers1 = detector.fingersUp(hand1)
            cnt = fingers1[0]+fingers1[1]+fingers1[2]+fingers1[3]+fingers1[4]
            # orders
            if cnt==0:
                print("STOP!")
            else:
                if handType1=='Right':
                    if fingers1[1]==1 and fingers1[2]==0 and fingers1[3]==0 and fingers1[0]==0 and fingers1[4]==0:
                        text = "Initializing Face Recognition model"
                        text_to_speech(text, language='en')
                        if mark_your_attendance():
                            print("No Closed")
                            mark_your_attendance()
                        else:
                            print("Yes Closed")
                            allCodeHere()
                    elif fingers1[1]==1 and fingers1[2]==1 and fingers1[3]==0 and fingers1[4]==0 and fingers1[0]==0:
                        text = "Initializing OCR model"
                        text_to_speech(text, language='en')
                        if Detect_OCR():
                            print("No Closed")
                            Detect_OCR()
                        else:
                            print("Yes Closed")
                            allCodeHere()
                    elif fingers1[1]==1 and fingers1[2]==1 and fingers1[3]==1 and fingers1[4]==0 and fingers1[0]==0:
                        text = "Initializing Object Detection"
                        text_to_speech(text, language='en')    
                        if detect_objects():
                            print("No Closed")
                            detect_objects()
                        else:
                            print("Yes Closed")
                            allCodeHere()
                elif handType1=='Left':
                    if fingers1[0]==1 and fingers1[1]==1 and fingers1[2]==0 and fingers1[3]==0 and fingers1[4]==0:
                        # cap.release()
                        # cv2.destroyWindow("Hands") 
                        text = "See you soon"
                        text_to_speech(text, language='en')
                        break


        cv2.imshow("Hands", img)
        # Wait for Esc key to stop
        k = cv2.waitKey(1) & 0xff
        if k == 27:
            break

    cap.release()
    cv2.destroyAllWindows() 

@app.route("/recording", methods = ['POST', 'GET'])
def recording():
    if request.method == 'POST':
        print("POST")
        f2 = request.form.get('abc')
        print("audio file")
        print(f2)

        allCodeHere()
        
        return render_template('services.html')
    return render_template('services.html')


@app.route("/faceRegister", methods = ['POST', 'GET'])
def faceRegister():
    if request.method == 'POST':
        print("POST")
        user_name = request.form.get('uName')
        print("user_name: ",user_name)

        register_yourself(user_name)

        
        return render_template('services.html')
    return render_template('services.html')
##########################################################################################################
#                                               about
##########################################################################################################
@app.route("/about", methods = ['POST', 'GET'])
def about():
    username=session.get('uname')
    return render_template('about.html')
##########################################################################################################
#                                               contact
##########################################################################################################
@app.route("/contact", methods = ['POST', 'GET'])
def contact():
    username=session.get('uname')
    return render_template('contact.html',firstName=username)
#########################################################################################################
#                                       Home page
#########################################################################################################
@app.route("/")
def root():
    return render_template('index.html')



if __name__=='__main__':
    # app.run(debug=True)
    app.run('0.0.0.0')
