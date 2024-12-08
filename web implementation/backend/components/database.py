import sqlite3
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

def create_database():
    """
    Creates the Users table if it doesn't already exist.
    """
    conn = sqlite3.connect("voting_system.db")
    cursor = conn.cursor()

    # Create Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT UNIQUE,  -- Add email column
            role TEXT NOT NULL,
            has_voted BOOLEAN DEFAULT 0,
            device_id TEXT
        )
    """)
    conn.commit()
    conn.close()


def add_user_to_db(username, email, password_hash, role, device_id=None):
    """
    Adds a user to the Users table.
    """
    conn = sqlite3.connect("voting_system.db")
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO Users (username, email, password_hash, role, device_id)
            VALUES (?, ?, ?, ?, ?)
        """, (username, email, password_hash, role, device_id))
        conn.commit()
        print(f"User '{username}' added successfully.")
    except sqlite3.IntegrityError as e:
        print(f"Error adding user '{username}': {str(e)}")
    finally:
        conn.close()


def fetch_user(username):
    """
    Fetches a user from the database by username.
    """
    conn = sqlite3.connect("voting_system.db")
    cursor = conn.cursor()

    # Query to fetch all user details
    cursor.execute("SELECT id, username, password_hash, role, has_voted, device_id FROM Users WHERE username = ?", (username,))
    user = cursor.fetchone()  # Returns a tuple (id, username, password_hash, role, has_voted, device_id)
    conn.close()
    return user


def add_admin_user():
    conn = sqlite3.connect("voting_system.db")
    cursor = conn.cursor()

    # Insert admin user
    admin_username = "admin"
    admin_password = "admin"
    admin_email = None  # Set email to None or a default value
    admin_role = "admin"
    admin_device_id = "unique-device-id-for-admin"
    password_hash = bcrypt.generate_password_hash(admin_password).decode('utf-8')

    try:
        cursor.execute("""
            INSERT INTO Users (username, password_hash, email, role, device_id)
            VALUES (?, ?, ?, ?, ?)
        """, (admin_username, password_hash, admin_email, admin_role, admin_device_id))
        conn.commit()
        print(f"Admin user '{admin_username}' added successfully.")
    except sqlite3.IntegrityError:
        print(f"Admin user '{admin_username}' already exists.")
    finally:
        conn.close()



create_database() 

if __name__ == "__main__":
    add_admin_user() 