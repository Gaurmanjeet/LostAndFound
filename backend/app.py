import os

from flask import Flask, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

from routes.auth import auth_bp
from routes.items import items_bp
from routes.admin import admin_bp
from routes.notifications import notifications_bp


load_dotenv()

app = Flask(__name__)


# =========================================================
# PATHS
# =========================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# =========================================================
# CONFIGURATION
# =========================================================

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

app.secret_key = os.getenv(
    "SECRET_KEY",
    "lost-and-found-development-key"
)


# =========================================================
# CORS
# =========================================================

CORS(
    app,
    supports_credentials=True
)


# =========================================================
# BLUEPRINTS
# =========================================================

app.register_blueprint(auth_bp)
app.register_blueprint(items_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(notifications_bp)

# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():
    return {
        "success": True,
        "message": "Lost & Found API is running",
        "status": "success"
    }


# =========================================================
# HEALTH CHECK
# =========================================================

@app.route("/api/health")
def health():
    return {
        "success": True,
        "status": "healthy"
    }


# =========================================================
# UPLOADS
# =========================================================

@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        filename
    )


# =========================================================
# ERROR HANDLERS
# =========================================================

@app.errorhandler(413)
def file_too_large(error):
    return {
        "success": False,
        "message": "File is too large. Maximum size is 10 MB."
    }, 413


@app.errorhandler(404)
def not_found(error):
    return {
        "success": False,
        "message": "API endpoint not found."
    }, 404


@app.errorhandler(500)
def internal_error(error):
    return {
        "success": False,
        "message": "Internal server error."
    }, 500


# =========================================================
# RUN SERVER
# =========================================================

if __name__ == "__main__":
    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )