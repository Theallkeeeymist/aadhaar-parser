# Aadhaar Parser

A web application that takes an image of an Aadhaar card, detects text regions with a custom-trained YOLOv8 model, reads each region with Tesseract OCR, lets the user review and edit the extracted values in a form, and saves the result to a database.

> **Scope of this document:** every statement below was verified against the repository's source code, configuration, committed training artifacts (plots, CSVs) or the metadata embedded in the committed model weights. Items that could not be verified from the repository are listed under [Not verifiable from this repository](#not-verifiable-from-this-repository).

---

## Pipeline

1. The user selects an image in the web page (`index.html`) and clicks **Upload**.
2. The page sends the image as multipart form data to `POST /api/upload/`.
3. The backend saves the file to `media/temp/`, reads it with OpenCV and resizes it to **640 x 640**.
4. The YOLOv8 model runs detection with a confidence threshold of **0.5**.
5. Each detected box is cropped, converted to grayscale, binarised with a fixed threshold (**150**), and passed to Tesseract via `pytesseract`.
6. Detected class indices are mapped to fields (see [Class mapping](#class-mapping)). Aadhaar number text is stripped to digits only; date-of-birth text is matched against a `DD/MM/YYYY` or `DD-MM-YYYY` pattern.
7. The extracted values are returned as JSON and shown in an editable form (Name, Gender, Date of Birth, Aadhaar Number).
8. On **Submit to Database**, the form values are sent to `POST /api/save/` and stored.

## Tech stack

| Layer | Technology | Version (from `requirements.txt`) |
|---|---|---|
| Web framework | Django | 5.2.3 |
| Detection model | Ultralytics YOLOv8 (`yolov8n.pt` base) | ultralytics 8.3.157 |
| OCR | pytesseract (requires a separate Tesseract install) | 0.3.13 |
| Image processing | opencv-python | 4.11.0.86 |
| Deep learning | torch / torchvision | 2.7.1 / 0.22.1 |
| Database drivers | mysqlclient / psycopg2-binary | 2.2.7 / 2.9.10 |
| DB URL parsing | dj-database-url | 3.0.1 |
| Server | gunicorn | 23.0.0 |
| Augmentation | albumentations | 2.0.8 |
| Frontend | Plain HTML, CSS and JavaScript (single template, no framework) | n/a |

Python 3.12 is the interpreter configured in the committed PyCharm project files (`Python 3.12 (document_parser)`).

## Repository structure

```
aadhaar-parser/
├── aadhaar_backend/              # Django project root
│   ├── manage.py
│   ├── requirements.txt          # byte-identical copy of the root requirements.txt
│   ├── aadhaar_backend/          # settings.py, urls.py, wsgi.py, asgi.py
│   └── parser_app/
│       ├── views.py              # upload/parse, save, home views
│       ├── utils.py              # YOLO inference + OCR logic
│       ├── models.py             # AadhaarData model
│       ├── urls.py
│       ├── templates/index.html  # the entire frontend
│       ├── migrations/0001_initial.py
│       └── aadhaar_detection_YOLOv8_model.pt   # weights loaded by the app
├── scripts/
│   ├── train_model.py            # YOLOv8 training entry point
│   ├── augment.py                # synthetic image generator
│   ├── test_img.py               # single-image test script
│   ├── testing.py                # alternative OCR pipeline experiment
│   ├── webcam_detection.py       # live webcam capture + scan
│   ├── yolov8n.pt                # pretrained base weights
│   ├── trained_model/            # weights + evaluation plots of the deployed model
│   └── aadhaar_yolo/             # local training runs (aadhar_detector, aadhar_detector2)
├── config.yaml                   # YOLO dataset config used by train_model.py
├── data.py                       # downloads 5 sample card images
├── requirements.txt
└── README.md
```

## API endpoints

Defined in `parser_app/urls.py`:

| Method | Path | Purpose |
|---|---|---|
| GET | `/` | Serves the upload/verification page |
| POST | `/api/upload/` | Accepts form field `image`, returns extracted fields as JSON |
| POST | `/api/save/` | Accepts JSON (`name`, `aadhaar`, `date_of_birth`, `gender`), saves a record |
| GET/POST | `/parse/` | Stub view (returns an error JSON when no image is posted) |
| GET | `/admin/` | Django admin (`AadhaarData` is registered) |

**Upload response keys:** `NAME`, `GENDER`, `DATE_OF_BIRTH`, `AADHAAR_NUMBER` (each `null` if not detected).

**Save behaviour:** if a record with the same `aadhaar_number` already exists, the endpoint returns HTTP 400 with `"Aadhaar Number already exists."`. Success returns `{"message": "Data Saved!"}`.

Both `/api/upload/` and `/api/save/` are decorated with `@csrf_exempt`. They are plain Django views returning `JsonResponse`; the Django REST Framework decorators (`@api_view`, `@permission_classes`) are present only as comments.

## Database

`AadhaarData` model (`parser_app/models.py`):

| Field | Type | Constraints |
|---|---|---|
| `name` | CharField(1000) | nullable, blank |
| `gender` | CharField(15) | nullable, blank |
| `aadhaar_number` | CharField(15) | **unique**, required |
| `date_of_birth` | CharField(10) | nullable, blank (a code comment states CharField is used because OCR output is unreliable for date parsing) |

**Connection selection** (`settings.py`):

- If the environment variable `DATABASE_URL` is set, it is parsed with `dj_database_url` (this is the path used for PostgreSQL; git history contains the commit message "Added postgre url for render").
- Otherwise it falls back to MySQL on `localhost:3306`, database name `aadhaar_db`.

## Class mapping

The deployed model has **5 output classes**. Their names stored inside the weights file are the bare strings `'0'`, `'1'`, `'2'`, `'3'`, `'4'`. The application translates indices with this table (`utils.py`):

| Class index | Mapped field |
|---|---|
| 0 | `AADHAAR_NUMBER` |
| 1 | `DATE_OF_BIRTH` |
| 2 | `GENDER` |
| 3 | `NAME` |
| 4 | *(not mapped; treated as `UNKNOWN` and not stored in the output)* |

## Model

### Deployed model (`aadhaar_backend/parser_app/aadhaar_detection_YOLOv8_model.pt`)

Read directly from the checkpoint metadata:

| Property | Value |
|---|---|
| Base model | `yolov8n.pt` |
| Ultralytics version | 8.3.160 |
| Saved | 2025-06-27 |
| Classes | 5 |
| Training data path | `/kaggle/input/aadhar-dataset/data.yaml` (trained on Kaggle) |
| Epochs | 50 |
| Image size | 640 |
| Batch size | 8 |
| Seed | 0 |

The same file (identical MD5) is committed as `scripts/trained_model/aadhaar_detection_YOLOv8_model.pt`.

### Validation results for the deployed model

Source: the evaluation plots committed in `scripts/trained_model/` and the metric history stored in the checkpoint.

| Metric | Value | Source |
|---|---|---|
| mAP@0.5 (all classes) | **0.935** | `PR_curve.png` |
| mAP@0.5 at final epoch 50 | 0.934 | checkpoint metrics |
| mAP@0.5:0.95 at final epoch 50 | 0.652 | checkpoint metrics |
| F1 (all classes) | **0.91** at confidence 0.520 | `F1_curve.png` |
| Precision (all classes) | **1.00** at confidence 0.942 | `P_curve.png` |
| Recall (all classes) | **0.98** at confidence 0.000 | `R_curve.png` |
| Final-epoch precision / recall | 0.874 / 0.961 | checkpoint metrics |

**Per-class mAP@0.5** (`PR_curve.png`):

| Class | mAP@0.5 |
|---|---|
| 0 | 0.994 |
| 1 | 0.993 |
| 2 | 0.993 |
| 3 | 0.994 |
| 4 | **0.700** |

**Validation instance counts** (derived from `confusion_matrix.png`): about 517 (class 0), 508 (class 1), 515 (class 2), 508 (class 3) and **12 (class 4)**. Class 4 has very few validation instances and is the only class with substantially lower performance; the confusion matrix shows 30 background regions predicted as class 4.

### Local training runs (`scripts/aadhaar_yolo/`)

`train_model.py` trains `yolov8n.pt` for 30 epochs at image size 640, batch 8, using `config.yaml`. Both committed runs (`aadhar_detector`, `aadhar_detector2`) used identical hyperparameters and ran on **CPU**.

`config.yaml` defines a **single class** (`0: aadhaar`). Consequently `aadhar_detector2/weights/best.pt` is a **1-class** model (`aadhaar`), is a different model from the deployed 5-class one, and is not the model the Django app loads. Its committed `results.csv` reports mAP@0.5 of 0.995 and mAP@0.5:0.95 of 0.995 at epoch 30; note that `config.yaml` sets both `train` and `val` to the same `images` folder, so these figures are not held-out results.

## Data augmentation

`scripts/augment.py` generates **500** images from a single source image using Albumentations (brightness/contrast, motion blur, rotation up to 15 degrees, horizontal flip, random shadow, resize to 640 x 640) and writes a full-image label `0 0.5 0.5 1.0 1.0` for each.

## Other scripts

| Script | What it does |
|---|---|
| `scripts/test_img.py` | Runs the model on one image, applies OCR per box, saves annotated output and shows it with matplotlib |
| `scripts/testing.py` | Experimental pipeline: loads the 1-class `best.pt`, resizes the image to 1024 x 768, and extracts fields with OCR text heuristics and regexes (denoising, adaptive thresholding, digit whitelist for the Aadhaar number) |
| `scripts/webcam_detection.py` | Opens webcam 0; press `s` to scan a frame and `q` to quit; saves `aadhaar_webcam_result.jpg` |
| `data.py` | Downloads 5 sample Aadhaar images from public URLs into `aadhaar_samples/` |

These scripts contain hard-coded absolute Windows paths under `C:\Users\sudha\PycharmProjects\document_parser\...` and will need path edits to run elsewhere.

## Running locally

Prerequisites: Python, a MySQL server (or a `DATABASE_URL`), and the **Tesseract OCR engine** installed on the system (`pytesseract` is only a wrapper).

```bash
git clone https://github.com/Theallkeeeymist/aadhaar-parser.git
cd aadhaar-parser/aadhaar_backend
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Then open `http://127.0.0.1:8000/`.

## Known limitations

- Only field detection classes 0-3 are used; class 4 detections are discarded.
- The deployed model's class names are numeric, so the code path that would choose the date-of-birth-specific Tesseract configuration (`--psm 7 --oem 1`) is never taken; all fields are read with `--psm 6`.
- Each field of a given type is stored once; if the model detects the same class twice, the later detection overwrites the earlier one.
- If YOLO detects nothing, all four returned fields are `null` and the user fills the form manually.
- `parser_app/tests.py` contains no tests.
- There is no user authentication on any endpoint.
- Uploaded files are written to `media/temp/` and are not deleted after processing.
