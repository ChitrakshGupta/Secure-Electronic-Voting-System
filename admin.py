# admin.py
import json
from rsa_helpers import generate_keys, encrypt_data

# Admin generates RSA keys for the election process
private_key, public_key = generate_keys()

# Save admin's private key securely for tally server use
with open('private_key.pem', 'wb') as f:
    f.write(private_key)
print("Admin's private key saved for tally server use.")

# Save public key to file to share with voters
with open('public_key.pem', 'wb') as f:
    f.write(public_key)
print("Public key saved for voters to use.")

# Admin creates and saves list of candidates
candidates = ["Candidate A", "Candidate B", "Candidate C"]

# Save the candidates to a file to be shared securely with the voters
with open('candidates.json', 'w') as f:
    json.dump(candidates, f)
print("Candidate list saved for voters.")
