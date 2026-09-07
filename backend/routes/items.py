from flask import (
    Blueprint,
    request,
    jsonify,
    session
)

import os
import uuid
from werkzeug.utils import secure_filename

from database import get_db_connection
from difflib import SequenceMatcher

items_bp = Blueprint("items", __name__)


# =========================================================
# CREATE ITEM + AUTOMATIC MATCHING
# =========================================================

@items_bp.route("/api/items", methods=["POST"])
def create_item():

    if "user_id" not in session:
        return jsonify({
            "success": False,
            "message": "Please login first."
        }), 401

    data = request.get_json()

    title = data.get("title")
    category = data.get("category")
    description = data.get("description")
    location = data.get("location")
    item_date = data.get("item_date")
    item_type = data.get("item_type")

    if not title or not category or not location or not item_date or not item_type:
        return jsonify({
            "success": False,
            "message": "Required fields are missing."
        }), 400

    if item_type not in ["lost", "found"]:
        return jsonify({
            "success": False,
            "message": "Invalid item type."
        }), 400

    connection = None
    cursor = None

    try:

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # -------------------------------------------------
        # 1. INSERT NEW ITEM
        # -------------------------------------------------

        query = """
            INSERT INTO items
            (
                user_id,
                title,
                category,
                description,
                location,
                item_date,
                item_type
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        cursor.execute(
            query,
            (
                session["user_id"],
                title,
                category,
                description,
                location,
                item_date,
                item_type
            )
        )

        new_item_id = cursor.lastrowid


        # -------------------------------------------------
        # 2. FIND OPPOSITE TYPE ITEMS
        # -------------------------------------------------

        opposite_type = "found" if item_type == "lost" else "lost"

        cursor.execute("""
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
        """, (opposite_type, new_item_id))

        existing_items = cursor.fetchall()


        # -------------------------------------------------
        # 3. CALCULATE MATCH SCORE
        # -------------------------------------------------

        for existing in existing_items:

            score = 0

            # Category = 40 points
            if (
                category
                and existing["category"]
                and category.lower() == existing["category"].lower()
            ):
                score += 40


            # Location = 30 points
            location_similarity = SequenceMatcher(
                None,
                location.lower(),
                existing["location"].lower()
            ).ratio()

            if location_similarity >= 0.6:
                score += 30


            # Title = 20 points
            title_similarity = SequenceMatcher(
                None,
                title.lower(),
                existing["title"].lower()
            ).ratio()

            if title_similarity >= 0.5:
                score += 20


            # Description = 10 points
            if description and existing["description"]:

                description_similarity = SequenceMatcher(
                    None,
                    description.lower(),
                    existing["description"].lower()
                ).ratio()

                if description_similarity >= 0.3:
                    score += 10


            # -------------------------------------------------
            # 4. CREATE MATCH IF SCORE >= 50
            # -------------------------------------------------

            if score >= 50:

                if item_type == "lost":

                    lost_id = new_item_id
                    found_id = existing["id"]

                else:

                    lost_id = existing["id"]
                    found_id = new_item_id


                cursor.execute("""
                    INSERT IGNORE INTO matches
                    (
                        lost_item_id,
                        found_item_id,
                        match_score
                    )
                    VALUES (%s, %s, %s)
                """, (
                    lost_id,
                    found_id,
                    score
                ))


        # -------------------------------------------------
        # 5. SAVE EVERYTHING
        # -------------------------------------------------

        connection.commit()


        return jsonify({
            "success": True,
            "message": "Item reported successfully.",
            "item_id": new_item_id
        }), 201


    except Exception as error:

        if connection:
            connection.rollback()

        print(error)

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
# =========================================================

@items_bp.route("/api/items", methods=["GET"])
def get_items():

    connection = None
    cursor = None

    try:

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                id,
                title,
                category,
                description,
                location,
                item_date,
                item_type,
                status,
                image_path
            FROM items
            ORDER BY created_at DESC
        """)

        items = cursor.fetchall()

        return jsonify({
            "success": True,
            "items": items
        }), 200


    except Exception as error:

        print(error)

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
# =========================================================

@items_bp.route("/api/items/<int:item_id>", methods=["GET"])
def get_item(item_id):

    connection = None
    cursor = None

    try:

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                items.id,
                items.title,
                items.category,
                items.description,
                items.location,
                items.item_date,
                items.item_type,
                items.status,
                items.image_path,
                users.full_name
            FROM items
            JOIN users
                ON items.user_id = users.id
            WHERE items.id = %s
        """, (item_id,))

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

        print(error)

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
# DASHBOARD
# =========================================================

@items_bp.route("/api/dashboard", methods=["GET"])
def get_dashboard():

    if "user_id" not in session:

        return jsonify({
            "success": False,
            "message": "Please login first."
        }), 401


    connection = None
    cursor = None

    try:

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        user_id = session["user_id"]


        # -------------------------------------------------
        # USER REPORT COUNTS
        # -------------------------------------------------

        cursor.execute("""
            SELECT
                SUM(item_type = 'lost') AS lost_count,
                SUM(item_type = 'found') AS found_count
            FROM items
            WHERE user_id = %s
        """, (user_id,))

        counts = cursor.fetchone()

        lost_count = counts["lost_count"] or 0
        found_count = counts["found_count"] or 0


        # -------------------------------------------------
        # USER MATCH COUNT
        # -------------------------------------------------

        cursor.execute("""
            SELECT COUNT(*) AS match_count
            FROM matches m
            JOIN items i
                ON (
                    m.lost_item_id = i.id
                    OR m.found_item_id = i.id
                )
            WHERE i.user_id = %s
              AND m.status = 'pending'
        """, (user_id,))

        match_result = cursor.fetchone()

        match_count = match_result["match_count"] or 0


        # -------------------------------------------------
        # RECENT REPORTS
        # -------------------------------------------------

        cursor.execute("""
            SELECT
                id,
                title,
                category,
                location,
                item_date,
                item_type,
                status
            FROM items
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT 5
        """, (user_id,))

        recent_reports = cursor.fetchall()


        return jsonify({

            "success": True,

            "user": {
                "name": session.get("user_name")
            },

            "stats": {
                "lost": lost_count,
                "found": found_count,
                "matches": match_count,
                "claims": 0
            },

            "recent_reports": recent_reports

        }), 200


    except Exception as error:

        print(error)

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
# =========================================================

@items_bp.route("/api/stats", methods=["GET"])
def get_stats():

    connection = None
    cursor = None

    try:

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)


        cursor.execute("""
            SELECT
                SUM(item_type = 'lost') AS lost_items,
                SUM(item_type = 'found') AS found_items,
                SUM(status = 'returned') AS returned_items
            FROM items
        """)

        item_stats = cursor.fetchone()


        cursor.execute("""
            SELECT COUNT(*) AS total_users
            FROM users
        """)

        user_stats = cursor.fetchone()


        return jsonify({

            "success": True,

            "stats": {

                "lost": item_stats["lost_items"] or 0,

                "found": item_stats["found_items"] or 0,

                "users": user_stats["total_users"] or 0,

                "returned": item_stats["returned_items"] or 0

            }

        }), 200


    except Exception as error:

        print(error)

        return jsonify({
            "success": False,
            "message": "Failed to load statistics."
        }), 500


    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()
from flask import Blueprint, request, jsonify, session
from database import get_db_connection
from difflib import SequenceMatcher


items_bp = Blueprint("items", __name__)


# =========================================================
# CREATE ITEM + AUTOMATIC MATCHING
# =========================================================

@items_bp.route("/api/items", methods=["POST"])
def create_item():

    if "user_id" not in session:
        return jsonify({
            "success": False,
            "message": "Please login first."
        }), 401

    data = request.get_json()

    title = data.get("title")
    category = data.get("category")
    description = data.get("description")
    location = data.get("location")
    item_date = data.get("item_date")
    item_type = data.get("item_type")

    if not title or not category or not location or not item_date or not item_type:
        return jsonify({
            "success": False,
            "message": "Required fields are missing."
        }), 400

    if item_type not in ["lost", "found"]:
        return jsonify({
            "success": False,
            "message": "Invalid item type."
        }), 400

    connection = None
    cursor = None

    try:

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # -------------------------------------------------
        # 1. INSERT NEW ITEM
        # -------------------------------------------------

        query = """
            INSERT INTO items
            (
                user_id,
                title,
                category,
                description,
                location,
                item_date,
                item_type
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        cursor.execute(
            query,
            (
                session["user_id"],
                title,
                category,
                description,
                location,
                item_date,
                item_type
            )
        )

        new_item_id = cursor.lastrowid


        # -------------------------------------------------
        # 2. FIND OPPOSITE TYPE ITEMS
        # -------------------------------------------------

        opposite_type = "found" if item_type == "lost" else "lost"

        cursor.execute("""
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
        """, (opposite_type, new_item_id))

        existing_items = cursor.fetchall()


        # -------------------------------------------------
        # 3. CALCULATE MATCH SCORE
        # -------------------------------------------------

        for existing in existing_items:

            score = 0

            # Category = 40 points
            if (
                category
                and existing["category"]
                and category.lower() == existing["category"].lower()
            ):
                score += 40


            # Location = 30 points
            location_similarity = SequenceMatcher(
                None,
                location.lower(),
                existing["location"].lower()
            ).ratio()

            if location_similarity >= 0.6:
                score += 30


            # Title = 20 points
            title_similarity = SequenceMatcher(
                None,
                title.lower(),
                existing["title"].lower()
            ).ratio()

            if title_similarity >= 0.5:
                score += 20


            # Description = 10 points
            if description and existing["description"]:

                description_similarity = SequenceMatcher(
                    None,
                    description.lower(),
                    existing["description"].lower()
                ).ratio()

                if description_similarity >= 0.3:
                    score += 10


            # -------------------------------------------------
            # 4. CREATE MATCH IF SCORE >= 50
            # -------------------------------------------------

            if score >= 50:

                if item_type == "lost":

                    lost_id = new_item_id
                    found_id = existing["id"]

                else:

                    lost_id = existing["id"]
                    found_id = new_item_id


                cursor.execute("""
                    INSERT IGNORE INTO matches
                    (
                        lost_item_id,
                        found_item_id,
                        match_score
                    )
                    VALUES (%s, %s, %s)
                """, (
                    lost_id,
                    found_id,
                    score
                ))


        # -------------------------------------------------
        # 5. SAVE EVERYTHING
        # -------------------------------------------------

        connection.commit()


        return jsonify({
            "success": True,
            "message": "Item reported successfully.",
            "item_id": new_item_id
        }), 201


    except Exception as error:

        if connection:
            connection.rollback()

        print(error)

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
# =========================================================

@items_bp.route("/api/items", methods=["GET"])
def get_items():

    connection = None
    cursor = None

    try:

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                id,
                title,
                category,
                description,
                location,
                item_date,
                item_type,
                status,
                image_path
            FROM items
            ORDER BY created_at DESC
        """)

        items = cursor.fetchall()

        return jsonify({
            "success": True,
            "items": items
        }), 200


    except Exception as error:

        print(error)

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
# =========================================================

@items_bp.route("/api/items/<int:item_id>", methods=["GET"])
def get_item(item_id):

    connection = None
    cursor = None

    try:

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                items.id,
                items.title,
                items.category,
                items.description,
                items.location,
                items.item_date,
                items.item_type,
                items.status,
                items.image_path,
                users.full_name
            FROM items
            JOIN users
                ON items.user_id = users.id
            WHERE items.id = %s
        """, (item_id,))

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

        print(error)

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
# DASHBOARD
# =========================================================

@items_bp.route("/api/dashboard", methods=["GET"])
def get_dashboard():

    if "user_id" not in session:

        return jsonify({
            "success": False,
            "message": "Please login first."
        }), 401


    connection = None
    cursor = None

    try:

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        user_id = session["user_id"]


        # -------------------------------------------------
        # USER REPORT COUNTS
        # -------------------------------------------------

        cursor.execute("""
            SELECT
                SUM(item_type = 'lost') AS lost_count,
                SUM(item_type = 'found') AS found_count
            FROM items
            WHERE user_id = %s
        """, (user_id,))

        counts = cursor.fetchone()

        lost_count = counts["lost_count"] or 0
        found_count = counts["found_count"] or 0


        # -------------------------------------------------
        # USER MATCH COUNT
        # -------------------------------------------------

        cursor.execute("""
            SELECT COUNT(*) AS match_count
            FROM matches m
            JOIN items i
                ON (
                    m.lost_item_id = i.id
                    OR m.found_item_id = i.id
                )
            WHERE i.user_id = %s
              AND m.status = 'pending'
        """, (user_id,))

        match_result = cursor.fetchone()

        match_count = match_result["match_count"] or 0


        # -------------------------------------------------
        # RECENT REPORTS
        # -------------------------------------------------

        cursor.execute("""
            SELECT
                id,
                title,
                category,
                location,
                item_date,
                item_type,
                status
            FROM items
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT 5
        """, (user_id,))

        recent_reports = cursor.fetchall()


        return jsonify({

            "success": True,

            "user": {
                "name": session.get("user_name")
            },

            "stats": {
                "lost": lost_count,
                "found": found_count,
                "matches": match_count,
                "claims": 0
            },

            "recent_reports": recent_reports

        }), 200


    except Exception as error:

        print(error)

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
# =========================================================

@items_bp.route("/api/stats", methods=["GET"])
def get_stats():

    connection = None
    cursor = None

    try:

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)


        cursor.execute("""
            SELECT
                SUM(item_type = 'lost') AS lost_items,
                SUM(item_type = 'found') AS found_items,
                SUM(status = 'returned') AS returned_items
            FROM items
        """)

        item_stats = cursor.fetchone()


        cursor.execute("""
            SELECT COUNT(*) AS total_users
            FROM users
        """)

        user_stats = cursor.fetchone()


        return jsonify({

            "success": True,

            "stats": {

                "lost": item_stats["lost_items"] or 0,

                "found": item_stats["found_items"] or 0,

                "users": user_stats["total_users"] or 0,

                "returned": item_stats["returned_items"] or 0

            }

        }), 200


    except Exception as error:

        print(error)

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
# =========================================================

@items_bp.route("/api/claims", methods=["POST"])
def create_claim():

    if "user_id" not in session:
        return jsonify({
            "success": False,
            "message": "Please login first."
        }), 401

    data = request.get_json()

    item_id = data.get("item_id")
    claim_description = data.get("claim_description")

    if not item_id or not claim_description:
        return jsonify({
            "success": False,
            "message": "Item ID and claim description are required."
        }), 400

    connection = None
    cursor = None

    try:

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Check item
        cursor.execute("""
            SELECT id, user_id, item_type, status
            FROM items
            WHERE id = %s
        """, (item_id,))

        item = cursor.fetchone()

        if not item:
            return jsonify({
                "success": False,
                "message": "Item not found."
            }), 404

        # Only found items can be claimed
        if item["item_type"] != "found":
            return jsonify({
                "success": False,
                "message": "Only found items can be claimed."
            }), 400

        if item["status"] != "active":
            return jsonify({
                "success": False,
                "message": "This item is no longer available for claim."
            }), 400

        # User cannot claim their own found item
        if item["user_id"] == session["user_id"]:
            return jsonify({
                "success": False,
                "message": "You cannot claim your own reported item."
            }), 400

        # Check duplicate claim
        cursor.execute("""
            SELECT id
            FROM claims
            WHERE item_id = %s
              AND claimant_id = %s
              AND status = 'pending'
        """, (
            item_id,
            session["user_id"]
        ))

        existing_claim = cursor.fetchone()

        if existing_claim:
            return jsonify({
                "success": False,
                "message": "You have already submitted a claim for this item."
            }), 400

        # Create claim
        cursor.execute("""
            INSERT INTO claims
            (
                item_id,
                claimant_id,
                claim_description
            )
            VALUES (%s, %s, %s)
        """, (
            item_id,
            session["user_id"],
            claim_description
        ))

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

        print(error)

        return jsonify({
            "success": False,
            "message": "Failed to submit claim."
        }), 500

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()  
@items_bp.route("/api/claims/my", methods=["GET"])
def get_my_claims():

    if "user_id" not in session:
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
                c.id,
                c.item_id,
                c.claim_description,
                c.status,
                c.created_at,

                items.title,
                items.category,
                items.location,
                items.item_type

            FROM claims c

            JOIN items
                ON c.item_id = items.id

            WHERE c.claimant_id = %s

            ORDER BY c.created_at DESC
        """, (session["user_id"],))

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