from datetime import date, datetime

from sqlalchemy import Date, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import clock
from .database import Base, UTCDateTime


class Developer(Base):
    """Someone who signed up in the portal to get API keys."""

    __tablename__ = "developers"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(254), unique=True)
    password_hash: Mapped[str] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, default=clock.now)

    keys: Mapped[list["ApiKey"]] = relationship(back_populates="developer", order_by="ApiKey.id")


class ApiKey(Base):
    """An API key. Only a SHA-256 hash of the secret is stored; the full key is shown once, at creation.

    `prefix` (the start of the key) is kept in plain text so people can tell their keys apart.
    """

    __tablename__ = "api_keys"

    id: Mapped[int] = mapped_column(primary_key=True)
    developer_id: Mapped[int] = mapped_column(ForeignKey("developers.id"), index=True)
    name: Mapped[str] = mapped_column(String(60))
    prefix: Mapped[str] = mapped_column(String(16))
    key_hash: Mapped[str] = mapped_column(String(64), unique=True)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, default=clock.now)
    last_used_at: Mapped[datetime | None] = mapped_column(UTCDateTime)
    revoked_at: Mapped[datetime | None] = mapped_column(UTCDateTime)

    developer: Mapped[Developer] = relationship(back_populates="keys")


class UsageDay(Base):
    """Requests made with one key on one UTC day. One row per (key, day), incremented in place."""

    __tablename__ = "usage_days"
    __table_args__ = (UniqueConstraint("api_key_id", "day"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    api_key_id: Mapped[int] = mapped_column(ForeignKey("api_keys.id"), index=True)
    day: Mapped[date] = mapped_column(Date)
    count: Mapped[int] = mapped_column(Integer, default=0)
