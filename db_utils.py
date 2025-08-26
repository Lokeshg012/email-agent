# db_utils.py
import os
import mysql.connector
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# Database configuration
DB_CONFIG = {
    'host': os.getenv("DB_HOST"),
    'port': int(os.getenv("DB_PORT")),
    'user': os.getenv("DB_USER"),
    'password': os.getenv("DB_PASSWORD"),
    'database': os.getenv("DB_NAME"),
    'ssl_ca': os.getenv("DB_SSL_CA")
}

def get_db_connection():
    """Establishes and returns a database connection."""
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except mysql.connector.Error as err:
        print(f"❌ Database Connection Error: {err}")
        return None

def fetch_contacts(status: str | None = "pending", needs_enrichment: bool = False):
    """
    Fetches contacts from the database.
    - `status`: 'pending', 'replied', etc. If None, fetches all contacts.
    - `needs_enrichment`: If True, fetches only contacts where industry is NULL.
    """
    conn = get_db_connection()
    if not conn: return []
    
    contacts = []
    try:
        cursor = conn.cursor(dictionary=True)
        if needs_enrichment:
            query = "SELECT * FROM contacts WHERE industry IS NULL"
            cursor.execute(query)
        elif status is None:
            query = "SELECT * FROM contacts"
            cursor.execute(query)
        else:
            query = "SELECT * FROM contacts WHERE status = %s"
            cursor.execute(query, (status,))
        contacts = cursor.fetchall()
    except mysql.connector.Error as err:
        print(f"❌ Error fetching contacts: {err}")
    finally:
        cursor.close()
        conn.close()
    return contacts

def update_contact_industry(contact_id: int, industry: str):
    """Updates the industry for a specific contact."""
    conn = get_db_connection()
    if not conn: return
    
    try:
        cursor = conn.cursor()
        query = "UPDATE contacts SET industry = %s WHERE id = %s"
        cursor.execute(query, (industry, contact_id))
        conn.commit()
        print(f"✅ DB: Updated industry for contact {contact_id} to '{industry}'")
    except mysql.connector.Error as err:
        print(f"❌ DB Error updating industry: {err}")
    finally:
        cursor.close()
        conn.close()

def log_sent_email(contact_id: int, email_content: str, email_type: str):
    """
    Logs a sent email (initial or drip) and updates the relevant date and timestamp columns.
    `email_type` can be 'initial', 'drip1', 'drip2', or 'drip3'.
    """
    conn = get_db_connection()
    if not conn: return

    column_map = {
        'initial': 'initial_email_content',
        'drip1': 'drip1_email_content',
        'drip2': 'drip2_email_content',
        'drip3': 'drip3_email_content',
    }
    date_column = f"{email_type}_date" if 'drip' in email_type else None
    
    if email_type not in column_map:
        print(f"❌ Invalid email type for logging: {email_type}")
        return

    content_column = column_map[email_type]
    
    try:
        cursor = conn.cursor()
        now = datetime.now()
        
        if date_column:  # Drip email
            query = f"UPDATE contacts SET {content_column} = %s, {date_column} = %s, last_email_sent = %s WHERE id = %s"
            cursor.execute(query, (email_content, now, now, contact_id))
        else:  # Initial email
            query = f"UPDATE contacts SET {content_column} = %s, last_email_sent = %s WHERE id = %s"
            cursor.execute(query, (email_content, now, contact_id))
            
        conn.commit()
        print(f"✅ DB: Logged '{email_type}' email for contact {contact_id}.")
    except mysql.connector.Error as err:
        print(f"❌ DB Error logging sent email: {err}")
    finally:
        cursor.close()
        conn.close()
        
def log_reply(contact_id: int, reply_body: str):
    """Updates a contact's status to 'replied' and stores the reply content and date."""
    conn = get_db_connection()
    if not conn: return
    
    try:
        cursor = conn.cursor()
        query = "UPDATE contacts SET status = 'replied', reply_email_content = %s, reply_date = %s WHERE id = %s"
        cursor.execute(query, (reply_body, datetime.now(), contact_id))
        conn.commit()
        print(f"✅ DB: Marked contact {contact_id} as 'replied'.")
    except mysql.connector.Error as err:
        print(f"❌ DB Error marking as replied: {err}")
    finally:
        cursor.close()
        conn.close()
