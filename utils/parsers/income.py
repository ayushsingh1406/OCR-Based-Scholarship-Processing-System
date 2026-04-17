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
    full_text = " ".join(texts)
    
    # Strategy 1: 'certify that [Mr./Mrs./Smt] NAME, son/daughter/wife of'
    # Handle periods after 'that' and titles like Mr., Mrs., Smt
    match = re.search(
        r'certify that[\.,\s]+(?:Mr\.?|Mrs\.?|Ms\.?|Smt\.?|Sri\.?|Shri\.?)?\s*([A-Za-z][A-Za-z\s\.]+?)(?:\s*,\s*|\s+)(?:son|daughter|wife|is a|W/o|S/o|D/o)',
        full_text, re.IGNORECASE
    )
    if match:
        name = match.group(1).strip().rstrip(',. ')
        # Fix spacing for merged titles
        name = re.sub(r'([sS]mt\.?|[sS]ri\.?|[sS]hri\.?)(?=[a-zA-Z])', r'\1 ', name)
        if len(name) > 2:
            return name.title()

    # Strategy 2: Keyword-based extraction
    for i, t in enumerate(texts):
        t_upper = t.upper()
        if ("NAME" in t_upper and "PFC" not in t_upper and "FATHER" not in t_upper and "MOTHER" not in t_upper) or "SHRI" in t_upper or "SMT" in t_upper:
            t_fixed = re.sub(r'([sS]mt\.?|[sS]ri\.?|[sS]hri\.?)(?=[a-zA-Z])', r'\1 ', t)
            parts = re.split(r'[:\-]', t_fixed)
            if len(parts) > 1 and len(parts[1].strip()) > 3:
                return parts[1].strip().title()
            # Check next line
            if i + 1 < len(texts):
                next_t = texts[i+1].strip()
                # Ensure it doesn't look like a header or irrelevant label
                if len(next_t) > 3 and not any(kw in next_t.upper() for kw in ["FATHER", "HUSBAND", "DATE", "RS", "INCOME", "RESIDENT", "ADDRESS"]):
                    return next_t.title()
    return None

def _extract_father_name(texts: List[str]) -> Optional[str]:
    # Strategy 1: From affidavit text 'son of Mr. NAME'
    full_text = " ".join(texts)
    match = re.search(
        r'(?:son|daughter|wife)\s+of\s+(?:Mr\.?|Mrs\.?|Ms\.?|Smt\.?|Sri\.?|Shri\.?)?\s*([A-Za-z][A-Za-z\s\.]+?)(?:\s*,|\s+is\s)',
        full_text, re.IGNORECASE
    )
    if match:
        name = match.group(1).strip().rstrip(',. ')
        if len(name) > 2:
            return name.title()
    
    # Strategy 2: Keyword on line
    for i, t in enumerate(texts):
        t_upper = t.upper()
        if "FATHER" in t_upper or "HUSBAND" in t_upper or "S/O" in t_upper or "D/O" in t_upper or "W/O" in t_upper:
            parts = re.split(r'[:\-]', t)
            if len(parts) > 1 and len(parts[1].strip()) > 3:
                return parts[1].strip().title()
            
            # Check next line
            if i + 1 < len(texts):
                next_t = texts[i+1].strip()
                if len(next_t) > 3 and not any(kw in next_t.upper() for kw in ["DATE", "RS", "INCOME", "RESIDENT", "ADDRESS"]):
                    return next_t.title()
    return None

def _extract_annual_income(texts: List[str]) -> Optional[str]:
    valid_amounts = []
    
    for i, t in enumerate(texts):
        t_upper = t.upper().replace(' ', '')
        if "RS" in t_upper or "RUPEE" in t_upper or "INCOME" in t_upper or "INR" in t_upper:
            # Match amounts on same line
            matches = re.findall(r'(\d{1,2}(?:,\d{2,3})+(?:\.\d{2})?|\d{4,8}(?:\.\d{2})?)', t)
            for m in matches:
                val = m.replace(',', '')
                try:
                    if 1000 <= float(val) <= 100000000:
                        valid_amounts.append(float(val))
                except ValueError:
                    pass
            
            # Check NEXT line for amount (e.g., "Total annual Income Rs." then "92000")
            if not valid_amounts and i + 1 < len(texts):
                next_digits = re.sub(r'[^\d,.]', '', texts[i+1].strip())
                if next_digits:
                    try:
                        val = float(next_digits.replace(',', ''))
                        if 1000 <= val <= 100000000:
                            valid_amounts.append(val)
                    except ValueError:
                        pass
                    
    # Fallback to scanning for large formatted currencies anywhere
    if not valid_amounts:
        for t in texts:
            matches = re.findall(r'\b(\d{1,2}(?:,\d{2,3})+|\d{4,7})\b', t)
            for m in matches:
                val = m.replace(',', '')
                try:
                    if 1000 <= float(val) <= 100000000:
                        valid_amounts.append(float(val))
                except ValueError:
                    pass
                    
    if valid_amounts:
        amount = max(valid_amounts)
        return f"Rs. {int(amount)}"
            
    return None

def _extract_issue_date(texts: List[str]) -> Optional[str]:
    months = {'january':'01','february':'02','march':'03','april':'04','may':'05','june':'06',
              'july':'07','august':'08','september':'09','october':'10','november':'11','december':'12'}
    
    for t in texts:
        t_upper = t.upper()
        if "DATE" in t_upper or "ISSUED" in t_upper or "DINANK" in t_upper:
            # Numeric format: dd/mm/yyyy or dd-mm-yyyy
            match = re.search(r'(\d{2})[/\-\.](\d{2})[/\-\.](20[0-2]\d|19\d{2})', t)
            if match:
                return f"{match.group(1)}/{match.group(2)}/{match.group(3)}"
            
            # Textual format: 30 March 2026
            match = re.search(r'(\d{1,2})\s+(\w+)\s+(20[0-2]\d|19\d{2})', t)
            if match:
                day = match.group(1).zfill(2)
                month_str = match.group(2).lower()
                year = match.group(3)
                if month_str in months:
                    return f"{day}/{months[month_str]}/{year}"
            
    # Standalone date search
    for t in texts:
        match = re.search(r'\b(\d{2})[/\-\.](\d{2})[/\-\.](20[0-2]\d|19\d{2})\b', t)
        if match:
            return f"{match.group(1)}/{match.group(2)}/{match.group(3)}"
    return None
