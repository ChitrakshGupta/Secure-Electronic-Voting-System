import pickle
import json
from phe import paillier
import os

# Load Paillier keys
def load_paillier_keys():
    with open('paillier_public_key.pkl', 'rb') as f:
        public_key_paillier = pickle.load(f)
    with open('paillier_private_key.pkl', 'rb') as f:
        private_key_paillier = pickle.load(f)
    return public_key_paillier, private_key_paillier

# Load the candidate mapping
def load_candidate_mapping():
    with open('candidate_mapping.json', 'r') as f:
        return json.load(f)

# Load Paillier keys and candidates
public_key_paillier, private_key_paillier = load_paillier_keys()
candidate_ids = load_candidate_mapping()  # Load candidate mapping here

# Define a scaling factor (e.g., divide votes by 100 to reduce size)
SCALING_FACTOR = 10

def unscale_vote(scaled_vote_count):
    """ Scale up the vote count after decryption """
    return scaled_vote_count * SCALING_FACTOR

# Initialize session state
voting_active = True  # Voting session starts as active

def stop_voting_session():
    global voting_active
    voting_active = False
    print("Voting session stopped. Displaying results...")

def reset_votes():
    """ Reset the stored votes before starting a new session. """
    # Clear the previous votes (reset the file or use another method)
    with open("votes.json", "w") as f:
        json.dump([], f)  # Empty list means no votes have been cast

def tally_votes():
    # Load the encrypted votes from the file
    with open("votes.json", "r") as f:
        votes = json.load(f)
    
    # Initialize total vote tally as an EncryptedNumber for each candidate
    total_vote = {candidate_id: public_key_paillier.encrypt(0) for candidate_id in candidate_ids}

    for vote in votes:
        selected_candidate_id = vote['selected_candidate_id']
        
        if selected_candidate_id not in total_vote:
            print(f"Invalid candidate ID: {selected_candidate_id}")
            continue
        
        # Convert the raw ciphertext back into an EncryptedNumber object
        encrypted_vote = paillier.EncryptedNumber(public_key_paillier, vote['encrypted_vote'])

        # Add the encrypted vote to the corresponding candidate's tally
        total_vote[selected_candidate_id] += encrypted_vote

    # Decrypt the final tally and check for overflow
    for candidate_id, encrypted_tally in total_vote.items():
        try:
            # Decrypt the final tally using the private key
            decrypted_tally = private_key_paillier.decrypt(encrypted_tally)
            
            # Unscale the tally to the original scale
            final_tally = decrypted_tally // SCALING_FACTOR
            
            print(f"Candidate {candidate_id} has {final_tally} votes")
        except OverflowError:
            print(f"Overflow error while decrypting tally for Candidate {candidate_id}. Check vote size.")
        except Exception as e:
            print(f"Error while decrypting tally for Candidate {candidate_id}: {e}")

# Main loop for voting session
def run_tally_server():
    global voting_active
    while voting_active:
        # Reset votes before starting each session
        reset_votes()
        print("Previous votes have been cleared. Starting new session...")

        command = input("Enter 'stop' to end the voting session and tally the votes: ")
        if command.lower() == 'stop':
            stop_voting_session()
            tally_votes()

if __name__ == "__main__":
    run_tally_server()
