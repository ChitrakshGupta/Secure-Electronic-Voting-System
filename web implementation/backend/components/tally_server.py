import pickle
import json
from phe import paillier
import os

# Directory where keys and votes are stored
KEYS_DIRECTORY = r"keys"
VOTES_FILE = "keys/votes.json"

import sqlite3

DB_FILE = "voting_system.db"  # Path to your database file

def reset_voter_status():
    """
    Reset the has_voted column for all voters in the database.
    """
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("UPDATE Users SET has_voted = 0 WHERE role = 'voter'")
        conn.commit()
        conn.close()
        print("Voter status reset successfully.")
    except sqlite3.Error as e:
        print(f"Error resetting voter status: {e}")
        raise


# Load Paillier keys
def load_paillier_keys():
    """
    Load Paillier keys from disk.
    """
    with open(os.path.join(KEYS_DIRECTORY, 'paillier_public_key.pkl'), 'rb') as f:
        public_key_paillier = pickle.load(f)
    with open(os.path.join(KEYS_DIRECTORY, 'paillier_private_key.pkl'), 'rb') as f:
        private_key_paillier = pickle.load(f)
    return public_key_paillier, private_key_paillier


# Load candidate mapping
def load_candidate_mapping():
    with open(os.path.join(KEYS_DIRECTORY, 'candidate_mapping.json'), 'r') as f:
        return json.load(f)

# Load keys and candidates
public_key_paillier, private_key_paillier = load_paillier_keys()
candidate_ids = load_candidate_mapping()

# Define a scaling factor
SCALING_FACTOR = 10

def reset_votes():
    """
    Reset the stored votes and clear the votes file.
    """
    with open(VOTES_FILE, "w") as f:
        json.dump([], f)
    print("Votes reset successfully.")


def validate_and_parse_vote(vote):
    """
    Validate and parse a single vote entry.
    """
    try:
        encrypted_vote = paillier.EncryptedNumber(
            public_key_paillier,
            int(vote['encrypted_vote']),
            int(vote.get('exponent', 0))  # Default exponent to 0 if missing
        )
        candidate_id = str(vote['selected_candidate_id'])  # Ensure it's a string for consistency
        return encrypted_vote, candidate_id
    except KeyError as e:
        print(f"Vote missing key {e}: {vote}")
    except Exception as e:
        print(f"Error parsing vote: {e}")
    return None, None



def tally_votes():
    """
    Tally votes stored in the votes file and map them to the correct candidates.
    """
    if not os.path.exists(VOTES_FILE):
        print("No votes found to tally.")
        return {}

    # Reload keys and candidate mapping to ensure consistent state
    global public_key_paillier, private_key_paillier, candidate_ids
    public_key_paillier, private_key_paillier = load_paillier_keys()
    candidate_ids = load_candidate_mapping()  # Load candidate ID-to-name mapping

    with open(VOTES_FILE, "r") as f:
        votes = json.load(f)

    # Initialize total vote tally for each candidate
    total_vote = {candidate_id: public_key_paillier.encrypt(0) for candidate_id in candidate_ids.keys()}

    for vote in votes:
        encrypted_vote, candidate_id = validate_and_parse_vote(vote)
        if encrypted_vote and candidate_id in total_vote:
            total_vote[candidate_id] += encrypted_vote  # Add encrypted vote to the correct candidate
        else:
            print(f"Skipping invalid vote: {vote}")

    results = {}
    for candidate_id, encrypted_tally in total_vote.items():
        try:
            # Decrypt and scale the tally
            decrypted_tally = private_key_paillier.decrypt(encrypted_tally)
            final_tally = int(decrypted_tally / SCALING_FACTOR)  # Properly scale
            
            # Map the candidate ID to the candidate name
            candidate_name = candidate_ids.get(candidate_id, f"Unknown Candidate ({candidate_id})")
            results[candidate_name] = final_tally
            
            print(f"{candidate_name} has {final_tally} votes")
        except Exception as e:
            print(f"Error tallying votes for Candidate {candidate_id}: {e}")
            results[candidate_ids.get(candidate_id, f"Unknown Candidate ({candidate_id})")] = "Error"

    return results
