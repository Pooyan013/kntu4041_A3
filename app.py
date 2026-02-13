import functools
import json
import os
import sqlite3
import urllib.parse
import urllib.request
from typing import Optional

from flask import Flask, flash, g, jsonify, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

DEFAULT_WMS_BASE_URL = "http://localhost:8080/geoserver/wms"
DEFAULT_WMS_LAYER = "topp:states"
DEFAULT_WMS_SERVER_TYPE = "geoserver"
WMS_SERVER_TYPE = ("geoserver")
SECRET_KEY = ("geoserver")

def init_db(db_path: str) -> None:
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            );
            """
        )
        conn.commit()
    finally:
        conn.close()


def validate_register(username: str, email: str, password: str, confirm_password: str) -> Optional[str]:
    if not username:
        return "Username is required."
    if len(username) < 3:
        return "Username must be at least 3 characters."
    if not email:
        return "Email is required."
    if "@" not in email or "." not in email:
        return "Please enter a valid email."
    if not password:
        return "Password is required."
    if len(password) < 6:
        return "Password must be at least 6 characters."
    if password != confirm_password:
        return "Passwords do not match."
    return None


def validate_feature_info_url(url: str, allowed_base_url: str) -> str:
    if len(url) > 8000:
        raise ValueError("FeatureInfo URL is too long.")

    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError("Only http/https FeatureInfo URLs are allowed.")

    allowed = urllib.parse.urlparse(allowed_base_url)
    if parsed.scheme != allowed.scheme or parsed.netloc != allowed.netloc:
        raise ValueError("FeatureInfo URL host must match configured WMS_BASE_URL.")

    allowed_path = allowed.path or ""
    if allowed_path and not parsed.path.startswith(allowed_path):
        raise ValueError("FeatureInfo URL path must match configured WMS_BASE_URL.")

    query = urllib.parse.parse_qs(parsed.query)
    req = (query.get("REQUEST") or query.get("request") or [""])[0].lower()
    if req != "getfeatureinfo":
        raise ValueError("URL must be a WMS GetFeatureInfo request.")

    return url


def fetch_url_text(url: str, *, timeout_s: int = 12, max_bytes: int = 1_000_000) -> tuple[str, str]:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "WebGIS-Final-Project/1.0",
            "Accept": "application/json, text/plain, */*",
        },
    )

    with urllib.request.urlopen(req, timeout=timeout_s) as resp:
        content_type = (resp.headers.get("Content-Type") or "text/plain").split(";", 1)[0].strip().lower()
        raw = resp.read(max_bytes + 1)

    if len(raw) > max_bytes:
        raise ValueError("GetFeatureInfo response too large.")

    return raw.decode("utf-8", errors="replace"), content_type


def create_app() -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-secret-key-change-me"),
        DATABASE=os.path.join(app.instance_path, "webgis.sqlite3"),
        WMS_BASE_URL=os.environ.get("WMS_BASE_URL", DEFAULT_WMS_BASE_URL),
        WMS_LAYER=os.environ.get("WMS_LAYER", DEFAULT_WMS_LAYER),
        WMS_SERVER_TYPE=os.environ.get("WMS_SERVER_TYPE", DEFAULT_WMS_SERVER_TYPE),
    )

    os.makedirs(app.instance_path, exist_ok=True)
    init_db(app.config["DATABASE"])

    def get_db() -> sqlite3.Connection:
        if "db" not in g:
            conn = sqlite3.connect(app.config["DATABASE"])
            conn.row_factory = sqlite3.Row
            g.db = conn
        return g.db

    @app.teardown_appcontext
    def close_db(exception: Optional[BaseException]) -> None:
        db = g.pop("db", None)
        if db is not None:
            db.close()

    @app.before_request
    def load_logged_in_user() -> None:
        user_id = session.get("user_id")
        if not user_id:
            g.user = None
            return

        db = get_db()
        g.user = db.execute(
            "SELECT id, username, email FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()

        if g.user is None:
            session.clear()

    def login_required(view):
        @functools.wraps(view)
        def wrapped_view(**kwargs):
            if g.user is None:
                return redirect(url_for("login", next=request.path))
            return view(**kwargs)

        return wrapped_view

    @app.get("/")
    def index():
        if g.user is not None:
            return redirect(url_for("map_page"))
        return redirect(url_for("login"))

    @app.get("/about")
    def about():
        return render_template("about.html", title="Made By")

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if g.user is not None:
            return redirect(url_for("map_page"))

        if request.method == "POST":
            username = (request.form.get("username") or "").strip()
            email = (request.form.get("email") or "").strip()
            password = request.form.get("password") or ""
            confirm_password = request.form.get("confirm_password") or ""

            error = validate_register(username, email, password, confirm_password)
            if error:
                flash(error, "error")
                return render_template("register.html", title="Register")

            db = get_db()
            try:
                cur = db.execute(
                    "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
                    (username, email, generate_password_hash(password)),
                )
                db.commit()
            except sqlite3.IntegrityError:
                flash("Username or email already exists.", "error")
                return render_template("register.html", title="Register")

            session.clear()
            session["user_id"] = cur.lastrowid
            flash("Registration successful. Welcome!", "success")
            return redirect(url_for("map_page"))

        return render_template("register.html", title="Register")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if g.user is not None:
            return redirect(url_for("map_page"))

        if request.method == "POST":
            username = (request.form.get("username") or "").strip()
            password = request.form.get("password") or ""

            if not username or not password:
                flash("Please enter username and password.", "error")
                return render_template("login.html", title="Login")

            db = get_db()
            user = db.execute(
                "SELECT id, username, password_hash FROM users WHERE username = ?",
                (username,),
            ).fetchone()

            if user is None or not check_password_hash(user["password_hash"], password):
                flash("Invalid username or password.", "error")
                return render_template("login.html", title="Login")

            session.clear()
            session["user_id"] = user["id"]
            flash("Logged in successfully.", "success")

            next_url = request.args.get("next")
            if next_url and next_url.startswith("/"):
                return redirect(next_url)
            return redirect(url_for("map_page"))

        return render_template("login.html", title="Login")

    @app.route("/logout", methods=["POST", "GET"])
    def logout():
        session.clear()
        flash("You have been logged out.", "info")
        return redirect(url_for("login"))

    @app.get("/map")
    @login_required
    def map_page():
        return render_template(
            "map.html",
            title="Map",
            container_class="container container--full",
            wms_base_url=app.config["WMS_BASE_URL"],
            wms_layer=app.config["WMS_LAYER"],
            wms_server_type=app.config["WMS_SERVER_TYPE"],
        )

    @app.get("/api/feature-info")
    @login_required
    def feature_info():
        url = (request.args.get("url") or "").strip()
        if not url:
            return jsonify({"error": "Missing 'url' parameter."}), 400

        try:
            validated_url = validate_feature_info_url(url, app.config["WMS_BASE_URL"])
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

        try:
            body, content_type = fetch_url_text(validated_url)
        except Exception as e:
            return jsonify({"error": f"Failed to fetch GetFeatureInfo: {e}"}), 502

        if content_type.startswith("application/json"):
            try:
                return jsonify(json.loads(body))
            except json.JSONDecodeError:
                return jsonify({"raw": body, "content_type": content_type})

        return jsonify({"raw": body, "content_type": content_type})

    @app.errorhandler(404)
    def not_found(_e):
        return render_template("error.html", title="Not Found", message="Page not found."), 404

    @app.errorhandler(500)
    def server_error(_e):
        return render_template("error.html", title="Error", message="Unexpected server error."), 500

    return app


app = create_app()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    debug = (os.environ.get("FLASK_DEBUG") or "").strip() in {"1", "true", "True", "yes", "on"}
    app.run(host="127.0.0.1", port=port, debug=debug)
