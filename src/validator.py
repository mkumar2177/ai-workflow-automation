import re

MANDATORY_FIELDS = ["customer_name", "email", "request_type", "message"]
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validate_record(record: dict, seen_ids: set) -> dict:
    """
    Validate a single record.

    Returns a dict:
        {
            "status": "VALID" | "INVALID",
            "errors": [list of error strings]
        }
    """
    errors = []

    # 1. Mandatory field check
    for field in MANDATORY_FIELDS:
        value = record.get(field, "")
        if value is None or str(value).strip() == "":
            errors.append(f"Missing mandatory field: {field}")

    # 2. Email format check
    email = str(record.get("email", "")).strip()
    if email and not EMAIL_PATTERN.match(email):
        errors.append(f"Invalid email format: {email}")

    # 3. Duplicate check
    request_id = record.get("request_id")
    if request_id in seen_ids:
        errors.append(f"Duplicate request_id: {request_id}")

    status = "VALID" if not errors else "INVALID"
    return {"status": status, "errors": errors}


def validate_batch(records: list) -> tuple:
    """
    Validate a list of records.

    Returns (valid_records, invalid_records) where each invalid record
    carries its list of validation errors attached under 'validation_errors'.
    """
    valid_records = []
    invalid_records = []
    seen_ids = set()

    for record in records:
        result = validate_record(record, seen_ids)
        if result["status"] == "VALID":
            valid_records.append(record)
        else:
            record["validation_errors"] = result["errors"]
            invalid_records.append(record)

        # Register the id as seen even if invalid, so a later duplicate
        # of an invalid row is also correctly flagged.
        if record.get("request_id"):
            seen_ids.add(record["request_id"])

    return valid_records, invalid_records
