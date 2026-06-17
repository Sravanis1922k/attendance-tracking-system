"""Recognition Agent — matches detected faces to known people."""
import face_recognition
import numpy as np
from pathlib import Path
import config, logging
logger = logging.getLogger(__name__)

class RecognitionAgent:
    def __init__(self, known_faces_dir: str):
        self.dir = known_faces_dir
        self.encodings = []
        self.names = []
        self.load()

    def load(self):
        self.encodings, self.names = [], []
        for person_dir in Path(self.dir).iterdir():
            if not person_dir.is_dir(): continue
            for img_path in person_dir.glob("*.jpg"):
                img = face_recognition.load_image_file(str(img_path))
                encs = face_recognition.face_encodings(img)
                if encs:
                    self.encodings.append(encs[0])
                    self.names.append(person_dir.name)
            for img_path in person_dir.glob("*.png"):
                img = face_recognition.load_image_file(str(img_path))
                encs = face_recognition.face_encodings(img)
                if encs:
                    self.encodings.append(encs[0])
                    self.names.append(person_dir.name)
        logger.info(f"Loaded {len(self.encodings)} encodings for {len(set(self.names))} people")

    def reload(self):
        self.load()

    def get_count(self):
        return len(set(self.names))

    def identify(self, encoding) -> tuple[str, float]:
        if not self.encodings:
            return "Unknown", 0.0
        distances = face_recognition.face_distance(self.encodings, encoding)
        best = int(np.argmin(distances))
        confidence = round(1 - float(distances[best]), 3)
        if confidence >= config.CONFIDENCE_THRESHOLD:
            return self.names[best], confidence
        return "Unknown", confidence
