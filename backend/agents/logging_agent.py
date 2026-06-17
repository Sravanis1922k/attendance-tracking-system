"""Logging Agent — records attendance with duplicate suppression."""
import csv, os, logging
from datetime import datetime
from pathlib import Path
import config

logger = logging.getLogger(__name__)
LOG_FILE = config.ATTENDANCE_LOG

class LoggingAgent:
    def __init__(self):
        self._marked_today: set = set()
        self._init_file()

    def _init_file(self):
        if not os.path.exists(LOG_FILE):
            with open(LOG_FILE, "w", newline="") as f:
                csv.writer(f).writerow(["name","date","time","confidence"])

    def log(self, name: str, confidence: float = 1.0) -> dict:
        now  = datetime.now()
        date = now.strftime("%Y-%m-%d")
        time = now.strftime("%H:%M:%S")
        key  = (name, date)
        if key in self._marked_today:
            return {"status": "already_marked", "name": name, "date": date}
        with open(LOG_FILE, "a", newline="") as f:
            csv.writer(f).writerow([name, date, time, round(confidence, 3)])
        self._marked_today.add(key)
        logger.info(f"Marked: {name} at {time} (conf={confidence:.3f})")
        return {"status": "marked", "name": name, "date": date, "time": time}

    def get_records(self, date: str = None) -> list[dict]:
        if not os.path.exists(LOG_FILE): return []
        records = []
        with open(LOG_FILE, newline="") as f:
            for row in csv.DictReader(f):
                if date and row.get("date") != date: continue
                records.append(row)
        return records

    def clear(self):
        self._marked_today.clear()
        with open(LOG_FILE, "w", newline="") as f:
            csv.writer(f).writerow(["name","date","time","confidence"])
