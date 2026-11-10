"""Turn the holiday table into dates: per region and year, observed days off, business-day maths.

Everything here is pure and cached per (region, year); there is no database involved.
"""

from dataclasses import dataclass
from datetime import date, timedelta
from functools import lru_cache

from .data import FIRST_YEAR, HOLIDAYS, LAST_YEAR, REGIONS, Holiday
from .rules import SATURDAY, SUNDAY

STATUTORY, OPTIONAL = "statutory", "optional"


class OutOfRange(ValueError):
    """A year or date outside the supported range. The message is shown to API users."""


@dataclass(frozen=True)
class Occurrence:
    holiday: Holiday
    region: str
    kind: str  # "statutory" or "optional"
    date: date  # the holiday itself
    observed: date  # the weekday people usually get off when it falls on a weekend

    @property
    def name(self) -> str:
        return self.holiday.name_in(self.region)

    @property
    def note(self) -> str | None:
        return self.holiday.notes.get(self.region)


def check_year(year: int) -> None:
    if not FIRST_YEAR <= year <= LAST_YEAR:
        raise OutOfRange(f"Years {FIRST_YEAR} to {LAST_YEAR} are supported; got {year}.")


def check_region(region: str) -> str:
    code = region.upper()
    if code not in REGIONS:
        raise KeyError(code)
    return code


def _is_weekend(d: date) -> bool:
    return d.weekday() >= SATURDAY


@lru_cache(maxsize=1024)
def region_holidays(region: str, year: int) -> tuple[Occurrence, ...]:
    """Every statutory and optional holiday in a region for one year, in date order.

    Observed dates are worked out in two passes so moved holidays never collide:
    1. Holidays that stay on their own date claim it first.
    2. Weekend holidays then move to the next weekday nobody has claimed. So when Christmas is on
       Saturday and Boxing Day on Sunday, they're observed Monday the 27th and Tuesday the 28th;
       when Christmas is on Sunday, Boxing Day keeps Monday and Christmas moves to Tuesday.
    """
    check_year(year)
    applicable = [
        (h, STATUTORY if region in h.statutory else OPTIONAL, h.rule.on(year))
        for h in HOLIDAYS
        if region in h.statutory or region in h.optional
    ]

    def moves(h: Holiday, d: date) -> bool:
        rule = h.shift_for(region)
        return (rule == "weekend" and _is_weekend(d)) or (rule == "sunday" and d.weekday() == SUNDAY)

    claimed = {d for h, _, d in applicable if not moves(h, d)}
    observed: dict[str, date] = {}
    for h, _, d in sorted(applicable, key=lambda item: item[2]):
        if not moves(h, d):
            observed[h.id] = d
            continue
        day = d + timedelta(days=1)
        while _is_weekend(day) or day in claimed:
            day += timedelta(days=1)
        claimed.add(day)
        observed[h.id] = day

    occurrences = [Occurrence(h, region, kind, d, observed[h.id]) for h, kind, d in applicable]
    return tuple(sorted(occurrences, key=lambda o: (o.date, o.holiday.id)))


def holidays_for(region: str, year: int, include_optional: bool = True) -> list[Occurrence]:
    return [o for o in region_holidays(region, year) if include_optional or o.kind == STATUTORY]


def national(year: int) -> list[tuple[Holiday, date, list[Occurrence]]]:
    """Each holiday once, with where (and how) it's observed across the country."""
    check_year(year)
    by_holiday: dict[str, list[Occurrence]] = {}
    for region in REGIONS:
        for o in region_holidays(region, year):
            by_holiday.setdefault(o.holiday.id, []).append(o)
    rows = [(occs[0].holiday, occs[0].date, occs) for occs in by_holiday.values()]
    return sorted(rows, key=lambda row: (row[1], row[0].id))


def upcoming(region: str, after: date, count: int, include_optional: bool) -> list[Occurrence]:
    """The next `count` holidays strictly after a date (by the holiday's own date)."""
    found: list[Occurrence] = []
    year = max(after.year, FIRST_YEAR)
    while len(found) < count and year <= LAST_YEAR:
        found += [o for o in holidays_for(region, year, include_optional) if o.date > after]
        year += 1
    return found[:count]


# ---------- business days ----------


@lru_cache(maxsize=1024)
def _days_off(region: str, year: int) -> frozenset[date]:
    return frozenset(o.observed for o in region_holidays(region, year) if o.kind == STATUTORY)


def holidays_on(region: str, day: date) -> list[Occurrence]:
    """Holidays whose date or observed day off is `day`."""
    check_year(day.year)
    return [o for o in region_holidays(region, day.year) if day in (o.date, o.observed)]


def is_business_day(region: str, day: date) -> bool:
    """Not a weekend and not a statutory day off (the observed one, for moved holidays)."""
    check_year(day.year)
    return not _is_weekend(day) and day not in _days_off(region, day.year)


def count_business_days(region: str, start: date, end: date) -> int:
    """Business days from start to end, both inclusive."""
    if end < start:
        raise OutOfRange("end must be on or after start.")
    return sum(is_business_day(region, start + timedelta(days=i)) for i in range((end - start).days + 1))


def add_business_days(region: str, start: date, days: int) -> date:
    """Move `days` business days forward (or back, if negative). Zero returns start unchanged."""
    step = timedelta(days=1 if days >= 0 else -1)
    current, remaining = start, abs(days)
    while remaining:
        current += step
        if is_business_day(region, current):
            remaining -= 1
    return current
