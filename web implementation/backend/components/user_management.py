from flask import Blueprint, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from flask_bcrypt import Bcrypt
import os
from .middleware import token_required
from .database import add_user_to_db, fetch_user
import sqlite3

PHOTO_FOLDER = r"photos"

user_mgmt_bp = Blueprint("user_management", __name__)
bcrypt = Bcrypt()

# Serve static photos
@user_mgmt_bp.route("/photos/<filename>", methods=["GET"])
def serve_photo(filename):
    """
    Serve voter photos.
    """
    return send_from_directory(PHOTO_FOLDER, filename)


@user_mgmt_bp.route("/add-voter", methods=["POST"])
@token_required
def add_voter():
    """
    Add a voter. Admins only.
    """
    if request.user["role"] != "admin":
        return jsonify({"error": "Unauthorized"}), 403

    data = request.form
    username = data.get("username")
    email = data.get("email")
    photo = request.files.get("photo")

    if not username or not email:
        return jsonify({"error": "Username and email are required"}), 400

    # Use a dummy password
    dummy_password = "Dummy@123"
    password_hash = bcrypt.generate_password_hash(dummy_password).decode("utf-8")

    try:
        add_user_to_db(username, email, password_hash, role="voter")

        if photo:
            voter_id = fetch_user(username)[0]
            filename = secure_filename(f"{voter_id}.jpg")
            photo_path = os.path.join(PHOTO_FOLDER, filename)
            os.makedirs(PHOTO_FOLDER, exist_ok=True)
            photo.save(photo_path)

        return jsonify({"message": "Voter added successfully!"}), 201
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


@user_mgmt_bp.route("/voters", methods=["GET"])
@token_required
def get_voters():
    """
    Retrieve all voters. Admins only.
    """
    if request.user["role"] != "admin":
        return jsonify({"error": "Unauthorized"}), 403

    try:
        conn = sqlite3.connect("voting_system.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, email FROM Users WHERE role='voter'")
        voters = cursor.fetchall()
        conn.close()

        voter_list = [
            {"id": voter[0], "username": voter[1], "email": voter[2]} for voter in voters
        ]
        return jsonify({"voters": voter_list}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to fetch voters: {str(e)}"}), 500



@user_mgmt_bp.route("/update-voter/<int:voter_id>", methods=["PUT"])
@token_required
def update_voter(voter_id):
    """
    Update voter details. Admins only.
    """
    if request.user["role"] != "admin":
        return jsonify({"error": "Unauthorized"}), 403

    data = request.form
    username = data.get("username")
    email = data.get("email")
    photo = request.files.get("photo")

    if not username or not email:
        return jsonify({"error": "Username and email are required"}), 400

    try:
        conn = sqlite3.connect("voting_system.db")
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE Users SET username = ?, email = ? WHERE id = ?",
            (username, email, voter_id),
        )
        conn.commit()

        if photo:
            filename = secure_filename(f"{voter_id}.jpg")
            photo_path = os.path.join(PHOTO_FOLDER, filename)
            os.makedirs(PHOTO_FOLDER, exist_ok=True)
            photo.save(photo_path)

        conn.close()
        return jsonify({"message": "Voter updated successfully!"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to update voter: {str(e)}"}), 500



@user_mgmt_bp.route("/delete-voter/<int:voter_id>", methods=["DELETE"])
@token_required
def delete_voter(voter_id):
    """
    Delete a voter. Admins only.
    """
    if request.user["role"] != "admin":
        return jsonify({"error": "Unauthorized"}), 403

    try:
        conn = sqlite3.connect("voting_system.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Users WHERE id = ?", (voter_id,))
        conn.commit()

        photo_path = os.path.join(PHOTO_FOLDER, f"{voter_id}.jpg")
        if os.path.exists(photo_path):
            os.remove(photo_path)

        conn.close()
        return jsonify({"message": "Voter deleted successfully!"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to delete voter: {str(e)}"}), 500
