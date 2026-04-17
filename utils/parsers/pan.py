import re
from typing import Optional, List, Dict, Any

def parse_pan(texts: List[str]) -> Dict[str, Any]:
    """
    Extract fields from a PAN card.
    Expects texts to be cleaned/filtered OCR text.
    Returns extracted fields as a dictionary.
    """
    pan_number = _extract_pan_number(texts)
    
    # Identify DOB and its index for backward tracking
    dob, dob_idx = _extract_dob_and_idx(texts)
    
    name, father_name = _extract_names(texts, dob_idx)

    result = {
        "pan_number": pan_number,
        "name": name,
        "father_name": father_name,
        "dob": dob,
    }
    
    return {k: v for k, v in result.items() if v is not None}

def _extract_pan_number(texts: List[str]) -> Optional[str]:
    """Find the standard PAN format: 5 letters, 4 digits, 1 letter."""
    for t in texts:
        # Aggressively remove whitespaces and special characters before regex
        t_clean = re.sub(r'[^a-zA-Z0-9]', '', t.upper())
        match = re.search(r'([A-Z]{5}[0-9]{4}[A-Z]{1})', t_clean)
        if match:
            return match.group(1)
    return None

def _extract_dob_and_idx(texts: List[str]):
    for i, t in enumerate(texts):
        # Accommodate hyphens, slashes, or periods
        match = re.search(r'(\d{2})[/\-\.](\d{2})[/\-\.](\d{4})', t)
        if match:
            day, month, year = int(match.group(1)), int(match.group(2)), int(match.group(3))
            if 1 <= day <= 31 and 1 <= month <= 12 and 1900 <= year <= 2025:
                return f"{match.group(1)}/{match.group(2)}/{match.group(3)}", i
    return None, -1

def _is_valid_pan_name(t: str) -> bool:
    """Validate if the string looks like an Indian proper name in PAN format."""
    # PAN names are mostly ALPHABETICAL.
    # Eliminate strings filled with digits or known keywords.
    blacklist = ["INCOME", "TAX", "DEPARTMENT", "GOVT", "INDIA", "FATHER", "NAME", "SIGNATURE", "PERMANENT", "ACCOUNT", "NUMBER", "CARD", "DATE", "BIRTH", "YEAR"]
    t_clean = t.strip()
    t_upper = t_clean.upper()
    if any(b in t_upper for b in blacklist):
        return False
    if len(t_clean) < 3:
        return False
        
    # Check if string is predominantly alphabetic
    alpha_ratio = sum(1 for c in t_clean if c.isalpha()) / len(t_clean) if len(t_clean) > 0 else 0
    return alpha_ratio > 0.7

def _extract_names(texts: List[str], dob_idx: int):
    """
    Attempts to extract Applicant and Father names robustly.
    Strategy 1: Find keywords 'NAME' and 'FATHER' and take the immediate next valid alphabetic line.
    Strategy 2: Backward-chaining from DOB if keywords are obfuscated.
    """
    app_name, father_name = None, None
    
    # Strategy 1: Keyword search anywhere in the array
    for i, t in enumerate(texts):
        t_upper = t.upper()
        if not app_name and ("NAME" in t_upper and "FATHER" not in t_upper):
            # Look at immediate next lines
            for j in range(i+1, min(len(texts), i+4)):
                if _is_valid_pan_name(texts[j]):
                    app_name = texts[j].title()
                    break
        elif not father_name and ("FATHER" in t_upper):
            # Look at immediate next lines
            for j in range(i+1, min(len(texts), i+4)):
                if _is_valid_pan_name(texts[j]):
                    father_name = texts[j].title()
                    break
                    
    # If both found, return them
    if app_name and father_name:
        return app_name, father_name
        
    # Strategy 2: Fallback to Backward-chaining from DOB
    if dob_idx != -1:
        valid_names = []
        for i in range(dob_idx - 1, -1, -1):
            t = texts[i]
            if _is_valid_pan_name(t):
                valid_names.append(t.title())
                if len(valid_names) == 2:
                    break
                    
        if len(valid_names) == 2:
            return app_name or valid_names[1], father_name or valid_names[0]
        elif len(valid_names) == 1:
            return app_name or valid_names[0], father_name
            
    return app_name, father_name
