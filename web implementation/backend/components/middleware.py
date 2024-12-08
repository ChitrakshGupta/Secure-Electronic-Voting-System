from flask import request, jsonify
import jwt
from functools import wraps

SECRET_KEY = "your_secret_key_here"

def token_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = None

        # Extract token from Authorization header
        if "Authorization" in request.headers:
            token = request.headers["Authorization"].split(" ")[1]

        if not token:
            return jsonify({"error": "Token is missing!"}), 401

        try:
            # Decode the JWT and populate the user context
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            request.user = {
                "id": data["id"],
                "role": data["role"]
            }
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired!"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token!"}), 401

        return func(*args, **kwargs)
    return wrapper
