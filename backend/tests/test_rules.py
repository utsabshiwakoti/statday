from datetime import date

import pytest

from app.holidays.rules import (
    MONDAY,
    EasterOffset,
    Fixed,
    FridayBeforeLastSunday,
    NearestWeekday,
    NthWeekday,
    WeekdayBefore,
    easter_sunday,
)


@pytest.mark.parametrize("year, expected", [
    (2024, date(2024, 3, 31)),
    (2025, date(2025, 4, 20)),
    (2026, date(2026, 4, 5)),
    (2027, date(2027, 3, 28)),
    (2038, date(2038, 4, 25)),  # the latest possible date
    (2285, date(2285, 3, 22)),  # the earliest possible date
])
def test_easter(year, expected):
    assert easter_sunday(year) == expected


def test_good_friday_and_easter_monday():
    assert EasterOffset(-2).on(2026) == date(2026, 4, 3)
    assert EasterOffset(1).on(2026) == date(2026, 4, 6)


def test_nth_weekday():
    assert NthWeekday(3, MONDAY, 2).on(2026) == date(2026, 2, 16)  # Family Day
    assert NthWeekday(1, MONDAY, 9).on(2026) == date(2026, 9, 7)  # Labour Day
    assert NthWeekday(2, MONDAY, 10).on(2026) == date(2026, 10, 12)  # Thanksgiving
    assert NthWeekday(1, MONDAY, 6).on(2026) == date(2026, 6, 1)  # month starting on the weekday itself


def test_victoria_day_is_strictly_before_may_25():
    rule = WeekdayBefore(MONDAY, 5, 25)
    assert rule.on(2026) == date(2026, 5, 18)
    assert rule.on(2027) == date(2027, 5, 24)
    assert rule.on(2025) == date(2025, 5, 19)  # May 25, 2025 was a Sunday
    assert rule.on(2015) == date(2015, 5, 18)  # May 25, 2015 was itself a Monday: go back a week


def test_nearest_monday_newfoundland_2026():
    assert NearestWeekday(MONDAY, 3, 17).on(2026) == date(2026, 3, 16)  # St. Patrick's Day
    assert NearestWeekday(MONDAY, 4, 23).on(2026) == date(2026, 4, 20)  # St. George's Day
    assert NearestWeekday(MONDAY, 6, 24).on(2026) == date(2026, 6, 22)  # Discovery Day
    assert NearestWeekday(MONDAY, 7, 12).on(2026) == date(2026, 7, 13)  # Orangemen's Day


def test_yukon_heritage_day():
    assert FridayBeforeLastSunday(2).on(2026) == date(2026, 2, 20)
    assert FridayBeforeLastSunday(2).on(2027) == date(2027, 2, 26)


def test_descriptions_read_like_the_law():
    assert NthWeekday(3, MONDAY, 2).describe() == "Third Monday in February"
    assert WeekdayBefore(MONDAY, 5, 25).describe() == "Monday before May 25"
    assert Fixed(7, 1).describe() == "July 1"
    assert EasterOffset(-2).describe() == "2 days before Easter Sunday"
