from cryptography.fernet import Fernet

# Generate a secret key for encryption and decryption
SECRET_KEY = Fernet.generate_key()
cipher = Fernet(SECRET_KEY)

def encrypt_text(text):
    """
    Encrypt a given text using Fernet encryption.
    """
    try:
        return cipher.encrypt(text.encode()).decode()
    except Exception as e:
        print(f"[ERROR] Encryption failed: {e}")
        return None

def decrypt_text(encrypted_text):
    """
    Decrypt a given encrypted text using Fernet encryption.
    """
    try:
        return cipher.decrypt(encrypted_text.encode()).decode()
    except Exception as e:
        print(f"[ERROR] Decryption failed: {e}")
        return None
