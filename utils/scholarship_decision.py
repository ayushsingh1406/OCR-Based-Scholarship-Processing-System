import json
import re
from difflib import SequenceMatcher
from typing import Dict, Any, List, Optional
from utils.document_classifier import DocumentType

class ScholarshipDecisionEngine:
    def __init__(self, income_ceiling: int = 1200000, marks_floor: float = 50.0, max_scholarship: int = 100000):
        self.income_ceiling = income_ceiling
        self.marks_floor = marks_floor
        self.max_scholarship = max_scholarship

    def _get_similarity(self, s1: str, s2: str) -> float:
        """Calculate fuzzy string similarity between two strings."""
        if not s1 or not s2:
            return 0.0
        s1, s2 = s1.lower().strip(), s2.lower().strip()
        # Remove common prefixes/titles
        for title in ["mr.", "mrs.", "ms.", "smt.", "shri", "sh.", "sri"]:
            s1 = s1.replace(title, "").strip()
            s2 = s2.replace(title, "").strip()
        
        # Remove extra spaces
        s1 = re.sub(r'\s+', '', s1)
        s2 = re.sub(r'\s+', '', s2)
        
        return SequenceMatcher(None, s1, s2).ratio()

    def analyze(self, results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze all document results and make a scholarship decision.
        """
        # 1. Distribute results by document type
        id_doc = None
        marksheet_doc = None
        income_doc = None

        for name, data in results.items():
            doc_type = data.get("document_type")
            if doc_type in [DocumentType.AADHAAR, DocumentType.PAN]:
                # If multiple IDs, prioritize Aadhaar or the first one
                if not id_doc or doc_type == DocumentType.AADHAAR:
                    id_doc = data
            elif doc_type == DocumentType.MARKSHEET:
                marksheet_doc = data
            elif doc_type == DocumentType.INCOME:
                income_doc = data

        # 2. Extract Key Metrics
        income_val = 0
        percentage_val = 0.0
        
        if income_doc and "annual_income" in income_doc:
            income_str = re.sub(r'[^\d]', '', str(income_doc["annual_income"]))
            income_val = int(income_str) if income_str else 0
            
        if marksheet_doc and "percentage" in marksheet_doc:
            pct_str = re.sub(r'[^\d.]', '', str(marksheet_doc["percentage"]))
            percentage_val = float(pct_str) if pct_str else 0.0

        # 3. Consistency Checks (Fuzzy Matching)
        reasons = []
        consistency_scores = []
        
        # Student Name Match (ID vs Marksheet)
        if id_doc and marksheet_doc:
            student_id_name = id_doc.get("name")
            student_ms_name = marksheet_doc.get("student_name")
            sim = self._get_similarity(student_id_name, student_ms_name)
            consistency_scores.append(sim)
            if sim < 0.8:
                reasons.append(f"Student name variation across documents (Similarity: {int(sim*100)}%)")

        # Parent/Guardian Match (Marksheet vs Income or ID)
        if marksheet_doc and income_doc:
            ms_father = marksheet_doc.get("father_name")
            inc_applicant = income_doc.get("applicant_name")
            inc_father = income_doc.get("father_husband_name")
            
            # Check if income applicant is the father or the student
            sim_father = max(self._get_similarity(ms_father, inc_applicant), 
                             self._get_similarity(ms_father, inc_father))
            consistency_scores.append(sim_father)
            if sim_father < 0.7:
                reasons.append(f"Parental name variation between Marksheet and Income Cert (Similarity: {int(sim_father*100)}%)")

        # 4. Authenticity Validation (Watermarks)
        docs = [id_doc, marksheet_doc, income_doc]
        missing_watermarks = False
        for doc in docs:
            if doc:
                wm = doc.get("watermark_detection", {})
                # Require ashoka_emblem as baseline authenticity
                if not wm.get("ashoka_emblem", False):
                    missing_watermarks = True
                    reasons.append(f"Authenticity warning: Ashoka Emblem not clearly detected in {doc.get('document_type')}")

        # 5. Determine Scholarship Amount (Dynamic)
        # academic_score = max(0, (percentage - 50) / 50) -> 0 to 1
        academic_score = max(0.0, (percentage_val - self.marks_floor) / (100.0 - self.marks_floor)) if percentage_val >= self.marks_floor else 0.0
        # need_score = max(0, (ceiling - income) / ceiling) -> 0 to 1
        need_score = max(0.0, (self.income_ceiling - income_val) / self.income_ceiling) if income_val <= self.income_ceiling else 0.0
        
        # Priority to Needy (70% weight)
        combined_score = (0.3 * academic_score) + (0.7 * need_score)
        scholarship_amount = int(combined_score * self.max_scholarship)

        # 6. Final Status Logic
        status = "APPROVED"
        
        # Calculate consistency metrics
        avg_consistency = sum(consistency_scores) / len(consistency_scores) if consistency_scores else 0.0
        
        # Rejection Criteria (Strict)
        if income_val > self.income_ceiling:
            status = "NOT APPROVED"
            reasons.append(f"Annual income (₹{income_val:,}) exceeds ceiling of ₹{self.income_ceiling:,}")
        elif percentage_val < self.marks_floor:
            status = "NOT APPROVED"
            reasons.append(f"Percentage ({percentage_val}%) is below minimum required {self.marks_floor}%")
        elif not id_doc or not marksheet_doc or not income_doc:
            status = "NOT APPROVED"
            reasons.append("Critical document missing (ID, Marksheet, or Income Certificate)")
        elif avg_consistency < 0.5:
            status = "NOT APPROVED"
            reasons.append(f"Major data inconsistency ({int(avg_consistency*100)}%) detected between documents")
        
        # Manual Inspection Criteria
        if status == "APPROVED":
            if avg_consistency < 0.75:
                status = "MANUAL"
                reasons.append(f"Moderate data inconsistency ({int(avg_consistency*100)}%) requires human verification")
            elif missing_watermarks:
                status = "MANUAL"
            elif income_val > 1000000 and percentage_val < 75:
                # High income + Average marks = Manual Review
                status = "MANUAL"
                reasons.append("High income bracket requires secondary verification for average academic scores")

        if not reasons:
            reasons.append("Application meets all standard criteria for the selected bracket")

        decision = {
            "status": status,
            "scholarship_amount": scholarship_amount if status == "APPROVED" else 0,
            "analysis": {
                "academic_performance": f"{percentage_val}%",
                "annual_income": f"₹{income_val:,}",
                "data_consistency": f"{int(sum(consistency_scores)/len(consistency_scores)*100)}%" if consistency_scores else "N/A",
                "authenticity_check": "FAILED" if missing_watermarks else "PASSED"
            },
            "reasons": reasons
        }
        
        return decision
