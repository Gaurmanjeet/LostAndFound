import csv
import io

from flask import Blueprint, jsonify, session, Response

from database import get_db_connection


admin_bp = Blueprint("admin", __name__)


# =========================================================
# ADMIN CHECK
# =========================================================

def is_admin():
    return (
        "user_id" in session
        and session.get("user_role") == "admin"
    )


# =========================================================
# ADMIN DASHBOARD
# =========================================================

@admin_bp.route("/api/admin/dashboard", methods=["GET"])
def admin_dashboard():

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

        # Total users
        cursor.execute("SELECT COUNT(*) AS total_users FROM users")
        total_users = cursor.fetchone()["total_users"]

        # Total items
        cursor.execute("SELECT COUNT(*) AS total_items FROM items")
        total_items = cursor.fetchone()["total_items"]

        # Lost
        cursor.execute("""
            SELECT COUNT(*) AS lost_items
            FROM items
            WHERE item_type = 'lost'
        """)
        lost_items = cursor.fetchone()["lost_items"]

        # Found
        cursor.execute("""
            SELECT COUNT(*) AS found_items
            FROM items
            WHERE item_type = 'found'
        """)
        found_items = cursor.fetchone()["found_items"]

        # Active
        cursor.execute("""
            SELECT COUNT(*) AS active_items
            FROM items
            WHERE status = 'active'
        """)
        active_items = cursor.fetchone()["active_items"]

        # Returned
        cursor.execute("""
            SELECT COUNT(*) AS returned_items
            FROM items
            WHERE status = 'returned'
        """)
        returned_items = cursor.fetchone()["returned_items"]

        # Pending claims
        cursor.execute("""
            SELECT COUNT(*) AS pending_claims
            FROM claims
            WHERE status = 'pending'
        """)
        pending_claims = cursor.fetchone()["pending_claims"]

        # Approved claims
        cursor.execute("""
            SELECT COUNT(*) AS approved_claims
            FROM claims
            WHERE status = 'approved'
        """)
        approved_claims = cursor.fetchone()["approved_claims"]

        # Rejected claims
        cursor.execute("""
            SELECT COUNT(*) AS rejected_claims
            FROM claims
            WHERE status = 'rejected'
        """)
        rejected_claims = cursor.fetchone()["rejected_claims"]

        # Matches
        cursor.execute("""
            SELECT COUNT(*) AS total_matches
            FROM matches
        """)
        total_matches = cursor.fetchone()["total_matches"]

        return jsonify({
            "success": True,
            "stats": {
                "total_users": total_users,
                "total_items": total_items,
                "lost_items": lost_items,
                "found_items": found_items,
                "active_items": active_items,
                "returned_items": returned_items,
                "pending_claims": pending_claims,
                "approved_claims": approved_claims,
                "rejected_claims": rejected_claims,
                "total_matches": total_matches
            }
        }), 200

    except Exception as error:
        print("Admin dashboard error:", error)

        return jsonify({
            "success": False,
            "message": "Failed to load admin dashboard."
        }), 500

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# GET ALL REPORTS
# =========================================================

@admin_bp.route("/api/admin/reports", methods=["GET"])
def get_all_reports():

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
                i.id,
                i.user_id,
                i.title,
                i.category,
                i.description,
                i.location,
                i.item_date,
                i.item_type,
                i.status,
                i.image_path,
                i.created_at,

                u.full_name AS reporter_name,
                u.email AS reporter_email,

                COALESCE(
                    (
                        SELECT MAX(m.match_score)
                        FROM matches m
                        WHERE
                            m.lost_item_id = i.id
                            OR m.found_item_id = i.id
                    ),
                    0
                ) AS match_score

            FROM items i

            JOIN users u
                ON i.user_id = u.id

            ORDER BY i.created_at DESC
        """)

        reports = cursor.fetchall()

        return jsonify({
            "success": True,
            "reports": reports
        }), 200

    except Exception as error:
        print("Get admin reports error:", error)

        return jsonify({
            "success": False,
            "message": "Failed to fetch reports."
        }), 500

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# DOWNLOAD ALL REPORTS - CSV
# =========================================================

@admin_bp.route("/api/admin/reports/download", methods=["GET"])
def download_reports():

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
                i.id,
                i.title,
                i.category,
                i.description,
                i.location,
                i.item_date,
                i.item_type,
                i.status,
                i.image_path,
                i.created_at,
                u.full_name AS reporter_name,
                u.email AS reporter_email,

                COALESCE(
                    (
                        SELECT MAX(m.match_score)
                        FROM matches m
                        WHERE
                            m.lost_item_id = i.id
                            OR m.found_item_id = i.id
                    ),
                    0
                ) AS match_score

            FROM items i

            JOIN users u
                ON i.user_id = u.id

            ORDER BY i.created_at DESC
        """)

        reports = cursor.fetchall()

        output = io.StringIO()

        writer = csv.writer(output)

        writer.writerow([
            "ID",
            "Title",
            "Category",
            "Description",
            "Location",
            "Item Date",
            "Type",
            "Status",
            "Match Score",
            "Reporter",
            "Reporter Email",
            "Image",
            "Created At"
        ])

        for report in reports:
            writer.writerow([
                report.get("id"),
                report.get("title"),
                report.get("category"),
                report.get("description"),
                report.get("location"),
                report.get("item_date"),
                report.get("item_type"),
                report.get("status"),
                report.get("match_score"),
                report.get("reporter_name"),
                report.get("reporter_email"),
                report.get("image_path"),
                report.get("created_at")
            ])

        csv_data = output.getvalue()
        output.close()

        return Response(
            csv_data,
            mimetype="text/csv",
            headers={
                "Content-Disposition":
                    "attachment; filename=lost_found_reports.csv"
            }
        )

    except Exception as error:
        print("Download reports error:", error)

        return jsonify({
            "success": False,
            "message": "Failed to generate report."
        }), 500

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# GET ALL USERS
# =========================================================

@admin_bp.route("/api/admin/users", methods=["GET"])
def get_all_users():

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
                id,
                full_name,
                email,
                role,
                created_at
            FROM users
            ORDER BY created_at DESC
        """)

        users = cursor.fetchall()

        return jsonify({
            "success": True,
            "users": users
        }), 200

    except Exception as error:
        print("Get users error:", error)

        return jsonify({
            "success": False,
            "message": "Failed to fetch users."
        }), 500

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# GET ALL CLAIMS
# =========================================================

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
                c.id,
                c.id AS claim_id,
                c.item_id,
                c.claimant_id,
                c.claim_description,
                c.status,
                c.status AS claim_status,
                c.created_at,

                claimant.full_name AS claimant_name,
                claimant.email AS claimant_email,

                item.title AS item_title,
                item.category,
                item.description AS item_description,
                item.location,
                item.item_date,
                item.item_type,
                item.status AS item_status,

                reporter.full_name AS reporter_name,
                reporter.email AS reporter_email,

                COALESCE(
                    (
                        SELECT MAX(m.match_score)
                        FROM matches m
                        WHERE
                            m.found_item_id = item.id
                            AND m.lost_item_id IN (
                                SELECT li.id
                                FROM items li
                                WHERE li.user_id = c.claimant_id
                                  AND li.item_type = 'lost'
                            )
                    ),
                    0
                ) AS match_score

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
        print("Get claims error:", error)

        return jsonify({
            "success": False,
            "message": "Failed to fetch claims."
        }), 500

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# GET SINGLE CLAIM
# =========================================================

@admin_bp.route(
    "/api/admin/claims/<int:claim_id>",
    methods=["GET"]
)
def get_claim(claim_id):

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
                c.id,
                c.item_id,
                c.claimant_id,
                c.claim_description,
                c.status,
                c.created_at,

                claimant.full_name AS claimant_name,
                claimant.email AS claimant_email,

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
        print("Get claim error:", error)

        return jsonify({
            "success": False,
            "message": "Failed to fetch claim."
        }), 500

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# APPROVE CLAIM
# =========================================================

@admin_bp.route(
    "/api/admin/claims/<int:claim_id>/approve",
    methods=["POST"]
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

        # -------------------------------------------------
        # GET CLAIM
        # -------------------------------------------------

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

        # -------------------------------------------------
        # GET FOUND ITEM
        # -------------------------------------------------

        cursor.execute("""
            SELECT
                id,
                user_id,
                title,
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

        if item["item_type"] != "found":
            return jsonify({
                "success": False,
                "message": "Only found items can be claimed."
            }), 400

        # -------------------------------------------------
        # CHECK MATCH SCORE
        #
        # Claimant must have a lost item that matches
        # this found item with score >= 50.
        # -------------------------------------------------

        cursor.execute("""
            SELECT
                MAX(m.match_score) AS best_match_score
            FROM matches m
            JOIN items lost_item
                ON m.lost_item_id = lost_item.id
            WHERE
                m.found_item_id = %s
                AND lost_item.user_id = %s
                AND lost_item.item_type = 'lost'
                AND m.status IN ('pending', 'approved')
        """, (
            claim["item_id"],
            claim["claimant_id"]
        ))

        match_result = cursor.fetchone()

        best_match_score = match_result["best_match_score"]

        if best_match_score is None:
            return jsonify({
                "success": False,
                "message": (
                    "This claim cannot be approved because "
                    "no matching lost item was found."
                )
            }), 400

        if best_match_score < 50:
            return jsonify({
                "success": False,
                "message": (
                    f"Match score is only {best_match_score}%. "
                    "Minimum required score is 50%."
                )
            }), 400

        # -------------------------------------------------
        # APPROVE CLAIM
        # -------------------------------------------------

        cursor.execute("""
            UPDATE claims
            SET status = 'approved'
            WHERE id = %s
        """, (claim_id,))

        # -------------------------------------------------
        # MARK ITEM RETURNED
        # -------------------------------------------------

        cursor.execute("""
            UPDATE items
            SET status = 'returned'
            WHERE id = %s
        """, (claim["item_id"],))

        # -------------------------------------------------
        # REJECT OTHER PENDING CLAIMS
        # -------------------------------------------------

        cursor.execute("""
            UPDATE claims
            SET status = 'rejected'
            WHERE item_id = %s
              AND id != %s
              AND status = 'pending'
        """, (
            claim["item_id"],
            claim_id
        ))

        # -------------------------------------------------
        # CLOSE RELATED MATCHES
        # -------------------------------------------------

        cursor.execute("""
            UPDATE matches
            SET status = 'closed'
            WHERE
                lost_item_id = %s
                OR found_item_id = %s
        """, (
            claim["item_id"],
            claim["item_id"]
        ))

        # -------------------------------------------------
        # NOTIFICATION TO APPROVED USER
        # -------------------------------------------------

        cursor.execute("""
            INSERT INTO notifications
                (user_id, title, message, type)
            VALUES
                (%s, %s, %s, %s)
        """, (
            claim["claimant_id"],
            "Claim Approved",
            (
                f'Your claim for "{item["title"]}" has been approved. '
                "Please collect your item from the Lost & Found Office "
                "with a valid ID."
            ),
            "claim_approved"
        ))

        connection.commit()

        return jsonify({
            "success": True,
            "message": (
                "Claim approved successfully. "
                "User has been notified."
            ),
            "match_score": best_match_score
        }), 200

    except Exception as error:

        if connection:
            connection.rollback()

        print("Approve claim error:", error)

        return jsonify({
            "success": False,
            "message": "Failed to approve claim."
        }), 500

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# REJECT CLAIM
# =========================================================

@admin_bp.route(
    "/api/admin/claims/<int:claim_id>/reject",
    methods=["POST"]
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
        cursor = connection.cursor(dictionary=True)

        # -------------------------------------------------
        # GET CLAIM + ITEM
        # -------------------------------------------------

        cursor.execute("""
            SELECT
                c.id,
                c.claimant_id,
                c.item_id,
                c.status,
                i.title AS item_title
            FROM claims c
            JOIN items i
                ON c.item_id = i.id
            WHERE c.id = %s
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
                "message": "Claim has already been processed."
            }), 400

        # -------------------------------------------------
        # REJECT CLAIM
        # -------------------------------------------------

        cursor.execute("""
            UPDATE claims
            SET status = 'rejected'
            WHERE id = %s
              AND status = 'pending'
        """, (claim_id,))

        # -------------------------------------------------
        # NOTIFICATION TO USER
        # -------------------------------------------------

        cursor.execute("""
            INSERT INTO notifications
                (user_id, title, message, type)
            VALUES
                (%s, %s, %s, %s)
        """, (
            claim["claimant_id"],
            "Claim Rejected",
            (
                f'Your claim for "{claim["item_title"]}" '
                "has been rejected by the Lost & Found administrator."
            ),
            "claim_rejected"
        ))

        connection.commit()

        return jsonify({
            "success": True,
            "message": (
                "Claim rejected successfully. "
                "User has been notified."
            )
        }), 200

    except Exception as error:

        if connection:
            connection.rollback()

        print("Reject claim error:", error)

        return jsonify({
            "success": False,
            "message": "Failed to reject claim."
        }), 500

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# MARK ITEM RETURNED MANUALLY
# =========================================================

@admin_bp.route(
    "/api/admin/items/<int:item_id>/returned",
    methods=["POST"]
)
def mark_item_returned(item_id):

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
                id,
                title,
                status
            FROM items
            WHERE id = %s
        """, (item_id,))

        item = cursor.fetchone()

        if not item:
            return jsonify({
                "success": False,
                "message": "Item not found."
            }), 404

        cursor.execute("""
            UPDATE items
            SET status = 'returned'
            WHERE id = %s
        """, (item_id,))

        # Close related matches
        cursor.execute("""
            UPDATE matches
            SET status = 'closed'
            WHERE
                lost_item_id = %s
                OR found_item_id = %s
        """, (
            item_id,
            item_id
        ))

        connection.commit()

        return jsonify({
            "success": True,
            "message": "Item marked as returned."
        }), 200

    except Exception as error:

        if connection:
            connection.rollback()

        print("Return item error:", error)

        return jsonify({
            "success": False,
            "message": "Failed to update item."
        }), 500

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()