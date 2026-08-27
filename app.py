from flask import Flask, request, jsonify, session, send_from_directory
from flask_cors import CORS
from flask_bcrypt import Bcrypt
import sqlite3
import os
from datetime import datetime

app = Flask(__name__, static_folder=".", static_url_path="")
app.secret_key = "CHANGE_THIS_TO_A_LONG_RANDOM_SECRET_KEY"

CORS(app, supports_credentials=True)
bcrypt = Bcrypt(app)

DATABASE = "yashtech.db"


# =========================
# DATABASE
# =========================

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT,
            email TEXT,
            message TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS visits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            visitor_id TEXT,
            page TEXT,
            visited_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE,
            completed_lessons INTEGER DEFAULT 0,
            quiz_score INTEGER DEFAULT 0,
            progress_percentage INTEGER DEFAULT 0,
            updated_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


init_db()


# =========================
# HOME PAGE
# =========================

@app.route("/")
def home():
    return send_from_directory(".", "index.html")
@app.route("/<path:filename>")
def serve_file(filename):
    return send_from_directory(".", filename)


# =========================
# SIGNUP
# =========================

@app.route("/api/signup", methods=["POST"])
def signup():

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "Invalid request."
        }), 400

    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    confirm_password = data.get("confirm_password", "")

    if not name or not email or not password:
        return jsonify({
            "success": False,
            "message": "All fields are required."
        }), 400

    if password != confirm_password:
        return jsonify({
            "success": False,
            "message": "Passwords do not match."
        }), 400

    if len(password) < 6:
        return jsonify({
            "success": False,
            "message": "Password must contain at least 6 characters."
        }), 400

    conn = get_db()
    cursor = conn.cursor()

    existing_user = cursor.execute(
        "SELECT id FROM users WHERE email = ?",
        (email,)
    ).fetchone()

    if existing_user:
        conn.close()

        return jsonify({
            "success": False,
            "message": "An account with this email already exists."
        }), 409

    password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO users
        (name, email, password_hash, created_at)
        VALUES (?, ?, ?, ?)
    """, (
        name,
        email,
        password_hash,
        created_at
    ))

    user_id = cursor.lastrowid

    cursor.execute("""
        INSERT INTO progress
        (user_id, completed_lessons, quiz_score,
         progress_percentage, updated_at)
        VALUES (?, 0, 0, 0, ?)
    """, (
        user_id,
        created_at
    ))

    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "message": "Account created successfully."
    })


# =========================
# LOGIN
# =========================

@app.route("/api/login", methods=["POST"])
def login():

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "Invalid request."
        }), 400

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    conn = get_db()

    user = conn.execute(
        "SELECT * FROM users WHERE email = ?",
        (email,)
    ).fetchone()

    conn.close()

    if not user:
        return jsonify({
            "success": False,
            "message": "Invalid email or password."
        }), 401

    if not bcrypt.check_password_hash(
        user["password_hash"],
        password
    ):
        return jsonify({
            "success": False,
            "message": "Invalid email or password."
        }), 401

    session["user_id"] = user["id"]
    session["user_name"] = user["name"]
    session["user_email"] = user["email"]

    return jsonify({
        "success": True,
        "message": "Login successful.",
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"]
        }
    })


# =========================
# CURRENT USER
# =========================

@app.route("/api/me")
def current_user():

    if "user_id" not in session:
        return jsonify({
            "logged_in": False
        })

    conn = get_db()

    user = conn.execute(
        "SELECT id, name, email, created_at FROM users WHERE id = ?",
        (session["user_id"],)
    ).fetchone()

    conn.close()

    if not user:
        session.clear()

        return jsonify({
            "logged_in": False
        })

    return jsonify({
        "logged_in": True,
        "user": dict(user)
    })


# =========================
# LOGOUT
# =========================

@app.route("/api/logout", methods=["POST"])
def logout():

    session.clear()

    return jsonify({
        "success": True,
        "message": "Logged out successfully."
    })


# =========================
# STUDENT DASHBOARD
# =========================

@app.route("/api/dashboard")
def dashboard():

    if "user_id" not in session:
        return jsonify({
            "success": False,
            "message": "Please login first."
        }), 401

    user_id = session["user_id"]

    conn = get_db()

    user = conn.execute("""
        SELECT id, name, email, created_at
        FROM users
        WHERE id = ?
    """, (user_id,)).fetchone()

    progress = conn.execute("""
        SELECT completed_lessons,
               quiz_score,
               progress_percentage
        FROM progress
        WHERE user_id = ?
    """, (user_id,)).fetchone()

    conn.close()

    return jsonify({
        "success": True,
        "user": dict(user),
        "progress": dict(progress) if progress else {
            "completed_lessons": 0,
            "quiz_score": 0,
            "progress_percentage": 0
        }
    })


# =========================
# FEEDBACK
# =========================

@app.route("/api/feedback", methods=["POST"])
def submit_feedback():

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "Invalid request."
        }), 400

    message = data.get("message", "").strip()

    if not message:
        return jsonify({
            "success": False,
            "message": "Feedback message is required."
        }), 400

    user_id = session.get("user_id")
    name = session.get("user_name", data.get("name", "Guest"))
    email = session.get("user_email", data.get("email", ""))

    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = get_db()

    conn.execute("""
        INSERT INTO feedback
        (user_id, name, email, message, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (
        user_id,
        name,
        email,
        message,
        created_at
    ))

    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "message": "Feedback submitted successfully."
    })


# =========================
# VISITOR TRACKING
# =========================

@app.route("/api/track-visit", methods=["POST"])
def track_visit():

    data = request.get_json() or {}

    page = data.get("page", "/")

    visitor_id = request.cookies.get("visitor_id")

    if not visitor_id:
        visitor_id = os.urandom(16).hex()

    visited_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = get_db()

    conn.execute("""
        INSERT INTO visits
        (visitor_id, page, visited_at)
        VALUES (?, ?, ?)
    """, (
        visitor_id,
        page,
        visited_at
    ))

    conn.commit()
    conn.close()

    response = jsonify({
        "success": True
    })

    response.set_cookie(
        "visitor_id",
        visitor_id,
        max_age=60 * 60 * 24 * 365,
        httponly=True,
        samesite="Lax"
    )

    return response


# =========================
# WEBSITE STATISTICS
# =========================

@app.route("/api/stats")
def stats():

    conn = get_db()

    total_students = conn.execute(
        "SELECT COUNT(*) FROM users"
    ).fetchone()[0]

    total_visitors = conn.execute(
        "SELECT COUNT(DISTINCT visitor_id) FROM visits"
    ).fetchone()[0]

    today = datetime.now().strftime("%Y-%m-%d")

    today_visitors = conn.execute("""
        SELECT COUNT(DISTINCT visitor_id)
        FROM visits
        WHERE visited_at LIKE ?
    """, (
        today + "%",
    )).fetchone()[0]

    total_feedback = conn.execute(
        "SELECT COUNT(*) FROM feedback"
    ).fetchone()[0]

    conn.close()

    return jsonify({
        "success": True,
        "total_students": total_students,
        "total_visitors": total_visitors,
        "today_visitors": today_visitors,
        "total_feedback": total_feedback
    })


# =========================
# ADMIN LOGIN
# =========================

ADMIN_EMAIL = "admin@yashtech.com"
ADMIN_PASSWORD = "Admin@123"


@app.route("/api/admin/login", methods=["POST"])
def admin_login():

    data = request.get_json()

    email = data.get("email", "")
    password = data.get("password", "")

    if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:

        session["admin_logged_in"] = True

        return jsonify({
            "success": True,
            "message": "Admin login successful."
        })

    return jsonify({
        "success": False,
        "message": "Invalid admin credentials."
    }), 401


# =========================
# ADMIN AUTH CHECK
# =========================

def admin_required():

    return session.get("admin_logged_in") is True


# =========================
# ADMIN DASHBOARD DATA
# =========================

@app.route("/api/admin/dashboard")
def admin_dashboard():

    if not admin_required():
        return jsonify({
            "success": False,
            "message": "Admin access required."
        }), 403

    conn = get_db()

    students = conn.execute("""
        SELECT id, name, email, created_at
        FROM users
        ORDER BY id DESC
    """).fetchall()

    feedback = conn.execute("""
        SELECT id, name, email, message, created_at
        FROM feedback
        ORDER BY id DESC
    """).fetchall()

    visits = conn.execute("""
        SELECT id, visitor_id, page, visited_at
        FROM visits
        ORDER BY id DESC
        LIMIT 100
    """).fetchall()

    conn.close()

    return jsonify({
        "success": True,
        "students": [dict(row) for row in students],
        "feedback": [dict(row) for row in feedback],
        "visits": [dict(row) for row in visits]
    })


# =========================
# ADMIN LOGOUT
# =========================

@app.route("/api/admin/logout", methods=["POST"])
def admin_logout():

    session.pop("admin_logged_in", None)

    return jsonify({
        "success": True
    })


# =========================
# RUN SERVER
# =========================

if __name__ == "__main__":
    app.run(debug=True)

    @app.route("/signup.html")
    def signup_page():
     return send_from_directory(".", "signup.html")


@app.route("/login.html")
def login_page():
    return send_from_directory(".", "login.html")


@app.route("/student-dashboard.html")
def student_dashboard_page():
    return send_from_directory(".", "student-dashboard.html")