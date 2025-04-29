import time
import base64
import os
import re
import pickle
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

messages = {}
deleted_emails_by_user = {}
_model = None
_vectorizer = None

def get_gmail_service():
    """
    Authenticate and return a Gmail API service instance.
    """
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())

    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('gmail', 'v1', credentials=creds)

def get_latest_messages(service, max_results=100):
    """
    Retrieve the latest message IDs from the user's Gmail account.
    """
    try:
        results = service.users().messages().list(userId='me', maxResults=max_results).execute()
        return results.get('messages', [])
    except Exception as e:
        print(f"[ERROR] Failed to fetch Gmail messages: {e}")
        return []

def should_ignore_text(text):
    """
    Determine if a text should be ignored based on predefined rules.
    """
    text = text.lower()
    ignore_keywords = [
        'virus free',
        'avast',
        'utm_medium',
        'utm_source',
        'utm_campaign',
        'utm_content',
    ]
    if any(keyword in text for keyword in ignore_keywords):
        return True

    url_pattern = r'(http[s]?://\S+)'
    links = re.findall(url_pattern, text)
    if links:
        links_text = ' '.join(links)
        link_ratio = len(links_text) / max(len(text), 1)
        if link_ratio > 0.7:
            return True

    return False

def extract_message_text(service, msg_id):
    """
    Extract and clean the text content of a Gmail message.
    """
    try:
        msg = service.users().messages().get(userId='me', id=msg_id, format='full').execute()
        headers = msg.get('payload', {}).get('headers', [])
        sender = next((h['value'] for h in headers if h['name'] == 'From'), '')

        if 'no-reply@' in sender or 'google.com' in sender:
            return ""

        parts = msg.get('payload', {}).get('parts', [])
        for part in parts:
            if part.get('mimeType') == 'text/plain':
                data = part.get('body', {}).get('data')
                if data:
                    decoded = base64.urlsafe_b64decode(data).decode('utf-8').strip()
                    cleaned = clean_text(decoded)
                    if should_ignore_text(cleaned):
                        return ""
                    return cleaned

        body_data = msg.get('payload', {}).get('body', {}).get('data')
        if body_data:
            decoded = base64.urlsafe_b64decode(body_data).decode('utf-8').strip()
            cleaned = clean_text(decoded)
            if should_ignore_text(cleaned):
                return ""
            return cleaned

    except Exception as e:
        print(f"[ERROR] Failed to extract message text: {e}")
    return ""

def clean_text(text):
    """
    Clean text by removing non-alphanumeric characters and lowering case.
    """
    return re.sub(r'\W+', ' ', text).lower()

def classify_local_message(message):
    """
    Classify a local message using the pre-trained phishing detection model.
    """
    global _model, _vectorizer
    try:
        if _model is None or _vectorizer is None:
            with open('models/phishing_model.pkl', 'rb') as f:
                _model = pickle.load(f)
            with open('models/vectorizer.pkl', 'rb') as f:
                _vectorizer = pickle.load(f)

        vec = _vectorizer.transform([message])
        prediction = _model.predict(vec)[0]
        return "phishing" if int(prediction) == 1 else "not_phishing"
    except Exception as e:
        print(f"[ERROR] Local model prediction failed: {e}")
        return 'error'

def fetch_gmail_periodically():
    """
    Continuously fetch Gmail messages in a background thread.
    """
    global messages
    service = None
    username = "gmail_user"

    while True:
        try:
            if not service:
                print("[DEBUG] Connecting to Gmail...")
                service = get_gmail_service()
                print("[DEBUG] Gmail service connected.")

            print("[DEBUG] Fetching emails...")
            message_ids = get_latest_messages(service)
            print(f"[DEBUG] {len(message_ids)} messages fetched.")

            if username not in messages:
                messages[username] = []

            deleted_set = deleted_emails_by_user.get(username, set())

            for msg in message_ids:
                text = extract_message_text(service, msg['id'])
                if not text.strip() or len(text) > 50:
                    continue

                if any(m['message'] == text for m in messages[username]):
                    continue

                if text in deleted_set:
                    continue

                result = classify_local_message(text)
                messages[username].append({'message': text, 'result': result})
                print(f"[DEBUG] New email for {username}: {text[:30]}... → {result}")

        except Exception as e:
            print(f"[WARNING] Problem fetching Gmail messages: {e}")
            service = None

        time.sleep(30)

def fetch_gmail_once(username):
    """
    Fetch Gmail messages once for a specific user.
    """
    global messages

    try:
        print(f"[DEBUG] Fetching emails (manual request) for {username}...")
        service = get_gmail_service()
        message_ids = get_latest_messages(service)
        print(f"[DEBUG] {len(message_ids)} messages fetched manually.")

        if username not in messages:
            messages[username] = []

        deleted_set = deleted_emails_by_user.get(username, set())

        new_messages = []
        for msg in message_ids:
            text = extract_message_text(service, msg['id'])
            if not text.strip() or len(text) > 50:
                continue

            if any(m['message'] == text for m in messages[username]):
                continue

            if text in deleted_set:
                continue

            result = classify_local_message(text)
            message_entry = {'message': text, 'result': result}
            messages[username].append(message_entry)
            new_messages.append(message_entry)
            print(f"[DEBUG] New email for {username}: {text[:30]}... → {result}")

        print(f"[DEBUG] {len(new_messages)} new emails added manually for {username}.")
    except Exception as e:
        print(f"[ERROR] Manual Gmail fetch failed: {e}")
