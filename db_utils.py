# db_utils.py (add this)
from datetime import datetime

def log_initial_email(contact_id: int, client_email: str, email_content: str):
    """Insert the initial email content into content_info_of_mails"""
    import mysql.connector
    from dotenv import load_dotenv
    import os

    load_dotenv()

    db_config = {
        'host': os.getenv('DB_HOST'),
        'port': int(os.getenv('DB_PORT')),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'database': os.getenv('DB_NAME'),
        'ssl_ca': os.getenv('DB_SSL_CA')
    }

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    query = """
    INSERT INTO content_info_of_mails
        (contact_id, client_email, initial_email_content, created_at, updated_at)
    VALUES (%s, %s, %s, %s, %s)
    """
    now = datetime.now()
    cursor.execute(query, (contact_id, client_email, email_content, now, now))
    conn.commit()
    cursor.close()
    conn.close()
    print(f"✅ Logged initial email for contact_id {contact_id}")
