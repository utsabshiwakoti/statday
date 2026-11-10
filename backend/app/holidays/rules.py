"""How each holiday's date is worked out for a given year.

Every rule is a small frozen dataclass with `on(year) -> date` and a human-readable `describe()`,
so the holiday table in data.py reads like the law ("third Monday in February").
"""

from dataclasses import dataclass
from datetime import date, timedelta

WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
MONTHS = ["", "January", "February", "March", "April", "May", "June", "July", "August",
          "September", "October", "November", "December"]
ORDINALS = {1: "First", 2: "Second", 3: "Third", 4: "Fourth"}
MONDAY, FRIDAY, SATURDAY, SUNDAY = 0, 4, 5, 6


def easter_sunday(year: int) -> date:
    """Western (Gregorian) Easter, using the 'anonymous Gregorian algorithm' (Meeus/Jones/Butcher).

    Easter is the first Sunday after the ecclesiastical full moon on or after March 21. The
    arithmetic below computes that without astronomy; it's exact for every Gregorian year.
    """
    a = year % 19  # position in the 19-year lunar cycle
    b, c = divmod(year, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30  # days from March 21 to the full moon (roughly)
    i, k = divmod(c, 4)
    weekday_fix = (32 + 2 * e + 2 * i - h - k) % 7  # days from the full moon to the next Sunday
    m = (a + 11 * h + 22 * weekday_fix) // 451
    month, day = divmod(h + weekday_fix - 7 * m + 114, 31)
    return date(year, month, day + 1)


@dataclass(frozen=True)
class Fixed:
    """The same calendar date every year, e.g. Canada Day on July 1."""

    month: int
    day: int

    def on(self, year: int) -> date:
        return date(year, self.month, self.day)

    def describe(self) -> str:
        return f"{MONTHS[self.month]} {self.day}"


@dataclass(frozen=True)
class NthWeekday:
    """E.g. the third Monday in February (Family Day)."""

    n: int
    weekday: int
    month: int

    def on(self, year: int) -> date:
        first = date(year, self.month, 1)
        offset = (self.weekday - first.weekday()) % 7
        return first + timedelta(days=offset + 7 * (self.n - 1))

    def describe(self) -> str:
        return f"{ORDINALS[self.n]} {WEEKDAYS[self.weekday]} in {MONTHS[self.month]}"


@dataclass(frozen=True)
class WeekdayBefore:
    """The last given weekday strictly before a date, e.g. the Monday before May 25 (Victoria Day)."""

    weekday: int
    month: int
    day: int

    def on(self, year: int) -> date:
        anchor = date(year, self.month, self.day)
        back = (anchor.weekday() - self.weekday) % 7 or 7  # "before", so never the anchor itself
        return anchor - timedelta(days=back)

    def describe(self) -> str:
        return f"{WEEKDAYS[self.weekday]} before {MONTHS[self.month]} {self.day}"


@dataclass(frozen=True)
class NearestWeekday:
    """The given weekday closest to a date, e.g. the Monday nearest March 17 in Newfoundland."""

    weekday: int
    month: int
    day: int

    def on(self, year: int) -> date:
        anchor = date(year, self.month, self.day)
        forward = (self.weekday - anchor.weekday()) % 7
        # Ties can't happen for one weekday: forward and backward distances add up to 7.
        return anchor + timedelta(days=forward if forward <= 3 else forward - 7)

    def describe(self) -> str:
        return f"{WEEKDAYS[self.weekday]} nearest {MONTHS[self.month]} {self.day}"


@dataclass(frozen=True)
class EasterOffset:
    """Days relative to Easter Sunday: -2 is Good Friday, +1 is Easter Monday."""

    days: int

    def on(self, year: int) -> date:
        return easter_sunday(year) + timedelta(days=self.days)

    def describe(self) -> str:
        if self.days < 0:
            return f"{-self.days} days before Easter Sunday"
        return f"{self.days} day{'s' if self.days > 1 else ''} after Easter Sunday"


@dataclass(frozen=True)
class FridayBeforeLastSunday:
    """Yukon's Heritage Day: the Friday before the last Sunday in February."""

    month: int

    def on(self, year: int) -> date:
        next_month = date(year + self.month // 12, self.month % 12 + 1, 1)
        last_day = next_month - timedelta(days=1)
        last_sunday = last_day - timedelta(days=(last_day.weekday() - SUNDAY) % 7)
        return last_sunday - timedelta(days=2)

    def describe(self) -> str:
        return f"Friday before the last Sunday in {MONTHS[self.month]}"


Rule = Fixed | NthWeekday | WeekdayBefore | NearestWeekday | EasterOffset | FridayBeforeLastSunday
