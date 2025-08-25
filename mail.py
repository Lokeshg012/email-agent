# generate_mail.py
import mysql.connector
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

# ---------- CONFIG ----------
db_config = {
    'host': 'email-agent-email-agent.b.aivencloud.com',
    'port': 13503,
    'user': 'avnadmin',
    'password': os.getenv('AIVEN_PASSWORD'),
    'database': 'defaultdb',
    'ssl_ca': 'ca.pem'
}

# OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# ---------- FUNCTIONS ----------
def generate_mail(contact):
    """Generate a cold outreach mail using contact details."""
    prompt = f"""
You are writing a professional cold outreach email.  

Sender details:  
- Name: Piyush Mishra  
- Company: XYZ Company  
- Role: Business Development Partner for Pulp Strategy (a digital marketing and strategy agency).  

Recipient details:  
- Name: {contact['name']}  
- Company: {contact['company_name']}  
- Website: {contact['company_url']}  
- Industry: {contact['industry']}  

Instructions:  
- Write the email as if it’s coming from Piyush Mishra (XYZ Company) on behalf of Pulp Strategy.  
- Make it personalized by referencing their company and industry.  
- Highlight how **Pulp Strategy** can add value in their industry context.  
- Keep the tone professional, friendly, and non-generic.  
- Structure: **Subject line + Email body**.  
- End with a polite call-to-action for a quick call/meeting.  
"""


    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return response.choices[0].message.content.strip()

def fetch_first_contact():
    """Fetch the first contact with industry filled."""
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT id, name, company_name, company_url, industry FROM contacts WHERE industry IS NOT NULL LIMIT 1;")
    row = cursor.fetchone()

    cursor.close()
    conn.close()
    return row

# ---------- MAIN ----------
if __name__ == "__main__":
    contact = fetch_first_contact()
    if contact:
        print(f"✉️ Generating mail for: {contact['name']} ({contact['company_name']})")
        mail_content = generate_mail(contact)
        print("\n------ GENERATED MAIL ------\n")
        print(mail_content)
    else:
        print("❌ No contact with industry found.")
