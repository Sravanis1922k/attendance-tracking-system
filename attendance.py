"""
Computer Vision Based Attendance Tracking System
Stack: Python, OpenCV, face_recognition
"""

import cv2
import face_recognition
import numpy as np
import os
import csv
import logging
from datetime import datetime
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

KNOWN_FACES_DIR = "known_faces"
ATTENDANCE_LOG  = "attendance_log.csv"
CONFIDENCE_THRESHOLD = 0.5   # lower = stricter


# ---------------------------------------------------------------------------
# 1. Load known faces
# ---------------------------------------------------------------------------

def load_known_faces(faces_dir: str = KNOWN_FACES_DIR):
    encodings, names = [], []
    for person_dir in Path(faces_dir).iterdir():
        if not person_dir.is_dir():
            continue
        for img_path in person_dir.glob("*.jpg"):
            img = face_recognition.load_image_file(str(img_path))
            enc_list = face_recognition.face_encodings(img)
            if enc_list:
                encodings.append(enc_list[0])
                names.append(person_dir.name)
    logger.info(f"Loaded {len(encodings)} face encodings for {len(set(names))} people")
    return encodings, names


# ---------------------------------------------------------------------------
# 2. Recognition helpers
# ---------------------------------------------------------------------------

def identify_face(face_encoding, known_encodings, known_names) -> tuple[str, float]:
    """Return (name, confidence) for a detected face encoding."""
    if not known_encodings:
        return "Unknown", 0.0
    distances = face_recognition.face_distance(known_encodings, face_encoding)
    best_idx  = int(np.argmin(distances))
    confidence = 1 - float(distances[best_idx])
    if confidence >= CONFIDENCE_THRESHOLD:
        return known_names[best_idx], confidence
    return "Unknown", confidence


# ---------------------------------------------------------------------------
# 3. Attendance logging
# ---------------------------------------------------------------------------

def log_attendance(name: str, log_file: str = ATTENDANCE_LOG):
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")

    # avoid duplicate entries on the same day
    existing = set()
    if os.path.exists(log_file):
        with open(log_file, newline="") as f:
            for row in csv.reader(f):
                if row:
                    existing.add((row[0], row[1]))   # (name, date)

    if (name, date_str) not in existing:
        with open(log_file, "a", newline="") as f:
            csv.writer(f).writerow([name, date_str, time_str])
        logger.info(f"Marked attendance: {name} at {time_str}")


# ---------------------------------------------------------------------------
# 4. Real-time recognition loop
# ---------------------------------------------------------------------------

def run_attendance_system(source=0):
    """
    source: 0 = default webcam, or path to video file for testing.
    Press 'q' to quit.
    """
    known_encodings, known_names = load_known_faces()
    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        logger.error("Cannot open video source")
        return

    frame_count = 0
    PROCESS_EVERY_N = 3   # skip frames for performance

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        display = frame.copy()

        if frame_count % PROCESS_EVERY_N == 0:
            small = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb   = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)

            locations  = face_recognition.face_locations(rgb, model="hog")
            encodings  = face_recognition.face_encodings(rgb, locations)

            for (top, right, bottom, left), enc in zip(locations, encodings):
                # scale back to original frame size
                top, right, bottom, left = top*4, right*4, bottom*4, left*4

                name, conf = identify_face(enc, known_encodings, known_names)

                color = (0, 200, 0) if name != "Unknown" else (0, 0, 200)
                cv2.rectangle(display, (left, top), (right, bottom), color, 2)
                label = f"{name} ({conf:.2f})"
                cv2.rectangle(display, (left, bottom-28), (right, bottom), color, cv2.FILLED)
                cv2.putText(display, label, (left+4, bottom-6),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

                if name != "Unknown":
                    log_attendance(name)

        cv2.imshow("Attendance System  [q = quit]", display)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
    logger.info(f"Attendance log saved to {ATTENDANCE_LOG}")


# ---------------------------------------------------------------------------
# 5. CLI helpers
# ---------------------------------------------------------------------------

def print_report(log_file: str = ATTENDANCE_LOG):
    if not os.path.exists(log_file):
        print("No attendance log found.")
        return
    with open(log_file) as f:
        rows = list(csv.reader(f))
    print(f"\n{'Name':<25} {'Date':<12} {'Time'}")
    print("-" * 50)
    for row in rows:
        if row:
            print(f"{row[0]:<25} {row[1]:<12} {row[2]}")
    print(f"\nTotal entries: {len(rows)}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "report":
        print_report()
    else:
        run_attendance_system()
