from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
import base64

# Generate RSA keys
def generate_keys():
    key = RSA.generate(2048)
    private_key = key.export_key()
    public_key = key.publickey().export_key()
    return private_key, public_key

# Save the keys to files
def save_keys(private_key, public_key, voter_id):
    with open(f'{voter_id}_private_key.pem', 'wb') as f:
        f.write(private_key)
    with open(f'{voter_id}_public_key.pem', 'wb') as f:
        f.write(public_key)

# Encrypt data with the public key
def encrypt_data(public_key, data):
    rsa_key = RSA.import_key(public_key)
    cipher = PKCS1_OAEP.new(rsa_key)
    encrypted_data = cipher.encrypt(data.encode('utf-8'))
    return base64.b64encode(encrypted_data).decode('utf-8')

# Decrypt data with the private key
def decrypt_data(private_key, encrypted_data):
    rsa_key = RSA.import_key(private_key)
    cipher = PKCS1_OAEP.new(rsa_key)
    decrypted_data = cipher.decrypt(base64.b64decode(encrypted_data.encode('utf-8')))
    return decrypted_data.decode('utf-8')

# Function to sign data with voter's private key
def sign_data(private_key, data):
    if isinstance(data, str):
        data = data.encode('utf-8')
    h = SHA256.new(data)
    rsa_key = RSA.import_key(private_key)
    signature = pkcs1_15.new(rsa_key).sign(h)
    return base64.b64encode(signature).decode('utf-8')

# Function to verify signature with public key
def verify_signature(public_key, data, signature):
    if isinstance(data, str):
        data = data.encode('utf-8')
    h = SHA256.new(data)
    rsa_key = RSA.import_key(public_key)
    try:
        pkcs1_15.new(rsa_key).verify(h, base64.b64decode(signature))
        return True
    except (ValueError, TypeError):
        return False