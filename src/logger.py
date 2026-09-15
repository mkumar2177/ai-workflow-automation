"""
logger.py
Minimal structured execution logger — writes timestamped events to a
log file so a failed or partial run can be traced later.
"""

import datetime
from pathlib import Path


class RunLogger:
    def __init__(self, log_path: str):
        self.log_path = log_path
        Path(log_path).parent.mkdir(parents=True, exist_ok=True)
        # Start each run with a clear separator
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(f"\n===== RUN START: {self._now()} =====\n")

    def _now(self):
        return datetime.datetime.now().isoformat(timespec="seconds")

    def log(self, level: str, message: str):
        line = f"[{self._now()}] [{level}] {message}"
        print(line)
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(line + "\n")

    def info(self, message):
        self.log("INFO", message)

    def warning(self, message):
        self.log("WARNING", message)

    def error(self, message):
        self.log("ERROR", message)
