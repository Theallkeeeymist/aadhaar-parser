from ultralytics import YOLO
import cv2
import pytesseract
import re
import matplotlib.pyplot as plt
import os

model=YOLO(r'C:\Users\sudha\PycharmProjects\document_parser\scripts\trained_model\best.pt')
confidence_threshold=0.5
image=r"C:\Users\sudha\PycharmProjects\document_parser\dataset\test\testimg2.png"
output=r"C:\Users\sudha\PycharmProjects\document_parser\results\testimg1\predimg.jpg"

image=cv2.imread(image)
resized_image=cv2.resize(image,(640,640))
results=model.predict(source=resized_image, conf=confidence_threshold)

keywords={
    "Name": ["name"],
    "Aadhaar Number": ["aadhaar", "uid", "unique", "aadhar", "adhar"],
    "Date of Birth": ["dob", "DOB", "year", "birth", "date"],
    "Gender": ["gender", "male", "female", "other"],
}
extracted_info={
    "GENDER": None,
    "AADHAAR_NUMBER": None,
    "NAME": None,
    "DATE_OF_BIRTH":None,
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

image_with_boxes=resized_image.copy()

results[0].save(filename=output)
print(f"Processed: {image} → {output}")

#print detected classes and boxes
for result in results:
    boxes=result.boxes.xyxy
    labels=result.boxes.cls
    for i in range(len(boxes)):
        x1,y1,x2,y2=map(int,boxes[i])
        cropped=resized_image[y1:y2, x1:x2]
        gray=cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
        _,thresh=cv2.threshold(gray,150,255, cv2.THRESH_BINARY)

        config="--psm 7 --oem 1" if result.names[int(labels[i])]=="DATE_OF_BIRTH" else "--psm 6"
        text=pytesseract.image_to_string(thresh, config=config).strip()

        label=result.names[int(labels[i])]
        print(f"Extracted test for {label}: {text}")

        if text:
            if label=="AADHAAR_NUMBER":
                text=clean_text(text)
            elif label=="DATE_OF_BIRTH":
                text=clean_text(text,is_date=True)

        field=classify_text(label)
        if field in extracted_info:
            extracted_info[field]=text

        cv2.rectangle(image_with_boxes, (x1,y1), (x2,y2),(0,255,0),2)
        cv2.putText(image_with_boxes, f"{label}: {text}", (x1,y1-10), cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,255,0),0)
    output2 = r"C:\Users\sudha\PycharmProjects\document_parser\results\testimg1\w_detail.jpg"
    cv2.imwrite(output2, image_with_boxes)
    plt.figure(figsize=(10,10))
    plt.imshow(cv2.cvtColor(image_with_boxes, cv2.COLOR_BGR2RGB))
    plt.axis('off')
    plt.show()