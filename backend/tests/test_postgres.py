"""Usage counting under concurrency, on a real Postgres server.

Run with:  TEST_DATABASE_URL=postgresql://user:pass@localhost:5432/statday_test pytest tests/test_postgres.py
(CI starts a Postgres service and sets this.) The database is wiped.
"""

import os
import threading

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.access import record_usage
from app.database import Base, _normalise_url
from app.models import ApiKey, Developer, UsageDay

URL = os.getenv("TEST_DATABASE_URL")
pytestmark = pytest.mark.skipif(not URL, reason="set TEST_DATABASE_URL to run Postgres tests")


def test_simultaneous_requests_are_all_counted():
    """A read-then-write counter would lose updates here; the upsert can't."""
    engine = create_engine(_normalise_url(URL), pool_size=10)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, expire_on_commit=False)
    with Session() as db:
        key = ApiKey(developer=Developer(email="pg@example.com", password_hash="x"),
                     name="pg", prefix="sd_pg", key_hash="0" * 64)
        db.add(key)
        db.commit()
        key_id = key.id

    threads_n, per_thread = 8, 25
    start = threading.Barrier(threads_n)

    def worker():
        with Session() as db:
            key = db.get(ApiKey, key_id)
            start.wait()  # release every thread at the same instant
            for _ in range(per_thread):
                record_usage(db, key)

    threads = [threading.Thread(target=worker) for _ in range(threads_n)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    with Session() as db:
        rows = db.scalars(select(UsageDay).where(UsageDay.api_key_id == key_id)).all()
    assert len(rows) == 1
    assert rows[0].count == threads_n * per_thread
    engine.dispose()
