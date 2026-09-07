from flask import Blueprint, jsonify, session
from database import get_db_connection

admin_bp = Blueprint("admin", __name__)


# ==========================================
# ADMIN CHECK
# ==========================================

def is_admin():
    return (
        "user_id" in session
        and session.get("user_role") == "admin"
    )


# ==========================================
# ADMIN DASHBOARD STATS
# ==========================================

@admin_bp.route("/api/admin/stats", methods=["GET"])
def admin_stats():

    if not is_admin():
        return jsonify({
            "success": False,
            "message": "Admin access required."
        }), 403

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT COUNT(*) AS total_users
            FROM users
        """)
        total_users = cursor.fetchone()["total_users"]

        cursor.execute("""
            SELECT COUNT(*) AS total_items
            FROM items
        """)
        total_items = cursor.fetchone()["total_items"]

        cursor.execute("""
            SELECT COUNT(*) AS total_lost
            FROM items
            WHERE item_type = 'lost'
        """)
        total_lost = cursor.fetchone()["total_lost"]

        cursor.execute("""
            SELECT COUNT(*) AS total_found
            FROM items
            WHERE item_type = 'found'
        """)
        total_found = cursor.fetchone()["total_found"]

        cursor.execute("""
            SELECT COUNT(*) AS pending_claims
            FROM claims
            WHERE status = 'pending'
        """)
        pending_claims = cursor.fetchone()["pending_claims"]

        cursor.execute("""
            SELECT COUNT(*) AS approved_claims
            FROM claims
            WHERE status = 'approved'
        """)
        approved_claims = cursor.fetchone()["approved_claims"]

        cursor.execute("""
            SELECT COUNT(*) AS rejected_claims
            FROM claims
            WHERE status = 'rejected'
        """)
        rejected_claims = cursor.fetchone()["rejected_claims"]

        cursor.execute("""
            SELECT COUNT(*) AS returned_items
            FROM items
            WHERE status = 'returned'
        """)
        returned_items = cursor.fetchone()["returned_items"]

        return jsonify({
            "success": True,
            "stats": {
                "users": total_users,
                "items": total_items,
                "lost": total_lost,
                "found": total_found,
                "pending_claims": pending_claims,
                "approved_claims": approved_claims,
                "rejected_claims": rejected_claims,
                "returned": returned_items
            }
        }), 200

    except Exception as error:
        print(error)

        return jsonify({
            "success": False,
            "message": "Failed to load admin statistics."
        }), 500

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ==========================================
# GET ALL CLAIMS
# ==========================================

@admin_bp.route("/api/admin/claims", methods=["GET"])
def get_all_claims():

    if not is_admin():
        return jsonify({
            "success": False,
            "message": "Admin access required."
        }), 403

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                c.id AS claim_id,
                c.claim_description,
                c.status AS claim_status,
                c.created_at,

                claimant.id AS claimant_id,
                claimant.full_name AS claimant_name,
                claimant.email AS claimant_email,

                item.id AS item_id,
                item.title AS item_title,
                item.category,
                item.description AS item_description,
                item.location,
                item.item_date,
                item.item_type,
                item.status AS item_status,

                reporter.id AS reporter_id,
                reporter.full_name AS reporter_name,
                reporter.email AS reporter_email

            FROM claims c

            JOIN users claimant
                ON c.claimant_id = claimant.id

            JOIN items item
                ON c.item_id = item.id

            JOIN users reporter
                ON item.user_id = reporter.id

            ORDER BY
                CASE
                    WHEN c.status = 'pending' THEN 1
                    WHEN c.status = 'approved' THEN 2
                    ELSE 3
                END,
                c.created_at DESC
        """)

        claims = cursor.fetchall()

        return jsonify({
            "success": True,
            "claims": claims
        }), 200

    except Exception as error:
        print(error)

        return jsonify({
            "success": False,
            "message": "Failed to fetch claims."
        }), 500

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ==========================================
# APPROVE CLAIM
# ==========================================

@admin_bp.route(
    "/api/admin/claims/<int:claim_id>/approve",
    methods=["PUT"]
)
def approve_claim(claim_id):

    if not is_admin():
        return jsonify({
            "success": False,
            "message": "Admin access required."
        }), 403

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Get claim
        cursor.execute("""
            SELECT
                id,
                item_id,
                claimant_id,
                status
            FROM claims
            WHERE id = %s
        """, (claim_id,))

        claim = cursor.fetchone()

        if not claim:
            return jsonify({
                "success": False,
                "message": "Claim not found."
            }), 404

        if claim["status"] != "pending":
            return jsonify({
                "success": False,
                "message": "This claim has already been processed."
            }), 400

        # Check item
        cursor.execute("""
            SELECT
                id,
                status,
                item_type
            FROM items
            WHERE id = %s
        """, (claim["item_id"],))

        item = cursor.fetchone()

        if not item:
            return jsonify({
                "success": False,
                "message": "Item not found."
            }), 404

        if item["status"] != "active":
            return jsonify({
                "success": False,
                "message": "This item is no longer active."
            }), 400

        # Approve selected claim
        cursor.execute("""
            UPDATE claims
            SET status = 'approved'
            WHERE id = %s
        """, (claim_id,))

        # Mark item as returned
        cursor.execute("""
            UPDATE items
            SET status = 'returned'
            WHERE id = %s
        """, (claim["item_id"],))

        # Reject all other pending claims
        cursor.execute("""
            UPDATE claims
            SET status = 'rejected'
            WHERE item_id = %s
              AND id != %s
              AND status = 'pending'
        """, (claim["item_id"], claim_id))

        # Close related matches
        cursor.execute("""
            UPDATE matches
            SET status = 'approved'
            WHERE
                (
                    lost_item_id = %s
                    OR found_item_id = %s
                )
        """, (claim["item_id"], claim["item_id"]))

        connection.commit()

        return jsonify({
            "success": True,
            "message": "Claim approved. Item marked as returned."
        }), 200

    except Exception as error:

        if connection:
            connection.rollback()

        print(error)

        return jsonify({
            "success": False,
            "message": "Failed to approve claim."
        }), 500

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ==========================================
# REJECT CLAIM
# ==========================================

@admin_bp.route(
    "/api/admin/claims/<int:claim_id>/reject",
    methods=["PUT"]
)
def reject_claim(claim_id):

    if not is_admin():
        return jsonify({
            "success": False,
            "message": "Admin access required."
        }), 403

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("""
            UPDATE claims
            SET status = 'rejected'
            WHERE id = %s
              AND status = 'pending'
        """, (claim_id,))

        if cursor.rowcount == 0:
            return jsonify({
                "success": False,
                "message": "Claim not found or already processed."
            }), 404

        connection.commit()

        return jsonify({
            "success": True,
            "message": "Claim rejected successfully."
        }), 200

    except Exception as error:

        if connection:
            connection.rollback()

        print(error)

        return jsonify({
            "success": False,
            "message": "Failed to reject claim."
        }), 500

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ==========================================
# GET SINGLE CLAIM
# ==========================================

@admin_bp.route(
    "/api/admin/claims/<int:claim_id>",
    methods=["GET"]
)
def get_single_claim(claim_id):

    if not is_admin():
        return jsonify({
            "success": False,
            "message": "Admin access required."
        }), 403

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                c.id AS claim_id,
                c.claim_description,
                c.status AS claim_status,
                c.created_at,

                claimant.full_name AS claimant_name,
                claimant.email AS claimant_email,

                item.id AS item_id,
                item.title AS item_title,
                item.category,
                item.description AS item_description,
                item.location,
                item.item_date,
                item.item_type,
                item.status AS item_status,

                reporter.full_name AS reporter_name,
                reporter.email AS reporter_email

            FROM claims c

            JOIN users claimant
                ON c.claimant_id = claimant.id

            JOIN items item
                ON c.item_id = item.id

            JOIN users reporter
                ON item.user_id = reporter.id

            WHERE c.id = %s
        """, (claim_id,))

        claim = cursor.fetchone()

        if not claim:
            return jsonify({
                "success": False,
                "message": "Claim not found."
            }), 404

        return jsonify({
            "success": True,
            "claim": claim
        }), 200

    except Exception as error:
        print(error)

        return jsonify({
            "success": False,
            "message": "Failed to fetch claim."
        }), 500

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()