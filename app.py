import mysql.connector
import os
db_config = {
    'host': 'email-agent-email-agent.b.aivencloud.com',
    'port': 13503,
    'user': 'avnadmin',
    'password':os.getenv('AIVEN_PASSWORD') ,
    'database': 'defaultdb',
    'ssl_ca': r'C:\Users\lokesh\OneDrive\Desktop\pulp-intern\ca.pem'
}

try:
    connection = mysql.connector.connect(**db_config)

    if connection.is_connected():
        print("✅ Connected to Aiven MySQL!")

        cursor = connection.cursor(dictionary=True)

        # Fetch only required columns
        cursor.execute("SELECT name, email, company_name, company_url FROM contacts;")
        rows = cursor.fetchall()

        for row in rows:
            print(row)   # Each row will be a dict with the 4 keys

        cursor.close()
        connection.close()

except mysql.connector.Error as e:
    print("❌ Error while connecting to MySQL:", e)
