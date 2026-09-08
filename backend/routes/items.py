import os
import uuid
from difflib import SequenceMatcher

from flask import Blueprint, request, jsonify, session, current_app
from werkzeug.utils import secure_filename

from database import get_db_connection


items_bp = Blueprint("items", __name__)


# =========================================================
# CONSTANTS
# =========================================================

ALLOWED_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "gif",
    "webp"
}

MAX_MATCH_SCORE = 100
MIN_MATCH_SCORE = 50


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def is_logged_in():
    return "user_id" in session


def allowed_file(filename):
    if not filename or "." not in filename:
        return False

    extension = filename.rsplit(".", 1)[1].lower()

    return extension in ALLOWED_EXTENSIONS


def save_uploaded_image(file):
    """
    Save uploaded image and return relative image path.
    Returns None if no image was uploaded.
    """

    if not file or not file.filename:
        return None

    if not allowed_file(file.filename):
        raise ValueError(
            "Invalid image format. "
            "Allowed formats: PNG, JPG, JPEG, GIF, WEBP."
        )

    original_name = secure_filename(file.filename)

    extension = original_name.rsplit(".", 1)[1].lower()

    unique_name = f"{uuid.uuid4().hex}.{extension}"

    upload_folder = current_app.config["UPLOAD_FOLDER"]

    os.makedirs(upload_folder, exist_ok=True)

    file_path = os.path.join(
        upload_folder,
        unique_name
    )

    file.save(file_path)

    return f"/uploads/{unique_name}"


def calculate_match_score(new_item, existing_item):
    """
    Calculate match score between lost and found items.

    Category  : 40 points
    Location  : 30 points
    Title     : 20 points
    Description: 10 points
    """

    score = 0

    # -----------------------------------------------------
    # CATEGORY
    # -----------------------------------------------------

    category_1 = (new_item.get("category") or "").strip().lower()
    category_2 = (existing_item.get("category") or "").strip().lower()

    if category_1 and category_2 and category_1 == category_2:
        score += 40

    # -----------------------------------------------------
    # LOCATION
    # -----------------------------------------------------

    location_1 = (new_item.get("location") or "").strip().lower()
    location_2 = (existing_item.get("location") or "").strip().lower()

    if location_1 and location_2:

        location_similarity = SequenceMatcher(
            None,
            location_1,
            location_2
        ).ratio()

        if location_similarity >= 0.60:
            score += 30

    # -----------------------------------------------------
    # TITLE
    # -----------------------------------------------------

    title_1 = (new_item.get("title") or "").strip().lower()
    title_2 = (existing_item.get("title") or "").strip().lower()

    if title_1 and title_2:

        title_similarity = SequenceMatcher(
            None,
            title_1,
            title_2
        ).ratio()

        if title_similarity >= 0.50:
            score += 20

    # -----------------------------------------------------
    # DESCRIPTION
    # -----------------------------------------------------

    description_1 = (
        new_item.get("description") or ""
    ).strip().lower()

    description_2 = (
        existing_item.get("description") or ""
    ).strip().lower()

    if description_1 and description_2:

        description_similarity = SequenceMatcher(
            None,
            description_1,
            description_2
        ).ratio()

        if description_similarity >= 0.30:
            score += 10

    return score


def create_matches_for_item(
    cursor,
    new_item_id,
    item_type,
    item_data
):
    """
    Find opposite-type active items and create matches.
    """

    opposite_type = (
        "found"
        if item_type == "lost"
        else "lost"
    )

    cursor.execute(
        """
        SELECT
            id,
            title,
            category,
            description,
            location
        FROM items
        WHERE item_type = %s
          AND status = 'active'
          AND id != %s
        """,
        (
            opposite_type,
            new_item_id
        )
    )

    existing_items = cursor.fetchall()

    created_matches = 0

    for existing in existing_items:

        score = calculate_match_score(
            item_data,
            existing
        )

        if score < MIN_MATCH_SCORE:
            continue

        if item_type == "lost":

            lost_id = new_item_id
            found_id = existing["id"]

        else:

            lost_id = existing["id"]
            found_id = new_item_id

        cursor.execute(
            """
            SELECT id
            FROM matches
            WHERE lost_item_id = %s
              AND found_item_id = %s
            """,
            (
                lost_id,
                found_id
            )
        )

        existing_match = cursor.fetchone()

        if existing_match:

            cursor.execute(
                """
                UPDATE matches
                SET match_score = %s
                WHERE id = %s
                """,
                (
                    score,
                    existing_match["id"]
                )
            )

        else:

            cursor.execute(
                """
                INSERT INTO matches
                (
                    lost_item_id,
                    found_item_id,
                    match_score
                )
                VALUES (%s, %s, %s)
                """,
                (
                    lost_id,
                    found_id,
                    score
                )
            )

            created_matches += 1

    return created_matches


# =========================================================
# CREATE ITEM
# POST /api/items
# =========================================================

@items_bp.route("/api/items", methods=["POST"])
def create_item():

    if not is_logged_in():

        return jsonify({
            "success": False,
            "message": "Please login first."
        }), 401

    connection = None
    cursor = None

    try:

        # -------------------------------------------------
        # SUPPORT JSON + FORM DATA
        # -------------------------------------------------

        if request.is_json:

            data = request.get_json(
                silent=True
            ) or {}

            title = data.get("title")
            category = data.get("category")
            description = data.get("description")
            location = data.get("location")
            item_date = data.get("item_date")
            item_type = data.get("item_type")

            image_file = None

        else:

            title = request.form.get("title")
            category = request.form.get("category")
            description = request.form.get("description")
            location = request.form.get("location")
            item_date = request.form.get("item_date")
            item_type = request.form.get("item_type")

            image_file = request.files.get("image")

        # -------------------------------------------------
        # CLEAN VALUES
        # -------------------------------------------------

        title = (title or "").strip()
        category = (category or "").strip()
        description = (description or "").strip()
        location = (location or "").strip()
        item_date = (item_date or "").strip()
        item_type = (item_type or "").strip().lower()

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------

        if not title:
            return jsonify({
                "success": False,
                "message": "Title is required."
            }), 400

        if not category:
            return jsonify({
                "success": False,
                "message": "Category is required."
            }), 400

        if not location:
            return jsonify({
                "success": False,
                "message": "Location is required."
            }), 400

        if not item_date:
            return jsonify({
                "success": False,
                "message": "Item date is required."
            }), 400

        if item_type not in ["lost", "found"]:

            return jsonify({
                "success": False,
                "message": "Invalid item type."
            }), 400

        # -------------------------------------------------
        # IMAGE
        # -------------------------------------------------

        image_path = None

        if image_file:

            try:

                image_path = save_uploaded_image(
                    image_file
                )

            except ValueError as error:

                return jsonify({
                    "success": False,
                    "message": str(error)
                }), 400

        # -------------------------------------------------
        # DATABASE
        # -------------------------------------------------

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        # -------------------------------------------------
        # INSERT ITEM
        # -------------------------------------------------

        cursor.execute(
            """
            INSERT INTO items
            (
                user_id,
                title,
                category,
                description,
                location,
                item_date,
                item_type,
                image_path
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
            """,
            (
                session["user_id"],
                title,
                category,
                description,
                location,
                item_date,
                item_type,
                image_path
            )
        )

        new_item_id = cursor.lastrowid

        # -------------------------------------------------
        # CREATE MATCHES
        # -------------------------------------------------

        item_data = {
            "title": title,
            "category": category,
            "description": description,
            "location": location
        }

        matches_created = create_matches_for_item(
            cursor,
            new_item_id,
            item_type,
            item_data
        )

        connection.commit()

        return jsonify({
            "success": True,
            "message": "Item reported successfully.",
            "item_id": new_item_id,
            "matches_created": matches_created
        }), 201

    except Exception as error:

        if connection:
            connection.rollback()

        print("Create item error:", error)

        return jsonify({
            "success": False,
            "message": "Failed to report item."
        }), 500

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# GET ALL ITEMS
#
# GET /api/items
#
# Optional:
# ?type=lost
# ?type=found
# ?category=Electronics
# ?location=Library
# ?search=phone
# ?status=active
# =========================================================

@items_bp.route("/api/items", methods=["GET"])
def get_items():

    connection = None
    cursor = None

    try:

        item_type = (
            request.args.get("type") or ""
        ).strip().lower()

        category = (
            request.args.get("category") or ""
        ).strip()

        location = (
            request.args.get("location") or ""
        ).strip()

        search = (
            request.args.get("search") or ""
        ).strip()

        status = (
            request.args.get("status") or ""
        ).strip().lower()

        query = """
            SELECT
                id,
                user_id,
                title,
                category,
                description,
                location,
                item_date,
                item_type,
                status,
                image_path,
                created_at
            FROM items
            WHERE 1 = 1
        """

        params = []

        # -------------------------------------------------
        # TYPE
        # -------------------------------------------------

        if item_type in ["lost", "found"]:

            query += """
                AND item_type = %s
            """

            params.append(item_type)

        # -------------------------------------------------
        # CATEGORY
        # -------------------------------------------------

        if category:

            query += """
                AND category = %s
            """

            params.append(category)

        # -------------------------------------------------
        # LOCATION
        # -------------------------------------------------

        if location:

            query += """
                AND location LIKE %s
            """

            params.append(
                f"%{location}%"
            )

        # -------------------------------------------------
        # SEARCH
        # -------------------------------------------------

        if search:

            query += """
                AND (
                    title LIKE %s
                    OR description LIKE %s
                    OR category LIKE %s
                    OR location LIKE %s
                )
            """

            search_value = f"%{search}%"

            params.extend([
                search_value,
                search_value,
                search_value,
                search_value
            ])

        # -------------------------------------------------
        # STATUS
        # -------------------------------------------------

        if status:

            query += """
                AND status = %s
            """

            params.append(status)

        query += """
            ORDER BY created_at DESC
        """

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        cursor.execute(
            query,
            tuple(params)
        )

        items = cursor.fetchall()

        return jsonify({
            "success": True,
            "count": len(items),
            "items": items
        }), 200

    except Exception as error:

        print("Get items error:", error)

        return jsonify({
            "success": False,
            "message": "Failed to fetch items."
        }), 500

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# GET SINGLE ITEM
# GET /api/items/<item_id>
# =========================================================

@items_bp.route(
    "/api/items/<int:item_id>",
    methods=["GET"]
)
def get_item(item_id):

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        cursor.execute(
            """
            SELECT
                items.id,
                items.user_id,
                items.title,
                items.category,
                items.description,
                items.location,
                items.item_date,
                items.item_type,
                items.status,
                items.image_path,
                items.created_at,
                users.full_name
            FROM items
            JOIN users
                ON items.user_id = users.id
            WHERE items.id = %s
            """,
            (item_id,)
        )

        item = cursor.fetchone()

        if not item:

            return jsonify({
                "success": False,
                "message": "Item not found."
            }), 404

        return jsonify({
            "success": True,
            "item": item
        }), 200

    except Exception as error:

        print("Get item error:", error)

        return jsonify({
            "success": False,
            "message": "Failed to fetch item."
        }), 500

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# GET POSSIBLE MATCHES
#
# GET /api/matches
# =========================================================

@items_bp.route(
    "/api/matches",
    methods=["GET"]
)
def get_matches():

    if not is_logged_in():

        return jsonify({
            "success": False,
            "message": "Please login first."
        }), 401

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        user_id = session["user_id"]

        cursor.execute(
            """
            SELECT DISTINCT
                m.id AS match_id,
                m.match_score,
                m.status AS match_status,

                lost.id AS lost_item_id,
                lost.title AS lost_title,
                lost.category AS lost_category,
                lost.description AS lost_description,
                lost.location AS lost_location,
                lost.item_date AS lost_date,
                lost.image_path AS lost_image,

                found.id AS found_item_id,
                found.title AS found_title,
                found.category AS found_category,
                found.description AS found_description,
                found.location AS found_location,
                found.item_date AS found_date,
                found.image_path AS found_image

            FROM matches m

            JOIN items lost
                ON m.lost_item_id = lost.id

            JOIN items found
                ON m.found_item_id = found.id

            WHERE
                (
                    lost.user_id = %s
                    OR found.user_id = %s
                )

            ORDER BY
                m.match_score DESC,
                m.id DESC
            """,
            (
                user_id,
                user_id
            )
        )

        matches = cursor.fetchall()

        return jsonify({
            "success": True,
            "count": len(matches),
            "matches": matches
        }), 200

    except Exception as error:

        print("Get matches error:", error)

        return jsonify({
            "success": False,
            "message": "Failed to fetch possible matches."
        }), 500

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# GET USER DASHBOARD
# GET /api/dashboard
# =========================================================

@items_bp.route(
    "/api/dashboard",
    methods=["GET"]
)
def get_dashboard():

    if not is_logged_in():

        return jsonify({
            "success": False,
            "message": "Please login first."
        }), 401

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        user_id = session["user_id"]

        # -------------------------------------------------
        # LOST / FOUND COUNTS
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                SUM(
                    CASE
                        WHEN item_type = 'lost'
                        THEN 1
                        ELSE 0
                    END
                ) AS lost_count,

                SUM(
                    CASE
                        WHEN item_type = 'found'
                        THEN 1
                        ELSE 0
                    END
                ) AS found_count

            FROM items
            WHERE user_id = %s
            """,
            (user_id,)
        )

        counts = cursor.fetchone()

        lost_count = (
            counts["lost_count"] or 0
        )

        found_count = (
            counts["found_count"] or 0
        )

        # -------------------------------------------------
        # MATCH COUNT
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT COUNT(DISTINCT m.id)
                AS match_count

            FROM matches m

            JOIN items lost
                ON m.lost_item_id = lost.id

            JOIN items found
                ON m.found_item_id = found.id

            WHERE
                (
                    lost.user_id = %s
                    OR found.user_id = %s
                )

                AND m.status = 'pending'
            """,
            (
                user_id,
                user_id
            )
        )

        match_result = cursor.fetchone()

        match_count = (
            match_result["match_count"] or 0
        )

        # -------------------------------------------------
        # CLAIM COUNT
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT COUNT(*) AS claim_count
            FROM claims
            WHERE claimant_id = %s
            """,
            (user_id,)
        )

        claim_result = cursor.fetchone()

        claim_count = (
            claim_result["claim_count"] or 0
        )

        # -------------------------------------------------
        # RECENT REPORTS
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                id,
                title,
                category,
                location,
                item_date,
                item_type,
                status,
                image_path,
                created_at
            FROM items
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT 5
            """,
            (user_id,)
        )

        recent_reports = cursor.fetchall()

        return jsonify({

            "success": True,

            "user": {
                "id": user_id,
                "name": session.get(
                    "user_name"
                ),
                "role": session.get(
                    "user_role"
                )
            },

            "stats": {

                "lost": lost_count,

                "found": found_count,

                "matches": match_count,

                "claims": claim_count
            },

            "recent_reports": recent_reports

        }), 200

    except Exception as error:

        print("Dashboard error:", error)

        return jsonify({
            "success": False,
            "message": "Failed to load dashboard."
        }), 500

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# HOME PAGE STATS
# GET /api/stats
# =========================================================

@items_bp.route(
    "/api/stats",
    methods=["GET"]
)
def get_stats():

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        cursor.execute(
            """
            SELECT

                SUM(
                    CASE
                        WHEN item_type = 'lost'
                        THEN 1
                        ELSE 0
                    END
                ) AS lost_items,

                SUM(
                    CASE
                        WHEN item_type = 'found'
                        THEN 1
                        ELSE 0
                    END
                ) AS found_items,

                SUM(
                    CASE
                        WHEN status = 'returned'
                        THEN 1
                        ELSE 0
                    END
                ) AS returned_items

            FROM items
            """
        )

        item_stats = cursor.fetchone()

        cursor.execute(
            """
            SELECT COUNT(*) AS total_users
            FROM users
            """
        )

        user_stats = cursor.fetchone()

        return jsonify({

            "success": True,

            "stats": {

                "lost": (
                    item_stats["lost_items"]
                    or 0
                ),

                "found": (
                    item_stats["found_items"]
                    or 0
                ),

                "users": (
                    user_stats["total_users"]
                    or 0
                ),

                "returned": (
                    item_stats["returned_items"]
                    or 0
                )
            }

        }), 200

    except Exception as error:

        print("Stats error:", error)

        return jsonify({
            "success": False,
            "message": "Failed to load statistics."
        }), 500

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# CREATE CLAIM
#
# POST /api/claims
# =========================================================

@items_bp.route(
    "/api/claims",
    methods=["POST"]
)
def create_claim():

    if not is_logged_in():

        return jsonify({
            "success": False,
            "message": "Please login first."
        }), 401

    data = request.get_json(
        silent=True
    ) or {}

    item_id = data.get("item_id")
    claim_description = (
        data.get("claim_description")
        or ""
    ).strip()

    if not item_id:

        return jsonify({
            "success": False,
            "message": "Item ID is required."
        }), 400

    if not claim_description:

        return jsonify({
            "success": False,
            "message": "Claim description is required."
        }), 400

    if len(claim_description) < 10:

        return jsonify({
            "success": False,
            "message": (
                "Claim description must contain "
                "at least 10 characters."
            )
        }), 400

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        # -------------------------------------------------
        # GET ITEM
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                id,
                user_id,
                item_type,
                status
            FROM items
            WHERE id = %s
            """,
            (item_id,)
        )

        item = cursor.fetchone()

        if not item:

            return jsonify({
                "success": False,
                "message": "Item not found."
            }), 404

        # -------------------------------------------------
        # ONLY FOUND ITEMS
        # -------------------------------------------------

        if item["item_type"] != "found":

            return jsonify({
                "success": False,
                "message": (
                    "Only found items can be claimed."
                )
            }), 400

        # -------------------------------------------------
        # ACTIVE ITEM
        # -------------------------------------------------

        if item["status"] != "active":

            return jsonify({
                "success": False,
                "message": (
                    "This item is no longer "
                    "available for claim."
                )
            }), 400

        # -------------------------------------------------
        # CANNOT CLAIM OWN ITEM
        # -------------------------------------------------

        if item["user_id"] == session["user_id"]:

            return jsonify({
                "success": False,
                "message": (
                    "You cannot claim your "
                    "own reported item."
                )
            }), 400

        # -------------------------------------------------
        # DUPLICATE PENDING CLAIM
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT id
            FROM claims
            WHERE item_id = %s
              AND claimant_id = %s
              AND status = 'pending'
            """,
            (
                item_id,
                session["user_id"]
            )
        )

        existing_claim = cursor.fetchone()

        if existing_claim:

            return jsonify({
                "success": False,
                "message": (
                    "You have already submitted "
                    "a claim for this item."
                )
            }), 409

        # -------------------------------------------------
        # CREATE CLAIM
        # -------------------------------------------------

        cursor.execute(
            """
            INSERT INTO claims
            (
                item_id,
                claimant_id,
                claim_description
            )
            VALUES
            (
                %s,
                %s,
                %s
            )
            """,
            (
                item_id,
                session["user_id"],
                claim_description
            )
        )

        claim_id = cursor.lastrowid

        connection.commit()

        return jsonify({
            "success": True,
            "message": "Claim submitted successfully.",
            "claim_id": claim_id
        }), 201

    except Exception as error:

        if connection:
            connection.rollback()

        print("Create claim error:", error)

        return jsonify({
            "success": False,
            "message": "Failed to submit claim."
        }), 500

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# GET MY CLAIMS
#
# GET /api/claims/my
# =========================================================

@items_bp.route(
    "/api/claims/my",
    methods=["GET"]
)
def get_my_claims():

    if not is_logged_in():

        return jsonify({
            "success": False,
            "message": "Please login first."
        }), 401

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        cursor.execute(
            """
            SELECT

                c.id,

                c.item_id,

                c.claim_description,

                c.status,

                c.created_at,

                items.title,

                items.category,

                items.location,

                items.item_type,

                items.status AS item_status,

                items.image_path

            FROM claims c

            JOIN items
                ON c.item_id = items.id

            WHERE c.claimant_id = %s

            ORDER BY
                c.created_at DESC
            """,
            (session["user_id"],)
        )

        claims = cursor.fetchall()

        return jsonify({
            "success": True,
            "count": len(claims),
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