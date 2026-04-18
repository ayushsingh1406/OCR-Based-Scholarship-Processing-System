# 📄 OCR-Based Scholarship Processing System

## 📌 Overview

This project is a **paperless scholarship processing system** that extracts structured information from government documents using OCR.

It supports documents like:

* Aadhaar Card
* PAN Card
* Marksheet
* Income Certificate

The system processes images and outputs **structured JSON data**, enabling automation of document verification workflows.

---

## 🚀 Features

* 🔍 OCR-based text extraction using PaddleOCR
* 🧹 Image preprocessing for improved accuracy
* 🧠 Document classification (Aadhaar, PAN, etc.)
* 📦 Structured JSON output
* 🧩 Modular architecture (preprocessing + parsing)
* 🐳 Docker support for reproducible environment
* ⚡ Model caching (no repeated downloads)

---

# 🐳 Recommended Setup (Docker)

> ✅ No need to install Python or dependencies
> ✅ Works on any system (Windows / Linux / Mac)

---

## 🔧 Step 1 — Install Docker

Download Docker Desktop:
https://www.docker.com/products/docker-desktop/

---

## 📥 Step 2 — Clone Repository

```
git clone https://github.com/ayushsingh1406/OCR-Based-Scholarship-Processing-System.git
cd OCR_Project
```

---

## 🏗️ Step 3 — Build Docker Image (ONE TIME)

```
docker build -t ocr-project .
```

---

## 📁 Step 4 — Create Model Cache Folder

```
mkdir paddle_models
```

---

## ▶️ Step 5 — Run Project

### 🔹 Windows (PowerShell)

```
docker run -it -v ${PWD}/paddle_models:/root/.paddlex ocr-project
```

---

### 🔹 Windows (CMD)

```
docker run -it -v %cd%/paddle_models:/root/.paddlex ocr-project
```

---

### 🔹 Linux / Mac

```
docker run -it -v $(pwd)/paddle_models:/root/.paddlex ocr-project
```

---

## ⚡ Important Note

* First run → models will download
* Next runs → no download (cached locally)

---

# 🧪 Usage

1. Place document images inside:

```
test_images/
```

2. Run the system (via Docker)

3. Output will be saved in:

```
output/result.json
```

---

# 🔁 Team Workflow

For collaborators:

```
git pull
docker build -t ocr-project .
docker run -it -v <path>/paddle_models:/root/.paddlex ocr-project
```

---

# 🖥️ Alternative (Without Docker)

> ⚠️ Not recommended (may cause dependency issues)

```
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Linux/Mac

pip install -r requirements.txt
python main.py
```

---

# 🔒 Data Privacy Notice

This repository does NOT include:

* Aadhaar images
* Sensitive personal data

Users must provide their own test data locally.

---

# 🛠️ Future Scope

* 🌐 API integration (FastAPI)
* 🗄️ Database integration
* 📤 Document upload system
* 🤖 Improved ML-based field extraction

---

# 👥 Contributors

* Ayush Kumar Singh
* Aditi Avinash Sable
* Heramb Pandey

---

# 📄 License

This project is for educational and development purposes.
