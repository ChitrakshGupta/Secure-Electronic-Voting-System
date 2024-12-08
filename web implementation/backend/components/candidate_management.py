from flask import Blueprint, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from .middleware import token_required
import os
import sqlite3

CANDIDATE_DATABASE_FILE = "candidate_system.db"
SYMBOL_FOLDER = "photos_symbol"

candidate_mgmt_bp = Blueprint("candidate_management", __name__)

# Serve candidate symbols
@candidate_mgmt_bp.route('/photos_symbol/<filename>', methods=["GET"])
def serve_symbol(filename):
    """
    Serve candidate symbol images.
    """
    try:
        return send_from_directory(SYMBOL_FOLDER, filename)
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404

# Initialize the candidate database
def initialize_candidate_database():
    """
    Create the Candidates table if it does not exist.
    """
    conn = sqlite3.connect(CANDIDATE_DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

initialize_candidate_database()

@candidate_mgmt_bp.route("/add-candidate", methods=["POST"])
@token_required
def add_candidate():
    """
    Add a candidate along with their symbol. Only admins are authorized.
    """
    if request.user.get("role") != "admin":
        return jsonify({"error": "Unauthorized"}), 403

    name = request.form.get("name")
    symbol = request.files.get("symbol")  # Symbol image file

    if not name:
        return jsonify({"error": "Candidate name is required"}), 400

    try:
        conn = sqlite3.connect(CANDIDATE_DATABASE_FILE)
        cursor = conn.cursor()

        # Insert candidate into the database
        cursor.execute("INSERT INTO Candidates (name) VALUES (?)", (name,))
        candidate_id = cursor.lastrowid
        conn.commit()

        # Save the symbol image if provided
        if symbol:
            os.makedirs(SYMBOL_FOLDER, exist_ok=True)
            filename = secure_filename(f"{candidate_id}.jpg")
            symbol.save(os.path.join(SYMBOL_FOLDER, filename))

        conn.close()
        return jsonify({"message": "Candidate added successfully"}), 201

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@candidate_mgmt_bp.route("/candidates", methods=["GET"])
@token_required
def get_candidates():
    """
    Retrieve all candidates. Accessible by both admins and voters.
    """
    try:
        conn = sqlite3.connect(CANDIDATE_DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM Candidates")
        candidates = cursor.fetchall()
        conn.close()

        return jsonify({"candidates": [{"id": c[0], "name": c[1]} for c in candidates]}), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


@candidate_mgmt_bp.route("/update-candidate/<int:candidate_id>", methods=["PUT"])
@token_required
def update_candidate(candidate_id):
    """
    Update a candidate's details and symbol.
    """
    if request.user.get("role") != "admin":
        return jsonify({"error": "Unauthorized"}), 403

    name = request.form.get("name")
    symbol = request.files.get("symbol")  # Symbol image file

    if not name:
        return jsonify({"error": "Candidate name is required"}), 400

    try:
        conn = sqlite3.connect(CANDIDATE_DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute("UPDATE Candidates SET name = ? WHERE id = ?", (name, candidate_id))
        conn.commit()

        # Update the symbol if provided
        if symbol:
            os.makedirs(SYMBOL_FOLDER, exist_ok=True)
            filename = secure_filename(f"{candidate_id}.jpg")
            symbol.save(os.path.join(SYMBOL_FOLDER, filename))

        conn.close()
        return jsonify({"message": "Candidate updated successfully"}), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@candidate_mgmt_bp.route("/delete-candidate/<int:candidate_id>", methods=["DELETE"])
@token_required
def delete_candidate(candidate_id):
    """
    Delete a candidate and their symbol. Only admins are authorized.
    """
    if request.user.get("role") != "admin":
        return jsonify({"error": "Unauthorized"}), 403

    try:
        conn = sqlite3.connect(CANDIDATE_DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Candidates WHERE id = ?", (candidate_id,))
        conn.commit()

        # Remove the candidate's symbol
        symbol_path = os.path.join(SYMBOL_FOLDER, f"{candidate_id}.jpg")
        if os.path.exists(symbol_path):
            os.remove(symbol_path)

        conn.close()
        return jsonify({"message": "Candidate deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
