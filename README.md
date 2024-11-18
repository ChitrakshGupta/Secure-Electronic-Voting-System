# Secure Electronic Voting System

This project is a **Secure Electronic Voting System** designed to ensure privacy, authenticity, and integrity in elections. The system uses cryptographic techniques such as **RSA encryption**, **Paillier encryption**, **Blind Signatures**, and **Digital Signatures** to protect votes and ensure voter anonymity while maintaining verifiability.

---

## Features

1. **Secure Voting**:
   - Encrypted votes using Paillier encryption for confidentiality.
   - Voters sign their encrypted votes with their private keys to ensure authenticity.

2. **Voter Anonymity**:
   - Votes are associated with voter IDs but cannot be traced back to specific voters.

3. **Integrity**:
   - Digital Signatures ensure the integrity of the votes during the process.

4. **Session Management**:
   - Supports voting sessions where results are calculated only after the session is stopped.
   - Previous votes are cleared before starting a new session.

5. **Pluggable Cryptographic Components**:
   - Implements RSA for signing and Paillier encryption for secure vote tallying.
   - Modular code for easy extension.

---

## Requirements

- Python 3.8 or higher
- Required libraries:
  - `phe` for Paillier encryption
  - `pycryptodome` for RSA and signature handling
  - `json` for vote storage
  - `pickle` for key serialization

Install dependencies using:
```bash
pip install phe pycryptodome
```

---

## Project Structure

- **`admin.py`**: Manages the overall election process, key generation, and vote tallying.
- **`voter.py`**: Allows voters to cast their votes after verifying eligibility and generating signatures.
- **`tally_server.py`**: Collects encrypted votes and decrypts them for final tallying.
- **`votes.json`**: Stores encrypted votes during a session.
- **`candidate_mapping.json`**: Maps candidate IDs to candidate names.
- **`rsa_helpers.py`**: Helper functions for RSA key handling and signing.
- **`voter_keys.py`**: Generates voter's public and private keys.
---

## How It Works

### 1. Key Generation
The **admin** generates:
- RSA keys for signing and verifying.
- Paillier keys for encrypting and decrypting votes.

### 2. Voting
- Voters use their unique voter ID to cast votes.
- Each vote is encrypted using the admin's Paillier public key.
- Votes are signed by voters using their RSA private key for authenticity.

### 3. Tallying
- The **tally server** decrypts votes after the session is stopped and displays the results.
- Only encrypted votes are stored during the session, ensuring security.

---

## Cryptographic Workflow

1. **Vote Encryption**:
   - Paillier encryption secures the vote content.

2. **Vote Signing**:
   - Voters sign the encrypted vote using RSA to ensure integrity and authenticity.

3. **Verification**:
   - The tally server verifies signatures before counting votes.

---

## How to Use

### Step 1: Start a Voting Session
Run the `tally_server.py` to initiate a session:
```bash
python tally_server.py
```

### Step 2: Voters Cast Votes
Run `voter.py` for each voter to cast their vote:
```bash
python voter.py
```

### Step 3: Stop the Session and Tally Votes
When all votes are cast, stop the session by typing `stop` in `tally_server.py`. The results will be displayed.

---

## Security Features

- **Confidentiality**: Votes are encrypted using Paillier cryptography.
- **Anonymity**: Blind Signatures (optional) ensure the admin cannot trace votes back to voters.
- **Integrity**: RSA signatures prevent vote tampering.
- **Authenticity**: Voter IDs are verified before accepting votes.

---

## Future Enhancements

- **Full Implementation of Blind Signatures** for enhanced voter anonymity.
- **Oblivious Transfer** for secure message selection.
- Web-based or mobile UI for easier voter access.

---

## Contributions

Feel free to open issues or submit pull requests. Contributions are welcome to improve the system's functionality and security.
