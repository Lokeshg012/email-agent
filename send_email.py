# email_utils.py
from generate_mail import fetch_first_contact, generate_mail
from db_utils import log_initial_email  # import the logging function
import os, smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT"))
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")


def send_email(to_address, subject, body):
    try:
        msg = MIMEText(body, "plain")
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = to_address
        msg["Subject"] = subject

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, to_address, msg.as_string())

        print(f"✅ Email sent to {to_address}")
        return True
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        return False


def send_initial_mail():
    contact = fetch_first_contact()
    if not contact:
        print("❌ No contact with industry found.")
        return

    subject, body = generate_mail(contact)
    print("\n------ DAY 1 MAIL ------\n")
    print("Subject:", subject)
    print("Body:", body)

    if send_email(contact["email"], subject, body):
        # Log the sent mail into content_info_of_mails table
        log_initial_email(contact["id"], contact["email"], body)


if __name__ == "__main__":
    send_initial_mail()
