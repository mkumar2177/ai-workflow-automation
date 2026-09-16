import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from data_processor import read_input, clean_batch, write_processed_csv
from validator import validate_batch
from classifier import classify_batch
from ai_summary import generate_summary
from report_generator import build_stats, write_summary_report
from logger import RunLogger

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_FILE = BASE_DIR / "data" / "input" / "requests.csv"
PROCESSED_FILE = BASE_DIR / "data" / "output" / "processed_valid.csv"
INVALID_FILE = BASE_DIR / "data" / "output" / "rejected_records.csv"
REPORT_FILE = BASE_DIR / "data" / "output" / "summary_report.csv"
LOG_FILE = BASE_DIR / "logs" / "run.log"

# Human-in-the-loop: any AI summary run in DEMO/fallback mode, or any
# batch with High-priority items, is flagged for mandatory human review
# before the report is treated as final.


def run_pipeline():
    logger = RunLogger(str(LOG_FILE))
    logger.info(f"Trigger received. Reading input file: {INPUT_FILE.name}")

    raw_records = read_input(str(INPUT_FILE))
    logger.info(f"Read {len(raw_records)} raw records.")

    cleaned_records = clean_batch(raw_records)
    logger.info("Cleaning complete (whitespace stripped, casing normalised).")

    valid_records, invalid_records = validate_batch(cleaned_records)
    logger.info(f"Validation complete: {len(valid_records)} valid, {len(invalid_records)} invalid.")
    for rec in invalid_records:
        logger.warning(f"Rejected {rec.get('request_id')}: {rec.get('validation_errors')}")

    valid_records = classify_batch(valid_records)
    logger.info("Priority classification complete.")

    write_processed_csv(valid_records, str(PROCESSED_FILE))
    write_processed_csv(invalid_records, str(INVALID_FILE))
    logger.info(f"Processed data written to {PROCESSED_FILE.name} and {INVALID_FILE.name}.")

    stats = build_stats(valid_records, invalid_records)
    ai_result = generate_summary(stats)
    logger.info(f"AI summary generated in {ai_result['mode']} mode.")

    needs_review = ai_result["mode"] != "LIVE" or stats["priority_counts"].get("High", 0) > 0
    if needs_review:
        logger.warning("HUMAN REVIEW REQUIRED before this report is treated as final "
                        "(DEMO-mode summary and/or High-priority items present).")
    else:
        logger.info("No High-priority items and summary generated live — routine review only.")

    write_summary_report(valid_records, stats, ai_result, str(REPORT_FILE))
    logger.info(f"Final report written to {REPORT_FILE.name}.")
    logger.info("Run complete.")

    return stats, ai_result


if __name__ == "__main__":
    run_pipeline()
