# OCR-Based Scholarship Processing System (Phase 1)

## 📌 Overview

This project is the first phase of a **paperless scholarship distribution system**.
It focuses on extracting structured data from Aadhaar cards using OCR techniques.

---

## 🚀 Features

* Aadhaar card text extraction using OCR
* Image preprocessing for improved accuracy
* Structured JSON output generation
* Modular pipeline (parser + preprocessing)

---

## 📂 Project Structure

```
OCR_Project/
│── main.py
│── utils/
│   ├── parser.py
│   ├── preprocess.py
│── test_images/      # Contains input images (not included in repo)
│── output/           # Contains OCR results (not included in repo)
│── requirements.txt
│── .gitignore
```

---

## ⚙️ Installation

1. Clone the repository:

```
git clone <your-repo-link>
cd OCR_Project
```

2. Create virtual environment:

```
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
```

3. Install dependencies:

```
pip install -r requirements.txt
```

---

## ▶️ Usage

1. Place Aadhaar images inside:

```
test_images/
```

2. Run the program:

```
python main.py
```

3. Output will be stored in:

```
output/result.json
```

---

## 🔒 Data Privacy Notice

This repository does NOT include:

* Aadhaar images
* OCR output files containing personal data

Users must provide their own test data locally.

---

## 🛠️ Future Scope

* Multi-document support
* Database integration
* API-based processing
* Full scholarship workflow automation

---

## 👥 Contributors

* Ayush Kumar Singh
* Aditi Avinash Sable
* Heramb Pandey

---

## 📄 License

This project is for educational and development purposes.
