import re
from typing import Optional, List, Dict, Any

def parse_marksheet(texts: List[str]) -> Dict[str, Any]:
    """
    Extract fields from a 10th/12th Marksheet.
    This is highly heuristic as marksheet formats vary by State/CBSE boards.
    """
    # ── Step 1: Try implicit computation (primary strategy) ──
    # CBSE/State boards lay out marks as: THEORY, PRACTICAL, TOTAL per subject.
    # We detect the A + B = C pattern to reliably identify subject totals.
    subject_totals = []
    i = 0
    while i < len(texts) - 2:
        try:
            a_str = re.sub(r'\D', '', texts[i])
            b_str = re.sub(r'\D', '', texts[i+1])
            c_str = re.sub(r'\D', '', texts[i+2])
            
            if a_str and b_str and c_str:
                a, b, c = int(a_str), int(b_str), int(c_str)
                # Valid subject total: Theory(a) + Practical(b) = Total(c)
                # Bounds: practical >= 10, total between 20-100
                if a + b == c and 20 <= c <= 100 and b >= 10:
                    subject_totals.append(c)
                    i += 3  # Skip past this matched triplet
                    continue
        except ValueError:
            pass
        i += 1
    
    total = None
    pct = None
    
    if subject_totals:
        computed_total = sum(subject_totals)
        max_total = len(subject_totals) * 100
        total = f"{computed_total} / {max_total}"
        pct = f"{round((computed_total / max_total) * 100, 2)}%"
    
    # ── Step 2: Fallback to explicit keyword extraction ──
    if not total:
        total = _extract_total_marks(texts)
    
    # ── Step 3: Try explicit percentage from OCR text ──
    explicit_pct = _extract_percentage(texts)
    if explicit_pct:
        pct = explicit_pct  # Prefer explicit if available
    
    result = {
        "board_name": _extract_board_name(texts),
        "student_name": _extract_student_name(texts),
        "father_name": _extract_parent_name(texts, ["FATHER", "F/N", "FATHER'S NAME"]),
        "mother_name": _extract_parent_name(texts, ["MOTHER", "M/N", "MOTHER'S NAME"]),
        "roll_number": _extract_roll_number(texts),
        "passing_year": _extract_passing_year(texts),
        "total_marks": total,
        "percentage": pct
    }
    
    return {k: v for k, v in result.items() if v is not None}

def _extract_board_name(texts: List[str]) -> Optional[str]:
    # Look for "Board", "University", "Council", "CBSE"
    for t in texts:
        t_lower = t.lower()
        if any(kw in t_lower for kw in ["board", "university", "council", "certificate examination", "secondary"]):
            return t.strip().title()
    return None

def _extract_student_name(texts: List[str]) -> Optional[str]:
    # Look for 'certify that' pattern commonly used by CBSE
    for i, t in enumerate(texts):
        if "CERTIFY THAT" in t.upper() or "NAME OF STUDENT" in t.upper():
            parts = re.split(r'[:\-]', t)
            if len(parts) > 1 and len(parts[1].strip()) > 3:
                return parts[1].strip().title()
            if i + 1 < len(texts):
                next_t = texts[i+1].strip()
                # Ensure the next line isn't just a number or roll prefix
                if not any(char.isdigit() for char in next_t) and len(next_t) > 3:
                    return next_t.title()

    # Fallback to keyword search, but strictly avoid 'MOTHER' and 'FATHER'
    for i, t in enumerate(texts):
        t_upper = t.upper()
        if "NAME" in t_upper or "CANDIDATE" in t_upper or "STUDENT" in t_upper:
            if "MOTHER" in t_upper or "FATHER" in t_upper or "GUARDIAN" in t_upper or "SCHOOL" in t_upper:
                continue
                
            parts = re.split(r'[:\-]', t)
            if len(parts) > 1 and len(parts[1].strip()) > 3:
                return parts[1].strip().title()
            
            # Check next line
            if i + 1 < len(texts):
                next_line = texts[i+1].strip()
                if len(next_line) > 3 and not any(kw in next_line.upper() for kw in ["ROLL", "REGISTRATION", "DOB", "DATE", "MOTHER", "FATHER"]):
                    return next_line.title()
    return None

def _extract_parent_name(texts: List[str], keywords: List[str]) -> Optional[str]:
    """Helper to extract mother or father's name robustly"""
    for i, t in enumerate(texts):
        t_upper = t.upper()
        if any(kw in t_upper for kw in keywords):
            # Try to grab inline (e.g. "Mother's Name URMILA PANDEY")
            # Replace the keyword with empty string to grab the rest
            t_cleaned = t_upper
            for kw in keywords:
                t_cleaned = t_cleaned.replace(kw, "")
            t_cleaned = t_cleaned.replace("NAME", "").replace("S/", "").replace("'", "").replace(":", "-").strip("- ")
            
            if len(t_cleaned) > 3:
                return t_cleaned.title()

            # Otherwise grab next line
            if i + 1 < len(texts):
                next_line = texts[i+1].strip()
                if len(next_line) > 3 and not any(char.isdigit() for char in next_line):
                    return next_line.title()
    return None

def _extract_roll_number(texts: List[str]) -> Optional[str]:
    for i, t in enumerate(texts):
        # Universal Seat/Roll Number patterns (e.g., M004935)
        # Matches 1 letter followed by exactly 6 digits, or standalone 6-10 digit numbers
        if "SEAT" in t.upper() or "ROLL" in t.upper() or "R/NO" in t.upper():
            parts = re.split(r'[:\-]', t)
            if len(parts) > 1:
                match = re.search(r'([A-Z]?[0-9]{5,10})', parts[1].replace(' ', ''))
                if match:
                    return match.group(1)
            # Check adjacent lines
            for j in range(i+1, min(len(texts), i+3)):
                match = re.search(r'^([A-Z]?[0-9]{5,10})$', texts[j].strip().replace(' ', ''))
                if match:
                    return match.group(1)
        # Standalone pattern match just in case header is totally lost
        match = re.search(r'\b([A-Z][0-9]{6})\b', t)
        if match:
            return match.group(1)
    return None

def _extract_passing_year(texts: List[str]) -> Optional[str]:
    for t in texts:
        # Match standalone year like 2018, 2020, 2024
        match = re.search(r'\b(199\d|20[0-2]\d)\b', t)
        if match:
            return match.group(1)
    return None

def _extract_total_marks(texts: List[str]) -> Optional[str]:
    # Look for aggregate format like 487/650 or nearby numbers to 'Total Marks'
    for i, t in enumerate(texts):
        if "TOTAL" in t.upper() or "GRAND TOTAL" in t.upper() or "MARKS OBTAINED" in t.upper():
            # Check for inline numbers e.g., "Total Marks: 487"
            digits = re.findall(r'\b\d{3,4}\b', t)
            if digits:
                return max(digits, key=int)  # Usually the larger number is the total, or it's the only one 
            
            # Check nearby lines
            nearby_digits = []
            for j in range(max(0, i-2), min(len(texts), i+3)):
                nearby_digits.extend(re.findall(r'\b\d{3,4}\b', texts[j]))
            if nearby_digits:
                # If we have multiple numbers like 487 and 650, format them
                unique_digits = sorted(list(set(int(d) for d in nearby_digits if 100 <= int(d) <= 2000)), reverse=True)
                if len(unique_digits) >= 2:
                    return f"{unique_digits[1]} / {unique_digits[0]}"
                elif len(unique_digits) == 1:
                    return str(unique_digits[0])
    return None

def _extract_percentage(texts: List[str]) -> Optional[str]:
    for i, t in enumerate(texts):
        if "%" in t or "PERCENTAGE" in t.upper() or "PERCENT" in t.upper():
            # Check inline
            match = re.search(r'(\d{2,3}[\.\,]\d{1,2})', t)
            if match:
                return match.group(1).replace(',', '.') + "%"
            # Check nearby lines
            for j in range(i, min(len(texts), i+2)):
                match = re.search(r'(\d{2,3}[\.\,]\d{1,2})', texts[j])
                if match:
                    return match.group(1).replace(',', '.') + "%"
    return None
