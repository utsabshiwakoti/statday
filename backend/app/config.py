import os
import secrets


class Settings:
    """Everything configurable comes from environment variables, read once at startup."""

    def __init__(self) -> None:
        self.database_url = os.getenv("DATABASE_URL", "sqlite:///./statday.db")
        # The random fallback means portal logins stop working on restart: the safe failure for a dev default.
        self.secret_key = os.getenv("SECRET_KEY") or secrets.token_urlsafe(32)
        self.static_dir = os.getenv("STATIC_DIR", "")
        self.cors_origins = [o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")]

        # Rate limits: requests per window, per API key or (without a key) per IP address.
        self.rate_window_seconds = int(os.getenv("RATE_WINDOW_SECONDS", "3600"))
        self.anonymous_limit = int(os.getenv("ANONYMOUS_LIMIT", "100"))
        self.key_limit = int(os.getenv("KEY_LIMIT", "1000"))
        self.max_keys_per_developer = int(os.getenv("MAX_KEYS_PER_DEVELOPER", "5"))


settings = Settings()
