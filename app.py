from __future__ import annotations

from datetime import datetime
from typing import Dict, List

from flask import Flask, jsonify, redirect, render_template, request, url_for

app = Flask(__name__)

# In-memory storage for simple school use. Replace with a database for production.
requests_store: List[Dict[str, str]] = []


@app.get("/")
def home():
    recent_requests = list(reversed(requests_store[-10:]))
    return render_template("index.html", recent_requests=recent_requests, now=datetime.now())


@app.post("/submit")
def submit_request():
    student_name = request.form.get("student_name", "").strip()
    song_title = request.form.get("song_title", "").strip()
    artist = request.form.get("artist", "").strip()
    message = request.form.get("message", "").strip()

    if not student_name or not song_title or not artist:
        return redirect(url_for("home"))

    requests_store.append(
        {
            "student_name": student_name,
            "song_title": song_title,
            "artist": artist,
            "message": message,
            "submitted_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
    )
    return redirect(url_for("home"))


@app.get("/health")
def health_check():
    return jsonify({"status": "ok", "requests_count": len(requests_store)})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
