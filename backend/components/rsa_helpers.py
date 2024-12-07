from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
import base64
from phe import paillier
import pickle
import os


# Generate RSA keys
def generate_keys():
    """
    Generate a pair of RSA keys.
    """
    key = RSA.generate(2048)
    private_key = key.export_key()
    public_key = key.publickey().export_key()
    return private_key, public_key


# Save the keys to files
def save_keys(private_key, public_key, voter_id, directory="keys"):
    """
    Save RSA keys to files.
    """
    os.makedirs(directory, exist_ok=True)  # Create directory if it doesn't exist

    with open(os.path.join(directory, f'{voter_id}_private_key.pem'), 'wb') as f:
        f.write(private_key)
    with open(os.path.join(directory, f'{voter_id}_public_key.pem'), 'wb') as f:
        f.write(public_key)


# Encrypt data with the public key
def encrypt_data(public_key, data):
    """
    Encrypt data using RSA public key.
    """
    rsa_key = RSA.import_key(public_key)
    cipher = PKCS1_OAEP.new(rsa_key)
    encrypted_data = cipher.encrypt(data.encode('utf-8'))
    return base64.b64encode(encrypted_data).decode('utf-8')


# Decrypt data with the private key
def decrypt_data(private_key, encrypted_data):
    """
    Decrypt data using RSA private key.
    """
    rsa_key = RSA.import_key(private_key)
    cipher = PKCS1_OAEP.new(rsa_key)
    decrypted_data = cipher.decrypt(base64.b64decode(encrypted_data.encode('utf-8')))
    return decrypted_data.decode('utf-8')


# Function to sign data with voter's private key
def sign_data(private_key, data):
    """
    Sign data using RSA private key.
    """
    rsa_key = RSA.import_key(private_key)
    h = SHA256.new(data.encode())
    signature = pkcs1_15.new(rsa_key).sign(h)
    return base64.b64encode(signature).decode('utf-8')


# Function to verify signature with public key
def verify_signature(public_key, data, signature):
    """
    Verify the signature using RSA public key.
    """
    rsa_key = RSA.import_key(public_key)
    h = SHA256.new(data.encode())
    try:
        pkcs1_15.new(rsa_key).verify(h, base64.b64decode(signature))
        return True
    except (ValueError, TypeError):
        return False


# Generate Paillier keys
def generate_paillier_keys():
    """
    Generate a pair of Paillier keys.
    """
    public_key, private_key = paillier.generate_paillier_keypair()
    return public_key, private_key


# Encrypt with Paillier
def encrypt_with_paillier(public_key, value):
    """
    Encrypt a value using Paillier public key.
    """
    return public_key.encrypt(value)


# Decrypt with Paillier
def decrypt_with_paillier(private_key, encrypted_value):
    """
    Decrypt a value using Paillier private key.
    """
    return private_key.decrypt(encrypted_value)


# Save Paillier keys to files
def save_paillier_keys(public_key, private_key, directory="keys"):
    """
    Save Paillier keys to files.
    """
    os.makedirs(directory, exist_ok=True)  # Create directory if it doesn't exist

    with open(os.path.join(directory, 'paillier_public_key.pkl'), 'wb') as f:
        pickle.dump(public_key, f)
    with open(os.path.join(directory, 'paillier_private_key.pkl'), 'wb') as f:
        pickle.dump(private_key, f)


# Load Paillier keys from files
def load_paillier_keys(directory="keys"):
    """
    Load Paillier keys from files.
    """
    with open(os.path.join(directory, 'paillier_public_key.pkl'), 'rb') as f:
        public_key = pickle.load(f)
    with open(os.path.join(directory, 'paillier_private_key.pkl'), 'rb') as f:
        private_key = pickle.load(f)
    return public_key, private_key
