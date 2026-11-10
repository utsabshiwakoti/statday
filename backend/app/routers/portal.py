"""The developer portal's backend: accounts, API keys and usage.

Not part of the public API, so it's left out of the OpenAPI docs and the SDK.
"""

from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .. import clock
from ..config import settings
from ..database import get_db
from ..models import ApiKey, Developer, UsageDay
from ..problems import Problem
from ..schemas import KeyCreated, KeyIn, KeyOut, Me, SignupIn, Token, UsageOut, UsagePoint
from ..security import create_access_token, get_developer, hash_password, new_api_key, verify_password

router = APIRouter(prefix="/api", include_in_schema=False)
CurrentDeveloper = Annotated[Developer, Depends(get_developer)]
DB = Annotated[Session, Depends(get_db)]


@router.post("/auth/signup", response_model=Token, status_code=status.HTTP_201_CREATED)
def signup(body: SignupIn, db: DB):
    developer = Developer(email=body.email.lower(), password_hash=hash_password(body.password))
    db.add(developer)
    try:
        db.commit()
    except IntegrityError:  # the unique constraint, not a pre-check, decides: no race between two signups
        db.rollback()
        raise Problem(409, "email-taken", "Email already registered", "Sign in instead.") from None
    return Token(access_token=create_access_token(developer.id))


@router.post("/auth/token", response_model=Token)
def login(form: Annotated[OAuth2PasswordRequestForm, Depends()], db: DB):
    developer = db.scalar(select(Developer).where(Developer.email == form.username.lower()))
    # Same message either way, so the form can't be used to find out who has an account.
    if developer is None or not verify_password(form.password, developer.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Wrong email or password.")
    return Token(access_token=create_access_token(developer.id))


@router.get("/me", response_model=Me)
def me(developer: CurrentDeveloper):
    return Me(email=developer.email, created_at=developer.created_at,
              limits={"requests_per_window": settings.key_limit, "window_seconds": settings.rate_window_seconds,
                      "max_keys": settings.max_keys_per_developer})


# ---------- keys ----------


def own_key(db: Session, developer: Developer, key_id: int) -> ApiKey:
    key = db.get(ApiKey, key_id)
    if key is None or key.developer_id != developer.id:  # 404 either way, so ids can't be probed
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No such key.")
    return key


def active_count(db: Session, developer: Developer) -> int:
    return db.scalar(select(func.count()).select_from(ApiKey).where(
        ApiKey.developer_id == developer.id, ApiKey.revoked_at.is_(None)))


@router.get("/keys", response_model=list[KeyOut])
def list_keys(developer: CurrentDeveloper, db: DB):
    return db.scalars(select(ApiKey).where(ApiKey.developer_id == developer.id).order_by(ApiKey.id)).all()


@router.post("/keys", response_model=KeyCreated, status_code=status.HTTP_201_CREATED)
def create_key(body: KeyIn, developer: CurrentDeveloper, db: DB):
    if active_count(db, developer) >= settings.max_keys_per_developer:
        raise Problem(409, "too-many-keys", "Too many keys",
                      f"You can have {settings.max_keys_per_developer} active keys. Revoke one first.")
    full, prefix, digest = new_api_key()
    key = ApiKey(developer_id=developer.id, name=body.name.strip(), prefix=prefix, key_hash=digest)
    db.add(key)
    db.commit()
    return KeyCreated(**KeyOut.model_validate(key, from_attributes=True).model_dump(), key=full)


@router.post("/keys/{key_id}/rotate", response_model=KeyCreated, status_code=status.HTTP_201_CREATED)
def rotate_key(key_id: int, developer: CurrentDeveloper, db: DB):
    """Revoke a key and issue a replacement with the same name, in one step."""
    old = own_key(db, developer, key_id)
    if old.revoked_at is not None:
        raise Problem(409, "key-revoked", "Key already revoked", "Create a new key instead.")
    old.revoked_at = clock.now()
    full, prefix, digest = new_api_key()
    key = ApiKey(developer_id=developer.id, name=old.name, prefix=prefix, key_hash=digest)
    db.add(key)
    db.commit()
    return KeyCreated(**KeyOut.model_validate(key, from_attributes=True).model_dump(), key=full)


@router.delete("/keys/{key_id}", response_model=KeyOut)
def revoke_key(key_id: int, developer: CurrentDeveloper, db: DB):
    """Revoke, don't delete: the key's usage history stays in the charts."""
    key = own_key(db, developer, key_id)
    if key.revoked_at is None:
        key.revoked_at = clock.now()
        db.commit()
    return key


# ---------- usage ----------


@router.get("/usage", response_model=UsageOut)
def usage(developer: CurrentDeveloper, db: DB, days: Annotated[int, Query(ge=1, le=90)] = 30):
    """Requests per day across all of the developer's keys, with zero-filled gaps for the chart."""
    today = clock.now().date()
    first = today - timedelta(days=days - 1)
    rows = db.execute(
        select(UsageDay.day, UsageDay.api_key_id, UsageDay.count)
        .join(ApiKey, ApiKey.id == UsageDay.api_key_id)
        .where(ApiKey.developer_id == developer.id, UsageDay.day >= first)
    ).all()
    per_day: dict = {}
    by_key: dict[int, int] = {}
    for day, key_id, count in rows:
        per_day[day] = per_day.get(day, 0) + count
        by_key[key_id] = by_key.get(key_id, 0) + count
    points = [UsagePoint(day=first + timedelta(days=i), count=per_day.get(first + timedelta(days=i), 0))
              for i in range(days)]
    return UsageOut(days=points, total=sum(p.count for p in points), by_key=by_key)
