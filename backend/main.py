"""
FACE-TRACK — Computer Vision Attendance System
FastAPI Backend — /register, /attendance/start, /attendance/stop, /report, /health
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import shutil, logging, csv, io
from pathlib import Path
from datetime import datetime

from agents.detection_agent import DetectionAgent
from agents.recognition_agent import RecognitionAgent
from agents.logging_agent import LoggingAgent

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="FACE-TRACK — Attendance System", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

KNOWN_FACES_DIR = Path("known_faces")
KNOWN_FACES_DIR.mkdir(exist_ok=True)

detection   = DetectionAgent()
recognition = RecognitionAgent(known_faces_dir=str(KNOWN_FACES_DIR))
logging_agent = LoggingAgent()

class AttendanceRecord(BaseModel):
    name: str
    date: str
    time: str
    confidence: float

@app.get("/health")
def health():
    return {"status": "ok", "version": "1.0.0", "registered_people": recognition.get_count()}

@app.post("/register")
async def register_person(name: str, file: UploadFile = File(...)):
    """Register a new person by uploading their photo."""
    allowed = {".jpg", ".jpeg", ".png"}
    ext = Path(file.filename).suffix.lower()
    if ext not in allowed:
        raise HTTPException(400, f"File type {ext} not supported. Use: jpg, jpeg, png")
    person_dir = KNOWN_FACES_DIR / name
    person_dir.mkdir(exist_ok=True)
    dest = person_dir / file.filename
    with open(dest, "wb") as f:
        shutil.copyfileobj(file.file, f)
    recognition.reload()
    logger.info(f"Registered: {name} with photo {file.filename}")
    return {"status": "registered", "name": name, "photo": file.filename}

@app.get("/registered")
def list_registered():
    """List all registered people."""
    people = [d.name for d in KNOWN_FACES_DIR.iterdir() if d.is_dir()]
    return {"people": people, "count": len(people)}

@app.get("/report")
def get_report(date: Optional[str] = None):
    """Get attendance report, optionally filtered by date."""
    records = logging_agent.get_records(date=date)
    return {"records": records, "count": len(records), "date": date or "all"}

@app.get("/report/download")
def download_report():
    """Download attendance log as CSV."""
    records = logging_agent.get_records()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Name", "Date", "Time", "Confidence"])
    for r in records:
        writer.writerow([r["name"], r["date"], r["time"], r["confidence"]])
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=attendance_log.csv"}
    )

@app.post("/mark")
def mark_attendance(record: AttendanceRecord):
    """Manually mark attendance (called by recognition pipeline)."""
    result = logging_agent.log(record.name, record.confidence)
    return result

@app.delete("/report/clear")
def clear_report():
    """Clear all attendance records."""
    logging_agent.clear()
    return {"status": "cleared"}
