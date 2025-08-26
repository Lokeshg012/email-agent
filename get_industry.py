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
def get_industry_from_llm(company_name, company_url):
    """Send company details to LLM and return industry type."""
    prompt = f"""
    Give me only the industry type of this company:
    Name: {company_name}
    URL: {company_url}
    Reply with only the industry name (like 'Fintech', 'Marketing', 'Sports Tech').
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    return response.choices[0].message.content.strip()

def enrich_and_update():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # Fetch contacts without industry
        cursor.execute("SELECT id, company_name, company_url FROM contacts WHERE industry IS NULL;")
        rows = cursor.fetchall()

        for row in rows:
            company_name = row["company_name"]
            company_url = row["company_url"]

            print(f" Fetching industry for: {company_name} ({company_url})")
            industry = get_industry_from_llm(company_name, company_url)
            print(f"Industry: {industry}")

            # Update database
            cursor.execute(
                "UPDATE contacts SET industry = %s WHERE id = %s",
                (industry, row["id"])
            )
            conn.commit()

        cursor.close()
        conn.close()

    except mysql.connector.Error as e:
        print("Database error:", e)

# ---------- MAIN ----------
if __name__ == "__main__":
    enrich_and_update()