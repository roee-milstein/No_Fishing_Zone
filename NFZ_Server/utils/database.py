import json
from datetime import datetime

def store_email_for_user(username, email_data):
    """
    Store an email for a specific user in a JSON file.
    A timestamp is added to each email entry.
    """
    filename = f"{username}_emails.json"

    email_data["timestamp"] = datetime.now().isoformat()

    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = []

    data.append(email_data)

    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, sort_keys=True)
    except Exception as e:
        print(f"[ERROR] Failed to save emails for user {username}: {e}")
