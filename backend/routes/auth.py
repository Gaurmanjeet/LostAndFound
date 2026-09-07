from flask import Blueprint, request, jsonify,session
from werkzeug.security import generate_password_hash
from database import get_db_connection

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/api/register", methods=["POST"])
def register():

    data = request.get_json()

    full_name = data.get("full_name")
    email = data.get("email")
    password = data.get("password")

    if not full_name or not email or not password:
        return jsonify({
            "success": False,
            "message": "All fields are required."
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

        # Check existing email
        cursor.execute(
            "SELECT id FROM users WHERE email = %s",
            (email,)
        )

        existing_user = cursor.fetchone()

        if existing_user:
            return jsonify({
                "success": False,
                "message": "Email already registered."
            }), 409

        # Hash password
        password_hash = generate_password_hash(password)

        # Insert user
        cursor.execute(
            """
            INSERT INTO users
            (full_name, email, password_hash)
            VALUES (%s, %s, %s)
            """,
            (full_name, email, password_hash)
        )

        connection.commit()

        return jsonify({
            "success": True,
            "message": "Account created successfully."
        }), 201

    except Exception as error:

        if connection:
            connection.rollback()

        return jsonify({
            "success": False,
            "message": "Registration failed."
        }), 500

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()
            from flask import session
from werkzeug.security import check_password_hash


@auth_bp.route("/api/login", methods=["POST"])
def login():

    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({
            "success": False,
            "message": "Email and password are required."
        }), 400

    connection = None
    cursor = None

    try:

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT id, full_name, email, password_hash, role
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

        if not check_password_hash(
            user["password_hash"],
            password
        ):
            return jsonify({
                "success": False,
                "message": "Invalid email or password."
            }), 401

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

        return jsonify({
            "success": False,
            "message": "Login failed."
        }), 500

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()
@auth_bp.route("/api/logout", methods=["POST"])
def logout():

    session.clear()

    return jsonify({
        "success": True,
        "message": "Logged out successfully."
    }), 200