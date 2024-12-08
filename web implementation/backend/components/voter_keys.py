from .rsa_helpers import generate_keys, save_keys
import os
import sqlite3

DATABASE_FILE = "voting_system.db"
KEYS_DIRECTORY = "keys"

# Ensure keys directory exists
os.makedirs(KEYS_DIRECTORY, exist_ok=True)

def fetch_users_by_role(role):
    """
    Fetch all users with a specific role from the database.
    """
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    cursor.execute("SELECT id, username FROM Users WHERE role = ?", (role,))
    users = [{"id": row[0], "username": row[1]} for row in cursor.fetchall()]
    conn.close()
    return users

def generate_voter_keys():
    """
    Generate a pair of RSA keys for each voter in the database.
    Keys are saved using the voter's unique ID as the file name.
    """
    voters = fetch_users_by_role("voter")

    for voter in voters:
        voter_id = str(voter["id"])  # Use ID instead of username
        private_key, public_key = generate_keys()
        save_keys(private_key, public_key, voter_id, KEYS_DIRECTORY)
        print(f"Keys generated for voter ID: {voter_id}")

    return {"message": f"Keys generated for {len(voters)} voters."}
