# llm_utils.py
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize the OpenAI client
try:
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
except Exception as e:
    print(f"❌ Failed to initialize OpenAI client: {e}")
    client = None

def get_industry_from_llm(company_name: str, company_url: str) -> str | None:
    """
    Uses an LLM to determine the industry of a company.
    """
    if not client: return None
    
    prompt = f"""
    Analyze the following company and determine its primary industry.
    Company Name: {company_name}
    Company URL: {company_url}
    
    Provide only the industry name (e.g., "FinTech", "Digital Marketing", "Healthcare AI").
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0
        )
        return response.choices[0].message.content.strip().replace("\"", "")
    except Exception as e:
        print(f"❌ LLM Error (get_industry): {e}")
        return None

def generate_email_content(contact: dict, email_type: str) -> tuple[str | None, str | None]:
    """
    Generates personalized email content for initial outreach or follow-ups.
    `email_type` can be 'initial', 'drip1', 'drip2', or 'drip3'.
    """
    if not client: return None, None

    # Determine the context of the email
    if email_type == 'initial':
        day_label = "an initial outreach email"
        goal = "The goal is to introduce Pulp Strategy and explain how our marketing services can help their business grow, prompting them to consider a partnership."
    else: # Drip emails
        day_num = email_type.replace('drip', '')
        day_label = f"a Day {day_num} follow-up"
        if day_num == '1':
            goal = "The goal is to gently remind them of the initial email and re-engage them with a friendly check-in."
        elif day_num == '2':
            goal = "The goal is to provide a piece of value, like a relevant statistic for their industry, to demonstrate expertise."
        else: # Drip 3
            goal = "This is a final, brief check-in. Keep it short and ask if timing is not right, aiming for a definitive response."

    prompt = f"""
    You are Lokesh, a business development expert at Pulp Strategy, a top-tier marketing company.
    You are drafting {day_label} to a potential client.
    
    Recipient Details:
    - Name: {contact['name']}
    - Company: {contact['company_name']}
    - Industry: {contact['industry']}

    Email Instructions:
    - {goal}
    - Keep the tone professional, confident, and highly personalized.
    - Your response MUST be in the following format, with nothing before or after:
    Subject: [Email Subject Line]
    Body:
    [Email Body Content]
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.75
        )
        full_response = response.choices[0].message.content.strip()
        
        # Parse the subject and body
        subject = full_response.split("Subject:")[1].split("Body:")[0].strip()
        body = full_response.split("Body:")[1].strip()
        
        return subject, body
    except Exception as e:
        print(f"❌ LLM Error (generate_email for {email_type}): {e}")
        return None, None

def generate_meeting_request_email(contact: dict) -> tuple[str | None, str | None]:
    """
    Generates an email to send after a positive reply, prompting to book a meeting.
    """
    if not client: return None, None

    prompt = f"""
    You are Lokesh from Pulp Strategy. A potential client has replied positively to your outreach.
    Draft a brief, friendly, and professional email to them to book a meeting.
    
    Recipient Name: {contact['name']}
    
    Instructions:
    - Thank them for their reply.
    - Prompt them to book a meeting using a placeholder link.
    - Keep it concise and professional.
    - Your response MUST be in the following format, with nothing before or after:
    Subject: [Email Subject Line]
    Body:
    [Email Body Content]
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5
        )
        full_response = response.choices[0].message.content.strip()
        
        subject = full_response.split("Subject:")[1].split("Body:")[0].strip()
        body = full_response.split("Body:")[1].strip().replace("[Google Calendar Link]", "https://your-calendar-link.com")
        
        return subject, body
    except Exception as e:
        print(f"❌ LLM Error (generate_meeting_request): {e}")
        return None, None
