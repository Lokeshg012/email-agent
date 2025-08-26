# workflow_test_no_status.py
import time
from db_utils import fetch_contacts, update_contact_industry
from llm_work import get_industry_from_llm
from mail import send_drip_email

def test_email_workflow():
    # Fetch all contacts (no status filter)
    contacts = fetch_contacts(status=None)  # Adjusted fetch_contacts to handle None
    if not contacts:
        print("❌ No contacts found.")
        return

    for contact in contacts:
        print(f"\n--- Processing Contact: {contact['name']} ({contact['company_name']}) ---")

        # 1️⃣ Enrich industry if missing
        if not contact.get("industry"):
            industry = get_industry_from_llm(contact["company_name"], contact.get("company_url", ""))
            if industry:
                update_contact_industry(contact["id"], industry)
                contact["industry"] = industry
            else:
                print(f"❌ Failed to get industry for {contact['company_name']}")

        # 2️⃣ Send initial email
        print("✉️ Sending initial email...")
        send_drip_email(contact, "initial")

        # 3️⃣ Simulate drip sequence
        for i in range(1, 4):
            print(f"\n⏱ Simulating Day {i} drip...")
            time.sleep(2)  # Short delay for testing
            drip_type = f"drip{i}"
            send_drip_email(contact, drip_type)

if __name__ == "__main__":
    test_email_workflow()
