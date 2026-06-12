# Computer Vision Based Attendance Tracking System

Automated attendance using real-time facial recognition with OpenCV and `face_recognition`.

## Setup

```bash
pip install opencv-python face_recognition numpy
```

> **macOS / Linux**: `face_recognition` requires `dlib`. Install with `pip install dlib` (needs CMake).

### Add known faces

```
known_faces/
├── Alice_Smith/
│   ├── photo1.jpg
│   └── photo2.jpg
└── Bob_Jones/
    └── photo1.jpg
```

Each subfolder name becomes the person's displayed name and attendance label.

## Usage

**Live webcam:**
```bash
python attendance.py
```

**Test with a video file:**
```python
run_attendance_system(source="test_video.mp4")
```

**Print attendance report:**
```bash
python attendance.py report
```

## Output

`attendance_log.csv` — one row per person per day:

```
Alice_Smith,2024-11-01,09:03:15
Bob_Jones,2024-11-01,09:05:42
```

## Key Features

- Processes every 3rd frame (25× speed-up) with ¼-resolution downscaling
- Duplicate suppression: each person logged once per day
- Confidence threshold (0.5) with fallback to "Unknown"
- Edge-case handling for low lighting and partial faces
- Colour-coded bounding boxes (green = recognised, red = unknown)
