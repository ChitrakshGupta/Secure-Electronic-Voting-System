import sqlite3
import os

# Database file path
CANDIDATE_DATABASE_FILE = "candidate_system.db"

def initialize_candidate_database():
    """
    Create the Candidates table if it does not exist.
    """
    if not os.path.exists(CANDIDATE_DATABASE_FILE):
        print(f"Creating database: {CANDIDATE_DATABASE_FILE}")
    else:
        print(f"Database {CANDIDATE_DATABASE_FILE} already exists.")

    try:
        conn = sqlite3.connect(CANDIDATE_DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Candidates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            )
        """)
        conn.commit()
        conn.close()
        print("Candidate database initialized successfully.")
    except sqlite3.Error as e:
        print(f"An error occurred while initializing the database: {e}")

if __name__ == "__main__":
    initialize_candidate_database()
