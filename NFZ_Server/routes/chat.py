from flask import Blueprint, request, jsonify
import datetime
from utils.encryption_util import decrypt_text

chat_bp = Blueprint('chat', __name__)

chat_messages = []

@chat_bp.route('/send_message', methods=['POST'])
def send_message():
    """
    Handle sending a new chat message from a user.
    """
    try:
        data = request.get_json()
        username = data.get('username')
        message = data.get('message')

        if username and message:
            if len(message) > 5000:
                return jsonify({'status': 'error', 'message': 'Message too long'}), 400

            timestamp = datetime.datetime.now().isoformat()
            chat_messages.append({
                'username': username,
                'message': message,
                'timestamp': timestamp,
            })
            return jsonify({'status': 'ok', 'message': 'Message sent successfully'}), 200

        return jsonify({'status': 'error', 'message': 'Invalid request'}), 400
    except Exception as e:
        print(f"[ERROR] Failed to process send_message: {e}")
        return jsonify({'status': 'error', 'message': 'Server error'}), 500

@chat_bp.route('/chat_messages', methods=['GET'])
def get_chat_messages():
    """
    Retrieve all chat messages, decrypting each message before returning.
    """
    decrypted_messages = []
    for msg in chat_messages:
        decrypted_msg = msg.copy()
        decrypted_msg['message'] = decrypt_text(msg['message']) or msg['message']
        decrypted_messages.append(decrypted_msg)
    return jsonify(decrypted_messages)
