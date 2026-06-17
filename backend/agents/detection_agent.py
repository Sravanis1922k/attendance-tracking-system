"""Detection Agent — finds face locations in a frame."""
import face_recognition
import numpy as np
import config, logging
logger = logging.getLogger(__name__)

class DetectionAgent:
    def __init__(self):
        self.model = config.DETECTION_MODEL
        self.scale = config.RESIZE_SCALE

    def detect(self, frame: np.ndarray) -> list:
        """Returns list of face locations (top, right, bottom, left) scaled to original size."""
        import cv2
        small = cv2.resize(frame, (0, 0), fx=self.scale, fy=self.scale)
        rgb   = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)
        locations = face_recognition.face_locations(rgb, model=self.model)
        scale_inv = int(1 / self.scale)
        scaled = [(t*scale_inv, r*scale_inv, b*scale_inv, l*scale_inv) for t,r,b,l in locations]
        logger.debug(f"Detected {len(scaled)} faces")
        return scaled

    def get_encodings(self, frame: np.ndarray, locations: list) -> list:
        """Returns face encodings for detected locations."""
        import cv2
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        small_locs = [
            (int(t*self.scale), int(r*self.scale), int(b*self.scale), int(l*self.scale))
            for t,r,b,l in locations
        ]
        import cv2 as _cv2
        small = _cv2.resize(frame, (0,0), fx=self.scale, fy=self.scale)
        rgb_small = _cv2.cvtColor(small, _cv2.COLOR_BGR2RGB)
        return face_recognition.face_encodings(rgb_small, small_locs)
