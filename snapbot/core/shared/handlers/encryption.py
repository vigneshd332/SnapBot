import os
from typing import Optional

from cryptography.fernet import Fernet, InvalidToken

KEY = os.getenv("ENCRYPTION_KEY").encode()  # Convert the key string to bytes
fernet = Fernet(KEY)  # Load the fernet using the key


def encrypt(message: str) -> str:
    """Returns the encrypted version of the provided message."""
    encrypted_message = fernet.encrypt(message.encode()).decode()
    return encrypted_message


def decrypt(encrypted_message: str) -> Optional[str]:
    """Returns the decrypted( original ) version of the provided encrypted message."""
    try:
        decrypted_message = fernet.decrypt(encrypted_message)
    except InvalidToken:
        return None
    return decrypted_message.decode()
