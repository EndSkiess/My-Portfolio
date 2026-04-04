import os
import requests
import json
import random
import string
from dotenv import load_dotenv

load_dotenv()
raven_url = os.getenv('RAVEN_URL', 'http://localhost:8080').split(',')[0]
raven_database = os.getenv('RAVEN_DATABASE', 'shizu_bot')

def secret():
    parts = [''.join(random.choices(string.ascii_uppercase + string.digits, k=4)) for _ in range(3)]
    random_code = "-".join(parts)
    print("Generated:", random_code)
    try:
        doc_id = "easteregg/active_codes"
        # Get existing codes
        resp = requests.get(f"{raven_url}/databases/{raven_database}/docs?id={doc_id}")
        codes = []
        if resp.status_code == 200:
            data = resp.json()
            if "Results" in data and len(data["Results"]) > 0:
                doc = data["Results"][0]
                codes = doc.get("codes", [])
        
        codes.append(random_code)
        
        # Put updated codes
        put_resp = requests.put(f"{raven_url}/databases/{raven_database}/docs?id={doc_id}", json={"codes": codes})
        put_resp.raise_for_status()
        print("Successfully saved to DB using REST!")
    except Exception as e:
        print(f"Error saving code to database: {e}")

secret()
