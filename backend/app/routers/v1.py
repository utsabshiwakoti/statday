"""The public API, version 1. Breaking changes would go in /v2; v1 stays as it is."""

from datetime import date
from typing import Annotated
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, Query, Request

from .. import clock
from ..access import api_access
from ..caching import DAY, cached_json
from ..holidays import calendar
from ..holidays.data import BY_ID, REGION_TIMEZONES, REGIONS
from ..holidays.rules import WEEKDAYS
from ..problems import Problem
from ..schemas import (
    BusinessDayAdd,
    BusinessDayCount,
    DateInfo,
    Holiday,
    HolidayOccurrence,
    HolidayPage,
    HolidayType,
    NextHolidays,
    Observance,
    Pagination,
    ProblemDetail,
    Region,
    RegionCode,
    RegionHolidays,
    RegionList,
)

problem = {"model": ProblemDetail, "content": {"application/problem+json": {}}}
router = APIRouter(
    prefix="/v1",
    dependencies=[Depends(api_access)],
    responses={
        304: {"description": "Not modified: your `If-None-Match` ETag is still current."},
        401: {**problem, "description": "The API key is invalid or revoked."},
        422: {**problem, "description": "A parameter is invalid or out of range."},
        429: {**problem, "description": "Rate limit reached; see `Retry-After`."},
    },
)

MAX_RANGE_DAYS = 366 * 5  # keeps list and count requests cheap
Year = Annotated[int | None, Query(description="Defaults to the current year.", examples=[2026])]
IncludeOptional = Annotated[bool, Query(description="Include holidays that aren't statutory.")]


# ---------- converting to response shapes ----------


def region_out(code: str) -> Region:
    name_en, name_fr, kind = REGIONS[code]
    return Region(code=code, name_en=name_en, name_fr=name_fr, type=kind, timezone=REGION_TIMEZONES[code])


def occurrence_out(o: calendar.Occurrence) -> HolidayOccurrence:
    h = o.holiday
    return HolidayOccurrence(id=h.id, name=o.name, name_en=h.name_en, name_fr=h.name_fr, date=o.date,
                             observed_date=o.observed, weekday=WEEKDAYS[o.date.weekday()], type=o.kind, note=o.note)


def holiday_out(h, day: date, occurrences: list[calendar.Occurrence]) -> Holiday:
    return Holiday(
        id=h.id, name_en=h.name_en, name_fr=h.name_fr, date=day, weekday=WEEKDAYS[day.weekday()],
        rule=h.rule.describe(),
        regions=[Observance(region=o.region, type=o.kind, name=o.name, observed_date=o.observed, note=o.note)
                 for o in occurrences],
    )


def check_range(start: date, end: date) -> None:
    if end < start:
        raise Problem(422, "invalid-range", "Invalid range", "`end` must be on or after `start`.")
    if (end - start).days > MAX_RANGE_DAYS:
        raise Problem(422, "invalid-range", "Invalid range", "Ranges can be at most 5 years long.")
    calendar.check_year(start.year)
    calendar.check_year(end.year)


# ---------- endpoints ----------


@router.get("/regions", response_model=RegionList, tags=["regions"], summary="List regions")
def list_regions(request: Request):
    """The federal jurisdiction (`CA`, for federally regulated workplaces) plus every province and territory."""
    return cached_json(request, RegionList(data=[region_out(code) for code in REGIONS]), DAY)


@router.get("/regions/{region}/holidays", response_model=RegionHolidays, tags=["regions"],
            summary="Holidays in a region")
def region_holidays(request: Request, region: RegionCode, year: Year = None, include_optional: IncludeOptional = True):
    """Every holiday in one region for a year, in date order, with the observed day off for weekend dates."""
    year = year or clock.today_in(region).year
    occurrences = calendar.holidays_for(region, year, include_optional)
    payload = RegionHolidays(region=region_out(region), year=year, data=[occurrence_out(o) for o in occurrences])
    return cached_json(request, payload, DAY)


@router.get("/regions/{region}/holidays/next", response_model=NextHolidays, tags=["regions"],
            summary="Next holidays in a region")
def next_holidays(
    request: Request,
    region: RegionCode,
    after: Annotated[date | None, Query(description="Defaults to today in the region.")] = None,
    count: Annotated[int, Query(ge=1, le=10)] = 1,
    include_optional: IncludeOptional = False,
):
    """The next holidays strictly after a date. Statutory only unless `include_optional=true`."""
    after = after or clock.today_in(region)
    calendar.check_year(after.year)
    found = calendar.upcoming(region, after, count, include_optional)
    payload = NextHolidays(region=region, after=after, data=[occurrence_out(o) for o in found])
    # Without `after`, the answer changes at midnight, so cache it for less time.
    return cached_json(request, payload, DAY if "after" in request.query_params else 300)


@router.get("/regions/{region}/dates/{day}", response_model=DateInfo, tags=["business days"],
            summary="Check a date")
def check_date(request: Request, region: RegionCode, day: date):
    """Is this date a business day in the region, and is it (or is it observed as) a holiday?"""
    payload = DateInfo(
        region=region, date=day, weekday=WEEKDAYS[day.weekday()], is_weekend=day.weekday() >= 5,
        is_business_day=calendar.is_business_day(region, day),
        holidays=[occurrence_out(o) for o in calendar.holidays_on(region, day)],
    )
    return cached_json(request, payload, DAY)


@router.get("/regions/{region}/business-days", response_model=BusinessDayCount, tags=["business days"],
            summary="Count business days")
def count_business_days(request: Request, region: RegionCode, start: date, end: date):
    """Business days from `start` to `end`, both inclusive. Weekends and statutory days off don't count."""
    check_range(start, end)
    days_off = [
        o for year in range(start.year, end.year + 1) for o in calendar.holidays_for(region, year, False)
        if start <= o.observed <= end and o.observed.weekday() < 5
    ]
    payload = BusinessDayCount(
        region=region, start=start, end=end, calendar_days=(end - start).days + 1,
        business_days=calendar.count_business_days(region, start, end),
        days_off=[occurrence_out(o) for o in days_off],
    )
    return cached_json(request, payload, DAY)


@router.get("/regions/{region}/business-days/add", response_model=BusinessDayAdd, tags=["business days"],
            summary="Add business days")
def add_business_days(
    request: Request,
    region: RegionCode,
    start: date,
    days: Annotated[int, Query(ge=-1000, le=1000, description="Negative to count backwards.")],
):
    """The date `days` business days after `start`, e.g. a deadline of "10 business days from today"."""
    calendar.check_year(start.year)
    result = calendar.add_business_days(region, start, days)
    low, high = sorted((start, result))
    skipped = [
        o for year in range(low.year, high.year + 1) for o in calendar.holidays_for(region, year, False)
        if low < o.observed <= high and o.observed.weekday() < 5
    ]
    payload = BusinessDayAdd(region=region, start=start, days=days, result=result,
                             days_off=[occurrence_out(o) for o in skipped])
    return cached_json(request, payload, DAY)


@router.get("/holidays", response_model=HolidayPage, tags=["holidays"], summary="Search holidays")
def list_holidays(
    request: Request,
    year: Annotated[int | None, Query(description="Shorthand for `start` and `end` covering one year.")] = None,
    start: Annotated[date | None, Query(description="Defaults to January 1 of the current year.")] = None,
    end: Annotated[date | None, Query(description="Defaults to December 31 of `start`'s year.")] = None,
    region: RegionCode | None = None,
    type: HolidayType | None = None,
    q: Annotated[str | None, Query(max_length=60, description="Search English and French names.")] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    per_page: Annotated[int, Query(ge=1, le=100)] = 20,
):
    """Holidays across Canada between two dates, with the regions observing each one.

    Filters narrow both the holidays and their `regions` list (e.g. `region=ON&type=statutory`).
    Results are paginated: see `pagination` in the body, or the `Link` and `X-Total-Count` headers.
    """
    if year is not None:
        calendar.check_year(year)
    start = start or date(year or clock.today_in("CA").year, 1, 1)
    end = end or date(start.year, 12, 31)
    check_range(start, end)

    rows: list[Holiday] = []
    for year in range(start.year, end.year + 1):
        for h, day, occurrences in calendar.national(year):
            if not start <= day <= end:
                continue
            if q and q.casefold() not in f"{h.name_en} {h.name_fr} {h.id}".casefold():
                continue
            matching = [o for o in occurrences if (not region or o.region == region) and (not type or o.kind == type)]
            if matching:
                rows.append(holiday_out(h, day, matching))

    total = len(rows)
    pages = max(1, -(-total // per_page))  # ceiling division
    data = rows[(page - 1) * per_page: page * per_page]
    payload = HolidayPage(data=data, pagination=Pagination(page=page, per_page=per_page, total=total, pages=pages))
    return cached_json(request, payload, DAY, headers={"X-Total-Count": str(total),
                                                        "Link": link_header(request, page, pages)})


@router.get("/holidays/{holiday_id}", response_model=Holiday, tags=["holidays"], summary="Get a holiday",
            responses={404: {**problem, "description": "No holiday with this id."}})
def get_holiday(request: Request, holiday_id: str, year: Year = None):
    """One holiday in a given year: its date, the rule behind it, and how each region observes it."""
    holiday = BY_ID.get(holiday_id)
    if holiday is None:
        raise Problem(404, "unknown-holiday", "Unknown holiday",
                      f"No holiday with id '{holiday_id}'. GET /v1/holidays lists the ids.")
    year = year or clock.today_in("CA").year
    calendar.check_year(year)
    for h, day, occurrences in calendar.national(year):
        if h.id == holiday_id:
            return cached_json(request, holiday_out(h, day, occurrences), DAY)
    raise AssertionError("every holiday occurs every year")  # pragma: no cover


def link_header(request: Request, page: int, pages: int) -> str:
    """RFC 8288 links to the first, previous, next and last pages, keeping the other parameters."""

    def url(n: int) -> str:
        params = {**request.query_params, "page": str(n)}
        return f"<{request.url.path}?{urlencode(params)}>"

    links = [f'{url(1)}; rel="first"']
    if page > 1:
        links.append(f'{url(min(page - 1, pages))}; rel="prev"')
    if page < pages:
        links.append(f'{url(page + 1)}; rel="next"')
    links.append(f'{url(pages)}; rel="last"')
    return ", ".join(links)
