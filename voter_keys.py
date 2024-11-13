# generate_voter_keys.py
from rsa_helpers import generate_keys, save_keys


# Generate keys for the voter
voter_id = input("Enter your voter ID: ")
private_key, public_key = generate_keys()

# Save the voter's keys
save_keys(private_key, public_key, voter_id)
print(f"Keys generated and saved as {voter_id}_private_key.pem and {voter_id}_public_key.pem.")

# Load the admin’s public key to allow voter to encrypt their votes
with open('public_key.pem', 'rb') as f:
    admin_public_key = f.read()
print("Admin's public key loaded for vote encryption.")
