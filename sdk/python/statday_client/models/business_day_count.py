from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.holiday_occurrence import HolidayOccurrence


T = TypeVar("T", bound="BusinessDayCount")


@_attrs_define
class BusinessDayCount:
    """
    Attributes:
        region (str):
        start (datetime.date):
        end (datetime.date):
        calendar_days (int):
        business_days (int):
        days_off (list[HolidayOccurrence]): Statutory holidays observed on weekdays in the range.
    """

    region: str
    start: datetime.date
    end: datetime.date
    calendar_days: int
    business_days: int
    days_off: list[HolidayOccurrence]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        region = self.region

        start = self.start.isoformat()

        end = self.end.isoformat()

        calendar_days = self.calendar_days

        business_days = self.business_days

        days_off = []
        for days_off_item_data in self.days_off:
            days_off_item = days_off_item_data.to_dict()
            days_off.append(days_off_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "region": region,
                "start": start,
                "end": end,
                "calendar_days": calendar_days,
                "business_days": business_days,
                "days_off": days_off,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.holiday_occurrence import HolidayOccurrence  # noqa: PLC0415

        d = dict(src_dict)
        region = d.pop("region")

        start = datetime.date.fromisoformat(d.pop("start"))

        end = datetime.date.fromisoformat(d.pop("end"))

        calendar_days = d.pop("calendar_days")

        business_days = d.pop("business_days")

        days_off = []
        _days_off = d.pop("days_off")
        for days_off_item_data in _days_off:
            days_off_item = HolidayOccurrence.from_dict(days_off_item_data)

            days_off.append(days_off_item)

        business_day_count = cls(
            region=region,
            start=start,
            end=end,
            calendar_days=calendar_days,
            business_days=business_days,
            days_off=days_off,
        )

        business_day_count.additional_properties = d
        return business_day_count

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
