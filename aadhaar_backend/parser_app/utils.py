from ultralytics import YOLO
from django.conf import settings
import cv2
import pytesseract
import re
import matplotlib.pyplot as plt
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
model_path = os.path.join(settings.BASE_DIR, "best.pt")
print(f"📍 Looking for model at: {model_path}")
assert os.path.exists(model_path), f"❌ best.pt not found at: {model_path}"
model = YOLO(model_path)

def parse_from_image(image_path):
    image = cv2.imread(image_path)
    resized_image = cv2.resize(image, (640, 640))
    return extract_fields(resized_image)

confidence_threshold=0.5

keywords={
    "Name": ["name"],
    "Aadhaar Number": ["aadhaar", "uid", "unique", "aadhar", "adhar"],
    "Date of Birth": ["dob", "DOB", "year", "birth", "date"],
    "Gender": ["gender", "male", "female", "other"],
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

def extract_fields(image):
    results = model.predict(source=image, conf=confidence_threshold)
    image_with_boxes = image.copy()

    extracted_info = {
        "GENDER": None,
        "AADHAAR_NUMBER": None,
        "NAME": None,
        "DATE_OF_BIRTH": None,
    }

    for result in results:
        if result.boxes is None or result.boxes.xyxy is None:
            print("⚠️ No detections found by YOLO model.")
            continue  # skip this result if no boxes

        boxes = result.boxes.xyxy
        labels = result.boxes.cls

        print("📦 YOLO Detected:", [result.names[int(cls)] for cls in labels])

        for i in range(len(boxes)):
            # print(f"Detected labels: {result.names[int(labels[i])]}")
            label=result.names[int(labels[i])]
            # Coordinates of the aadhaar card
            x1, y1, x2, y2 = map(int, boxes[i])
            # Cropping that particular section to be detect
            cropped = image[y1:y2, x1:x2]

            # Preprocessing for better OCR
            gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (5, 5), 0)
            _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
            config = "--psm 6 --oem 1" if result.names[int(labels[i])] == "DATE_OF_BIRTH" else "--psm 6"
            # running tesseract
            text = pytesseract.image_to_string(thresh, config=config).strip()
            label = result.names[int(labels[i])]
            label=label.upper()

            print(f"Extracted text for {label}: {text}")

            if text:
                if label == "AADHAAR_NUMBER":
                    text = clean_text(text)
                elif label == "DATE_OF_BIRTH":
                    text = clean_text(text, is_date=True)
            field = classify_text(text)
            # print(f"Classified field: {field}")  # Debugging
            field=label.upper()
            if field in extracted_info:
                extracted_info[field] = text
                # print(f"Updated extracted_info[{field}]: {text}")  # Debugging output
            else:
                print(f"⚠️ Skipped: {field} not in extracted_info keys")
            # elif label.upper() in extracted_info:
            #     extracted_info[label.upper()] = text
                # print(f"⚠️ Fallback: Updated extracted_info[{label.upper()}] = {text}")
            # else:
            #     print(f"Field {field} not found in extracted_info.")  # Debugging output

            cv2.rectangle(image_with_boxes, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(image_with_boxes, f"{label}:{text}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0),
                        1)
    return extracted_info, image_with_boxes