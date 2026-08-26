from flask import Flask, request, jsonify, render_template, session, redirect
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from functools import wraps
import sqlite3
import os
import getpass

app = Flask(__name__)

# IMPORTANT:
# Production mein is secret ko environment variable mein rakhna.
app.secret_key = os.environ.get(
    "SECRET_KEY",
    "change-this-secret-key-before-production"
)

CORS(app, supports_credentials=True)

bcrypt = Bcrypt(app)

DATABASE = "yashtech.db"


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# ---------- Database Initialization ----------
def init_db():

    conn = get_db()

    # Users
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Feedback
    conn.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rating INTEGER NOT NULL CHECK(rating >= 1 AND rating <= 5),
            message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Website visits
    conn.execute("""
        CREATE TABLE IF NOT EXISTS visits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            visitor_id TEXT,
            page TEXT,
            visited_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Admin
    conn.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


# ---------- Admin Setup ----------
def setup_admin():

    conn = get_db()

    existing_admin = conn.execute(
        "SELECT id FROM admins LIMIT 1"
    ).fetchone()

    conn.close()

    if existing_admin:
        return

    print("\n===================================")
    print("       YashTech Admin Setup")
    print("===================================")

    print("No admin account found.")
    print("Create your admin account now.\n")

    email = input("Admin email: ").strip()

    while not email:
        email = input("Admin email cannot be empty: ").strip()

    password = getpass.getpass("Admin password: ")

    while not password:
        password = getpass.getpass(
            "Admin password cannot be empty: "
        )

    confirm_password = getpass.getpass(
        "Confirm admin password: "
    )

    while password != confirm_password:

        print("Passwords do not match.")

        password = getpass.getpass(
            "Admin password: "
        )

        confirm_password = getpass.getpass(
            "Confirm admin password: "
        )

    password_hash = bcrypt.generate_password_hash(
        password
    ).decode("utf-8")

    conn = get_db()

    conn.execute(
        """
        INSERT INTO admins (email, password_hash)
        VALUES (?, ?)
        """,
        (email, password_hash)
    )

    conn.commit()
    conn.close()

    print("\nAdmin account created successfully!")
    print("You can now use the admin dashboard.\n")


# ---------- Home ----------
@app.route("/")
def home():

    return jsonify({
        "message": "YashTech Backend is running!"
    })


# ---------- Signup ----------
@app.route("/api/signup", methods=["POST"])
def signup():

    data = request.get_json(silent=True) or {}

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if not name or not email or not password:

        return jsonify({
            "message": "All fields are required"
        }), 400

    conn = get_db()

    existing_user = conn.execute(
        "SELECT id FROM users WHERE email = ?",
        (email,)
    ).fetchone()

    if existing_user:

        conn.close()

        return jsonify({
            "message": "Email already registered"
        }), 409

    password_hash = bcrypt.generate_password_hash(
        password
    ).decode("utf-8")

    conn.execute(
        """
        INSERT INTO users (name, email, password_hash)
        VALUES (?, ?, ?)
        """,
        (name, email, password_hash)
    )

    conn.commit()
    conn.close()

    return jsonify({
        "message": "Account created successfully"
    }), 201


# ---------- User Login ----------
@app.route("/api/login", methods=["POST"])
def login():

    data = request.get_json(silent=True) or {}

    email = data.get("email")
    password = data.get("password")

    if not email or not password:

        return jsonify({
            "message": "Email and password are required"
        }), 400

    conn = get_db()

    user = conn.execute(
        "SELECT * FROM users WHERE email = ?",
        (email,)
    ).fetchone()

    conn.close()

    if not user:

        return jsonify({
            "message": "Invalid email or password"
        }), 401

    if not bcrypt.check_password_hash(
        user["password_hash"],
        password
    ):

        return jsonify({
            "message": "Invalid email or password"
        }), 401

    return jsonify({
        "message": "Login successful",
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"]
        }
    }), 200


# ---------- Feedback ----------
@app.route("/api/feedback", methods=["POST"])
def submit_feedback():

    data = request.get_json(silent=True) or {}

    rating = data.get("rating")
    message = data.get("message", "").strip()

    try:
        rating = int(rating)

    except (TypeError, ValueError):

        return jsonify({
            "message": "Please provide a valid rating"
        }), 400

    if rating < 1 or rating > 5:

        return jsonify({
            "message": "Rating must be between 1 and 5"
        }), 400

    if len(message) > 1000:

        return jsonify({
            "message": "Feedback is too long"
        }), 400

    conn = get_db()

    conn.execute(
        """
        INSERT INTO feedback (rating, message)
        VALUES (?, ?)
        """,
        (rating, message if message else None)
    )

    conn.commit()
    conn.close()

    return jsonify({
        "message": "Thank you for your feedback!"
    }), 201


# ---------- Track Visitor ----------
@app.route("/api/visit", methods=["POST"])
def track_visit():

    data = request.get_json(silent=True) or {}

    visitor_id = data.get("visitor_id")
    page = data.get("page", "/")

    if not visitor_id:

        return jsonify({
            "message": "Visitor ID is required"
        }), 400

    conn = get_db()

    conn.execute(
        """
        INSERT INTO visits (visitor_id, page)
        VALUES (?, ?)
        """,
        (visitor_id, page)
    )

    conn.commit()
    conn.close()

    return jsonify({
        "message": "Visit recorded"
    }), 201


# =====================================================
#                    ADMIN SYSTEM
# =====================================================


# ---------- Admin Login Page ----------
@app.route("/admin-login")
def admin_login_page():

    if session.get("admin_logged_in"):

        return redirect("/admin")

    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>YashTech Admin Login</title>

        <meta name="viewport"
              content="width=device-width, initial-scale=1.0">

        <style>

            * {
                box-sizing: border-box;
            }

            body {
                margin: 0;
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                font-family: Arial, sans-serif;
                background: #f5f5f5;
            }

            .login-box {
                width: 100%;
                max-width: 400px;
                background: white;
                padding: 30px;
                border-radius: 14px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.10);
            }

            h1 {
                margin-top: 0;
            }

            input {
                width: 100%;
                padding: 12px;
                margin: 8px 0 15px;
                border: 1px solid #ddd;
                border-radius: 8px;
                font-size: 15px;
            }

            button {
                width: 100%;
                padding: 12px;
                border: none;
                border-radius: 8px;
                background: #111;
                color: white;
                cursor: pointer;
                font-size: 15px;
            }

            button:hover {
                opacity: 0.9;
            }

            #message {
                margin-top: 15px;
                color: #c00;
            }

        </style>
    </head>

    <body>

        <div class="login-box">

            <h1>Admin Login</h1>

            <p>YashTech Analytics Dashboard</p>

            <form id="login-form">

                <label>Email</label>

                <input
                    type="email"
                    id="email"
                    required
                >

                <label>Password</label>

                <input
                    type="password"
                    id="password"
                    required
                >

                <button type="submit">
                    Login
                </button>

            </form>

            <div id="message"></div>

        </div>


        <script>

            document
                .getElementById("login-form")
                .addEventListener("submit", async function(event) {

                    event.preventDefault();

                    const email =
                        document.getElementById("email").value;

                    const password =
                        document.getElementById("password").value;

                    const message =
                        document.getElementById("message");

                    try {

                        const response = await fetch(
                            "/api/admin/login",
                            {
                                method: "POST",

                                headers: {
                                    "Content-Type":
                                        "application/json"
                                },

                                credentials: "include",

                                body: JSON.stringify({
                                    email: email,
                                    password: password
                                })
                            }
                        );

                        const data =
                            await response.json();

                        if (!response.ok) {

                            message.textContent =
                                data.message ||
                                "Login failed";

                            return;
                        }

                        window.location.href = "/admin";

                    } catch (error) {

                        console.error(error);

                        message.textContent =
                            "Unable to connect to server.";
                    }

                });

        </script>

    </body>
    </html>
    """


# ---------- Admin Login API ----------
@app.route("/api/admin/login", methods=["POST"])
def admin_login():

    data = request.get_json(silent=True) or {}

    email = data.get("email")
    password = data.get("password")

    if not email or not password:

        return jsonify({
            "message": "Email and password are required"
        }), 400

    conn = get_db()

    admin = conn.execute(
        """
        SELECT * FROM admins
        WHERE email = ?
        """,
        (email,)
    ).fetchone()

    conn.close()

    if not admin:

        return jsonify({
            "message": "Invalid admin credentials"
        }), 401

    if not bcrypt.check_password_hash(
        admin["password_hash"],
        password
    ):

        return jsonify({
            "message": "Invalid admin credentials"
        }), 401

    session.clear()

    session["admin_logged_in"] = True
    session["admin_id"] = admin["id"]
    session["admin_email"] = admin["email"]

    return jsonify({
        "message": "Admin login successful"
    }), 200


# ---------- Admin Authentication ----------
def admin_required(function):

    @wraps(function)
    def decorated_function(*args, **kwargs):

        if not session.get("admin_logged_in"):

            if request.path == "/admin":

                return redirect("/admin-login")

            return jsonify({
                "message": "Admin authentication required"
            }), 401

        return function(*args, **kwargs)

    return decorated_function


# ---------- Admin Dashboard ----------
@app.route("/admin")
@admin_required
def admin_dashboard():

    return render_template("admin.html")


# ---------- Protected Analytics ----------
@app.route("/api/analytics", methods=["GET"])
@admin_required
def analytics():

    conn = get_db()

    total_visits = conn.execute(
        "SELECT COUNT(*) AS count FROM visits"
    ).fetchone()["count"]

    unique_visitors = conn.execute(
        """
        SELECT COUNT(DISTINCT visitor_id) AS count
        FROM visits
        """
    ).fetchone()["count"]

    total_feedback = conn.execute(
        "SELECT COUNT(*) AS count FROM feedback"
    ).fetchone()["count"]

    average_rating = conn.execute(
        "SELECT AVG(rating) AS average FROM feedback"
    ).fetchone()["average"]

    today_visits = conn.execute(
        """
        SELECT COUNT(*) AS count
        FROM visits
        WHERE DATE(visited_at) = DATE('now')
        """
    ).fetchone()["count"]

    recent_feedback = conn.execute(
        """
        SELECT id, rating, message, created_at
        FROM feedback
        ORDER BY id DESC
        LIMIT 20
        """
    ).fetchall()

    daily_visits = conn.execute(
        """
        SELECT DATE(visited_at) AS date,
               COUNT(*) AS visits
        FROM visits
        GROUP BY DATE(visited_at)
        ORDER BY date DESC
        LIMIT 7
        """
    ).fetchall()

    conn.close()

    return jsonify({

        "total_visits": total_visits,

        "unique_visitors": unique_visitors,

        "today_visits": today_visits,

        "total_feedback": total_feedback,

        "average_rating":
            round(average_rating, 2)
            if average_rating is not None else 0,

        "recent_feedback": [
            dict(row)
            for row in recent_feedback
        ],

        "daily_visits": [
            dict(row)
            for row in daily_visits
        ]

    })


# ---------- Admin Logout ----------
@app.route("/api/admin/logout", methods=["POST"])
@admin_required
def admin_logout():

    session.clear()

    return jsonify({
        "message": "Admin logged out successfully"
    }), 200


# ---------- Start Server ----------
if __name__ == "__main__":

    init_db()

    setup_admin()

    app.run(
        debug=True,
        port=5000
    )