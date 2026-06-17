# docs — Sample Attendance Reports

This folder contains sample attendance reports and documentation for FACE-TRACK.

## Sample CSV Report

Here is an example of what the attendance log looks like:

```
name,date,time,confidence
Alice_Smith,2024-11-01,09:03:15,0.92
Bob_Jones,2024-11-01,09:05:42,0.87
Alice_Smith,2024-11-02,08:58:30,0.95
Carol_White,2024-11-02,09:10:05,0.88
Bob_Jones,2024-11-02,09:12:18,0.91
```

## Fields Explained

| Field | Description |
|---|---|
| `name` | Person's name (matches their folder in `known_faces/`) |
| `date` | Date of attendance in `YYYY-MM-DD` format |
| `time` | Time of recognition in `HH:MM:SS` format |
| `confidence` | Match confidence score (0.0 – 1.0, higher = more certain) |

## Downloading Reports

You can download the full attendance log as a CSV anytime from the Streamlit dashboard:
1. Open http://localhost:8501
2. Go to the **Attendance Report** tab
3. Click **⬇️ Download CSV**

## API Access

You can also fetch reports directly from the API:

```bash
# Get all records
curl http://localhost:8000/report

# Get records for a specific date
curl http://localhost:8000/report?date=2024-11-01

# Download CSV
curl http://localhost:8000/report/download -o attendance_log.csv
```
# docs — Sample Attendance Reports

This folder contains sample attendance reports and documentation for FACE-TRACK.

## Sample CSV Report

Here is an example of what the attendance log looks like:

```
name,date,time,confidence
Alice_Smith,2024-11-01,09:03:15,0.92
Bob_Jones,2024-11-01,09:05:42,0.87
Alice_Smith,2024-11-02,08:58:30,0.95
Carol_White,2024-11-02,09:10:05,0.88
Bob_Jones,2024-11-02,09:12:18,0.91
```

## Fields Explained

| Field | Description |
|---|---|
| `name` | Person's name (matches their folder in `known_faces/`) |
| `date` | Date of attendance in `YYYY-MM-DD` format |
| `time` | Time of recognition in `HH:MM:SS` format |
| `confidence` | Match confidence score (0.0 – 1.0, higher = more certain) |

## Downloading Reports

You can download the full attendance log as a CSV anytime from the Streamlit dashboard:
1. Open http://localhost:8501
2. Go to the **Attendance Report** tab
3. Click **⬇️ Download CSV**

## API Access

You can also fetch reports directly from the API:

```bash
# Get all records
curl http://localhost:8000/report

# Get records for a specific date
curl http://localhost:8000/report?date=2024-11-01

# Download CSV
curl http://localhost:8000/report/download -o attendance_log.csv
```
