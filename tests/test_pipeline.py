"""
test_pipeline.py
Small test script covering the main validation/classification scenarios.
Run with: python tests/test_pipeline.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from validator import validate_record
from classifier import classify_priority
from ai_summary import generate_summary

results = []


def check(test_id, description, condition):
    status = "PASS" if condition else "FAIL"
    results.append((test_id, description, status))
    print(f"{test_id}: {status} - {description}")


# TC-01 Valid input
r = {"request_id": "T1", "customer_name": "A", "email": "a@example.com",
     "request_type": "Billing", "message": "refund please"}
res = validate_record(r, set())
check("TC-01", "Valid input is accepted", res["status"] == "VALID")

# TC-02 Missing field
r2 = {"request_id": "T2", "customer_name": "A", "email": "a@example.com",
      "request_type": "Billing", "message": ""}
res2 = validate_record(r2, set())
check("TC-02", "Missing message field is rejected", res2["status"] == "INVALID")

# TC-03 Invalid email format
r3 = {"request_id": "T3", "customer_name": "A", "email": "not-an-email",
      "request_type": "General", "message": "hi"}
res3 = validate_record(r3, set())
check("TC-03", "Invalid email format is rejected", "Invalid email format" in str(res3["errors"]))

# TC-04 Duplicate record
seen = {"T1"}
r4 = {"request_id": "T1", "customer_name": "A", "email": "a@example.com",
      "request_type": "Billing", "message": "refund"}
res4 = validate_record(r4, seen)
check("TC-04", "Duplicate request_id is rejected", res4["status"] == "INVALID")

# TC-05 Empty input record
r5 = {}
res5 = validate_record(r5, set())
check("TC-05", "Empty record is rejected", res5["status"] == "INVALID")

# TC-06 Priority classification - refund keyword -> High
r6 = {"request_type": "Billing", "message": "Refund not received"}
check("TC-06", "Refund keyword classified as High priority", classify_priority(r6) == "High")

# TC-07 AI summary - DEMO fallback works without API key
stats = {"total_valid": 5, "priority_counts": {"High": 2}, "type_counts": {"Billing": 2}}
ai_res = generate_summary(stats)
check("TC-07", "AI summary falls back to DEMO mode without API key", ai_res["mode"] == "DEMO")

passed = sum(1 for _, _, s in results if s == "PASS")
print(f"\n{passed}/{len(results)} test cases passed.")
