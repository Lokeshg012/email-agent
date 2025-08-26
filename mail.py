import os
import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from dotenv import load_dotenv
from db_utils import log_sent_email, log_reply
from llm_work import generate_email_content, generate_meeting_request_email

load_dotenv()

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT"))
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
IMAP_HOST = os.getenv("IMAP_HOST")
IMAP_PORT = int(os.getenv("IMAP_PORT"))

def send_email(to_address: str, subject: str, body: str):
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = to_address
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
        print(f"✅ Email sent to {to_address}")
        return True
    except Exception as e:
        print(f"❌ Email send error: {e}")
        return False

def check_email_reply(sender_email: str, since_days: int = 7):
    try:
        mail = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT)
        mail.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        mail.select("inbox")

        date = (datetime.now() - timedelta(days=since_days)).strftime("%d-%b-%Y")
        status, data = mail.search(None, f'(FROM "{sender_email}" SINCE {date})')
        if status != "OK" or not data[0]:
            return None

        mail_ids = data[0].split()
        for mail_id in reversed(mail_ids):
            status, msg_data = mail.fetch(mail_id, "(RFC822)")
            if status != "OK":
                continue
            msg = email.message_from_bytes(msg_data[0][1])
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        return part.get_payload(decode=True).decode()
            else:
                return msg.get_payload(decode=True).decode()
        return None
    except Exception as e:
        print(f"❌ Check reply error: {e}")
        return None
    finally:
        try:
            mail.logout()
        except: pass

def send_drip_email(contact: dict, drip_type: str):
    reply_content = check_email_reply(contact['email'])
    if reply_content:
        log_reply(contact['id'], reply_content)
        print(f"✅ Contact {contact['id']} replied. No drip sent.")
        return

    subject, body = generate_email_content(contact, drip_type)
    if not subject or not body:
        print(f"❌ Failed to generate {drip_type} email for contact {contact['id']}")
        return

    if send_email(contact['email'], subject, body):
        log_sent_email(contact['id'], body, drip_type)
