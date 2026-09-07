import os
from flask import Flask
from flask_cors import CORS

from routes.auth import auth_bp
from routes.items import items_bp
from routes.admin import admin_bp



app = Flask(__name__)
UPLOAD_FOLDER = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "uploads"
)

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.secret_key ="lost-and-found-development-key"

CORS(app,supports_credentials=True)  # Enable CORS for all routes and allow credentials


# Register authentication routes
app.register_blueprint(auth_bp)
app.register_blueprint(items_bp)
app.register_blueprint(admin_bp)


@app.route("/")
def home():

    return {
        "message": "Lost & Found API is running",
        "status": "success"
    }


@app.route("/api/health")
def health():

    return {
        "status": "healthy"
    }


if __name__ == "__main__":
    app.run(debug=True)