import cv2
from ultralytics import YOLO
import pytesseract
import re
import os
# from scripts.test_img import clean_text, classify_text
# from scripts.testing import aadhaar_number

model=YOLO(r'C:\Users\sudha\PycharmProjects\document_parser\scripts\trained_model\best.pt')
confidence_threshold=0.5

keywords = {
    "Name": ["name", "neme", "nam", "naae"],
    "Aadhaar Number": ["aadhaar", "aadhar", "adhar", "uid", "unique", "identification"],
    "Date of Birth": ["dob", "birth", "date", "birthdate", "yob", "year"],
    "Gender": ["gender", "male", "female", "other", "m", "f"],
}

extracted_info = {
    "GENDER": None,
    "AADHAAR_NUMBER": None,
    "NAME": None,
    "DATE_OF_BIRTH": None,
}

def classify_text(text):
    for field,keys in keywords.items():
        if any(key.lower() in text.lower() for key in keys):
            return field.upper().replace(" ", "_")
    return "UNKNOWN"
def clean_text(text, is_date=False):
    if is_date:
        date_match=re.search(r'\b\d{2}[/\-]\d{2}[/\-]\d{4}', text)
        return date_match.group(0) if date_match else None
    else:
        return re.sub(r'\D+', '', text).strip()

cap=cv2.VideoCapture(0)
print("Press 's' to scan your aadhaar or 'q' to quit")

while True:
    ret,frame=cap.read()
    if not ret:
        break

    # results=model(frame, stream=True) this on here produces continuous frames
    resized_frame=cv2.resize(frame, (640,640))
    cv2.imshow("Live Feed - press 's' to scan aadhaar", resized_frame)

    key=cv2.waitKey(1) & 0xFF
    if key==ord('s'):
        aadhaar_frame=resized_frame.copy()
        results=model.predict(source=aadhaar_frame, conf=confidence_threshold)

        image_with_boxes=aadhaar_frame.copy()

        for result in results:
            boxes=result.boxes.xyxy
            labels=result.boxes.cls

            for i in range(len(boxes)):
                print(f"Detected labels: {result.names[int(labels[i])]}")
                # Coordinates of the aadhaar card
                x1,y1,x2,y2=map(int,boxes[i])
                # Cropping that particular section to be detect
                cropped=aadhaar_frame[y1:y2, x1:x2]

                # Preprocessing for better OCR
                gray=cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
                gray = cv2.GaussianBlur(gray, (5, 5), 0)
                _, thresh=cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
                config="--psm 11 --oem 1" if result.names[int(labels[i])]=="DATE_OF_BIRTH" else "--psm 6"
                # running tesseract
                text=pytesseract.image_to_string(thresh, config=config).strip()
                label=result.names[int(labels[i])]
                print(f"Extracted text for {label}: {text}")

                if text:
                    if label=="AADHAAR_NUMBER":
                        text=clean_text(text)
                    elif label=="DATE_OF_BIRTH":
                        text=clean_text(text, is_date=True)
                field=classify_text(text)
                print(f"Classified field: {field}") #Debugging
                if field in extracted_info:
                    extracted_info[field]=text
                    print(f"Updated extracted_info[{field}]: {text}")  # Debugging output
                elif label.upper() in extracted_info:
                    extracted_info[label.upper()] = text
                    print(f"⚠️ Fallback: Updated extracted_info[{label.upper()}] = {text}")
                else:
                    print(f"Field {field} not found in extracted_info.")  # Debugging output

                cv2.rectangle(image_with_boxes, (x1,y1), (x2,y2), (0,255,0), 2)
                cv2.putText(image_with_boxes, f"{label}:{text}", (x1,y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1)

        cv2.imshow("Detected Aadhaar", image_with_boxes)
        cv2.imwrite("aadhaar_webcam_result.jpg", image_with_boxes)
        print("✅ Aadhaar data saved and processed.")
        print("📝 Extracted Info: ", extracted_info)

        cv2.waitKey(0)

    elif key==ord('q'):
        print("Exiting...")
        break

cap.release()
cv2.destroyAllWindows()