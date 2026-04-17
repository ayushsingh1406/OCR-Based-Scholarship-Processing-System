"""
Robust Aadhaar Card Field Extractor
Handles multiple Aadhaar card formats and OCR inconsistencies.
"""

import re
from typing import Optional, List


# ─────────────────────────────────────────────────
#  Aadhaar Number  (12 digits, various formats)
# ─────────────────────────────────────────────────
def extract_aadhaar(texts: List[str]) -> Optional[str]:
    """
    Strategy:
    1. Try to find a clean 12-digit number in a single line (with or without spaces).
    2. Try to assemble 12 digits from adjacent 4-digit groups across lines.
    3. Try partial groups (e.g. 8+4, 4+8, etc.)
    Avoids VID numbers (16-digit) and enrollment numbers.
    """
    # First, identify VID-related indices to exclude
    # VID appears AFTER the Aadhaar number on the card, so only exclude
    # the VID line itself and lines after it (not before)
    vid_indices = set()
    for i, t in enumerate(texts):
        if 'vid' in t.lower():
            vid_indices.update(range(i, min(len(texts), i + 5)))

    # --- Pass 1: single line with exactly 12 digits and no VID context ---
    for i, t in enumerate(texts):
        if i in vid_indices:
            continue
        digits = re.sub(r'\D', '', t)
        if len(digits) == 12 and _is_likely_aadhaar_line(t, digits):
            return _format_aadhaar(digits)

    # --- Pass 2: line with "Aadhaar No" context ---
    for i, t in enumerate(texts):
        t_lower = t.lower()
        if 'aadhaar' in t_lower and 'no' in t_lower:
            # Look at this and next lines for the number
            for j in range(i, min(len(texts), i + 3)):
                digits = re.sub(r'\D', '', texts[j])
                if len(digits) == 12:
                    return _format_aadhaar(digits)

    # --- Pass 3: assemble from consecutive lines with 4-digit groups ---
    digit_groups = []
    for i, t in enumerate(texts):
        if i in vid_indices:
            continue
        t_stripped = t.strip()
        digits = re.sub(r'\D', '', t_stripped)
        # Line is purely a 4-digit group (allow some whitespace around)
        if digits and len(digits) == 4 and len(t_stripped) <= 6:
            digit_groups.append((i, digits))

    # Try to find 3 consecutive 4-digit groups
    for idx in range(len(digit_groups) - 2):
        i0, d0 = digit_groups[idx]
        i1, d1 = digit_groups[idx + 1]
        i2, d2 = digit_groups[idx + 2]
        if i1 - i0 <= 3 and i2 - i1 <= 3:
            combined = d0 + d1 + d2
            return _format_aadhaar(combined)

    # --- Pass 4: 8-digit + 4-digit adjacent (common OCR split) ---
    for i, t in enumerate(texts):
        if i in vid_indices:
            continue
        digits = re.sub(r'\D', '', t.strip())
        if len(digits) == 8:
            for j in range(max(0, i - 2), min(len(texts), i + 3)):
                if j == i or j in vid_indices:
                    continue
                adj_digits = re.sub(r'\D', '', texts[j].strip())
                if len(adj_digits) == 4 and len(texts[j].strip()) <= 6:
                    combined = digits + adj_digits if j > i else adj_digits + digits
                    if len(combined) == 12:
                        return _format_aadhaar(combined)

    # --- Pass 5: any line containing exactly 12+ digits, take first 12 ---
    for i, t in enumerate(texts):
        if i in vid_indices:
            continue
        digits = re.sub(r'\D', '', t)
        if len(digits) >= 12:
            t_lower = t.lower()
            if 'vid' in t_lower or 'enrollment' in t_lower or 'enrol' in t_lower:
                continue
            if 'mobile' in t_lower or 'phone' in t_lower:
                continue
            return _format_aadhaar(digits[:12])

    # --- Pass 6: look for formatted aadhaar (XXXX XXXX XXXX) pattern ---
    for i, t in enumerate(texts):
        if i in vid_indices:
            continue
        match = re.search(r'(\d{4})\s+(\d{4})\s*(\d{4})', t)
        if match:
            combined = match.group(1) + match.group(2) + match.group(3)
            return _format_aadhaar(combined)

    return None


def _is_likely_aadhaar_line(text: str, digits: str) -> bool:
    """Check if a line is likely an Aadhaar number (not VID, enrollment, etc.)"""
    t_lower = text.lower()
    if 'vid' in t_lower or 'enrollment' in t_lower or 'enrol' in t_lower:
        return False
    if 'mobile' in t_lower or 'phone' in t_lower:
        return False
    non_digit_non_space = re.sub(r'[\d\s\-]', '', text)
    return len(non_digit_non_space) <= 3


def _format_aadhaar(digits: str) -> str:
    """Format 12 digits as XXXX XXXX XXXX"""
    return f"{digits[:4]} {digits[4:8]} {digits[8:12]}"


# ─────────────────────────────────────────────────
#  VID (Virtual ID - 16 digits)
# ─────────────────────────────────────────────────
def extract_vid(texts: List[str]) -> Optional[str]:
    """Extract VID if present. VID is a 16-digit number."""
    for i, t in enumerate(texts):
        t_lower = t.lower()
        if 'vid' in t_lower:
            digits = re.sub(r'\D', '', t)
            for j in range(i + 1, min(len(texts), i + 4)):
                adj_digits = re.sub(r'\D', '', texts[j].strip())
                if adj_digits and len(adj_digits) <= 8:
                    digits += adj_digits
                if len(digits) >= 16:
                    break
            if len(digits) >= 16:
                d = digits[:16]
                return f"{d[:4]} {d[4:8]} {d[8:12]} {d[12:16]}"
    return None


# ─────────────────────────────────────────────────
#  Date of Birth
# ─────────────────────────────────────────────────
def extract_dob(texts: List[str]) -> Optional[str]:
    """
    Strategy:
    1. Look for DOB keyword + date pattern on same line.
    2. Look for standalone date pattern dd/mm/yyyy.
    """
    # --- Pass 1: line containing DOB keyword ---
    for t in texts:
        t_upper = t.upper().replace(' ', '')
        if 'DOB' in t_upper or 'D.O.B' in t_upper or 'BIRTH' in t_upper:
            match = re.search(r'(\d{2})[/\-\.](\d{2})[/\-\.](\d{4})', t)
            if match:
                return f"{match.group(1)}/{match.group(2)}/{match.group(3)}"

    # --- Pass 2: any line with dd/mm/yyyy pattern ---
    for t in texts:
        match = re.search(r'(\d{2})[/\-\.](\d{2})[/\-\.](\d{4})', t)
        if match:
            day, month, year = int(match.group(1)), int(match.group(2)), int(match.group(3))
            if 1 <= day <= 31 and 1 <= month <= 12 and 1900 <= year <= 2025:
                return f"{match.group(1)}/{match.group(2)}/{match.group(3)}"

    return None


# ─────────────────────────────────────────────────
#  Gender
# ─────────────────────────────────────────────────
def extract_gender(texts: List[str]) -> Optional[str]:
    """Extract gender from OCR text."""
    for t in texts:
        t_lower = t.lower().strip()
        if re.search(r'\bfemale\b', t_lower):
            return "Female"
        if re.search(r'\bmale\b', t_lower) and 'female' not in t_lower:
            return "Male"
        if 'male' in t_lower and 'female' not in t_lower:
            return "Male"
    return None


# ─────────────────────────────────────────────────
#  Name (most robust extraction)
# ─────────────────────────────────────────────────

_NAME_BLACKLIST = {
    "government", "india", "aadhaar", "aadhar", "uidai",
    "dob", "male", "female", "birth", "date", "issue",
    "address", "unique", "identification", "authority",
    "proof", "identity", "citizenship", "verification",
    "authentication", "scanning", "offline", "online",
    "code", "xml", "used", "should", "not", "with",
    "enrollment", "your", "mera", "meri", "pehchan",
    "bharat", "sarkar", "vid", "help", "www", "uidai",
    "mobile", "phone", "pin", "state", "district",
    "sector", "flat", "floor", "street", "ward",
    "details", "issued", "govemment",
    # Common OCR garbage that looks alphabetic
    "hra", "hror", "hrct", "htet", "hqut",
}

_TEMPLATE_PHRASES = [
    "government of india", "govemment of india",
    "unique identification authority", "authorityoftndia", "unique ldentification",
    "aadhaar is proof", "proof of identity",
    "not of citizenship", "date of birth",
    "mera aadhar", "meri pehchan",
    "your aadhaar no", "enrollment no",
    "help@uidai", "www.uidai",
]

# Common garbage OCR patterns (short nonsense)
_GARBAGE_PATTERNS = re.compile(
    r'^[A-Z]{2,4}[a-z]{0,2}$|'     # HRA, HROR, HRCT, etc.
    r'^[a-z]{2,3}[A-Z]|'            # wrAP, etc.
    r'^\d+[A-Z]+\d*$|'              # 4806DEI7467, etc.
    r'^[^a-zA-Z]*$|'                # no letters at all
    r'^.{1,2}$'                     # too short
)


def _is_valid_name_word(word: str) -> bool:
    """Check if a word looks like a valid name word (not OCR garbage)."""
    if len(word) < 2:
        return False
    if word.lower() in _NAME_BLACKLIST:
        return False
    # Must be mostly alphabetic
    if not word.replace('.', '').replace("'", '').replace('-', '').isalpha():
        return False
    # Must start with uppercase (for English names)
    if not word[0].isupper():
        return False
    # Reject if ALL uppercase and <= 4 chars (likely OCR noise like "HRA", "BHTET")
    if word.isupper() and len(word) <= 5:
        return False
    # Rest should be mostly lowercase (names like "Kumar" not "HROR")
    if len(word) > 1 and word[1:].isupper() and len(word) <= 6:
        return False
    return True


def extract_name(texts: List[str]) -> Optional[str]:
    """
    Strategy:
    1. Find DOB line and look for name 1-3 lines before it.
    2. Try to merge adjacent single-word name lines (e.g., "Heramb" + "Pandey").
    3. Look for 2-3 word alphabetic lines.
    4. Handle CamelCase names without spaces.
    """
    # Find the DOB line index
    dob_idx = -1
    for i, t in enumerate(texts):
        t_upper = t.upper().replace(' ', '')
        if 'DOB' in t_upper or re.search(r'\d{2}/\d{2}/\d{4}', t):
            dob_idx = i
            break

    # Find the gender line index
    gender_idx = -1
    for i, t in enumerate(texts):
        t_lower = t.lower().strip()
        if 'male' in t_lower or 'female' in t_lower:
            gender_idx = i
            break

    # Collect candidate name lines with scoring
    candidates = []

    for i, t in enumerate(texts):
        t_clean = t.strip()
        if not t_clean or len(t_clean) < 3:
            continue

        t_lower = t_clean.lower()

        # Skip obvious non-name lines
        if any(phrase in t_lower for phrase in _TEMPLATE_PHRASES):
            continue
        if re.search(r'\d{4,}', t_clean):
            continue
        if re.search(r'[{}$@#%&*=+<>|\\~`]', t_clean):
            continue
        if re.search(r'\b[SDWC]/O\b', t_clean, re.IGNORECASE):
            continue
        if re.search(r'\bAddress\b', t_clean, re.IGNORECASE):
            continue
        if re.search(r'\b(DOB|D\.O\.B)\b', t_clean, re.IGNORECASE):
            continue
        # Skip mostly non-ASCII 
        ascii_chars = sum(1 for c in t_clean if ord(c) < 128)
        if ascii_chars < len(t_clean) * 0.7:
            continue
        # Skip garbage patterns
        if _GARBAGE_PATTERNS.match(t_clean):
            continue

        # Try to extract a valid name
        name = _try_extract_name(t_clean)
        if not name:
            continue

        # ── Scoring ──
        score = 0

        # Proximity to DOB (names are 1-3 lines before DOB)
        if dob_idx >= 0:
            dist = dob_idx - i  # positive if name is before DOB
            if 1 <= dist <= 3:
                score += 20 - dist  # highest for immediately before DOB
            elif dist == 0:
                score += 5  # same line (unlikely but possible)
            elif -2 <= dist < 0:
                score += 5  # just after DOB (less likely)

        # Proximity to gender line (name is usually 1-2 lines before gender)
        if gender_idx >= 0:
            gdist = gender_idx - i
            if 1 <= gdist <= 3:
                score += 10

        # Multi-word names get a bonus
        word_count = len(name.split())
        if word_count >= 2:
            score += 5
        if word_count == 3:
            score += 3

        # Name length bonus
        if len(name) >= 8:
            score += 3

        candidates.append((name, score, i))

    # ── Try merging adjacent known-name lines ──
    # Sort candidates by line number to find adjacencies easily
    valid_name_lines = {item[2]: item[0] for item in candidates}
    for i in range(len(texts) - 1):
        if i in valid_name_lines and (i+1) in valid_name_lines:
            n1 = valid_name_lines[i]
            n2 = valid_name_lines[i+1]
            merged = f"{n1} {n2}"
            score = 0
            if dob_idx >= 0:
                dist = dob_idx - i
                if 1 <= dist <= 4:
                    score += 20 - dist
            if gender_idx >= 0:
                gdist = gender_idx - i
                if 1 <= gdist <= 4:
                    score += 10
            score += 25  # strong bonus for being a merged multi-line name
            candidates.append((merged.title(), score, i))

    if candidates:
        # Sort by score descending, then by position
        candidates.sort(key=lambda x: (-x[1], x[2]))
        # Special case for back-only cards: name shouldn't usually be present unless it's very robust
        # But for now, we'll just return the best candidate
        return candidates[0][0]

    return None


def _try_extract_name(text: str) -> Optional[str]:
    """Try to extract a name from a single text line."""
    text = text.strip()

    # Handle CamelCase names without spaces (e.g., "MerajKhan")
    if text.replace(' ', '').isalpha() and ' ' not in text and len(text) > 3:
        split = re.findall(r'[A-Z][a-z]+', text)
        if len(split) >= 2:
            # Verify each part looks like a name
            if all(_is_valid_name_word(s) for s in split):
                return ' '.join(split).title()

    # Multi-word line
    words = text.split()
    if 1 <= len(words) <= 4:
        valid_words = [w for w in words if _is_valid_name_word(w)]
        if valid_words and len(valid_words) == len(words):
            name = ' '.join(valid_words)
            if len(name) >= 3:
                return name.title()

    # Handle "Name:" prefix
    match = re.match(r'(?:Name\s*:\s*)([A-Za-z\s]+)', text, re.IGNORECASE)
    if match:
        name = match.group(1).strip()
        if name and len(name) >= 3:
            return name.title()

    return None


def _is_blacklisted(text: str) -> bool:
    """Check if text contains blacklisted words."""
    words = set(re.findall(r'[a-z]+', text.lower()))
    if words and len(words.intersection(_NAME_BLACKLIST)) > len(words) * 0.5:
        return True
    return False


# ─────────────────────────────────────────────────
#  Father / Mother / Guardian Name
# ─────────────────────────────────────────────────
def extract_relation_name(texts: List[str]) -> Optional[dict]:
    """
    Extract S/O, D/O, W/O, C/O names.
    Returns dict like {"relation": "S/O", "name": "Dinesh Diwakar"}
    """
    relation_patterns = [
        r'([SDWC])\s*/\s*[Oo]\s*[:\-]?\s*([A-Za-z][A-Za-z\s\.]+)',
        r'([SDWC])/O\s*[:\-]?\s*([A-Za-z][A-Za-z\s\.]+)',
        r'([SDWC])/O([A-Z][a-z]+[A-Z][A-Za-z]+)',  # CamelCase like S/OSudhdanKhan
    ]

    candidates = []

    for t in texts:
        for pattern in relation_patterns:
            match = re.search(pattern, t)
            if match:
                relation_letter = match.group(1).upper()
                name = match.group(2).strip()

                # Split CamelCase if no spaces
                if ' ' not in name and len(name) > 3:
                    split = re.findall(r'[A-Z][a-z]+', name)
                    if len(split) >= 2:
                        name = ' '.join(split)

                # Clean up: stop at common address/noise words
                stop_words = ['flat', 'floor', 'street', 'sector', 'ward',
                              'house', 'plot', 'block', 'lane', 'road',
                              'village', 'town', 'city', 'dist', 'po:',
                              'vtc:', 'vtc', 'sub district', 'district', 'state', 'pin',
                              'noida', 'delhi', 'saniana', 'saniyana', 'f Haryana', ',']
                for sw in stop_words:
                    idx = name.lower().find(sw)
                    if idx >= 0:
                        name = name[:idx]

                # Stop at lowercase words (likely address leaking into name, e.g. "Arvind Kumarmeera saray")
                words = name.split()
                clean_words = []
                for w in words:
                    if w.islower() and len(w) > 2:
                        break  # stop incorporating words
                    clean_words.append(w)
                name = ' '.join(clean_words)

                name = re.sub(r'\s+', ' ', name).strip().rstrip(',.- ')

                if name and len(name) >= 2:
                    rel_map = {'S': 'S/O', 'D': 'D/O', 'W': 'W/O', 'C': 'C/O'}
                    candidates.append({
                        "relation": rel_map.get(relation_letter, f"{relation_letter}/O"),
                        "name": name.title()
                    })

    if candidates:
        # Prefer the candidate with the most clear formatting (fewest words, avoiding long merged lines)
        candidates.sort(key=lambda x: len(x['name']))
        return candidates[0]

    return None


# ─────────────────────────────────────────────────
#  Address
# ─────────────────────────────────────────────────

_ADDRESS_STOP_WORDS = [
    "aadhaar", "unique", "uidai", "help@", "www.",
    "mera", "meri", "your aadhaar", "1947",
]


def extract_address(texts: list[str]) -> Optional[str]:
    """
    Strategy:
    1. Find "Address:" keyword and collect lines until a stop condition.
    2. If no keyword, look for lines with address-like content.
    3. Clean and format the final address.
    """
    address_lines = []
    collecting = False

    for i, t in enumerate(texts):
        t_clean = t.strip()
        t_lower = t_clean.lower()

        if len(t_clean) < 2:
            continue

        # Detect address start
        if re.search(r'\baddress\b', t_lower, re.IGNORECASE):
            collecting = True
            addr_part = re.sub(r'^.*?[Aa]ddress\s*[:\-]?\s*', '', t_clean)
            if addr_part.strip():
                address_lines.append(addr_part.strip())
            continue

        if collecting:
            if any(stop in t_lower for stop in _ADDRESS_STOP_WORDS):
                break
            digits = re.sub(r'\D', '', t_clean)
            if len(digits) >= 10 and len(t_clean) > 0 and len(digits) / len(t_clean) > 0.7:
                break
            # Skip mostly non-ASCII
            ascii_chars = sum(1 for c in t_clean if ord(c) < 128)
            if ascii_chars < len(t_clean) * 0.3:
                continue

            address_lines.append(t_clean)

    if address_lines:
        address = _clean_address(' '.join(address_lines))
        if address and len(address) > 10:
            return address

    # --- Fallback: C/O based address (like Jatin's card) ---
    co_lines = []
    co_collecting = False
    for i, t in enumerate(texts):
        t_clean = t.strip()
        t_lower = t_clean.lower()
        if re.search(r'[SDWC]/O', t_clean):
            co_collecting = True
            co_lines.append(t_clean)
            continue
        if co_collecting:
            if any(stop in t_lower for stop in _ADDRESS_STOP_WORDS):
                break
            # Skip if it looks like Aadhaar number or non-address
            digits = re.sub(r'\D', '', t_clean)
            if len(digits) >= 10 and len(t_clean) > 0 and len(digits) / len(t_clean) > 0.7:
                break
            if len(t_clean) < 3:
                continue
            # Must contain letters
            if not re.search(r'[a-zA-Z]', t_clean):
                continue
            co_lines.append(t_clean)

    if co_lines:
        address = _clean_address(' '.join(co_lines))
        if address and len(address) > 10:
            return address

    return None


def _clean_address(address: str) -> str:
    """Clean and format address string."""
    address = address.replace('，', ',')
    address = address.replace('．', '.')
    # Add spaces after commas/colons if missing
    address = re.sub(r',(\S)', r', \1', address)
    address = re.sub(r':(\S)', r': \1', address)
    # Add space in CamelCase within address (e.g., "NoidaSector" -> "Noida Sector")
    address = re.sub(r'([a-z])([A-Z])', r'\1 \2', address)
    # Normalize whitespace
    address = re.sub(r'\s+', ' ', address)
    address = address.strip(' ,.-:;')
    return address


# ─────────────────────────────────────────────────
#  Pincode
# ─────────────────────────────────────────────────
def extract_pincode(texts: list[str]) -> Optional[str]:
    """Extract 6-digit Indian pincode."""
    for t in texts:
        match = re.search(r'PIN\s*[Cc]ode\s*[:\-]?\s*(\d{6})', t, re.IGNORECASE)
        if match:
            return match.group(1)

    # Look in address context
    for t in texts:
        t_lower = t.lower()
        if any(kw in t_lower for kw in ['address', 'dist', 'state', 'sector', 'pradesh', 'haryana']):
            match = re.search(r'\b(\d{6})\b', t)
            if match:
                pin = match.group(1)
                if pin[0] != '0' and int(pin) >= 100000:
                    return pin

    # Standalone 6-digit on its own line
    for t in texts:
        t_stripped = t.strip()
        if re.match(r'^\d{6}$', t_stripped):
            pin = t_stripped
            if pin[0] != '0':
                return pin

    return None


# ─────────────────────────────────────────────────
#  Enrollment Number
# ─────────────────────────────────────────────────
def extract_enrollment_no(texts: list[str]) -> Optional[str]:
    """Extract enrollment number if present."""
    for t in texts:
        t_lower = t.lower()
        if 'enrollment' in t_lower or 'enrol' in t_lower:
            match = re.search(r'(\d{4}/\d{5}/\d{5})', t)
            if match:
                return match.group(1)
    return None


# ─────────────────────────────────────────────────
#  Issue Date
# ─────────────────────────────────────────────────
def extract_issue_date(texts: list[str]) -> Optional[str]:
    """Extract issue date if visible."""
    for t in texts:
        t_lower = t.lower()
        if 'issue' in t_lower or 'issued' in t_lower:
            match = re.search(r'(\d{2}[/\-\.]\d{2}[/\-\.]\d{4})', t)
            if match:
                return match.group(1).replace('-', '/').replace('.', '/')
    return None


# ─────────────────────────────────────────────────
#  Card Side Detection
# ─────────────────────────────────────────────────
def detect_card_side(texts: list[str]) -> str:
    """Detect if the image is front, back, or both sides of Aadhaar card."""
    full_text = ' '.join(texts).lower()
    has_front = bool(re.search(r'dob|male|female|government.*india', full_text))
    has_back = bool(re.search(r'address|unique.*identification|uidai|pin\s*code', full_text))

    if has_front and has_back:
        return "both"
    elif has_back:
        return "back"
    else:
        return "front"


# ─────────────────────────────────────────────────
#  Master Extraction Function
# ─────────────────────────────────────────────────
def extract_all_fields(texts: list[str]) -> dict:
    """
    Extract all available fields from OCR text.
    Returns a dict with all extracted fields.
    """
    card_side = detect_card_side(texts)

    relation_info = extract_relation_name(texts)
    guardian_name = None
    relation_type = None
    if relation_info:
        guardian_name = relation_info["name"]
        relation_type = relation_info["relation"]

    result = {
        "card_side": card_side,
        "name": None if card_side == "back" else extract_name(texts),
        "dob": extract_dob(texts),
        "gender": extract_gender(texts),
        "aadhaar_number": extract_aadhaar(texts),
        "vid": extract_vid(texts),
        "relation_type": relation_type,
        "guardian_name": guardian_name,
        "address": extract_address(texts),
        "pincode": extract_pincode(texts),
        "enrollment_no": extract_enrollment_no(texts),
        "issue_date": extract_issue_date(texts),
    }

    return {k: v for k, v in result.items() if v is not None}