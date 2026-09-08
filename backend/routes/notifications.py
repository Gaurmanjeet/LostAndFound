from flask import Blueprint, jsonify, session

from database import get_db_connection


notifications_bp = Blueprint("notifications", __name__)


# =========================================================
# AUTH CHECK
# =========================================================

def is_logged_in():
    return "user_id" in session


# =========================================================
# GET USER NOTIFICATIONS
# =========================================================

@notifications_bp.route("/api/notifications", methods=["GET"])
def get_notifications():

    if not is_logged_in():
        return jsonify({
            "success": False,
            "message": "Please login first."
        }), 401

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                id,
                title,
                message,
                type,
                is_read,
                created_at
            FROM notifications
            WHERE user_id = %s
            ORDER BY created_at DESC
        """, (session["user_id"],))

        notifications = cursor.fetchall()

        return jsonify({
            "success": True,
            "notifications": notifications
        }), 200

    except Exception as error:

        print("Get notifications error:", error)

        return jsonify({
            "success": False,
            "message": "Failed to load notifications."
        }), 500

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# GET UNREAD NOTIFICATION COUNT
# =========================================================

@notifications_bp.route(
    "/api/notifications/unread-count",
    methods=["GET"]
)
def unread_count():

    if not is_logged_in():
        return jsonify({
            "success": False,
            "message": "Please login first."
        }), 401

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT COUNT(*) AS unread_count
            FROM notifications
            WHERE user_id = %s
              AND is_read = FALSE
        """, (session["user_id"],))

        result = cursor.fetchone()

        return jsonify({
            "success": True,
            "unread_count": result["unread_count"]
        }), 200

    except Exception as error:

        print("Unread notification error:", error)

        return jsonify({
            "success": False,
            "message": "Failed to get notification count."
        }), 500

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# MARK ONE NOTIFICATION AS READ
# =========================================================

@notifications_bp.route(
    "/api/notifications/<int:notification_id>/read",
    methods=["POST"]
)
def mark_notification_read(notification_id):

    if not is_logged_in():
        return jsonify({
            "success": False,
            "message": "Please login first."
        }), 401

    connection = None
    cursor = None

    try:

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("""
            UPDATE notifications
            SET is_read = TRUE
            WHERE id = %s
              AND user_id = %s
        """, (
            notification_id,
            session["user_id"]
        ))

        if cursor.rowcount == 0:

            return jsonify({
                "success": False,
                "message": "Notification not found."
            }), 404

        connection.commit()

        return jsonify({
            "success": True,
            "message": "Notification marked as read."
        }), 200

    except Exception as error:

        if connection:
            connection.rollback()

        print("Mark notification error:", error)

        return jsonify({
            "success": False,
            "message": "Failed to update notification."
        }), 500

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# MARK ALL NOTIFICATIONS AS READ
# =========================================================

@notifications_bp.route(
    "/api/notifications/read-all",
    methods=["POST"]
)
def mark_all_read():

    if not is_logged_in():
        return jsonify({
            "success": False,
            "message": "Please login first."
        }), 401

    connection = None
    cursor = None

    try:

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("""
            UPDATE notifications
            SET is_read = TRUE
            WHERE user_id = %s
              AND is_read = FALSE
        """, (session["user_id"],))

        connection.commit()

        return jsonify({
            "success": True,
            "message": "All notifications marked as read."
        }), 200

    except Exception as error:

        if connection:
            connection.rollback()

        print("Mark all notifications error:", error)

        return jsonify({
            "success": False,
            "message": "Failed to update notifications."
        }), 500

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()