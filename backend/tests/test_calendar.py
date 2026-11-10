from datetime import date

import pytest

from app.holidays import calendar
from app.holidays.data import FIRST_YEAR, HOLIDAYS, LAST_YEAR, REGIONS

COMMON = {"new-years-day", "good-friday", "canada-day", "labour-day", "christmas-day"}

# Statutory holidays per region, from each jurisdiction's employment standards law (see README sources).
STATUTORY = {
    "CA": COMMON | {"victoria-day", "truth-and-reconciliation", "thanksgiving", "remembrance-day", "boxing-day"},
    "AB": COMMON | {"family-day", "victoria-day", "thanksgiving", "remembrance-day"},
    "BC": COMMON | {"family-day", "victoria-day", "bc-day", "truth-and-reconciliation", "thanksgiving",
                    "remembrance-day"},
    "MB": COMMON | {"louis-riel-day", "victoria-day", "truth-and-reconciliation", "thanksgiving"},
    "NB": COMMON | {"family-day", "new-brunswick-day", "remembrance-day"},
    "NL": COMMON | {"remembrance-day"},
    "NS": COMMON | {"nova-scotia-heritage-day", "remembrance-day"},
    "ON": COMMON | {"family-day", "victoria-day", "thanksgiving", "boxing-day"},
    "PE": COMMON | {"islander-day", "truth-and-reconciliation", "remembrance-day"},
    "QC": COMMON | {"national-patriots-day", "fete-nationale", "thanksgiving"},
    "SK": COMMON | {"family-day", "victoria-day", "saskatchewan-day", "thanksgiving", "remembrance-day"},
    "NT": COMMON | {"victoria-day", "national-indigenous-peoples-day", "civic-holiday", "truth-and-reconciliation",
                    "thanksgiving", "remembrance-day"},
    "NU": COMMON | {"victoria-day", "nunavut-day", "civic-holiday", "truth-and-reconciliation", "thanksgiving",
                    "remembrance-day"},
    "YT": COMMON | {"victoria-day", "national-indigenous-peoples-day", "discovery-day-yukon",
                    "truth-and-reconciliation", "thanksgiving", "remembrance-day"},
}


@pytest.mark.parametrize("region", sorted(REGIONS))
def test_statutory_holidays_per_region(region):
    found = {o.holiday.id for o in calendar.holidays_for(region, 2026, include_optional=False)}
    assert found == STATUTORY[region]


def test_ids_are_unique_and_names_present():
    ids = [h.id for h in HOLIDAYS]
    assert len(ids) == len(set(ids))
    assert all(h.name_en and h.name_fr for h in HOLIDAYS)
    assert all(not (h.statutory & h.optional) for h in HOLIDAYS)  # a region is one or the other


def observed(region, year, holiday_id):
    return next(o.observed for o in calendar.holidays_for(region, year) if o.holiday.id == holiday_id)


def test_weekend_holidays_move_to_the_next_free_weekday():
    # 2026: Boxing Day is a Saturday -> Monday the 28th.
    assert observed("ON", 2026, "boxing-day") == date(2026, 12, 28)
    # 2027: Christmas is Saturday, Boxing Day Sunday -> Monday 27th and Tuesday 28th.
    assert observed("ON", 2027, "christmas-day") == date(2027, 12, 27)
    assert observed("ON", 2027, "boxing-day") == date(2027, 12, 28)
    # 2022-style year (Christmas on Sunday): 2033. Boxing Day keeps Monday, Christmas moves to Tuesday.
    assert observed("ON", 2033, "boxing-day") == date(2033, 12, 26)
    assert observed("ON", 2033, "christmas-day") == date(2033, 12, 27)


def test_shift_rules():
    # Remembrance Day is never moved: 2029-11-11 is a Sunday.
    assert observed("NS", 2029, "remembrance-day") == date(2029, 11, 11)
    # In Quebec only Sunday moves: Canada Day 2028 is a Saturday and stays put...
    assert observed("QC", 2028, "canada-day") == date(2028, 7, 1)
    assert observed("ON", 2028, "canada-day") == date(2028, 7, 3)
    # ...and Fête nationale 2029 is a Sunday, so it moves to Monday.
    assert observed("QC", 2029, "fete-nationale") == date(2029, 6, 25)


def test_local_names():
    by_id = {o.holiday.id: o for o in calendar.holidays_for("NS", 2026)}
    assert by_id["civic-holiday"].name == "Natal Day"
    assert by_id["civic-holiday"].kind == "optional"


def test_year_range_is_enforced():
    calendar.holidays_for("ON", FIRST_YEAR)
    calendar.holidays_for("ON", LAST_YEAR)
    with pytest.raises(calendar.OutOfRange):
        calendar.holidays_for("ON", LAST_YEAR + 1)


def test_upcoming_crosses_into_next_year():
    found = calendar.upcoming("NS", date(2026, 12, 20), 2, include_optional=False)
    assert [o.holiday.id for o in found] == ["christmas-day", "new-years-day"]
    assert found[1].date == date(2027, 1, 1)


def test_business_days():
    # Boxing Day is only a business-day holiday where it's statutory.
    assert not calendar.is_business_day("ON", date(2026, 12, 28))
    assert calendar.is_business_day("NS", date(2026, 12, 28))
    # December 2026 in Nova Scotia: 23 weekdays minus Christmas.
    assert calendar.count_business_days("NS", date(2026, 12, 1), date(2026, 12, 31)) == 22
    # Every weekday that isn't a statutory day off, across a whole year.
    assert calendar.count_business_days("ON", date(2026, 1, 1), date(2026, 12, 31)) == 261 - 9


def test_add_business_days():
    # Wed Dec 23 + 3 in NS: Thu 24, (Fri 25 Christmas), Mon 28, Tue 29.
    assert calendar.add_business_days("NS", date(2026, 12, 23), 3) == date(2026, 12, 29)
    # Ontario also skips Boxing Day observed on the 28th.
    assert calendar.add_business_days("ON", date(2026, 12, 23), 3) == date(2026, 12, 30)
    assert calendar.add_business_days("ON", date(2026, 12, 30), -3) == date(2026, 12, 23)
    assert calendar.add_business_days("ON", date(2026, 12, 26), 0) == date(2026, 12, 26)
