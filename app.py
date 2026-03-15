from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from zoneinfo import ZoneInfo

from flask import Flask, g, jsonify, redirect, render_template, request, session, url_for

app = Flask(__name__)
app.secret_key = "song-request-secret-key-change-this"
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "song_requests.db"
KST = ZoneInfo("Asia/Seoul")

ADMIN_USERS: Dict[str, Dict[str, str]] = {
    "sentimentaleunjun": {"password": "A292513a!!", "role": "감성은준(관리자)"},
    "vicepresident23": {"password": "A292513a!!", "role": "키큰민서(관리자)"},
    "teacher23": {"password": "A292513a!!", "role": "선생님(관리자)"},
    "president23": {"password": "A292513a!!", "role": "지우지우(관리자)"},
}


def now_kst() -> datetime:
    return datetime.now(KST)


def get_db() -> sqlite3.Connection:
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_: Optional[BaseException] = None) -> None:
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db() -> None:
    db = sqlite3.connect(DB_PATH)
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS song_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT NOT NULL,
            song_title TEXT NOT NULL,
            artist TEXT NOT NULL,
            message TEXT NOT NULL DEFAULT '',
            selected INTEGER NOT NULL DEFAULT 0,
            submitted_at TEXT NOT NULL
        )
        """
    )
    db.commit()
    db.close()


def fetch_recent_requests(limit: int = 20) -> List[Dict[str, Any]]:
    rows = (
        get_db()
        .execute(
            """
            SELECT id, student_name, song_title, artist, message, selected, submitted_at
            FROM song_requests
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        )
        .fetchall()
    )
    return [dict(row) for row in rows]


def get_current_admin() -> Optional[Dict[str, str]]:
    username = session.get("admin_username")
    if not username:
        return None

    admin_data = ADMIN_USERS.get(username)
    if not admin_data:
        session.clear()
        return None

    return {"username": username, "role": admin_data["role"]}


@app.get("/")
def home():
    recent_requests = fetch_recent_requests(limit=20)
    current_admin = get_current_admin()
    return render_template(
        "index.html",
        recent_requests=recent_requests,
        now=now_kst(),
        current_admin=current_admin,
        login_error=request.args.get("login_error") == "1",
    )


@app.post("/submit")
def submit_request():
    student_name = request.form.get("student_name", "").strip()
    song_title = request.form.get("song_title", "").strip()
    artist = request.form.get("artist", "").strip()
    message = request.form.get("message", "").strip()

    if not student_name or not song_title or not artist:
        return redirect(url_for("home"))

    submitted_at = now_kst().strftime("%Y-%m-%d %H:%M")
    get_db().execute(
        """
        INSERT INTO song_requests (student_name, song_title, artist, message, selected, submitted_at)
        VALUES (?, ?, ?, ?, 0, ?)
        """,
        (student_name, song_title, artist, message, submitted_at),
    )
    get_db().commit()

    forwarded_for = request.headers.get("X-Forwarded-For", "")
    requester_ip = forwarded_for.split(",")[0].strip() if forwarded_for else (request.remote_addr or "unknown")
    app.logger.info(
        "New song request submitted by '%s' from ip=%s song='%s' artist='%s' at=%s",
        student_name,
        requester_ip,
        song_title,
        artist,
        submitted_at,
    )
    return redirect(url_for("home"))


@app.post("/admin/login")
def admin_login():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    admin_data = ADMIN_USERS.get(username)
    if not admin_data or admin_data["password"] != password:
        return redirect(url_for("home", login_error=1))

    session["admin_username"] = username
    return redirect(url_for("home"))


@app.post("/admin/logout")
def admin_logout():
    session.pop("admin_username", None)
    return redirect(url_for("home"))


@app.post("/admin/toggle/<int:request_id>")
def toggle_selected(request_id: int):
    if not get_current_admin():
        return redirect(url_for("home"))

    db = get_db()
    db.execute(
        """
        UPDATE song_requests
        SET selected = CASE WHEN selected = 1 THEN 0 ELSE 1 END
        WHERE id = ?
        """,
        (request_id,),
    )
    db.commit()

    return redirect(url_for("home"))


@app.post("/admin/delete/<int:request_id>")
def delete_request(request_id: int):
    if not get_current_admin():
        return redirect(url_for("home"))

    db = get_db()
    db.execute("DELETE FROM song_requests WHERE id = ?", (request_id,))
    db.commit()

    return redirect(url_for("home"))


@app.get("/health")
def health_check():
    return jsonify(
        {
            "status": "ok",
            "service": "song-request",
            "timestamp": now_kst().isoformat(),
        }
    )


@app.get("/감성은준")
def 감성은준():
    return "<h1>안녕 감성은준</h1>"


@app.get("/민호야")
def 민호야():
    return "<h1>그만쳐먹어ㅓㅓㅓㅓㅓㅓㅓㅓㅓㅓㅓㅓㅓㅓㅓㅓㅓㅓㅓㅓㅓㅓㅓㅓㅓㅓㅓㅓㅓㅓㅓㅓㅓㅓㅓㅓㅓㅓㅓㅓㅓㅓㅓㅓㅓㅓㅓ 민호야</h1>"


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)


init_db()
