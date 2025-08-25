from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
import datetime
import time
from email import send_email, check_reply
from db_utils import fetch_contacts, store_email_log, update_contact_status

llm = ChatOpenAI(model="gpt-4o-mini")

def detect_industry(state):
    contact = state["contact"]
    prompt = f"""Given details:
    Name: {contact['name']}
    Company: {contact['company_name']}
    URL: {contact['company_url']}
    What industry does this company belong to? Reply with only the industry name."""
    industry = llm.invoke(prompt).content.strip()
    contact["industry"] = industry
    return {"contact": contact}

def draft_email(state):
    contact = state["contact"]
    day = state["day"]
    reply = state["reply"]

    if reply:   # If replied, send calendar booking email
        prompt = f"""Draft a short professional email to {contact['name']} ({contact['company_name']}) 
        thanking them for replying and suggesting to book a date in Google Calendar for a call."""
    else:
        prompt = f"""Draft a convincing cold email for day {day} to {contact['name']} from {contact['company_name']} 
        in {contact['industry']} industry. Goal: convert them into a client."""
    
    email = llm.invoke(prompt).content
    state["email"] = email
    return state

def send_and_log(state):
    contact = state["contact"]
    email_content = state["email"]
    day = state["day"]

    # Send Email
    send_email(contact["email"], f"Our Offer - Day {day}", email_content)

    # Log in DB
    store_email_log(contact["id"], day, f"Our Offer - Day {day}", email_content)
    update_contact_status(contact["id"], last_email_date=datetime.date.today())

    return state

def wait_and_check(state):
    contact = state["contact"]

    # Wait 1 day before next email
    time.sleep(5)  # ⏳ Replace 5 sec with 86400 for real 1 day

    # Check reply
    reply = check_reply(contact["email"])
    state["reply"] = reply

    if reply:
        update_contact_status(contact["id"], status="replied", reply_status=True)
        return {"reply": True}
    else:
        return {"reply": False, "day": state["day"] + 1}

# -------------------
# Build LangGraph
# -------------------
workflow = StateGraph(dict)

workflow.add_node("detect_industry", detect_industry)
workflow.add_node("draft_email", draft_email)
workflow.add_node("send_and_log", send_and_log)
workflow.add_node("wait_and_check", wait_and_check)

workflow.add_edge("detect_industry", "draft_email")
workflow.add_edge("draft_email", "send_and_log")
workflow.add_edge("send_and_log", "wait_and_check")
workflow.add_edge("wait_and_check", "draft_email")  # loop until reply

workflow.add_edge("wait_and_check", END)

graph = workflow.compile()
