import cv2
import easyocr

# Function to extract text from an image using EasyOCR
def extract_text_from_image(image_path):
    # Create an EasyOCR reader
    reader = easyocr.Reader(['en'], gpu=False)  # 'en' for English

    # Read text from the image
    result = reader.readtext(image_path)

    # Extract and return the text
    text = ' '.join([item[1] for item in result])
    return text

# Path to the image file
cap = cv2.VideoCapture(0)
while True:
    # Capture a frame from the video
    ret, frame = cap.read()

    if not ret:
        break

    # Extract text from the current frame

    # Read the image using OpenCV
    image = frame

    # Extract text from the image
    text = extract_text_from_image(image)

    # Print the extracted text
    print('Extracted Text:', text)

    cv2.imshow('Original Frame', frame)
    print('Extracted Text:', text)

    # Break the loop if the 'q' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture object and close all windows
cap.release()
cv2.destroyAllWindows()
