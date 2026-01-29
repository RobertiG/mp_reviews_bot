from base64 import urlsafe_b64encode
from hashlib import sha256
from cryptography.fernet import Fernet

from app.config import settings


def _derive_key(secret: str) -> bytes:
    digest = sha256(secret.encode("utf-8")).digest()
    return urlsafe_b64encode(digest)


def get_fernet() -> Fernet:
    if not settings.encryption_key:
        raise ValueError("ENCRYPTION_KEY is required")
    return Fernet(_derive_key(settings.encryption_key))


def encrypt_token(token: str) -> str:
    fernet = get_fernet()
    return fernet.encrypt(token.encode("utf-8")).decode("utf-8")


def mask_token(token: str) -> str:
    if len(token) <= 4:
        return "****"
    return f"{token[:2]}***{token[-2:]}"
