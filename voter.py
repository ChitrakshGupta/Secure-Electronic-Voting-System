import json
from rsa_helpers import encrypt_data, sign_data

# Load the public key of the admin
with open('public_key.pem', 'rb') as f:
    public_key = f.read()

# Voter casts their vote
def cast_vote(voter_id, vote_choice):
    # Encrypt the vote using the admin's public key
    encrypted_vote = encrypt_data(public_key, f"{voter_id}:{vote_choice}")
    return encrypted_vote

# Append vote to votes.json
def save_vote(voter_id, encrypted_vote, signature):
    vote_entry = {
        "voter_id": voter_id,
        "encrypted_vote": encrypted_vote,
        "signature": signature
    }
    # Append the vote to votes.json
    try:
        with open('votes.json', 'r') as f:
            votes = json.load(f)
    except FileNotFoundError:
        votes = []  # Start a new list if file doesn't exist

    votes.append(vote_entry)
    
    with open('votes.json', 'w') as f:
        json.dump(votes, f, indent=4)
    print("Vote successfully saved to votes.json.")

# Simulate the voting process
voter_id = input("Enter your voter ID: ")
vote_choice = input("Enter your vote (A, B, or C): ")

# Cast and save the encrypted vote
encrypted_vote = cast_vote(voter_id, vote_choice)

# Load voter's private key for signing
private_key_filename = f'{voter_id}_private_key.pem'
try:
    with open(private_key_filename, 'rb') as f:
        voter_private_key = f.read()
    
    # Sign the encrypted vote with the voter's private key
    signature = sign_data(voter_private_key, encrypted_vote)
    save_vote(voter_id, encrypted_vote, signature)
    print("Vote and signature saved successfully in votes.json")

except FileNotFoundError:
    print(f"Error: Private key file '{private_key_filename}' not found. Please generate keys first.")
