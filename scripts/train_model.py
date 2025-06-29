from ultralytics import YOLO
import os

#Loading a pre-trained YOLOv8 model
model=YOLO("yolov8n.pt")

project_root=os.path.dirname(os.path.abspath(__file__))
config_path=os.path.join(project_root,"..","config.yaml")

#training the model from the config we decided in config.yaml
model.train(
    data=config_path,
    epochs=30,
    imgsz=640,
    batch=8,
    project="aadhaar_yolo",
    name="aadhar_detector"
)