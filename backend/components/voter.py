import os
import json
import pickle
from phe import paillier
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from flask import Blueprint, request, jsonify
import sqlite3

cast_vote_endpoint = Blueprint('cast_vote_endpoint', __name__)

# Directory for keys and votes
DATA_DIR = "keys"
VOTES_FILE = os.path.join(DATA_DIR, 'votes.json')

# Load Paillier keys
def load_paillier_keys(data_dir):
    with open(os.path.join(data_dir, 'paillier_public_key.pkl'), 'rb') as f:
        public_key = pickle.load(f)
    with open(os.path.join(data_dir, 'paillier_private_key.pkl'), 'rb') as f:
        private_key = pickle.load(f)
    return public_key, private_key

# Check if the voter has already voted
def has_voted(voter_id, votes_file):
    if os.path.exists(votes_file):
        with open(votes_file, 'r') as f:
            votes = json.load(f)
            return any(vote['voter_id'] == str(voter_id) for vote in votes)
    return False

# Save the vote to the votes file
def save_vote(voter_id, encrypted_vote, signature, selected_candidate_id, votes_file):
    try:
        # Load existing votes
        with open(votes_file, "r") as f:
            votes = json.load(f)
    except FileNotFoundError:
        votes = []

    encrypted_vote_serializable = encrypted_vote.ciphertext()

    vote_entry = {
        "voter_id": voter_id,
        "encrypted_vote": encrypted_vote_serializable,
        "selected_candidate_id": selected_candidate_id,
        "exponent": encrypted_vote.exponent,
        "signature": signature.hex()
    }

    votes.append(vote_entry)

    # Save the vote in the votes.json file
    with open(votes_file, "w") as f:
        json.dump(votes, f, indent=4)

    # Update the `has_voted` column in the database
    try:
        conn = sqlite3.connect("voting_system.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE Users SET has_voted = 1 WHERE id = ?", (voter_id,))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error updating has_voted for voter {voter_id}: {e}")


# Encrypt the vote and get the candidate ID
def cast_vote(voter_id, selected_candidate_index, data_dir):
    """
    Cast a vote for a candidate based on the selected candidate index.
    """
    public_key_paillier, _ = load_paillier_keys(data_dir)

    # Load candidate mapping
    with open(os.path.join(data_dir, 'candidate_mapping.json'), 'r') as f:
        candidate_ids = json.load(f)

    # Convert candidate_ids to a list to ensure the index matches
    candidate_list = list(candidate_ids.keys())  # Ensure consistent ordering
    if selected_candidate_index < 0 or selected_candidate_index >= len(candidate_list):
        raise ValueError("Invalid candidate index")

    scaled_vote = 10  # Default scaling factor for a vote
    encrypted_vote = public_key_paillier.encrypt(scaled_vote)

    # Map the index to the candidate ID
    selected_candidate_id = candidate_list[selected_candidate_index]
    return encrypted_vote, selected_candidate_id


# Sign the encrypted vote using the voter's private RSA key
def sign_data(private_key, data):
    hash_obj = SHA256.new(data.encode())
    signature = pkcs1_15.new(private_key).sign(hash_obj)
    return signature

@cast_vote_endpoint.route('/cast-vote', methods=['POST'])
def cast_vote_route():
    try:
        # Parse the incoming JSON data
        data = request.json
        voter_id = data.get("voter_id")
        selected_candidate_index = data.get("selected_candidate_index")

        if not voter_id or selected_candidate_index is None:
            return jsonify({"success": False, "message": "Voter ID and candidate selection are required."}), 400

        # Check if the voter has already voted
        if has_voted(voter_id, VOTES_FILE):
            return jsonify({"success": False, "message": "You have already voted."}), 400

        # Cast the vote
        encrypted_vote, selected_candidate_id = cast_vote(voter_id, selected_candidate_index, DATA_DIR)

        # Load the voter's private RSA key
        voter_key_path = os.path.join(DATA_DIR, f"{voter_id}_private_key.pem")
        if not os.path.exists(voter_key_path):
            return jsonify({"success": False, "message": f"RSA private key not found for Voter ID {voter_id}."}), 400

        with open(voter_key_path, "rb") as f:
            private_key = RSA.import_key(f.read())

        # Sign the encrypted vote
        signature = sign_data(private_key, str(encrypted_vote))

        # Save the vote to the file
        save_vote(voter_id, encrypted_vote, signature, selected_candidate_id, VOTES_FILE)

        return jsonify({"success": True, "message": "Vote cast successfully."}), 200
    except FileNotFoundError as e:
        return jsonify({"success": False, "message": f"File not found: {str(e)}"}), 500
    except ValueError as e:
        return jsonify({"success": False, "message": f"Invalid input: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"success": False, "message": f"Error processing vote: {str(e)}"}), 500
