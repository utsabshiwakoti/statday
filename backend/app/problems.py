"""Errors as RFC 9457 "problem details": every error has the same JSON shape and media type.

    {"type": "/guide#unknown-holiday", "title": "Unknown holiday", "status": 404,
     "detail": "No holiday with id 'xmas'. ...", "instance": "/v1/holidays/xmas"}

`type` links to the section of the API guide that explains the error, so clients can switch on it.
"""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

from .holidays.calendar import OutOfRange

MEDIA_TYPE = "application/problem+json"


class Problem(Exception):
    """Raise anywhere in a request to send a problem+json response."""

    def __init__(self, status: int, slug: str, title: str, detail: str, headers: dict | None = None, **extra):
        self.status, self.slug, self.title, self.detail = status, slug, title, detail
        self.headers = headers or {}
        self.extra = extra


def problem_response(request: Request, status: int, slug: str | None, title: str, detail: str,
                     headers: dict | None = None, **extra) -> JSONResponse:
    body = {
        # "about:blank" is the RFC's value for "nothing more to say beyond the HTTP status".
        "type": f"/guide#{slug}" if slug else "about:blank",
        "title": title,
        "status": status,
        "detail": detail,
        "instance": request.url.path,
        **extra,
    }
    return JSONResponse(body, status_code=status, media_type=MEDIA_TYPE, headers=headers)


# Titles for HTTP errors raised by FastAPI itself (wrong method, unknown path, portal auth...).
_TITLES = {400: "Bad request", 401: "Unauthorized", 403: "Forbidden", 404: "Not found",
           405: "Method not allowed", 409: "Conflict"}


def install(app: FastAPI) -> None:
    @app.exception_handler(Problem)
    def _problem(request: Request, exc: Problem):
        return problem_response(request, exc.status, exc.slug, exc.title, exc.detail, exc.headers, **exc.extra)

    @app.exception_handler(OutOfRange)
    def _out_of_range(request: Request, exc: OutOfRange):
        return problem_response(request, 422, "out-of-range", "Out of range", str(exc))

    @app.exception_handler(RequestValidationError)
    def _validation(request: Request, exc: RequestValidationError):
        errors = [
            # loc looks like ("query", "year"); report it as "query.year".
            {"location": ".".join(str(part) for part in err["loc"]), "message": err["msg"]}
            for err in exc.errors()
        ]
        return problem_response(request, 422, "invalid-parameters", "Invalid parameters",
                                "One or more parameters are invalid; see `errors`.", errors=errors)

    # Starlette's class, so unknown paths and wrong methods (raised by the router) are covered too.
    @app.exception_handler(HTTPException)
    def _http(request: Request, exc: HTTPException):
        title = _TITLES.get(exc.status_code, "Error")
        detail = exc.detail if isinstance(exc.detail, str) else title
        return problem_response(request, exc.status_code, None, title, detail, exc.headers)
