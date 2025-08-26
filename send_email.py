# email_utils.py
import os
import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT"))
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
IMAP_HOST = os.getenv("IMAP_HOST")
IMAP_PORT = int(os.getenv("IMAP_PORT"))

def send_email(to_address, subject, body):
    """Send an email using SMTP"""
    try:
        msg = MIMEText(body, "plain")
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = to_address
        msg["Subject"] = subject

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, to_address, msg.as_string())

        print(f"✅ Email sent to {to_address} with subject: {subject}")
        return True
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        return False


def check_reply(from_address, subject_filter=None):
    """
    Check if a reply is received from the given address.
    Optionally filter by subject.
    """
    try:
        mail = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT)
        mail.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        mail.select("inbox")

        search_criteria = f'(FROM "{from_address}")'
        if subject_filter:
            search_criteria = f'(FROM "{from_address}" SUBJECT "{subject_filter}")'

        status, data = mail.search(None, search_criteria)
        if status != "OK":
            return None

        email_ids = data[0].split()
        if not email_ids:
            return None

        latest_email_id = email_ids[-1]
        status, msg_data = mail.fetch(latest_email_id, "(RFC822)")
        if status != "OK":
            return None

        msg = email.message_from_bytes(msg_data[0][1])
        mail.logout()

        return msg.get_payload(decode=True).decode(errors="ignore")

    except Exception as e:
        print(f"❌ Error checking reply: {e}")
        return None
