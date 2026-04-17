"""
Parsers for different document types.
"""
from .aadhaar import extract_all_fields as parse_aadhaar
from .pan import parse_pan
from .marksheet import parse_marksheet
from .income import parse_income

__all__ = ["parse_aadhaar", "parse_pan", "parse_marksheet", "parse_income"]
