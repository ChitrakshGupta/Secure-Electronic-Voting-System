import json
import os
from rsa_helpers import encrypt_data, sign_data

# Load the public key of the admin
with open('public_key.pem', 'rb') as f:
    public_key = f.read()

VOTES_FILE = 'votes.json'

# Check if voter has already voted
def has_voted(voter_id):
    if os.path.exists(VOTES_FILE):
        with open(VOTES_FILE, 'r') as f:
            votes = json.load(f)
            return any(vote['voter_id'] == voter_id for vote in votes)
    return False

# Voter casts their vote
def cast_vote(voter_id, vote_choice):
    encrypted_vote = encrypt_data(public_key, f"{voter_id}:{vote_choice}")
    return encrypted_vote

# Append vote to votes.json
def save_vote(voter_id, encrypted_vote, signature):
    vote_entry = {
        "voter_id": voter_id,
        "encrypted_vote": encrypted_vote,
        "signature": signature
    }

    try:
        with open(VOTES_FILE, 'r') as f:
            votes = json.load(f)
    except FileNotFoundError:
        votes = []

    votes.append(vote_entry)

    with open(VOTES_FILE, 'w') as f:
        json.dump(votes, f, indent=4)
    print("Vote successfully saved to votes.json.")

# Simulate the voting process
voter_id = input("Enter your voter ID: ")
if has_voted(voter_id):
    print("Error: You have already voted. Duplicate votes are not allowed.")
else:
    vote_choice = input("Enter your vote (A, B, or C): ")
    encrypted_vote = cast_vote(voter_id, vote_choice)

    private_key_filename = f'{voter_id}_private_key.pem'
    try:
        with open(private_key_filename, 'rb') as f:
            voter_private_key = f.read()
        
        signature = sign_data(voter_private_key, encrypted_vote)
        save_vote(voter_id, encrypted_vote, signature)
        print("Vote and signature saved successfully in votes.json")

    except FileNotFoundError:
        print(f"Error: Private key file '{private_key_filename}' not found. Please generate keys first.")
