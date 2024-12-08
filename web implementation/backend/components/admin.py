import os
import pickle
import json
from phe import paillier
from Crypto.PublicKey import RSA
import sqlite3

CANDIDATE_DATABASE_FILE = "candidate_system.db"
KEYS_DIRECTORY = "keys"

# Ensure the keys directory exists
os.makedirs(KEYS_DIRECTORY, exist_ok=True)

def generate_paillier_keys():
    public_key, private_key = paillier.generate_paillier_keypair()
    return public_key, private_key

def generate_rsa_keys():
    rsa_key = RSA.generate(2048)
    private_key = rsa_key.export_key()
    public_key = rsa_key.publickey().export_key()
    return private_key, public_key

def fetch_candidates_from_db():
    """
    Fetch all candidates from the database.
    """
    conn = sqlite3.connect(CANDIDATE_DATABASE_FILE)
    cursor = conn.cursor()

    # Fetch candidates from the database
    cursor.execute("SELECT id, name FROM Candidates")
    candidates = [{"id": row[0], "name": row[1]} for row in cursor.fetchall()]
    conn.close()
    return candidates

def start_voting():
    """
    Main logic for generating keys and preparing the encrypted candidate list.
    """
    # Generate Paillier keys
    public_key_paillier, private_key_paillier = generate_paillier_keys()

    # Save Paillier keys
    with open(os.path.join(KEYS_DIRECTORY, 'paillier_public_key.pkl'), 'wb') as f:
        pickle.dump(public_key_paillier, f)
    with open(os.path.join(KEYS_DIRECTORY, 'paillier_private_key.pkl'), 'wb') as f:
        pickle.dump(private_key_paillier, f)

    # Generate RSA keys
    private_key_rsa, public_key_rsa = generate_rsa_keys()

    # Save RSA keys
    with open(os.path.join(KEYS_DIRECTORY, 'private_key.pem'), 'wb') as f:
        f.write(private_key_rsa)
    with open(os.path.join(KEYS_DIRECTORY, 'public_key.pem'), 'wb') as f:
        f.write(public_key_rsa)

    # Fetch candidates from the database
    candidates = fetch_candidates_from_db()

    # Map each candidate to a unique ID
    candidate_ids = {candidate["id"]: candidate["name"] for candidate in candidates}

    # Encrypt each candidate's ID using Paillier encryption
    encrypted_candidates = [public_key_paillier.encrypt(candidate_id) for candidate_id in candidate_ids.keys()]

    # Save encrypted candidates and mapping
    with open(os.path.join(KEYS_DIRECTORY, 'candidates.pkl'), 'wb') as f:
        pickle.dump(encrypted_candidates, f)
    with open(os.path.join(KEYS_DIRECTORY, 'candidate_mapping.json'), 'w') as f:
        json.dump(candidate_ids, f)

    return {"message": "admin setup!"}
