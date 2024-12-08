import smtplib
from email.mime.text import MIMEText
from random import randint
import sqlite3
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access environment variables
sender_email = os.getenv("GMAIL_EMAIL")
sender_password = os.getenv("GMAIL_APP_PASSWORD")


def generate_and_send_passwords():
    conn = sqlite3.connect("voting_system.db")
    cursor = conn.cursor()

    # Fetch all voters with their emails
    cursor.execute("SELECT id, email FROM Users WHERE role = 'voter'")
    voters = cursor.fetchall()

    if not voters:
        return "No voters found to send passwords."

    smtp_server = "smtp.gmail.com"
    smtp_port = 465  # Use SSL

    try:
        # Connect to the SMTP server
        server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        server.login(sender_email, sender_password)

        if not sender_email or not sender_password:
            return "Failed to send passwords: Email configuration error."


        for voter_id, voter_email in voters:
            if not voter_email:
                continue

            # Generate a 6-digit password
            password = str(randint(100000, 999999))

            # Save the password hash to the database
            password_hash = bcrypt.generate_password_hash(password).decode("utf-8")
            cursor.execute("UPDATE Users SET password_hash = ? WHERE id = ?", (password_hash, voter_id))
            conn.commit()

            # Create the email content
            subject = "Your Voting Password"
            body = f"Dear Voter,\n\nYour voting password is: {password}\n\nPlease use this to log in and cast your vote."
            msg = MIMEText(body)
            msg["Subject"] = subject
            msg["From"] = sender_email
            msg["To"] = voter_email

            # Send the email
            server.sendmail(sender_email, voter_email, msg.as_string())

        server.quit()
        return "Passwords sent to all voters successfully."

    except smtplib.SMTPException as e:
        return f"Failed to send passwords: {e}"

    finally:
        conn.close()

