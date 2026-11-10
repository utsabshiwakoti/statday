"""Portal logins (passwords + JWT) and API keys (random secrets stored as SHA-256 hashes)."""

import hashlib
import hmac
import os
import secrets
from datetime import UTC, datetime, timedelta

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from .config import settings
from .database import get_db
from .models import Developer

ALGORITHM = "HS256"
TOKEN_TTL = timedelta(hours=12)
_SCRYPT = {"n": 2**14, "r": 8, "p": 1}  # scrypt: memory-hard password hash in the standard library
KEY_PREFIX = "sd_"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.scrypt(password.encode(), salt=salt, **_SCRYPT)
    return f"{salt.hex()}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        salt_hex, digest_hex = stored.split("$")
        actual = hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt_hex), **_SCRYPT)
    except ValueError:
        return False
    return hmac.compare_digest(actual, bytes.fromhex(digest_hex))  # constant-time compare


def create_access_token(developer_id: int) -> str:
    # Real wall-clock time, not app.clock: PyJWT checks "exp" against the real time too.
    payload = {"sub": str(developer_id), "exp": datetime.now(UTC) + TOKEN_TTL}
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)


def get_developer(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Developer:
    error = HTTPException(
        status.HTTP_401_UNAUTHORIZED, "Sign in again to continue.", headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        developer_id = int(jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        raise error from None
    developer = db.get(Developer, developer_id)
    if developer is None:
        raise error
    return developer


def new_api_key() -> tuple[str, str, str]:
    """Return (full key, display prefix, hash) for a key like `sd_3f9a1c2e_<32 random characters>`.

    The secret part has 192 random bits, so a fast hash (SHA-256) is enough: unlike a password it
    can't be guessed from a dictionary. That keeps the check on every API request cheap.
    """
    public = secrets.token_hex(4)
    key = f"{KEY_PREFIX}{public}_{secrets.token_urlsafe(24)}"
    return key, f"{KEY_PREFIX}{public}", hash_api_key(key)


def hash_api_key(key: str) -> str:
    return hashlib.sha256(key.encode()).hexdigest()
