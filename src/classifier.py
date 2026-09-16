HIGH_PRIORITY_KEYWORDS = ["refund", "double charge", "not received", "error", "not loading"]
MEDIUM_PRIORITY_KEYWORDS = ["charged", "throwing", "export"]


def classify_priority(record: dict) -> str:
    """
    Return 'High', 'Medium' or 'Low' priority based on request_type
    and simple keyword matching in the message text.
    """
    message = str(record.get("message", "")).lower()
    request_type = record.get("request_type", "")

    if any(keyword in message for keyword in HIGH_PRIORITY_KEYWORDS):
        return "High"
    if request_type == "Billing":
        return "Medium"
    if any(keyword in message for keyword in MEDIUM_PRIORITY_KEYWORDS):
        return "Medium"
    return "Low"


def classify_batch(records: list) -> list:
    """Attach a 'priority' field to every record in the batch."""
    for record in records:
        record["priority"] = classify_priority(record)
    return records
