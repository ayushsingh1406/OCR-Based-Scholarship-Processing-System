import re
from typing import Optional, List, Dict, Any

def parse_income(texts: List[str]) -> Dict[str, Any]:
    """
    Extract fields from an Income Certificate.
    """
    result = {
        "certificate_number": _extract_certificate_number(texts),
        "applicant_name": _extract_applicant_name(texts),
        "father_husband_name": _extract_father_name(texts),
        "annual_income": _extract_annual_income(texts),
        "issue_date": _extract_issue_date(texts)
    }
    
    return {k: v for k, v in result.items() if v is not None}

def _extract_certificate_number(texts: List[str]) -> Optional[str]:
    # Look for "Certificate No", "Application No", etc.
    for i, t in enumerate(texts):
        if any(kw in t.upper() for kw in ["CERTIFICATE NO", "APP NO", "APPLICATION NO", "ENROLLMENT", "CERTIFICATE CASE NO"]):
            parts = re.split(r'[:\-No]', t)
            # Find the longest contiguous alphanumeric string with digits
            candidates = re.findall(r'([A-Za-z0-9/:\-]{8,30})', t)
            for c in candidates:
                if sum(char.isdigit() for char in c) > 3:
                    return c.strip(':- ')
            
            if i + 1 < len(texts):
                next_t = texts[i+1].strip()
                if any(char.isdigit() for char in next_t):
                    return next_t
    return None

def _extract_applicant_name(texts: List[str]) -> Optional[str]:
    # Look for formal affidavit structure 'certify that [NAME] son of...'
    full_text = " ".join(texts)
    match = re.search(r'certify that\s+([A-Z\s\.]+)(?:\s+son|\s+daughter|\s+wife|\s+W/o|\s+S/o|\s+D/o)', full_text, re.IGNORECASE)
    if match:
        name = match.group(1).strip()
        # Fix spacing for merged titles like 'SmtCHHABI' -> 'Smt CHHABI'
        name_fixed = re.sub(r'([sS]mt\.?|[sS]ri\.?|[sS]hri\.?)(?=[a-zA-Z])', r'\1 ', name)
        if len(name_fixed) > 3:
            return name_fixed.title()

    # Usually below "Pramaan Patra" or keywords like "Name", "Sri/Smt/Kum"
    for i, t in enumerate(texts):
        t_upper = t.upper()
        if ("NAME" in t_upper and "PFC" not in t_upper) or "SRI" in t_upper or "SHRI" in t_upper or "SMT" in t_upper:
            # Fix spacing for merged titles like 'SmtCHHABI' -> 'Smt CHHABI'
            t_fixed = re.sub(r'([sS]mt\.?|[sS]ri\.?|[sS]hri\.?)(?=[a-zA-Z])', r'\1 ', t)
            parts = re.split(r'[:\-]', t_fixed)
            if len(parts) > 1 and len(parts[1].strip()) > 3:
                return parts[1].strip().title()
    return None

def _extract_father_name(texts: List[str]) -> Optional[str]:
    for i, t in enumerate(texts):
        t_upper = t.upper()
        if "FATHER" in t_upper or "HUSBAND" in t_upper or "S/O" in t_upper or "D/O" in t_upper or "W/O" in t_upper:
            parts = re.split(r'[:\-]', t)
            if len(parts) > 1 and len(parts[1].strip()) > 3:
                return parts[1].strip().title()
    return None

def _extract_annual_income(texts: List[str]) -> Optional[str]:
    # Look for "Rs", "Rupees", "Income", "Annual"
    valid_amounts = []
    
    for t in texts:
        t_upper = t.upper().replace(' ', '')
        if "RS" in t_upper or "RUPEE" in t_upper or "INCOME" in t_upper or "INR" in t_upper:
            matches = re.findall(r'(?:RS\.?|INR)?(\d{1,2}(?:,\d{2,3})+(?:\.\d{2})?|\d{4,8}(?:\.\d{2})?)', t_upper)
            for m in matches:
                val = m.replace(',', '')
                if 1000 <= float(val) <= 10000000:
                    valid_amounts.append(float(val))
                    
    # Fallback to scanning for large formatted currencies anywhere in the document
    if not valid_amounts:
        for t in texts:
            matches = re.findall(r'\b(\d{1,2}(?:,\d{2,3})+|\d{4,7})\b', t)
            for m in matches:
                val = m.replace(',', '')
                if 1000 <= float(val) <= 10000000:
                    valid_amounts.append(float(val))
                    
    if valid_amounts:
        amount = max(valid_amounts) # Extract highest logical income figure to brush off conversion rates
        # Format explicitly
        return f"Rs. {int(amount)}"
            
    return None

def _extract_issue_date(texts: List[str]) -> Optional[str]:
    for t in texts:
        t_upper = t.upper()
        if "DATE" in t_upper or "ISSUED" in t_upper or "DINANK" in t_upper:
            # Enforce Year is 20xx or 19xx
            match = re.search(r'(\d{2})[/\-\.](\d{2})[/\-\.](20[0-2]\d|19\d{2})', t)
            if match:
                return f"{match.group(1)}/{match.group(2)}/{match.group(3)}"
            
        # Standalone date search anywhere
        match = re.search(r'\b(\d{2})[/\-\.](\d{2})[/\-\.](20[0-2]\d|19\d{2})\b', t)
        if match:
            return f"{match.group(1)}/{match.group(2)}/{match.group(3)}"
    return None
