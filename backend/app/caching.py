"""HTTP caching with ETags.

Every successful API response gets an ETag (a hash of its exact bytes). A client that sends it
back in If-None-Match gets "304 Not Modified" with no body when nothing changed, which saves
bandwidth and lets HTTP caches revalidate instead of downloading again.
"""

import hashlib
import json

from fastapi import Request, Response
from pydantic import BaseModel

DAY = 86_400


def make_etag(body: bytes) -> str:
    return '"' + hashlib.sha256(body).hexdigest()[:32] + '"'


def etag_matches(if_none_match: str | None, etag: str) -> bool:
    """If-None-Match can be "*" or a list like `"abc", W/"def"`. Weak validators count for GET."""
    if not if_none_match:
        return False
    if if_none_match.strip() == "*":
        return True
    candidates = (tag.strip().removeprefix("W/") for tag in if_none_match.split(","))
    return etag in candidates


def cached_json(request: Request, payload: BaseModel, max_age: int, headers: dict | None = None) -> Response:
    """Serialise the payload once, then answer 304 if the client already has these exact bytes."""
    body = json.dumps(payload.model_dump(mode="json"), ensure_ascii=False, separators=(",", ":")).encode()
    etag = make_etag(body)
    cache_headers = {"ETag": etag, "Cache-Control": f"public, max-age={max_age}"}
    if etag_matches(request.headers.get("if-none-match"), etag):
        return Response(status_code=304, headers=cache_headers)
    return Response(body, media_type="application/json", headers={**cache_headers, **(headers or {})})
