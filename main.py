"""
Aadhaar Card OCR Extractor
==========================
Robust field extraction from any Aadhaar card image.
Supports front, back, or combined (both sides) images.

Usage:
    python main.py                              # Run on all images in test_images/
    python main.py test_images/some_image.jpg   # Run on a specific image
"""

import os
import sys
import json
import warnings

# ── Suppress noisy logs ──
os.environ["PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK"] = "True"
os.environ["FLAGS_log_level"] = "3"
warnings.filterwarnings("ignore")

import re
from paddleocr import PaddleOCR
from utils.parsers import parse_aadhaar, parse_pan, parse_marksheet, parse_income
from utils.document_classifier import classify_document, DocumentType
from utils.preprocess import preprocess_image


# ─────────────────────────────────────────────────
#  OCR Engine Initialization
# ─────────────────────────────────────────────────
def init_ocr():
    """Initialize PaddleOCR engine."""
    return PaddleOCR(use_textline_orientation=True)


# ─────────────────────────────────────────────────
#  OCR Text Cleaning
# ─────────────────────────────────────────────────
def clean_ocr_texts(result) -> list[str]:
    """
    Extract and clean text from PaddleOCR result.
    Applies multiple filtering heuristics to remove noise.
    """
    if not result or not result[0]:
        return []

    texts = result[0].get("rec_texts", [])
    scores = result[0].get("rec_scores", [])

    if not texts:
        return []

    cleaned = []
    for text, score in zip(texts, scores):
        text = text.strip()

        # Skip very low confidence results
        if score < 0.3:
            continue

        # Skip empty or single-char strings
        if len(text) < 2:
            continue

        # Skip lines with garbage Chinese/Japanese characters
        # (PaddleOCR sometimes produces these for Hindi text)
        cjk_count = sum(1 for c in text if '\u4e00' <= c <= '\u9fff' or
                        '\u3040' <= c <= '\u30ff' or
                        '\uff00' <= c <= '\uffef')
        if cjk_count > len(text) * 0.3:
            continue

        cleaned.append(text)

    return cleaned


# ─────────────────────────────────────────────────
#  Process a single document image
# ─────────────────────────────────────────────────
def process_document_image(ocr_engine, image_path: str, verbose: bool = False) -> dict:
    """
    Process a single Aadhaar card image and extract all fields.
    
    Args:
        ocr_engine: Initialized PaddleOCR instance
        image_path: Path to the Aadhaar card image
        verbose: If True, print intermediate OCR results
        
    Returns:
        Dictionary of extracted fields
    """
    if not os.path.exists(image_path):
        print(f"  [ERROR] File not found: {image_path}")
        return {}

    # Step 0: Convert .webp to .png (PaddleOCR doesn't support .webp)
    import cv2
    actual_path = image_path
    if image_path.lower().endswith('.webp'):
        img = cv2.imread(image_path)
        if img is not None:
            actual_path = os.path.join("output", "_temp_webp_converted.png")
            cv2.imwrite(actual_path, img)
        else:
            print(f"  [ERROR] Could not read .webp file: {image_path}")
            return {}

    # Step 1: Preprocess image
    try:
        preprocessed = preprocess_image(actual_path)
    except Exception as e:
        print(f"  [WARN] Preprocessing failed, using raw image: {e}")
        preprocessed = None

    # Step 2: Run OCR (try preprocessed first, fallback to raw)
    if preprocessed is not None:
        # Save preprocessed to temp file for PaddleOCR
        temp_path = os.path.join("output", "_temp_preprocessed.png")
        cv2.imwrite(temp_path, preprocessed)
        result = ocr_engine.ocr(temp_path)
        # Also run on raw image for comparison
        result_raw = ocr_engine.ocr(actual_path)
    else:
        result = ocr_engine.ocr(actual_path)
        result_raw = None

    # Step 3: Clean OCR output
    texts_preprocessed = clean_ocr_texts(result)
    texts_raw = clean_ocr_texts(result_raw) if result_raw else []

    # Merge: use preprocessed as primary, supplement with raw unique texts
    texts = texts_preprocessed.copy()
    for t in texts_raw:
        if t not in texts:
            texts.append(t)

    if verbose:
        print("\n  ── Cleaned OCR Texts ──")
        for i, t in enumerate(texts):
            print(f"    [{i:2d}] {t}")
        print()

    # Step 4: Classify and Extract fields
    doc_type = classify_document(texts)
    
    if verbose:
        print(f"  [INFO] Classified document as: {doc_type}")
        
    if doc_type == DocumentType.AADHAAR:
        fields = parse_aadhaar(texts)
    elif doc_type == DocumentType.PAN:
        fields = parse_pan(texts)
    elif doc_type == DocumentType.MARKSHEET:
        fields = parse_marksheet(texts)
    elif doc_type == DocumentType.INCOME:
        fields = parse_income(texts)
    else:
        fields = {}

    # Always include document type in output
    fields["document_type"] = doc_type

    return fields


# ─────────────────────────────────────────────────
#  Pretty Print Results
# ─────────────────────────────────────────────────
def print_results(fields: dict, image_name: str = ""):
    """Print extracted fields in a clean format."""
    separator = "═" * 50
    print(f"\n{separator}")
    if image_name:
        print(f"  📄 {image_name}")
    print(separator)

    field_labels = {
        "document_type": "📄 Document Type",
        "card_side": "🔖 Card Side",
        "name": "👤 Full Name",
        "student_name": "🎓 Student Name",
        "applicant_name": "👤 Applicant Name",
        "dob": "🎂 Date of Birth",
        "gender": "⚧  Gender",
        "aadhaar_number": "🔢 Aadhaar Number",
        "pan_number": "💳 PAN Number",
        "roll_number": "📝 Roll Number",
        "certificate_number": "📜 Certificate No",
        "vid": "🔐 VID",
        "relation_type": "👪 Relation",
        "father_name": "👨 Father's Name",
        "mother_name": "👩 Mother's Name",
        "guardian_name": "👨 Guardian Name",
        "father_husband_name": "👨 Father/Husband",
        "board_name": "🏛️ Board Name",
        "total_marks": "📊 Total Marks",
        "percentage": "📈 Percentage",
        "passing_year": "📅 Passing Year",
        "annual_income": "💰 Annual Income",
        "address": "🏠 Address",
        "pincode": "📮 PIN Code",
        "enrollment_no": "📋 Enrollment No",
        "issue_date": "📅 Issue Date",
    }

    if not fields:
        print("  ⚠️  No fields could be extracted.")
    else:
        for key, label in field_labels.items():
            if key in fields:
                value = fields[key]
                print(f"  {label:25s} : {value}")

    print(separator)


# ─────────────────────────────────────────────────
#  Main Entry Point
# ─────────────────────────────────────────────────
def main():
    # Ensure output directory exists
    os.makedirs("output", exist_ok=True)

    # Determine which images to process
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    non_flag_args = [a for a in sys.argv[1:] if not a.startswith("-")]

    if non_flag_args:
        image_paths = non_flag_args
    else:
        # Default: process all images in test_images/
        test_dir = "test_images"
        if not os.path.exists(test_dir):
            print(f"Error: '{test_dir}' directory not found.")
            sys.exit(1)

        image_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp'}
        image_paths = [
            os.path.join(test_dir, f)
            for f in sorted(os.listdir(test_dir))
            if os.path.splitext(f)[1].lower() in image_extensions
        ]

        if not image_paths:
            print(f"No images found in '{test_dir}/'")
            sys.exit(1)

    # Initialize OCR engine
    print("🔧 Initializing OCR engine...")
    ocr = init_ocr()
    print("✅ OCR engine ready.\n")

    # Process each image
    all_results = {}

    for img_path in image_paths:

        name = os.path.basename(img_path)
        print(f"🔍 Processing: {name}")

        fields = process_document_image(ocr, img_path, verbose=verbose)
        all_results[name] = fields
        print_results(fields, name)

    # Save all results as JSON
    output_json = os.path.join("output", "results.json")
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    print(f"\n📁 Results saved to: {output_json}")

    # Cleanup temp file
    temp_path = os.path.join("output", "_temp_preprocessed.png")
    if os.path.exists(temp_path):
        os.remove(temp_path)


if __name__ == "__main__":
    main()
