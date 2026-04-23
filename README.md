# 📄 OCR-Based Scholarship Processing System

## 📌 Overview

A **paperless scholarship processing system** that extracts structured data from government documents using Optical Recognition (OCR) and detects authenticity markers like Ashoka emblems, Aadhaar logos, and signatures using a custom-trained YOLOv8 model.

The system converts raw document images into **structured JSON intelligence**, enabling automated verification and rapid scholarship decision-making.

### 📑 Supported Documents
- Aadhaar Card  
- PAN Card  
- Marksheet (High School/Higher Secondary)
- Income Certificate  

---

## 🚀 Features

- 🔍 **Precision OCR** using PaddleOCR for multi-document parsing.
- 🧹 **Intelligent Preprocessing** for high-accuracy extraction.
- 🧠 **Auto-Classification** of document types.
- 📦 **Structured Data Synthesis** in JSON format.
- 🎯 **Visual Authenticity Layers** via YOLO detection.
- 🧩 **Decoupled Architecture** (FastAPI + React).
- 🐳 **Docker-Ready** for seamless deployment.

---

# 🐳 Recommended Setup (Docker)

> ✔ No local Python dependencies required  
> ✔ Cross-platform stability (Windows / Linux / Mac)  

### 📥 Step 1 — Clone & Navigate
```powershell
git clone https://github.com/ayushsingh1406/OCR-Based-Scholarship-Processing-System.git
cd OCR_Project
```

### 🏗️ Step 2 — Build Environment
```powershell
docker build -t ocr-project .
```

### ▶️ Step 3 — Start API Server
```powershell
docker run -it -p 8000:8000 `
  -v ${PWD}:/app `
  -v ${PWD}/paddle_models:/paddle_models `
  ocr-project uvicorn server:app --host 0.0.0.0 --port 8000
```

### 💻 Step 4 — Launch Frontend
Open a new terminal:
```powershell
cd frontend
npm install
npm run dev
```

---

## ⚡ Important Notes

- **`/app` mount**: Enables live processing of uploaded documents.
- **`/paddle_models` mount**: Caches OCR models (~2GB) to prevent redundant downloads.
- **Data Persistence**: Analysis results are stored in the `output/` directory for audit trails.

---

## 🧪 Usage Workflow

1. Navigate to the frontend workspace (default: `http://localhost:5173`).
2. Upload the required trinity: **Identity Proof**, **Academic Marksheet**, and **Income Certificate**.
3. Initialize the **Analysis Engine**.
4. Review the **Intelligence Report** and **Visual Evidence** sections.
5. Click on any document to view the full-resolution source or AI detection layer.

---

## 📂 Project Structure

```
OCR_Project/
├── server.py                        # FastAPI Gateway (API Layer)
├── main.py                          # Core OCR & Decision Engine
├── requirements.txt                 # Backend dependencies
├── Dockerfile                       # Container manifest
│
├── frontend/                        # React + Vite Workspace
│   ├── src/                         # UI logic (App.jsx, index.css)
│   ├── package.json                 # Node dependencies
│   └── index.html                   # Entry point
│
├── test_images/                     # Input: Active processing queue
├── output/                          # Output: Analysis results
│   ├── results.json                 # Raw field extraction
│   ├── decision.json                # Final eligibility status
│   └── annotated/                   # YOLO detection visuals
│
├── utils/                           # Engine Components
│   ├── preprocess.py                # Image optimization
│   ├── document_classifier.py       # Structural classification
│   ├── scholarship_decision.py      # Eligibility logic
│   ├── watermark_detector.py        # Authenticity detection
│   └── parsers/                     # Document-specific regex engines
│
├── paddle_models/                   # OCR Model Cache
└── yolo_detector/                   # YOLO Weights & Models
```

---

## 🔁 Manual Development (Local)

> ⚠️ Requires Python 3.10+ and Node.js

### 1. API Initialization
```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python server.py
```

### 2. UI Initialization
```powershell
cd frontend
npm install
npm run dev
```

---

## 🔒 Data Privacy

This system is designed for **local-first processing**. No document data is transmitted to external servers for OCR; all models run locally within the container or host environment.

---

## 👥 Contributors

- **Ayush Kumar Singh**
- **Aditi Avinash Sable**
- **Heramb Pandey**

---

## 📄 License

This project is intended for **educational and development purposes only**.