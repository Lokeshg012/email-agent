# db_utils.py
import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    'host': os.getenv("DB_HOST"),
    'port': int(os.getenv("DB_PORT")),
    'user': os.getenv("DB_USER"),
    'password': os.getenv("DB_PASSWORD"),
    'database': os.getenv("DB_NAME"),
    'ssl_ca': os.getenv("DB_SSL_CA", None)  # Optional SSL cert for Aiven
}


def get_connection():
    return mysql.connector.connect(**DB_CONFIG)


def fetch_contacts():
    """Fetch contacts from the database"""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM contacts WHERE status='pending'")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def store_email_log(contact_id, subject, body, sent_status):
    """Store email logs in a separate table"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO email_logs (contact_id, subject, body, sent_status, created_at)
        VALUES (%s, %s, %s, %s, NOW())
    """, (contact_id, subject, body, sent_status))
    conn.commit()
    cursor.close()
    conn.close()


def update_contact_status(contact_id, status, last_email_date=None):
    """Update contact status (e.g., replied, no_reply, meeting_booked)"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE contacts SET status=%s, last_email_date=%s WHERE id=%s
    """, (status, last_email_date, contact_id))
    conn.commit()
    cursor.close()
    conn.close()
