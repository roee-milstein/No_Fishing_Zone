from flask import Flask, request, jsonify
from flask_cors import CORS

from services.model import load_model_and_vectorizer, predict_phishing
from services.fetch_emails import fetch_gmail_periodically, fetch_gmail_once
from routes.auth import auth_bp
from routes.chat import chat_bp
from routes.chat import chat_messages
from utils.encryption_util import encrypt_text
import services.fetch_emails as fetch_emails

import time
import threading

# Initialize Flask app
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(chat_bp)

# Load model and vectorizer
model, vectorizer = load_model_and_vectorizer()

# Data storage for users
user_messages = {}
user_emails = {}
deleted_emails_by_user = {}

def start_gmail_fetching():
    """
    Start a background thread to periodically fetch Gmail messages.
    """
    thread = threading.Thread(target=fetch_gmail_periodically, daemon=True)
    thread.start()

@app.route('/predict_message', methods=['POST'])
def predict_message_route():
    """
    Classify a given message as phishing or not.
    """
    data = request.get_json()
    username = data.get("username", "unknown")
    message = data.get("message", "")

    if not message.strip():
        return jsonify({"status": "error", "message": "Empty message"}), 400

    label_numeric = predict_phishing(model, vectorizer, message)
    label_str = "phishing" if label_numeric == 1 else "not_phishing"

    user_messages.setdefault(username, []).append({
        "text": message,
        "timestamp": time.time(),
        "label": label_str
    })

    return jsonify({"status": "ok", "label": label_str})

@app.route('/send_chat_message', methods=['POST'])
def send_chat_message():
    """
    Receive and store a chat message from a user.
    """
    data = request.get_json()
    username = data.get("username", "anonymous")
    message = data.get("message", "")

    if not message.strip():
        return jsonify({"status": "error", "message": "Empty chat message"}), 400

    encrypted_message = encrypt_text(message) or message

    chat_messages.append({
        "username": username,
        "message": encrypted_message,
        "timestamp": time.time()
    })

    return jsonify({"status": "ok"})

@app.route('/get_messages', methods=['GET'])
def get_messages():
    """
    Retrieve all messages for a specific user, sorted by timestamp.
    """
    username = request.args.get("username", "")
    messages_for_user = user_messages.get(username, [])
    sorted_messages = sorted(messages_for_user, key=lambda x: x['timestamp'], reverse=True)
    return jsonify(sorted_messages)

@app.route('/delete_message', methods=['POST'])
def delete_message():
    """
    Delete a specific message for a user.
    """
    data = request.get_json()
    username = data.get("username", "")
    text = data.get("text", "")

    original_length = len(user_messages.get(username, []))
    user_messages[username] = [
        msg for msg in user_messages.get(username, []) if msg["text"] != text
    ]

    if len(user_messages[username]) < original_length:
        return jsonify({"status": "ok"})
    else:
        return jsonify({"status": "error", "message": "Message not found"}), 404

@app.route('/fetch_emails', methods=['POST'])
def fetch_emails_route():
    """
    Fetch emails from Gmail and assign them to a user, excluding deleted ones.
    """
    data = request.get_json()
    username = data.get("username", "")

    if not username:
        return jsonify({"status": "error", "message": "Username is required"}), 400

    fetch_gmail_once(username)

    deleted_set = deleted_emails_by_user.get(username, set())

    def normalize(s):
        return s.replace('\n', ' ').replace('\r', ' ').strip()

    user_emails[username] = [
        msg for msg in fetch_emails.messages.get(username, [])
        if isinstance(msg, dict) and normalize(msg.get("message", "")) not in deleted_set
    ]

    return jsonify({"status": "ok", "message": "Emails fetched successfully"})

@app.route('/get_emails', methods=['GET'])
def get_emails():
    """
    Retrieve all emails for a specific user.
    """
    username = request.args.get("username", "")
    emails_for_user = user_emails.get(username, [])
    return jsonify(emails_for_user)

@app.route('/delete_email', methods=['POST'])
def delete_email():
    """
    Mark an email as deleted for a user.
    """
    data = request.get_json()
    username = data.get("username", "")
    text = data.get("text", "")

    def normalize(s):
        return s.replace('\n', ' ').replace('\r', ' ').strip()

    if not username or not text:
        return jsonify({"status": "error", "message": "Username and text are required"}), 400

    deleted_emails_by_user.setdefault(username, set()).add(normalize(text))

    original_emails = user_emails.get(username, [])
    user_emails[username] = [
        email for email in original_emails
        if normalize(email.get("message", "")) != normalize(text)
    ]

    return jsonify({"status": "ok"})

if __name__ == '__main__':
    print("[DEBUG] Starting Gmail background threads...")
    threading.Thread(target=start_gmail_fetching, daemon=True).start()
    app.run(host='0.0.0.0', port=5000)
