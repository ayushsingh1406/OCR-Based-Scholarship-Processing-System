"""
Refactored Aadhaar Parser
- Same logic, improved readability and modularity
- Centralized utilities
- Reduced repetition
"""

import re
from typing import Optional, List, Dict

# ======================================================
# Common Utilities
# ======================================================

def extract_digits(text: str) -> str:
    return re.sub(r"\D", "", text)


def normalize_text(text: str) -> str:
    return text.strip()


def is_noise(text: str) -> bool:
    if len(text) < 3:
        return True
    if re.search(r"[^a-zA-Z0-9\s/:-]", text):
        return True
    return False


# ======================================================
# Aadhaar Number Extraction
# ======================================================

def extract_aadhaar(texts: List[str]) -> Optional[str]:
    vid_indices = set()
    for i, t in enumerate(texts):
        if 'vid' in t.lower():
            vid_indices.update(range(i, min(len(texts), i + 5)))

    # Single line direct match
    for i, t in enumerate(texts):
        if i in vid_indices:
            continue
        digits = extract_digits(t)
        if len(digits) == 12:
            return format_aadhaar(digits)

    # Multi-line assembly (4-4-4)
    groups = []
    for i, t in enumerate(texts):
        if i in vid_indices:
            continue
        digits = extract_digits(t)
        if len(digits) == 4:
            groups.append((i, digits))

    for i in range(len(groups) - 2):
        i0, d0 = groups[i]
        i1, d1 = groups[i+1]
        i2, d2 = groups[i+2]
        if i1 - i0 <= 3 and i2 - i1 <= 3:
            return format_aadhaar(d0 + d1 + d2)

    return None


def format_aadhaar(d: str) -> str:
    return f"{d[:4]} {d[4:8]} {d[8:12]}"


# ======================================================
# VID
# ======================================================

def extract_vid(texts: List[str]) -> Optional[str]:
    for i, t in enumerate(texts):
        if 'vid' in t.lower():
            digits = extract_digits(t)
            for j in range(i+1, min(len(texts), i+4)):
                digits += extract_digits(texts[j])
                if len(digits) >= 16:
                    d = digits[:16]
                    return f"{d[:4]} {d[4:8]} {d[8:12]} {d[12:16]}"
    return None


# ======================================================
# DOB
# ======================================================

def extract_dob(texts: List[str]) -> Optional[str]:
    pattern = r"(\d{2})[/\-.](\d{2})[/\-.](\d{4})"

    for t in texts:
        if any(k in t.upper() for k in ["DOB", "BIRTH"]):
            m = re.search(pattern, t)
            if m:
                return f"{m.group(1)}/{m.group(2)}/{m.group(3)}"

    for t in texts:
        m = re.search(pattern, t)
        if m:
            return f"{m.group(1)}/{m.group(2)}/{m.group(3)}"

    return None


# ======================================================
# Gender
# ======================================================

def extract_gender(texts: List[str]) -> Optional[str]:
    for t in texts:
        t = t.lower()
        if "female" in t:
            return "Female"
        if "male" in t:
            return "Male"
    return None


# ======================================================
# Name
# ======================================================

BLACKLIST = {"aadhaar", "government", "india", "uidai", "dob", "male", "female"}


def is_valid_name(word: str) -> bool:
    return word.isalpha() and word.lower() not in BLACKLIST and word[0].isupper()


def extract_name(texts: List[str]) -> Optional[str]:
    candidates = []

    for t in texts:
        t = normalize_text(t)
        if is_noise(t):
            continue

        words = t.split()
        if 1 <= len(words) <= 3 and all(is_valid_name(w) for w in words):
            candidates.append(" ".join(words))

    return candidates[0] if candidates else None


# ======================================================
# Relation
# ======================================================

def extract_relation_name(texts: List[str]) -> Optional[Dict]:
    pattern = r"([SDWC])/O\s*[:\-]?\s*([A-Za-z\s]+)"

    for t in texts:
        m = re.search(pattern, t, re.IGNORECASE)
        if m:
            return {
                "relation": m.group(1).upper() + "/O",
                "name": m.group(2).strip().title()
            }
    return None


# ======================================================
# Address
# ======================================================

def extract_address(texts: List[str]) -> Optional[str]:
    collecting = False
    lines = []

    for t in texts:
        t_clean = normalize_text(t)

        if "address" in t_clean.lower():
            collecting = True
            continue

        if collecting:
            if len(t_clean) < 3:
                break
            lines.append(t_clean)

    if lines:
        return " ".join(lines)

    return None


# ======================================================
# Pincode
# ======================================================

def extract_pincode(texts: List[str]) -> Optional[str]:
    for t in texts:
        m = re.search(r"\b\d{6}\b", t)
        if m:
            return m.group(0)
    return None


# ======================================================
# Master Function
# ======================================================

def extract_all_fields(texts: List[str]) -> Dict:
    relation = extract_relation_name(texts)

    result = {
        "name": extract_name(texts),
        "dob": extract_dob(texts),
        "gender": extract_gender(texts),
        "aadhaar_number": extract_aadhaar(texts),
        "vid": extract_vid(texts),
        "guardian_name": relation["name"] if relation else None,
        "relation_type": relation["relation"] if relation else None,
        "address": extract_address(texts),
        "pincode": extract_pincode(texts),
    }

    return {k: v for k, v in result.items() if v is not None}
