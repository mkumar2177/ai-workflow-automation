import csv
from collections import Counter
from pathlib import Path


def build_stats(valid_records: list, invalid_records: list) -> dict:
    """Compute summary statistics for the batch."""
    type_counts = Counter(r.get("request_type", "Unknown") for r in valid_records)
    priority_counts = Counter(r.get("priority", "Unknown") for r in valid_records)

    return {
        "total_received": len(valid_records) + len(invalid_records),
        "total_valid": len(valid_records),
        "total_invalid": len(invalid_records),
        "type_counts": dict(type_counts),
        "priority_counts": dict(priority_counts),
    }


def write_summary_report(valid_records: list, stats: dict, ai_summary: dict, output_path: str) -> None:
    """Write the final processed report as a CSV file (request-level + summary)."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["request_id", "customer_name", "request_type", "priority", "date_received"])
        for r in valid_records:
            writer.writerow([
                r.get("request_id"), r.get("customer_name"),
                r.get("request_type"), r.get("priority"), r.get("date_received"),
            ])

        writer.writerow([])
        writer.writerow(["--- BATCH SUMMARY ---"])
        writer.writerow(["Total received", stats["total_received"]])
        writer.writerow(["Total valid", stats["total_valid"]])
        writer.writerow(["Total invalid", stats["total_invalid"]])
        for t, c in stats["type_counts"].items():
            writer.writerow([f"Type: {t}", c])
        for p, c in stats["priority_counts"].items():
            writer.writerow([f"Priority: {p}", c])

        writer.writerow([])
        writer.writerow(["AI Summary", f"({ai_summary['mode']})"])
        writer.writerow([ai_summary["summary"]])
