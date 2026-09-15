"""
data_processor.py
Reads the raw input CSV, cleans it, and hands valid records forward
for classification and reporting.
"""

import csv
from pathlib import Path


def read_input(file_path: str) -> list:
    """Read the raw CSV file into a list of dictionaries."""
    records = []
    with open(file_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(dict(row))
    return records


def clean_record(record: dict) -> dict:
    """
    Basic cleaning on a single record:
        - Strip leading/trailing whitespace on all string fields
        - Normalise request_type casing
        - Fill a missing customer_name with 'Unknown Customer'
    """
    cleaned = {}
    for key, value in record.items():
        if isinstance(value, str):
            cleaned[key] = value.strip()
        else:
            cleaned[key] = value

    if not cleaned.get("customer_name"):
        cleaned["customer_name"] = "Unknown Customer"

    if cleaned.get("request_type"):
        cleaned["request_type"] = cleaned["request_type"].strip().title()

    return cleaned


def clean_batch(records: list) -> list:
    """Apply clean_record() to every record in the batch."""
    return [clean_record(r) for r in records]


def write_processed_csv(records: list, output_path: str) -> None:
    """Write a list of dictionaries to a CSV file, creating folders if needed."""
    if not records:
        return
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(records[0].keys())
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)
