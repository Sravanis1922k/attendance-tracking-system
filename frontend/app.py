"""
FACE-TRACK — Streamlit Frontend
Live camera feed + attendance dashboard
"""
import streamlit as st
import requests
import cv2
import face_recognition
import numpy as np
from datetime import datetime
import pandas as pd
import time

API = "http://localhost:8000"

st.set_page_config(page_title="FACE-TRACK", page_icon="👁️", layout="wide")

st.markdown("""
<style>
.main-title  { font-size:2rem; font-weight:700; color:#0F6E56; }
.sub-title   { color:#666; font-size:0.95rem; margin-top:-8px; margin-bottom:20px; }
.stat-box    { background:#fff; border:1px solid #e0e0e0; border-radius:10px;
               padding:1.2rem; text-align:center; }
.stat-num    { font-size:2rem; font-weight:700; color:#0F6E56; }
.stat-label  { font-size:12px; color:#888; margin-top:4px; }
.marked-pill { background:#e1f5ee; color:#0F6E56; border-radius:20px;
               padding:3px 12px; font-size:12px; display:inline-block; margin:3px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">👁️ FACE-TRACK</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Computer Vision Attendance System</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("📋 Register Person")
    reg_name = st.text_input("Full Name")
    reg_photo = st.file_uploader("Upload Photo", type=["jpg","jpeg","png"])
    if st.button("Register") and reg_name and reg_photo:
        res = requests.post(f"{API}/register?name={reg_name}",
                            files={"file": (reg_photo.name, reg_photo, reg_photo.type)})
        if res.status_code == 200:
            st.success(f"✅ {reg_name} registered!")
        else:
            st.error("Registration failed")

    st.divider()
    st.header("👥 Registered People")
    try:
        data = requests.get(f"{API}/registered").json()
        st.metric("Total", data["count"])
        for p in data["people"]:
            st.markdown(f'<span class="marked-pill">{p}</span>', unsafe_allow_html=True)
    except:
        st.warning("Backend not reachable")

    st.divider()
    conf_threshold = st.slider("Confidence Threshold", 0.3, 0.9, 0.5, 0.05)

# Tabs
tab1, tab2 = st.tabs(["📷 Live Recognition", "📊 Attendance Report"])

# ── Tab 1: Live Recognition ──────────────────────────────────────────────────
with tab1:
    col1, col2 = st.columns([2, 1])
    with col1:
        run = st.toggle("Start Camera", value=False)
        frame_placeholder = st.empty()
        status_placeholder = st.empty()

    with col2:
        st.subheader("Today's Attendance")
        today_placeholder = st.empty()

    if run:
        try:
            res = requests.get(f"{API}/registered").json()
            if res["count"] == 0:
                st.warning("⚠️ No people registered. Please register faces in the sidebar first.")
                st.stop()
        except:
            st.error("Cannot connect to backend. Is it running?")
            st.stop()

        # Load known faces locally for real-time processing
        import os
        from pathlib import Path
        known_enc, known_names = [], []
        faces_dir = Path("known_faces")

        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            st.error("❌ Cannot open webcam. Check camera connection.")
            st.stop()

        frame_count = 0
        marked_today = set()
        SKIP = 3

        while run:
            ret, frame = cap.read()
            if not ret: break

            frame_count += 1
            display = frame.copy()

            if frame_count % SKIP == 0:
                small = cv2.resize(frame, (0,0), fx=0.25, fy=0.25)
                rgb   = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)
                locs  = face_recognition.face_locations(rgb, model="hog")
                encs  = face_recognition.face_encodings(rgb, locs)

                for (top,right,bottom,left), enc in zip(locs, encs):
                    top,right,bottom,left = top*4,right*4,bottom*4,left*4
                    name, conf = "Unknown", 0.0
                    if known_enc:
                        dists = face_recognition.face_distance(known_enc, enc)
                        idx   = int(np.argmin(dists))
                        conf  = round(1 - float(dists[idx]), 3)
                        if conf >= conf_threshold:
                            name = known_names[idx]

                    color = (0,180,90) if name != "Unknown" else (0,0,200)
                    cv2.rectangle(display, (left,top), (right,bottom), color, 2)
                    label = f"{name} ({conf:.2f})"
                    cv2.rectangle(display, (left,bottom-28),(right,bottom), color, cv2.FILLED)
                    cv2.putText(display, label, (left+4,bottom-6),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255,255,255), 1)

                    if name != "Unknown" and name not in marked_today:
                        requests.post(f"{API}/mark", json={
                            "name": name, "date": datetime.now().strftime("%Y-%m-%d"),
                            "time": datetime.now().strftime("%H:%M:%S"), "confidence": conf
                        })
                        marked_today.add(name)

            frame_rgb = cv2.cvtColor(display, cv2.COLOR_BGR2RGB)
            frame_placeholder.image(frame_rgb, channels="RGB", use_column_width=True)

            # Update today's list
            marked_html = "".join([f'<span class="marked-pill">✅ {n}</span>' for n in marked_today])
            today_placeholder.markdown(marked_html or "No attendance marked yet", unsafe_allow_html=True)

            run = st.session_state.get("Live Recognition", True)

        cap.release()

# ── Tab 2: Attendance Report ─────────────────────────────────────────────────
with tab2:
    col1, col2, col3 = st.columns(3)
    date_filter = col1.date_input("Filter by date", value=None)
    col2.write("")
    if col3.button("🔄 Refresh"):
        st.rerun()

    try:
        params = {"date": str(date_filter)} if date_filter else {}
        data = requests.get(f"{API}/report", params=params).json()
        records = data["records"]

        m1, m2, m3 = st.columns(3)
        m1.markdown(f'<div class="stat-box"><div class="stat-num">{len(records)}</div><div class="stat-label">Total Records</div></div>', unsafe_allow_html=True)
        unique_people = len(set(r["name"] for r in records))
        m2.markdown(f'<div class="stat-box"><div class="stat-num">{unique_people}</div><div class="stat-label">Unique People</div></div>', unsafe_allow_html=True)
        today_count = len([r for r in records if r.get("date") == datetime.now().strftime("%Y-%m-%d")])
        m3.markdown(f'<div class="stat-box"><div class="stat-num">{today_count}</div><div class="stat-label">Present Today</div></div>', unsafe_allow_html=True)

        st.divider()
        if records:
            df = pd.DataFrame(records)
            st.dataframe(df, use_container_width=True, hide_index=True)
            csv_data = requests.get(f"{API}/report/download")
            st.download_button("⬇️ Download CSV", csv_data.content, "attendance_log.csv", "text/csv")
        else:
            st.info("No attendance records found.")
    except Exception as e:
        st.error(f"Cannot fetch report: {e}")
