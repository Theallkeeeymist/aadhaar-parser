import re
import cv2
import pytesseract
from ultralytics import YOLO

# Set Tesseract path
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Load trained YOLO model
model = YOLO(r"C:\Users\sudha\PycharmProjects\document_parser\scripts\aadhaar_yolo\aadhar_detector2\weights\best.pt")

# Input image path
img_path = r"C:\Users\sudha\PycharmProjects\document_parser\dataset\test\testimg2.png"
image = cv2.imread(img_path)
image = cv2.resize(image, (1024, 768))  # Normalize resolution for model stability

results = model(image)[0]

def clean_name(name_line):
    name_line = re.sub(r'^[^A-Za-z]+', '', name_line)
    name_line = re.sub(r'[^A-Za-z\s]', '', name_line)
    name_line = re.sub(r'\s+', ' ', name_line).strip().title()
    words = name_line.split()
    if words and (len(words[-1]) <= 2 or not words[-1].isalpha()):
        words = words[:-1]
    return " ".join(words)

def preprocess_ocr(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.fastNlMeansDenoising(gray, None, h=30, templateWindowSize=7, searchWindowSize=21)
    gray = cv2.medianBlur(gray, 3)
    versions = []

    _, th1 = cv2.threshold(gray, 120, 255, cv2.THRESH_BINARY)
    th2 = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                cv2.THRESH_BINARY, 11, 2)
    morph = cv2.morphologyEx(th1, cv2.MORPH_CLOSE,
                              cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2)))

    versions.extend([th1, th2, morph])
    return versions

# Init extracted fields
name, dob, gender, aadhaar_number = None, None, None, None

for box in results.boxes:
    x1, y1, x2, y2 = map(int, box.xyxy[0])
    cropped = image[y1:y2, x1:x2]
    cropped = cv2.resize(cropped, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)

    # --------- Extract Text Info Section ---------
    processed_text_img = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
    processed_text_img = cv2.fastNlMeansDenoising(processed_text_img, None, h=30)
    _, thresh = cv2.threshold(processed_text_img, 120, 255, cv2.THRESH_BINARY)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    processed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

    # OCR for Name, DOB, Gender
    config = r'--oem 3 --psm 6'
    text_ocr = pytesseract.image_to_string(processed, config=config)
    lines = [line.strip() for line in text_ocr.split('\n') if line.strip()]

    dob_index = None
    for i, line in enumerate(lines):
        if re.search(r'\bmale\b', line.lower()):
            gender = "Male"
        elif re.search(r'\bfemale\b', line.lower()):
            gender = "Female"
        elif re.search(r'\bother\b', line.lower()):
            gender = "Other"

        match = re.search(r'\d{2}/\d{2}/\d{4}', line)
        if match:
            dob_index = i
            dob = match.group()

    if dob_index is not None:
        for j in range(dob_index - 1, dob_index - 3, -1):
            if j >= 0:
                possible = lines[j]
                if len(possible.split()) >= 1 and sum(c.isalpha() for c in possible) > 2:
                    name = clean_name(possible)
                    break

    # -------- Aadhaar Number Detection Section --------
    h, w, _ = cropped.shape
    roi = cropped[int(0.5 * h):int(0.95 * h), int(0.05 * w):int(0.95 * w)]

    aadhaar_number_config = r'--oem 3 --psm 11 -c tessedit_char_whitelist=0123456789'
    aadhaar_number_regex = r'(\d{4}[\s\-]*){3}'

    for idx, version in enumerate(preprocess_ocr(roi)):
        ocr_out = pytesseract.image_to_string(version, config=aadhaar_number_config)
        match = re.search(aadhaar_number_regex, ocr_out)
        if match:
            aadhaar_number = ''.join(match.group().split())
            break

# ----------- FINAL OUTPUT -----------
print(f"\n🧾 Extracted Info:")
print(f"Name: {name}")
print(f"DOB: {dob}")
print(f"Gender: {gender}")
print(f"Aadhaar Number: {aadhaar_number}")
