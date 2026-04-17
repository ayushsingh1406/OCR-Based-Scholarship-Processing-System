import re
from typing import List

class DocumentType:
    AADHAAR = "AADHAAR"
    PAN = "PAN"
    MARKSHEET = "MARKSHEET"
    INCOME = "INCOME"
    UNKNOWN = "UNKNOWN"

def classify_document(texts: List[str]) -> str:
    """
    Classify the document type based on OCR text keywords.
    Uses a weighted scoring system to handle OCR noise and ambiguity.
    """
    full_text = " ".join(texts).upper()
    # Normalized version with common OCR typos handled
    full_text_norm = full_text.replace("GOVEMMENT", "GOVERNMENT").replace("GOVERMENT", "GOVERNMENT")
    
    scores = {
        DocumentType.AADHAAR: 0,
        DocumentType.PAN: 0,
        DocumentType.MARKSHEET: 0,
        DocumentType.INCOME: 0,
    }
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    #  AADHAAR signals
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    if "AADHAAR" in full_text or "AADHAR" in full_text:
        scores[DocumentType.AADHAAR] += 50
    if "UNIQUE IDENTIFICATION AUTHORITY" in full_text_norm:
        scores[DocumentType.AADHAAR] += 50
    if "UIDAI" in full_text:
        scores[DocumentType.AADHAAR] += 50
    if "MERA AADHAAR" in full_text:
        scores[DocumentType.AADHAAR] += 30
    # "Government of India" + DOB + Male/Female is strong Aadhaar signal
    if "GOVERNMENT OF INDIA" in full_text_norm:
        scores[DocumentType.AADHAAR] += 10
        if ("DOB" in full_text or "D.O.B" in full_text or "YEAR OF BIRTH" in full_text or "YOB" in full_text):
            scores[DocumentType.AADHAAR] += 15
        if ("MALE" in full_text or "FEMALE" in full_text):
            scores[DocumentType.AADHAAR] += 15
    # VID is exclusively Aadhaar
    if "VID" in full_text:
        scores[DocumentType.AADHAAR] += 20
    # Aadhaar-specific keywords
    for t in texts:
        t_upper = t.upper().replace(' ', '')
        if "AADHAARNO" in t_upper or "AADHARNO" in t_upper:
            scores[DocumentType.AADHAAR] += 30
        if re.search(r'ENROLLMENT\s*NO', t.upper()):
            scores[DocumentType.AADHAAR] += 10
            
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    #  PAN signals
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    if "INCOME TAX DEPARTMENT" in full_text or "INCOMETAXDEPARTMENT" in full_text:
        scores[DocumentType.PAN] += 50
    if "PERMANENT ACCOUNT NUMBER" in full_text:
        scores[DocumentType.PAN] += 50
    if "GOVT. OF INDIA" in full_text:
        scores[DocumentType.PAN] += 15
    # PAN number regex (strict: standalone 10-char alphanumeric)
    for t in texts:
        t_clean = re.sub(r'[^A-Z0-9]', '', t.upper())
        if re.fullmatch(r'[A-Z]{5}[0-9]{4}[A-Z]', t_clean):
            scores[DocumentType.PAN] += 40
    # "INCOME TAX" as separate words on a line (not "INCOME CERTIFICATE")
    for t in texts:
        t_upper = t.upper().replace(' ', '')
        if "INCOMETAX" in t_upper and "CERTIFICATE" not in t_upper:
            scores[DocumentType.PAN] += 30
    # Explicit "/Name" or "/Father's Name" labels (PAN-specific)
    for t in texts:
        if "/Name" in t or "/Father" in t or "Father's Name" in t.replace("'", "'"):
            scores[DocumentType.PAN] += 15
            
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    #  MARKSHEET signals
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    if "BOARD OF" in full_text or "CENTRAL BOARD" in full_text:
        scores[DocumentType.MARKSHEET] += 40
    if "SECONDARY EDUCATION" in full_text or "SECONDARYEDUCATION" in full_text:
        scores[DocumentType.MARKSHEET] += 40
    if "MARKS STATEMENT" in full_text or "MARKSSTATEMENT" in full_text:
        scores[DocumentType.MARKSHEET] += 40
    if "EXAMINATION" in full_text:
        scores[DocumentType.MARKSHEET] += 25
    if "DIVISIONAL BOARD" in full_text:
        scores[DocumentType.MARKSHEET] += 30
    if "CERTIFY THAT" in full_text and "MARKS" in full_text:
        scores[DocumentType.MARKSHEET] += 30
    if "TOTAL MARKS" in full_text or "MARKS OBTAINED" in full_text or "MARKSOBTAINED" in full_text:
        scores[DocumentType.MARKSHEET] += 25
    if "ROLL NO" in full_text or "ROLLNO" in full_text:
        scores[DocumentType.MARKSHEET] += 15
    # Subject names in marksheets
    subjects = ["ENGLISH", "HINDI", "MATHEMATICS", "PHYSICS", "CHEMISTRY", "BIOLOGY", "SCIENCE"]
    subj_count = sum(1 for s in subjects if s in full_text)
    if subj_count >= 2:
        scores[DocumentType.MARKSHEET] += 20 + subj_count * 5
        
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    #  INCOME CERTIFICATE signals
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    if "INCOME CERTIFICATE" in full_text or "INCOMECERTIFICATE" in full_text:
        scores[DocumentType.INCOME] += 50
    if "ANNUAL INCOME" in full_text:
        scores[DocumentType.INCOME] += 40
    if "TEHSILDAR" in full_text or "TAHASILDAR" in full_text:
        scores[DocumentType.INCOME] += 30
    if "PRAMAAN PATRA" in full_text:
        scores[DocumentType.INCOME] += 30
    if "CERTIFY THAT" in full_text and "INCOME" in full_text:
        scores[DocumentType.INCOME] += 25
    if "BLOCK DEVELOPMENT OFFICER" in full_text:
        scores[DocumentType.INCOME] += 25
    # "Rs." or "Rupees" with income context
    if ("RS." in full_text or "RUPEES" in full_text) and "INCOME" in full_text:
        scores[DocumentType.INCOME] += 20
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    #  Pick the winner
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    best_type = max(scores, key=scores.get)
    best_score = scores[best_type]
    
    if best_score >= 20:
        return best_type
    
    return DocumentType.UNKNOWN
