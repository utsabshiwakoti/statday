from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from . import problems
from .config import settings
from .database import engine, ensure_schema
from .holidays.data import FIRST_YEAR, LAST_YEAR
from .routers import portal, v1

DESCRIPTION = f"""
Statutory and public holidays for every Canadian province and territory, plus federally regulated
workplaces, from {FIRST_YEAR} to {LAST_YEAR}. Also: observed days off when a holiday lands on a weekend,
and business-day maths (count them, or add them to a date).

**Authentication.** Optional. Send an API key in the `X-API-Key` header for a higher rate limit.
Get one free in the [developer portal](/portal).

**Rate limits.** Every response has `RateLimit-Limit`, `RateLimit-Remaining` and `RateLimit-Reset`
headers. Going over returns `429` with `Retry-After`.

**Caching.** Responses carry an `ETag`. Send it back in `If-None-Match` to get `304 Not Modified`
when nothing changed.

**Errors.** Always `application/problem+json` ([RFC 9457](https://www.rfc-editor.org/rfc/rfc9457)).
The `type` field links to an explanation in the [guide](/guide).
"""

TAGS = [
    {"name": "regions", "description": "Holidays for one province, territory or the federal jurisdiction."},
    {"name": "holidays", "description": "Holidays across the country, with how each region observes them."},
    {"name": "business days", "description": "Working-day checks and date maths that skip weekends and holidays."},
]


@asynccontextmanager
async def lifespan(_: FastAPI):
    ensure_schema(engine)
    yield


app = FastAPI(
    title="StatDay API",
    version="1.0.0",
    summary="Canadian statutory holidays and business days.",
    description=DESCRIPTION,
    openapi_tags=TAGS,
    # Operation ids become SDK function names: "list_regions" rather than "list_regions_v1_regions_get".
    generate_unique_id_function=lambda route: route.name,
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
    # Browsers hide response headers from scripts unless they're listed here.
    expose_headers=["ETag", "Link", "X-Total-Count", "RateLimit-Limit", "RateLimit-Remaining",
                    "RateLimit-Reset", "RateLimit-Policy", "Retry-After"],
)
problems.install(app)


@app.middleware("http")
async def add_rate_limit_headers(request: Request, call_next):
    """api_access stores the limiter's decision on the request; put it on the response, errors included."""
    response = await call_next(request)
    for name, value in getattr(request.state, "rate_headers", {}).items():
        response.headers.setdefault(name, value)
    return response


app.include_router(v1.router)
app.include_router(portal.router)


def openapi_with_problem_json() -> dict:
    """FastAPI documents a response model under application/json. Errors are really sent as
    application/problem+json, so move the schema there; docs and the generated SDK then match the wire."""
    if app.openapi_schema:
        return app.openapi_schema
    schema = FastAPI.openapi(app)  # builds and caches app.openapi_schema
    for operations in schema["paths"].values():
        for operation in operations.values():
            for response in operation.get("responses", {}).values():
                content = response.get("content", {})
                if "application/problem+json" in content and "application/json" in content:
                    content["application/problem+json"] = content.pop("application/json")
    return schema


app.openapi = openapi_with_problem_json


@app.get("/api/health", include_in_schema=False)
def health():
    return {"status": "ok"}


def mount_frontend(application: FastAPI, directory: str | Path) -> None:
    """Serve the built React app from the same origin as the API, falling back to index.html so
    client-side routes like /portal survive a refresh. Registered last so it can't shadow the API."""
    root = Path(directory).resolve()
    index = root / "index.html"

    @application.get("/{path:path}", include_in_schema=False)
    def frontend(path: str):
        if path.startswith(("api/", "v1/")):
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Not found")
        candidate = (root / path).resolve()
        if path and candidate.is_file() and candidate.is_relative_to(root):  # no ../ escapes
            # Vite fingerprints everything under assets/, so those files can be cached forever.
            cache = "public, max-age=31536000, immutable" if path.startswith("assets/") else "no-cache"
            return FileResponse(candidate, headers={"Cache-Control": cache})
        return FileResponse(index, headers={"Cache-Control": "no-cache"})


_dist = Path(settings.static_dir) if settings.static_dir else Path(__file__).resolve().parents[2] / "frontend" / "dist"
if (_dist / "index.html").is_file():
    mount_frontend(app, _dist)
