"""Who is calling the public API: authenticate the key (if any), apply the rate limit, count usage.

Keys are optional. Without one, callers share a smaller per-IP allowance; with one they get a
bigger allowance and a usage history in the portal.
"""

from fastapi import Depends, Request, Security
from fastapi.security import APIKeyHeader
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as postgres_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.orm import Session

from . import clock
from .config import settings
from .database import get_db
from .models import ApiKey, UsageDay
from .problems import Problem
from .ratelimit import FixedWindowLimiter
from .security import hash_api_key

api_key_header = APIKeyHeader(
    name="X-API-Key",
    auto_error=False,
    description=(
        f"Optional. Without a key you get {settings.anonymous_limit} requests per hour per IP address; "
        f"with one, {settings.key_limit}. Create keys in the developer portal."
    ),
)
limiter = FixedWindowLimiter(settings.rate_window_seconds)


def api_access(request: Request, key: str | None = Security(api_key_header), db: Session = Depends(get_db)):
    api_key = None
    if key:
        api_key = db.scalar(select(ApiKey).where(ApiKey.key_hash == hash_api_key(key)))
        if api_key is None or api_key.revoked_at is not None:
            # A bad key is an error, not a silent fallback to anonymous: the caller would never notice.
            raise Problem(401, "invalid-key", "Invalid API key",
                          "This API key doesn't exist or was revoked. Send no key to use the anonymous limit.")
        caller, limit = f"key:{api_key.id}", settings.key_limit
    else:
        # Behind Render's proxy, uvicorn's --proxy-headers puts the real client address here.
        caller, limit = f"ip:{request.client.host if request.client else 'unknown'}", settings.anonymous_limit

    decision = limiter.hit(caller, limit)
    # A middleware in main.py copies these onto every response, errors included.
    request.state.rate_headers = decision.headers(limiter.window)
    if not decision.allowed:
        raise Problem(429, "rate-limited", "Too many requests",
                      f"You've used all {limit} requests for this window. Try again in {decision.reset_after} seconds."
                      + ("" if api_key else " An API key raises the limit."))
    if api_key is not None:
        record_usage(db, api_key)
    return api_key


def record_usage(db: Session, api_key: ApiKey) -> None:
    """Add one to today's counter for the key, as a single atomic upsert.

    "INSERT ... ON CONFLICT DO UPDATE" avoids the read-then-write race two simultaneous requests
    would have. Postgres and SQLite both support it, with the same SQLAlchemy API.
    """
    now = clock.now()
    insert = postgres_insert if db.get_bind().dialect.name == "postgresql" else sqlite_insert
    statement = insert(UsageDay).values(api_key_id=api_key.id, day=now.date(), count=1)
    statement = statement.on_conflict_do_update(
        index_elements=["api_key_id", "day"], set_={"count": UsageDay.__table__.c.count + 1}
    )
    db.execute(statement)
    api_key.last_used_at = now
    db.commit()
