import pickle
import json
from phe import paillier
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2

# Function to generate Paillier keys
def generate_paillier_keys():
    public_key, private_key = paillier.generate_paillier_keypair()
    return public_key, private_key

# Generate Paillier public and private keys
public_key_paillier, private_key_paillier = generate_paillier_keys()

# Save Paillier public and private keys for the admin and tally server
with open('paillier_public_key.pkl', 'wb') as f:
    pickle.dump(public_key_paillier, f)  # Serialize Paillier public key
    print("Paillier public key saved for tally server use.")

with open('paillier_private_key.pkl', 'wb') as f:
    pickle.dump(private_key_paillier, f)  # Serialize Paillier private key
    print("Paillier private key saved for decryption.")

# Generate RSA keys for vote encryption and signing
def generate_rsa_keys():
    rsa_key = RSA.generate(2048)
    private_key = rsa_key.export_key()
    public_key = rsa_key.publickey().export_key()
    return private_key, public_key

# Generate RSA public and private keys
private_key_rsa, public_key_rsa = generate_rsa_keys()

# Save RSA keys
with open('private_key.pem', 'wb') as f:
    f.write(private_key_rsa)
    print("RSA private key saved for voters.")

with open('public_key.pem', 'wb') as f:
    f.write(public_key_rsa)
    print("RSA public key saved for voters.")

# Candidates list
candidates = ["Candidate A", "Candidate B", "Candidate C"]

# Map each candidate to a unique integer
candidate_ids = {i: candidate for i, candidate in enumerate(candidates)}

# Encrypt each candidate's ID using Paillier encryption
encrypted_candidates = [public_key_paillier.encrypt(candidate_id) for candidate_id in candidate_ids.keys()]

# Save encrypted candidate list (using pickle to serialize EncryptedNumber objects)
with open('candidates.pkl', 'wb') as f:
    pickle.dump(encrypted_candidates, f)
    print("Encrypted candidate list saved for voters.")

# Save the mapping from encrypted IDs back to candidate names
with open('candidate_mapping.json', 'w') as f:
    json.dump(candidate_ids, f)  # Save the mapping from IDs to candidate names
    print("Candidate mapping saved for use in tally server.")
