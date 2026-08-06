import os
import hmac
import hashlib
import time
import secrets
from typing import Optional
from fastapi import Request, HTTPException, status
from fastapi.responses import RedirectResponse

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
SESSION_SECRET = os.getenv("SESSION_SECRET", "cybertrack_secret_key_2026_super_secure")

COOKIE_NAME = "cybertrack_session"
SESSION_MAX_AGE = 7 * 24 * 60 * 60  # 7 days in seconds


def verify_credentials(username: str, password: str) -> bool:
    """Constant-time verification of admin credentials."""
    user_match = secrets.compare_digest(username.strip(), ADMIN_USERNAME.strip())
    pass_match = secrets.compare_digest(password.strip(), ADMIN_PASSWORD.strip())
    return user_match and pass_match


def create_session_token(username: str) -> str:
    """Generate a signed HMAC session token containing username and timestamp."""
    timestamp = str(int(time.time()))
    payload = f"{username}:{timestamp}"
    signature = hmac.new(
        SESSION_SECRET.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    return f"{payload}:{signature}"


def verify_session_token(token: Optional[str]) -> bool:
    """Verify validity, expiration, and cryptographic signature of session token."""
    if not token or ":" not in token:
        return False

    parts = token.split(":")
    if len(parts) != 3:
        return False

    username, timestamp_str, signature = parts
    try:
        timestamp = int(timestamp_str)
    except ValueError:
        return False

    # Check expiration (7 days)
    if time.time() - timestamp > SESSION_MAX_AGE:
        return False

    # Verify signature
    payload = f"{username}:{timestamp_str}"
    expected_sig = hmac.new(
        SESSION_SECRET.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()

    return secrets.compare_digest(signature, expected_sig)


def is_authenticated(request: Request) -> bool:
    """Check if the incoming request has a valid session cookie."""
    token = request.cookies.get(COOKIE_NAME)
    return verify_session_token(token)
