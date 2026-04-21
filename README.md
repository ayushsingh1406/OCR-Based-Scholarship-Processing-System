# 📄 OCR-Based Scholarship Processing System

## 📌 Overview

A **paperless scholarship processing system** that extracts structured data from government documents using Optical Character Recognition (OCR).

The system processes document images and converts them into **structured JSON output**, enabling automated verification workflows.

### 📑 Supported Documents
- Aadhaar Card  
- PAN Card  
- Marksheet  
- Income Certificate  

---

## 🚀 Features

- 🔍 **OCR Extraction** using PaddleOCR  
- 🧹 **Image Preprocessing** for improved accuracy  
- 🧠 **Document Classification** (Aadhaar, PAN, etc.)  
- 📦 **Structured JSON Output**  
- 🧩 **Modular Architecture** (preprocessing + parsing)  
- 🐳 **Docker Support** for reproducibility  
- ⚡ **Model Caching** (avoids repeated downloads)  

---

# 🐳 Recommended Setup (Docker)

> ✔ No Python installation required  
> ✔ Cross-platform (Windows / Linux / Mac)  

---

## 🔧 Step 1 — Install Docker

Download Docker Desktop:  
https://www.docker.com/products/docker-desktop/

---

## 📥 Step 2 — Clone Repository

```bash
git clone https://github.com/ayushsingh1406/OCR-Based-Scholarship-Processing-System.git
cd OCR_Project
```

---

## 🏗️ Step 3 — Build Docker Image (One-Time)

```bash
docker build -t ocr-project .
```

---

## 📁 Step 4 — Create Model Cache Directory

```bash
mkdir paddle_models
```

---

## ▶️ Step 5 — Run the Project

This command mounts:

- 📂 Project directory → enables live updates  
- 📦 Model cache → avoids re-downloading OCR models  

---

### 🔹 Windows (PowerShell)

```bash
docker run -it -v ${PWD}:/app -v ${PWD}/paddle_models:/root/.paddlex ocr-project
```

---

### 🔹 Windows (CMD)

```bash
docker run -it -v %cd%:/app -v %cd%/paddle_models:/root/.paddlex ocr-project
```

---

### 🔹 Linux / Mac

```bash
docker run -it -v $(pwd):/app -v $(pwd)/paddle_models:/root/.paddlex ocr-project
```

---

## ⚡ Important Notes

- `/app` mount:
  - Enables live file updates (e.g., `test_images`)
  - Reflects code changes without rebuilding  

- `/root/.paddlex` mount:
  - Stores OCR models locally  
  - Prevents repeated downloads  

### ❗ Without `/app` mount:
- New images will NOT be detected  
- Code updates will NOT reflect  

---

## 💡 Tip

After building the image once:
- Add new images anytime to `test_images/`
- Re-run the container without rebuilding  

---

## 🧪 Usage

1. Place input images inside:

```
test_images/
```

2. Run the system (Docker)

3. Output will be generated at:

```
output/result.json
```

---

## � Project Structure

```
OCR_Project/
├── main.py                          # Entry point - runs OCR processing
├── requirements.txt                 # Python dependencies
├── Dockerfile                       # Docker configuration
├── README.md                        # This file
│
├── test_images/                     # Input: Place document images here
│   └── (user adds image files)
│
├── output/                          # Output: Generated results
│   ├── results.json                 # Main OCR extraction results
│   ├── decision.json                # Classification/decision output
│   └── annotated/                   # Annotated images (if enabled)
│
├── utils/                           # Core processing modules
│   ├── preprocess.py                # Image preprocessing
│   ├── document_classifier.py       # Document type classification
│   ├── scholarship_decision.py      # Scholarship eligibility logic
│   ├── watermark_detector.py        # Watermark detection
│   │
│   ├── parsers/                     # Document-specific parsers
│   │   ├── aadhaar.py               # Aadhaar card parsing
│   │   ├── pan.py                   # PAN card parsing
│   │   ├── income.py                # Income certificate parsing
│   │   └── marksheet.py             # Marksheet parsing
│   │
│   └── verification/                # Verification modules
│
├── paddle_models/                   # OCR Model storage (auto-downloaded)
│   ├── official_models/             # PaddleOCR models
│   │   ├── PP-LCNet_x1_0_doc_ori/   # Document classification model
│   │   ├── PP-LCNet_x1_0_textline_ori/  # Text line detection model
│   │   ├── PP-OCRv5_server_det/     # Text detection model
│   │   ├── PP-OCRv5_server_rec/     # Text recognition model
│   │   └── UVDoc/                   # Document understanding model
│   ├── func_ret/                    # Function return artifacts
│   ├── locks/                       # Lock files for model safety
│   └── temp/                        # Temporary processing files
│
└── yolo_detector/                   # YOLO detection models
    └── models/
        └── detector.pt              # YOLO detector weights
```

### 📋 Key Directories

| Directory | Purpose |
|-----------|---------|
| `test_images/` | **INPUT**: Place document images here before running |
| `output/` | **OUTPUT**: Results stored as JSON files |
| `utils/` | **CORE**: Processing logic and document parsers |
| `paddle_models/` | **MODELS**: OCR models (auto-managed, ~2GB) |
| `yolo_detector/` | **DETECTION**: YOLO-based object detection models |

---

## 🔁 Team Workflow

For collaborators:

```bash
git pull
docker build -t ocr-project .
docker run -it -v <path>/paddle_models:/root/.paddlex ocr-project
```

---

# 🖥️ Alternative Setup (Without Docker)

> ⚠️ Not recommended (possible dependency conflicts)

```bash
python -m venv venv

# Activate environment
venv\Scripts\activate        # Windows
source venv/bin/activate     # Linux/Mac

pip install -r requirements.txt
python main.py
```

---

## 🔒 Data Privacy Notice

This repository does NOT include:

- Aadhaar images  
- Any sensitive personal data  

Users must provide their own test data locally.

---

## 🛠️ Future Scope

- 🌐 FastAPI integration (API layer)  
- 🗄️ Database integration  
- 📤 Web-based document upload system  
- 🤖 Advanced ML-based field extraction  

---

## 👥 Contributors

- Ayush Kumar Singh  
- Aditi Avinash Sable  
- Heramb Pandey  

---

## 📄 License

This project is intended for **educational and development purposes only**.