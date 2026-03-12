from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from flask import Flask, jsonify, redirect, render_template, request, session, url_for

app = Flask(__name__)
app.secret_key = "song-request-secret-key-change-this"

ADMIN_USERS: Dict[str, Dict[str, str]] = {
    "sentimentaleunjun": {"password": "A292513a!!", "role": "감성은준(관리자)"},
    "vicepresident23": {"password": "A292513a!!", "role": "키큰민서(관리자)"},
    "teacher23": {"password": "A292513a!!", "role": "선생님(관리자)"},
    "president23": {"password": "A292513a!!", "role": "지우지우(관리자)"},
}

requests_store: List[Dict[str, Any]] = []
next_request_id = 1


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
    recent_requests = list(reversed(requests_store[-20:]))
    current_admin = get_current_admin()
    return render_template(
        "index.html",
        recent_requests=recent_requests,
        now=datetime.now(),
        current_admin=current_admin,
        login_error=request.args.get("login_error") == "1",
    )


@app.post("/submit")
def submit_request():
    global next_request_id

    student_name = request.form.get("student_name", "").strip()
    song_title = request.form.get("song_title", "").strip()
    artist = request.form.get("artist", "").strip()
    message = request.form.get("message", "").strip()

    if not student_name or not song_title or not artist:
        return redirect(url_for("home"))

    requests_store.append(
        {
            "id": next_request_id,
            "student_name": student_name,
            "song_title": song_title,
            "artist": artist,
            "message": message,
            "selected": False,
            "submitted_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
    )
    next_request_id += 1
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

    for item in requests_store:
        if item["id"] == request_id:
            item["selected"] = not item["selected"]
            break

    return redirect(url_for("home"))


@app.post("/admin/delete/<int:request_id>")
def delete_request(request_id: int):
    if not get_current_admin():
        return redirect(url_for("home"))

    for idx, item in enumerate(requests_store):
        if item["id"] == request_id:
            requests_store.pop(idx)
            break

    return redirect(url_for("home"))


@app.get("/health")
def health_check():
    selected_count = sum(1 for item in requests_store if item.get("selected"))
    return jsonify(
        {
            "status": "ok",
            "requests_count": len(requests_store),
            "selected_count": selected_count,
        }
    )

@app.get("/감성은준")
def 감성은준():
    return "<h1>안녕 감성은준</h1>"

@app.get("/민호야")
def 민호야():
    return "<h1>그만쳐먹어ㅓㅓㅓㅓㅓㅓㅓㅓㅓㅓㅓㅓㅓㅓㅓㅓㅓㅓㅓㅓㅓㅓㅓㅓㅓㅓㅓㅓㅓㅓㅓㅓㅓㅓㅓㅓㅓㅓㅓㅓㅓㅓㅓㅓㅓㅓㅓ 민호야</h1>"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
