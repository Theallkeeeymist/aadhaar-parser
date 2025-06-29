import cv2
import albumentations as A
import os

input_img_path=r"C:\Users\sudha\PycharmProjects\document_parser\dataset\train\aadhaar1.jpeg"
output_img_dir=r"C:\Users\sudha\PycharmProjects\document_parser\scripts\augmented\images"
output_label_dir=r"C:\Users\sudha\PycharmProjects\document_parser\scripts\augmented\labels"

os.makedirs(output_img_dir,exist_ok=True)
os.makedirs(output_label_dir,exist_ok=True)

yolo_label="0 0.5 0.5 1.0 1.0" #class id x_center, y_center width height makes .txt file with the same name hehe

augmentations=A.Compose([
    A.RandomBrightnessContrast(p=0.5),
    A.MotionBlur(blur_limit=3, p=0.3),
    A.Rotate(limit=15, p=0.3),
    A.HorizontalFlip(p=0.5),
    A.RandomShadow(p=0.3),
    A.Resize(640,640)
])

assert os.path.exists(input_img_path), f"File missing: {input_img_path}"
image=cv2.imread(input_img_path)
assert image is not None, "Image failed to load"

for i in range(500):
    augmented=augmentations(image=image)["image"]
    out_path=os.path.join(output_img_dir, f"aug_aadhaar_{i}.jpg")
    print("Saving to:", out_path)
    cv2.imwrite(out_path, augmented)

    with open(os.path.join(output_label_dir, f"aug_aadhaar_{i}.txt"), "w") as f:
        f.write(yolo_label)
