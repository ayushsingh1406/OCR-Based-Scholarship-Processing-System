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
    """
    full_text = " ".join(texts).upper()
    
    # Check PAN
    if "INCOME TAX DEPARTMENT" in full_text or "INCOMETAXDEPARTMENT" in full_text or "GOVT. OF INDIA" in full_text:
        return DocumentType.PAN
        
    # Check Aadhaar (handles both front and back)
    if "AADHAAR" in full_text or "UNIQUE IDENTIFICATION AUTHORITY" in full_text or "UIDAI" in full_text or "MERA AADHAAR" in full_text:
        return DocumentType.AADHAAR
    if "GOVERNMENT OF INDIA" in full_text and ("DOB" in full_text or "YEAR OF BIRTH" in full_text or "YOB" in full_text) and ("MALE" in full_text or "FEMALE" in full_text):
        return DocumentType.AADHAAR
        
    # Check Marksheet
    if "BOARD OF" in full_text or "CENTRAL BOARD" in full_text or "SECONDARY EDUCATION" in full_text or "MARKS STATEMENT" in full_text or "EXAMINATION" in full_text or "DIVISIONAL BOARD" in full_text:
        return DocumentType.MARKSHEET
        
    # Check Income Certificate
    if "INCOME CERTIFICATE" in full_text or "PRAMAAN PATRA" in full_text or "TEHSILDAR" in full_text or "GOVERNMENT OF" in full_text and "INCOME" in full_text:
        return DocumentType.INCOME

    # Further heuristics based on line content
    import re
    for t in texts:
        t_upper = t.upper().replace(' ', '')
        if "INCOMETAX" in t_upper or "PAN" in t_upper:
            return DocumentType.PAN
        
        # Regex for PAN
        if re.search(r'[A-Z]{5}[0-9]{4}[A-Z]', t_upper):
            return DocumentType.PAN
        if "MARKS" in t_upper or "GRADE" in t_upper or "CGPA" in t_upper:
            return DocumentType.MARKSHEET
        if "INCOME" in t_upper and ("RS" in t_upper or "RUPEES" in t_upper):
            return DocumentType.INCOME

    return DocumentType.UNKNOWN
