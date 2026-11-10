"""Response and request shapes. These also drive the OpenAPI docs and the generated SDK."""

from datetime import date, datetime
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, EmailStr, Field

from .holidays.data import REGIONS

# An enum gives the docs a dropdown and the SDK a typed parameter instead of a bare string.
RegionCode = StrEnum("RegionCode", {code: code for code in REGIONS})


class HolidayType(StrEnum):
    statutory = "statutory"
    optional = "optional"


class Region(BaseModel):
    code: str = Field(examples=["NS"])
    name_en: str = Field(examples=["Nova Scotia"])
    name_fr: str = Field(examples=["Nouvelle-Écosse"])
    type: Literal["federal", "province", "territory"]
    timezone: str = Field(examples=["America/Halifax"], description="Used to work out 'today' in the region.")


class RegionList(BaseModel):
    data: list[Region]


class HolidayOccurrence(BaseModel):
    """A holiday in one region."""

    id: str = Field(examples=["nova-scotia-heritage-day"])
    name: str = Field(description="The name used in this region.", examples=["Nova Scotia Heritage Day"])
    name_en: str
    name_fr: str
    date: date
    observed_date: date = Field(description="The day off when the holiday falls on a weekend (otherwise `date`).")
    weekday: str = Field(examples=["Monday"])
    type: HolidayType = Field(description="`statutory`: paid holiday under the region's employment law. "
                                          "`optional`: widely observed but not guaranteed.")
    note: str | None = None


class RegionHolidays(BaseModel):
    region: Region
    year: int
    data: list[HolidayOccurrence]


class Observance(BaseModel):
    """How one region observes a holiday."""

    region: str = Field(examples=["ON"])
    type: HolidayType
    name: str
    observed_date: date
    note: str | None = None


class Holiday(BaseModel):
    """A holiday in one year, with every region that observes it."""

    id: str = Field(examples=["canada-day"])
    name_en: str
    name_fr: str
    date: date
    weekday: str
    rule: str = Field(examples=["July 1"], description="How the date is worked out each year.")
    regions: list[Observance]


class Pagination(BaseModel):
    page: int
    per_page: int
    total: int
    pages: int


class HolidayPage(BaseModel):
    data: list[Holiday]
    pagination: Pagination


class NextHolidays(BaseModel):
    region: str
    after: date
    data: list[HolidayOccurrence]


class DateInfo(BaseModel):
    region: str
    date: date
    weekday: str
    is_weekend: bool
    is_business_day: bool
    holidays: list[HolidayOccurrence] = Field(
        description="Holidays on this date, or observed on it after a weekend shift."
    )


class BusinessDayCount(BaseModel):
    region: str
    start: date
    end: date
    calendar_days: int
    business_days: int
    days_off: list[HolidayOccurrence] = Field(description="Statutory holidays observed on weekdays in the range.")


class BusinessDayAdd(BaseModel):
    region: str
    start: date
    days: int
    result: date
    days_off: list[HolidayOccurrence] = Field(description="Statutory holidays skipped on the way.")


class ProblemDetail(BaseModel):
    """RFC 9457 problem details. Every error response has this shape."""

    type: str = Field(examples=["/guide#out-of-range"])
    title: str = Field(examples=["Out of range"])
    status: int = Field(examples=[422])
    detail: str = Field(examples=["Years 2023 to 2050 are supported; got 1999."])
    instance: str = Field(examples=["/v1/regions/NS/holidays"])
    errors: list[dict] | None = Field(None, description="Per-parameter messages, for `invalid-parameters`.")


# ---------- developer portal ----------


class SignupIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class Me(BaseModel):
    email: str
    created_at: datetime
    limits: dict[str, int]


class KeyIn(BaseModel):
    name: str = Field(min_length=1, max_length=60)


class KeyOut(BaseModel):
    id: int
    name: str
    prefix: str
    created_at: datetime
    last_used_at: datetime | None
    revoked_at: datetime | None


class KeyCreated(KeyOut):
    key: str = Field(description="The full key. Shown only once; store it somewhere safe.")


class UsagePoint(BaseModel):
    day: date
    count: int


class UsageOut(BaseModel):
    days: list[UsagePoint]
    total: int
    by_key: dict[int, int]
