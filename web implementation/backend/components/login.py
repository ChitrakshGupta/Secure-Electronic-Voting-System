from flask import Blueprint, request, jsonify
from flask_bcrypt import Bcrypt
import jwt
import datetime
from .database import fetch_user
import face_recognition
import os
from .face_recogination import load_user_face, match_face, capture_photo

# Initialize bcrypt and create a Flask blueprint
bcrypt = Bcrypt()
login_bp = Blueprint("login", __name__)

# Secret key for JWT token generation
SECRET_KEY = "your_secret_key_here"
PHOTO_FOLDER = "photos"  # Directory where voter photos are stored

@login_bp.route("/auth/login/<role>", methods=["POST"])
def login(role):
    """
    Handle login for admin and voter roles, with optional voter photo verification.

    Args:
        role (str): User role ('admin' or 'voter').

    Returns:
        JSON response:
            - Success: JWT token and user ID.
            - Error: Appropriate error message and HTTP status code.
    """
    # Parse the request JSON for login credentials
    data = request.json
    username = data.get("username")
    password = data.get("password")
    device_id = data.get("deviceId")  # Used for admin authentication

    # Fetch user details from the database
    user = fetch_user(username)
    print("DEBUG: Fetched User:", user)

    if not user:
        return jsonify({"error": "Invalid credentials or role"}), 403

    # Unpack user details
    user_id, user_username, user_password_hash, user_role, user_has_voted, user_device_id = user

    # Validate the password
    if not bcrypt.check_password_hash(user_password_hash, password):
        return jsonify({"error": "Invalid credentials"}), 403

    # Validate device ID for admin login
    if role == "admin" and user_device_id != device_id:
        return jsonify({"error": "Unauthorized device for admin login"}), 403

    # Ensure the user role matches the requested role
    if user_role != role:
        return jsonify({"error": "Invalid credentials or role"}), 403

    # If the user is a voter, perform face recognition
    if role == "voter":
        # Load the specific voter's face encoding
        voter_photo_path = os.path.join(PHOTO_FOLDER, f"{user_id}.jpg")

        if not os.path.exists(voter_photo_path):
            return jsonify({"error": "No registered photo for this voter"}), 403

        # Load the voter's photo and get its face encoding
        try:
            voter_image = face_recognition.load_image_file(voter_photo_path)
            voter_face_encoding = face_recognition.face_encodings(voter_image)[0]
        except IndexError:
            return jsonify({"error": "No face detected in the voter's registered photo"}), 403

        # Capture a photo of the voter
        captured_photo = capture_photo()
        if captured_photo is None:
            return jsonify({"error": "Face capture failed"}), 400

        # Match the captured photo with the voter's registered face encoding
        captured_face_locations = face_recognition.face_locations(captured_photo)
        captured_face_encodings = face_recognition.face_encodings(captured_photo, captured_face_locations)

        if not captured_face_encodings:
            return jsonify({"error": "No face detected in the captured photo"}), 400

        # Compare the captured encoding with the registered voter's encoding
        matches = face_recognition.compare_faces([voter_face_encoding], captured_face_encodings[0])
        face_distance = face_recognition.face_distance([voter_face_encoding], captured_face_encodings[0])

        if not matches[0]:
            return jsonify({"error": "Face recognition failed"}), 403

    # Generate a JWT token with user ID, role, and expiration
    try:
        token = jwt.encode(
            {
                "id": user_id,
                "role": user_role,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
            },
            SECRET_KEY,
            algorithm="HS256"
        )
    except Exception as e:
        return jsonify({"error": f"Token generation failed: {str(e)}"}), 500

    # Log debug info and return success response
    print("DEBUG: Generated user ID:", user_id)
    return jsonify({"token": token, "user_id": user_id}), 200
