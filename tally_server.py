import json
import os
from rsa_helpers import decrypt_data, verify_signature

# Load the admin's private key for decrypting votes
with open('private_key.pem', 'rb') as f:
    admin_private_key = f.read()

VOTES_FILE = 'votes.json'

def start_new_session():
    """Clear previous votes to start a new voting session."""
    if os.path.exists(VOTES_FILE):
        os.remove(VOTES_FILE)  # Delete the previous votes file
    print("New voting session started. All previous votes cleared.")

def save_vote(vote_entry):
    """Append a new vote to the votes.json file."""
    votes = []
    if os.path.exists(VOTES_FILE):
        with open(VOTES_FILE, 'r') as f:
            votes = json.load(f)

    votes.append(vote_entry)

    with open(VOTES_FILE, 'w') as f:
        json.dump(votes, f)

def tally_votes():
    """Process and tally votes from the current session."""
    try:
        with open(VOTES_FILE, 'r') as f:
            votes = json.load(f)
        
        print("Votes loaded successfully. Processing each vote...")

        # Initialize vote tally dictionary
        tally = {}
        valid_votes_count = 0

        for vote_entry in votes:
            voter_id = vote_entry['voter_id']
            encrypted_vote = vote_entry['encrypted_vote']
            signature = vote_entry['signature']

            # Load each voter's public key for signature verification
            try:
                with open(f"{voter_id}_public_key.pem", 'rb') as key_file:
                    voter_public_key = key_file.read()
            except FileNotFoundError:
                print(f"Public key for voter {voter_id} not found. Skipping this vote.")
                continue

            # Verify the voter's signature
            if not verify_signature(voter_public_key, encrypted_vote, signature):
                print(f"Invalid signature for voter {voter_id}. Skipping this vote.")
                continue

            # Decrypt the vote
            try:
                decrypted_vote = decrypt_data(admin_private_key, encrypted_vote)
                _, vote_choice = decrypted_vote.split(':')  # Format: "voter_id:vote_choice"
                
                # Count the vote
                tally[vote_choice] = tally.get(vote_choice, 0) + 1
                valid_votes_count += 1
                print(f"Vote counted for {vote_choice} from voter {voter_id}.")
            except Exception as e:
                print(f"Error decrypting vote for voter {voter_id}: {e}")

        if valid_votes_count == 0:
            print("No valid votes were tallied.")
        return tally

    except FileNotFoundError:
        print("No votes to tally. Ensure votes are cast before closing the session.")
        return {}

# Main session loop
try:
    start_new_session()

    print("Tally server is open for votes. Enter 'stop' to end the session and tally votes.")

    while True:
        command = input("Type 'stop' to end the voting session and tally votes: ").strip()
        
        if command.lower() == 'stop':
            print("\nEnding voting session and tallying results...\n")
            vote_tally = tally_votes()

            if vote_tally:
                print("\nFinal Vote Tally:")
                for candidate, count in vote_tally.items():
                    print(f"{candidate}: {count} votes")
            else:
                print("No valid votes were tallied.")
            break

except KeyboardInterrupt:
    print("\nSession interrupted. Tallying votes...\n")
    vote_tally = tally_votes()

    if vote_tally:
        print("\nFinal Vote Tally:")
        for candidate, count in vote_tally.items():
            print(f"{candidate}: {count} votes")
    else:
        print("No valid votes were tallied.")

finally:
    print("Voting session closed.")
