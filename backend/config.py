import os
from dotenv import load_dotenv
load_dotenv()

KNOWN_FACES_DIR     = os.getenv("KNOWN_FACES_DIR", "known_faces")
ATTENDANCE_LOG      = os.getenv("ATTENDANCE_LOG", "attendance_log.csv")
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.5"))
FRAME_SKIP          = int(os.getenv("FRAME_SKIP", "3"))
RESIZE_SCALE        = float(os.getenv("RESIZE_SCALE", "0.25"))
MAX_FACES_PER_FRAME = int(os.getenv("MAX_FACES_PER_FRAME", "10"))
DETECTION_MODEL     = os.getenv("DETECTION_MODEL", "hog")   # hog | cnn
CAMERA_SOURCE       = int(os.getenv("CAMERA_SOURCE", "0"))
