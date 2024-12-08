import json
import os
import pickle
from phe import paillier
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256

VOTES_FILE = 'votes.json'

# Function to load Paillier keys
def load_paillier_keys():
    with open('paillier_public_key.pkl', 'rb') as f:
        public_key = pickle.load(f)
    with open('paillier_private_key.pkl', 'rb') as f:
        private_key = pickle.load(f)
    return public_key, private_key

# Load Paillier keys
public_key_paillier, private_key_paillier = load_paillier_keys()

# Load candidate mapping
with open('candidate_mapping.json', 'r') as f:
    candidate_ids = json.load(f)

# Function to check if the voter has voted
def has_voted(voter_id):
    if os.path.exists(VOTES_FILE):
        try:
            with open(VOTES_FILE, 'r') as f:
                contents = f.read()
                if contents.strip() == "":
                    return False
                votes = json.loads(contents)
                return any(vote['voter_id'] == str(voter_id) for vote in votes)
        except json.decoder.JSONDecodeError:
            print("Error: Malformed votes file. Resetting the file.")
            reset_votes_file()
            return False
    else:
        reset_votes_file()
    return False

# Function to reset votes file
def reset_votes_file():
    with open(VOTES_FILE, 'w') as f:
        json.dump([], f)

# Save vote function update
def save_vote(voter_id, encrypted_vote, signature, selected_candidate_id):
    try:
        with open("votes.json", "r") as f:
            votes = json.load(f)
    except FileNotFoundError:
        votes = []

    encrypted_vote_serializable = encrypted_vote.ciphertext()

    vote_entry = {
        "voter_id": voter_id,
        "encrypted_vote": encrypted_vote_serializable,
        "selected_candidate_id": selected_candidate_id,
        "signature": signature.hex()
    }

    votes.append(vote_entry)

    with open("votes.json", "w") as f:
        json.dump(votes, f, indent=4)

# Function to scale vote before encryption (if needed)
def scale_vote(vote):
    SCALING_FACTOR = 10  # Adjust this factor as needed
    return vote * SCALING_FACTOR

# Simulate the voting process
def cast_vote(voter_id, selected_candidate_index):
    scaled_vote = scale_vote(1)
    encrypted_vote = public_key_paillier.encrypt(scaled_vote)
        
    # Map the candidate index to candidate ID
    selected_candidate_id = list(candidate_ids.keys())[selected_candidate_index]
    
    return encrypted_vote, selected_candidate_id

# Function to sign the encrypted vote
def sign_data(private_key, data):
    hash_obj = SHA256.new(data.encode())
    signature = pkcs1_15.new(private_key).sign(hash_obj)
    return signature

# Prompt voter input
voter_id = input("Enter your Voter ID: ")
selected_candidate_index = int(input(f"Select your candidate (0-{len(candidate_ids)-1}): "))

# Check if the voter has already voted
if has_voted(voter_id):
    print("You have already voted.")
else:
    encrypted_vote, selected_candidate_id = cast_vote(voter_id, selected_candidate_index)
    
    # Load the private RSA key for the voter
    with open(f"{voter_id}_private_key.pem", "rb") as f:
        private_key = RSA.import_key(f.read())

    # Sign the encrypted vote
    signature = sign_data(private_key, str(encrypted_vote))

    # Save the vote
    save_vote(voter_id, encrypted_vote, signature, selected_candidate_id)
    print("Vote cast successfully.")
