from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash

from database import get_db_connection


auth_bp = Blueprint("auth", __name__)


# =========================================================
# REGISTER
# =========================================================

@auth_bp.route("/api/register", methods=["POST"])
def register():

    data = request.get_json(silent=True) or {}

    full_name = data.get("full_name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    # -----------------------------------------------------
    # Validation
    # -----------------------------------------------------

    if not full_name or not email or not password:
        return jsonify({
            "success": False,
            "message": "All fields are required."
        }), 400

    if len(full_name) < 2:
        return jsonify({
            "success": False,
            "message": "Full name must contain at least 2 characters."
        }), 400

    if len(password) < 6:
        return jsonify({
            "success": False,
            "message": "Password must contain at least 6 characters."
        }), 400

    connection = None
    cursor = None

    try:

        connection = get_db_connection()
        cursor = connection.cursor()

        # -------------------------------------------------
        # Check existing email
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT id
            FROM users
            WHERE email = %s
            """,
            (email,)
        )

        existing_user = cursor.fetchone()

        if existing_user:
            return jsonify({
                "success": False,
                "message": "Email already registered."
            }), 409

        # -------------------------------------------------
        # Hash password
        # -------------------------------------------------

        password_hash = generate_password_hash(password)

        # -------------------------------------------------
        # Insert user
        # -------------------------------------------------

        cursor.execute(
            """
            INSERT INTO users
            (
                full_name,
                email,
                password_hash
            )
            VALUES (%s, %s, %s)
            """,
            (
                full_name,
                email,
                password_hash
            )
        )

        connection.commit()

        return jsonify({
            "success": True,
            "message": "Account created successfully."
        }), 201

    except Exception as error:

        if connection:
            connection.rollback()

        print("Registration error:", error)

        return jsonify({
            "success": False,
            "message": "Registration failed."
        }), 500

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# LOGIN
# =========================================================

@auth_bp.route("/api/login", methods=["POST"])
def login():

    data = request.get_json(silent=True) or {}

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    # -----------------------------------------------------
    # Validation
    # -----------------------------------------------------

    if not email or not password:
        return jsonify({
            "success": False,
            "message": "Email and password are required."
        }), 400

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        # -------------------------------------------------
        # Find user
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                id,
                full_name,
                email,
                password_hash,
                role
            FROM users
            WHERE email = %s
            """,
            (email,)
        )

        user = cursor.fetchone()

        if not user:
            return jsonify({
                "success": False,
                "message": "Invalid email or password."
            }), 401

        # -------------------------------------------------
        # Verify password
        # -------------------------------------------------

        if not check_password_hash(
            user["password_hash"],
            password
        ):
            return jsonify({
                "success": False,
                "message": "Invalid email or password."
            }), 401

        # -------------------------------------------------
        # Create session
        # -------------------------------------------------

        session.clear()

        session["user_id"] = user["id"]
        session["user_name"] = user["full_name"]
        session["user_role"] = user["role"]

        return jsonify({
            "success": True,
            "message": "Login successful.",
            "user": {
                "id": user["id"],
                "name": user["full_name"],
                "email": user["email"],
                "role": user["role"]
            }
        }), 200

    except Exception as error:

        print("Login error:", error)

        return jsonify({
            "success": False,
            "message": "Login failed."
        }), 500

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# LOGOUT
# =========================================================

@auth_bp.route("/api/logout", methods=["POST"])
def logout():

    session.clear()

    return jsonify({
        "success": True,
        "message": "Logged out successfully."
    }), 200


# =========================================================
# CURRENT USER
# =========================================================

@auth_bp.route("/api/me", methods=["GET"])
def current_user():

    if "user_id" not in session:
        return jsonify({
            "success": False,
            "authenticated": False,
            "message": "Not logged in."
        }), 401

    return jsonify({
        "success": True,
        "authenticated": True,
        "user": {
            "id": session.get("user_id"),
            "name": session.get("user_name"),
            "role": session.get("user_role")
        }
    }), 200