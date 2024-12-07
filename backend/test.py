# import sqlite3
# conn = sqlite3.connect("voting_system.db")
# cursor = conn.cursor()
# cursor.execute("SELECT * FROM Users WHERE role = 'admin'")
# print(cursor.fetchall())
# conn.close()


# import sqlite3
# import os

# db_path = os.path.abspath("voting_system.db")
# print("Database path:", db_path)

# conn = sqlite3.connect("voting_system.db")
# cursor = conn.cursor()
# cursor.execute("SELECT * FROM sqlite_master WHERE type='table';")
# print("Tables in database:", cursor.fetchall())
# conn.close()


# import sqlite3

# conn = sqlite3.connect("voting_system.db")
# cursor = conn.cursor()

# # Fetch all entries from the Users table
# cursor.execute("SELECT * FROM Users")
# users = cursor.fetchall()

# print("Users table contents:", users)

# conn.close()


import sqlite3

# Connect to the database
conn = sqlite3.connect("voting_system.db")
cursor = conn.cursor()

# Update the has_vote field
cursor.execute("UPDATE Users SET has_voted = 1 WHERE username = 'test3'")

# Commit the changes to the database
conn.commit()

# Confirm the update
print(f"Rows updated: {cursor.rowcount}")

# Close the connection
conn.close()

