# ⭐ Aadhaar Parser 

A full-stack Aadhaar card data extraction system that detects fields using YOLO, extracts information using Tesseract OCR, and provides a frontend for user verification and correction. All validated data is then saved into a MySQL database via a Django REST API. 🧾

---

## 🚀 Features 🚀🧩🔍 

* ✨ **YOLOv8-based Field Detection**: Custom-trained model detects Aadhaar-specific fields (Name, DOB, Gender, Aadhaar Number, etc.).
* 🔎 **OCR Text Extraction**: Tesseract OCR extracts text from each field box.
* 📝 **Error Handling**: User-editable form in frontend allows correcting OCR errors(in case there is one).
* 📤 **Data Submission**: Cleaned data is pushed to a MySQL database.
* 🧩 **Full-Stack Flow**:

  * 🧠 Backend: Django + Django REST Framework + MySQL
  * 🌐 Frontend: HTML + JS + minimal styling
  * 🤖 ML: YOLOv8 + Tesseract OCR

---

## 📊 Model Performance Summary 📉📈📌

* 📈 **Dataset Size**: \~2500 labeled images (with synthetic augmentation for background class)
* 🏷️ **Classes**: 5 Aadhaar fields + 1 background
* 🥇 **mAP\@0.5**: **0.935**
* 📉 **F1 Score**: **0.91 at confidence 0.52**
* 🎯 **Precision**: **1.00 at confidence 0.94**
* 🔁 **Recall**: **0.98 at confidence 0.00**

---

## 🧠 Tech Stack 💻🛠🧬

* 🦾 **YOLOv8** - Field detection (Ultralytics implementation)
* 🧾 **Tesseract OCR** - Text extraction
* 🛠 **Django REST Framework** - Backend API
* 🗃 **MySQL Workbench** - Database
* 💻 **HTML + CSS + JavaScript** - Frontend

---

## 📥 How It Works 🔍🖼️📄 📸📸📸

1. 🖼️ **User uploads Aadhaar image** via web UI.
2. 🔍 **YOLOv8 model** detects Aadhaar fields and returns cropped boxes.
3. 🔡 Each box is passed to **Tesseract OCR** for text extraction.
4. 🧾 OCR results are mapped to their respective fields (`name`, `dob`, `gender`, `aadhaar_number`, etc.).
5. ✏️ User can **verify and correct** OCR mistakes via editable form.
6. 💾 Final corrected data is **pushed to MySQL** using Django REST API.

---

## 🛠 Local Setup Instructions 🧪💻📦

### 1. 🧬 Clone Repository

```bash
git clone https://github.com/Thealchemist/aadhaar-parser.git
cd aadhaar-parser
```

### 2. 🐍 Set Up Python Environment

```bash
python -m venv venv
source venv/bin/activate  # Or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### 3. 🗄 MySQL Database

* 🏗 Create database in MySQL Workbench (e.g., `aadhaar_db`)
* ✍️ Update credentials in `aadhaar_backend/settings.py`:

  ```python
  DATABASES = {
      'default': {
          'ENGINE': 'django.db.backends.mysql',
          'NAME': 'aadhaar_db',
          'USER': 'your_username',
          'PASSWORD': 'your_password',
          'HOST': 'localhost',
          'PORT': '3306',
      }
  }
  ```

### 4. 🔧 Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. 🚀 Start Server

```bash
python manage.py runserver
```

### 6. 🌐 Visit Frontend

Open [http://127.0.0.1:8000](http://127.0.0.1:8000) and upload an Aadhaar card image to test the pipeline.

---

## ⚠️ Limitations ⛔️📉🧠

* ❌ May misclassify low-quality or rotated Aadhaar cards.
* 🔍 OCR can sometimes fail if font is unclear or digits are merged.
* 🧠 Deployment on free platforms like Render can fail due to memory usage.

---

## 📌 Future Improvements 🧪🚀🧠

* 🖼️ Add image preprocessing filters before OCR.
* 🔐 JWT-based login and user sessions.
* 🧼 Improve background rejection in YOLO model.
* ☁️ Deploy on Hugging Face Spaces or use AWS Lambda for scalable backend.

---

## 🤝 Author 👨‍💻📬🧾

Sudhanshu Anand

📧 [sudhanshuanand4529@gmail.com](mailto:sudhanshuanand4529@gmail.com)

🔗 [LinkedIn](https://www.linkedin.com/in/sudhanshu-anand-18043926a/) | [GitHub](https://github.com/Theallkeeeymist)

---

## ⭐️ Give a Star 🌟🧡🌟

If you found this useful, consider giving it a ⭐️ on [GitHub](https://github.com/Theallkeeeymist/aadhaar-parser)!

## ⚠️ Note: 

This code is only trained and validated for the front side of an Aadhaar card. It may not perform well in extracting address or other data from the back side.
