from flask import Blueprint, request, jsonify
import json
import os
from cryptography.fernet import Fernet

auth_bp = Blueprint('auth', __name__)

USERS_FILE = 'config/users.json'
KEY_FILE = 'secret.key'

def load_key():
    """
    Load an existing encryption key, or generate a new one if not found.
    """
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, 'wb') as key_file:
            key_file.write(key)
    else:
        with open(KEY_FILE, 'rb') as key_file:
            key = key_file.read()
    return key

key = load_key()
fernet = Fernet(key)

def encrypt_password(password):
    """
    Encrypt a password using Fernet encryption.
    """
    return fernet.encrypt(password.encode()).decode()

def decrypt_password(encrypted_password):
    """
    Decrypt an encrypted password using Fernet encryption.
    """
    return fernet.decrypt(encrypted_password.encode()).decode()

def load_users():
    """
    Load users from a JSON file.
    """
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_users(users):
    """
    Save users to a JSON file.
    """
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f)

users = load_users()

@auth_bp.route('/signup', methods=['POST'])
def signup():
    """
    Handle user signup by registering a new user.
    """
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({'status': 'error', 'message': 'Email and password are required'}), 400

        if email in users:
            return jsonify({'status': 'error', 'message': 'User already exists'}), 400

        encrypted_password = encrypt_password(password)
        users[email] = encrypted_password
        save_users(users)
        return jsonify({'status': 'ok', 'message': 'Signup successful'}), 200
    except Exception as e:
        print(f"[ERROR] Failed in signup: {e}")
        return jsonify({'status': 'error', 'message': 'Server error'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Handle user login by verifying credentials.
    """
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({'status': 'error', 'message': 'Email and password are required'}), 400

        encrypted_password = users.get(email)
        if not encrypted_password:
            return jsonify({'status': 'error', 'message': 'Invalid email or password'}), 401

        try:
            decrypted_password = decrypt_password(encrypted_password)
        except Exception:
            return jsonify({'status': 'error', 'message': 'Invalid email or password'}), 401

        if decrypted_password != password:
            return jsonify({'status': 'error', 'message': 'Invalid email or password'}), 401

        return jsonify({'status': 'ok', 'message': 'Login successful'}), 200
    except Exception as e:
        print(f"[ERROR] Failed in login: {e}")
        return jsonify({'status': 'error', 'message': 'Server error'}), 500

@auth_bp.route('/reset_password', methods=['POST'])
def reset_password():
    """
    Handle user password reset.
    """
    try:
        data = request.get_json()
        email = data.get('email')
        new_password = data.get('new_password')

        if not email or not new_password:
            return jsonify({'status': 'error', 'message': 'Email and new password are required'}), 400

        if email not in users:
            return jsonify({'status': 'error', 'message': 'User not found'}), 404

        encrypted_new_password = encrypt_password(new_password)
        users[email] = encrypted_new_password
        save_users(users)
        return jsonify({'status': 'ok', 'message': 'Password reset successful'}), 200
    except Exception as e:
        print(f"[ERROR] Failed in reset_password: {e}")
        return jsonify({'status': 'error', 'message': 'Server error'}), 500
