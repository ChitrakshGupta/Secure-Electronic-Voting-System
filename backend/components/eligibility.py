from flask import Blueprint, request, jsonify
import sqlite3
import logging

eligibility_bp = Blueprint("eligibility", __name__)
VOTER_DATABASE_FILE = "voting_system.db"

@eligibility_bp.route('/check-eligibility', methods=['POST'])
def check_eligibility():
    voter_id = request.json.get("voter_id")
    if not voter_id:
        logging.error("Voter ID not provided in the request.")
        return jsonify({"error": "Voter ID is required"}), 400

    try:
        conn = sqlite3.connect(VOTER_DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT has_voted FROM Users WHERE id = ?", (voter_id,))
        result = cursor.fetchone()
        conn.close()

        if result is None:
            return jsonify({"error": "Voter not found"}), 404

        has_voted = result[0]
        if has_voted:
            return jsonify({"message": "You have already voted.", "voter_id": None}), 200
        else:
            return jsonify({"message": "You are eligible to vote.", "voter_id": voter_id}), 200

    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return jsonify({"error": str(e)}), 500
