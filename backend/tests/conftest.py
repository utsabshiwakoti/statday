from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import access, clock
from app.database import Base, get_db
from app.main import app

# Tuesday 10 November 2026, 12:00 UTC (07:00 in Toronto). The next holiday is Remembrance Day.
NOW = datetime(2026, 11, 10, 12, 0, tzinfo=UTC)


@pytest.fixture(autouse=True)
def frozen_clock(monkeypatch):
    monkeypatch.setattr(clock, "now", lambda: NOW)
    return NOW


class FakeTime:
    """Stands in for time.time() in the rate limiter so tests can jump to the next window."""

    def __init__(self):
        self.value = 1_800_001_800.0  # 30 minutes into an hour-aligned window

    def __call__(self):
        return self.value


@pytest.fixture(autouse=True)
def fake_time(monkeypatch):
    fake = FakeTime()
    monkeypatch.setattr(access.limiter, "clock", fake)
    access.limiter.reset()
    return fake


@pytest.fixture()
def session_factory():
    # In-memory SQLite shared across threads; a fresh database for every test.
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


@pytest.fixture()
def client(session_factory):
    def override_get_db():
        db = session_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    # Not `with TestClient(app)`: that would run the lifespan against the real database.
    yield TestClient(app)
    app.dependency_overrides.clear()


def signup(client, email="dev@example.com", password="correct-horse") -> dict:
    res = client.post("/api/auth/signup", json={"email": email, "password": password})
    assert res.status_code == 201, res.text
    return {"Authorization": f"Bearer {res.json()['access_token']}"}


def create_key(client, auth, name="My app") -> dict:
    res = client.post("/api/keys", json={"name": name}, headers=auth)
    assert res.status_code == 201, res.text
    return res.json()
