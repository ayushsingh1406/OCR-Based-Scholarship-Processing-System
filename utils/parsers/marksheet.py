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
        
    # ── Step 4: Calculate percentage if we have total in fraction format ──
    if total and "/" in total and not pct:
        try:
            parts = total.split("/")
            obtained = float(parts[0].strip())
            max_val = float(parts[1].strip())
            if max_val > 0:
                pct = f"{round((obtained / max_val) * 100, 2)}%"
        except:
            pass
    
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
            # Ignore sub-lines that look like address or school names
            if any(kw in t_lower for kw in ["school", "vidyalaya", "kendra", "sector", "dated"]):
                continue
            return t.strip().title()
    return None

def _extract_student_name(texts: List[str]) -> Optional[str]:
    # ── Strategy 1: Formal Certify Pattern (Strongest) ──
    for i, t in enumerate(texts):
        t_upper = t.upper()
        if "CERTIFY THAT" in t_upper:
            # Check current line (inline name)
            clean = t_upper.replace("THIS IS TO CERTIFY THAT", "").replace(":", "").strip()
            if len(clean) > 3:
                return clean.title()
            
            # Check next lines
            for j in range(i + 1, min(len(texts), i + 4)):
                candidate = texts[j].strip()
                if len(candidate) < 3: continue
                if any(kw in candidate.upper() for kw in ["ROLL", "REGN", "NO.", "FATHER", "MOTHER", "SCHO", "BOARD", "EXAM"]):
                    continue
                return candidate.title()

    # ── Strategy 2: Keyword based extraction ──
    for i, t in enumerate(texts):
        t_upper = t.upper()
        if "NAME" in t_upper and any(kw in t_upper for kw in ["STUDENT", "CANDIDATE"]):
            parts = re.split(r'[:\-]', t)
            if len(parts) > 1 and len(parts[1].strip()) > 3:
                return parts[1].strip().title()
            if i + 1 < len(texts):
                next_t = texts[i+1].strip()
                if len(next_t) > 3 and not any(kw in next_t.upper() for kw in ["FATHER", "MOTHER", "DOB", "ROLL", "BOARD"]):
                    return next_t.title()
    return None

def _extract_parent_name(texts: List[str], keywords: List[str]) -> Optional[str]:
    """Helper to extract mother or father's name robustly"""
    for i, t in enumerate(texts):
        t_upper = t.upper()
        if any(kw in t_upper for kw in keywords):
            # 1. Check same line
            t_cleaned = t_upper
            for kw in keywords:
                t_cleaned = t_cleaned.replace(kw, "")
            t_cleaned = t_cleaned.replace("NAME", "").replace("S/", "").replace("'", "").replace(":", "").replace("-", "").strip()
            
            if len(t_cleaned) > 3:
                return t_cleaned.title()

            # 2. Check next lines
            for j in range(i + 1, min(len(texts), i + 3)):
                candidate = texts[j].strip()
                # Skip short noise
                if len(candidate) < 3 or any(kw in candidate.upper() for kw in ["SCHOOL", "BOARD", "DATED", "RESULT"]):
                    continue
                # Reject if it's mostly numbers
                if sum(c.isdigit() for c in candidate) > len(candidate) * 0.5:
                    continue
                return candidate.title()
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
    # Strategy 1: Look for fractional format like 434/500 or 434 / 500
    for i, t in enumerate(texts):
        # Look for explicit Total Marks keyword context
        if "TOTAL" in t.upper() or "GRAND TOTAL" in t.upper() or "MARKS OBTAINED" in t.upper():
            # Check this line and next 2 lines
            for j in range(i, min(len(texts), i + 3)):
                match = re.search(r'(\d{3,4})\s*/\s*(\d{3,4})', texts[j])
                if match:
                    return f"{match.group(1)} / {match.group(2)}"
                # Also check for space-separated big numbers e.g. "434 500"
                matches = re.findall(r'\b\d{3,4}\b', texts[j])
                if len(matches) >= 2:
                    obtained, total = int(matches[0]), int(matches[1])
                    if obtained < total and total >= 100:
                        return f"{obtained} / {total}"
    
    # Strategy 2: Standalone fraction search
    for t in texts:
        match = re.search(r'\b(\d{3})\s*/\s*(\d{3,4})\b', t)
        if match:
            return f"{match.group(1)} / {match.group(2)}"
            
    # Strategy 3: Original keyword-based search for single numbers
    for i, t in enumerate(texts):
        if "TOTAL" in t.upper() or "GRAND TOTAL" in t.upper() or "MARKS OBTAINED" in t.upper():
            digits = re.findall(r'\b\d{3,4}\b', t)
            if digits:
                return max(digits, key=int)
            
            nearby_digits = []
            for j in range(max(0, i-2), min(len(texts), i+3)):
                nearby_digits.extend(re.findall(r'\b\d{3,4}\b', texts[j]))
            if nearby_digits:
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
