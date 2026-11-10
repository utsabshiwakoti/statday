from datetime import UTC, date, datetime
from zoneinfo import ZoneInfo

from .holidays.data import REGION_TIMEZONES


def now() -> datetime:
    """The current time in UTC. Kept in one place so tests can freeze it."""
    return datetime.now(UTC)


def today_in(region: str) -> date:
    """Today's date where the region is. At 11 p.m. in Vancouver it's already tomorrow in Halifax."""
    return now().astimezone(ZoneInfo(REGION_TIMEZONES[region])).date()
