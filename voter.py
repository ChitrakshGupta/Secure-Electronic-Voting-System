import json
import os
import base64
import pickle
from rsa_helpers import encrypt_with_paillier, sign_data
from phe import paillier
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256

VOTES_FILE = 'votes.json'

# Check if voter has already voted
def has_voted(voter_id):
    if os.path.exists(VOTES_FILE):
        try:
            with open(VOTES_FILE, 'r') as f:
                contents = f.read()  # Read the file's contents to check for issues
                print("Contents of votes.json:", contents)
                if contents.strip() == "":  # In case the file is empty
                    print("Error: votes.json is empty. Initializing file.")
                    return False

                votes = json.loads(contents)  # Attempt to load the JSON data
                return any(vote['voter_id'] == str(voter_id) for vote in votes)
        except json.decoder.JSONDecodeError:
            print("Error: The votes.json file is malformed. Resetting the file.")
            # If JSON is malformed, reset the file content
            reset_votes_file()
            return False
    else:
        # If the file doesn't exist, initialize it as an empty list
        reset_votes_file()
    return False

# Function to reset the votes file to a valid empty list
def reset_votes_file():
    with open(VOTES_FILE, 'w') as f:
        json.dump([], f)

# Save vote function update
def save_vote(voter_id, encrypted_vote, signature, selected_candidate_id):
    # Load existing votes
    try:
        with open("votes.json", "r") as f:
            votes = json.load(f)
    except FileNotFoundError:
        votes = []

    # Store the raw ciphertext of the encrypted vote (not the whole EncryptedNumber object)
    encrypted_vote_serializable = encrypted_vote.ciphertext()  # Use the raw ciphertext

    # Create a vote entry
    vote_entry = {
        "voter_id": voter_id,
        "encrypted_vote": encrypted_vote_serializable,  # Store raw ciphertext as an integer
        "selected_candidate_id": selected_candidate_id,  # Store the candidate ID, not the encrypted vote
        "signature": signature.hex()  # Store the signature as a hex string
    }

    # Append the vote entry
    votes.append(vote_entry)

    # Save updated votes
    with open("votes.json", "w") as f:
        json.dump(votes, f, indent=4)

# Scaling factor to reduce vote size
SCALING_FACTOR = 10  # Adjust as needed (e.g., 10 or 100)

# Function to scale down votes
def scale_vote(vote):
    """Scale down vote value before encryption."""
    return vote * SCALING_FACTOR

# Simulate the voting process
def cast_vote(voter_id, selected_candidate_index):
    # Encrypt the vote with Paillier public key (for confidentiality)
    scaled_vote = scale_vote(1)
    encrypted_vote = public_key_paillier.encrypt(scaled_vote)
        
    # Get the actual candidate ID from the index, either as a list or dictionary
    if isinstance(candidate_ids, dict):
        # If candidate_ids is a dictionary, access it by key
        candidate_keys = list(candidate_ids.keys())
        selected_candidate_id = candidate_keys[selected_candidate_index]
    else:
        # If candidate_ids is a list, use the index directly
        selected_candidate_id = candidate_ids[selected_candidate_index]
    
    return encrypted_vote, selected_candidate_id


# Load the public key of the admin (Paillier public key)
with open('paillier_public_key.pkl', 'rb') as f:
    public_key_paillier = pickle.load(f)  # Correctly load the Paillier public key

# Load the candidate mapping
with open('candidate_mapping.json', 'r') as f:
    candidate_ids = json.load(f)

# Prompt for voter input
voter_id = input("Enter your Voter ID: ")
selected_candidate_index = int(input(f"Select your candidate (0-{len(candidate_ids)-1}): "))

# Check if the voter has already voted
if has_voted(voter_id):
    print("You have already voted.")
else:
    encrypted_vote, selected_candidate_id = cast_vote(voter_id, selected_candidate_index)
    
    # Sign the encrypted vote
    with open(f"{voter_id}_private_key.pem", "rb") as f:
        private_key = RSA.import_key(f.read())

    signature = sign_data(private_key, str(encrypted_vote))

    # Save the vote along with the signature
    save_vote(voter_id, encrypted_vote, signature, selected_candidate_id)
    print("Vote cast successfully.")