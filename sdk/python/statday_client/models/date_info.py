from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.holiday_occurrence import HolidayOccurrence


T = TypeVar("T", bound="DateInfo")


@_attrs_define
class DateInfo:
    """
    Attributes:
        region (str):
        date (datetime.date):
        weekday (str):
        is_weekend (bool):
        is_business_day (bool):
        holidays (list[HolidayOccurrence]): Holidays on this date, or observed on it after a weekend shift.
    """

    region: str
    date: datetime.date
    weekday: str
    is_weekend: bool
    is_business_day: bool
    holidays: list[HolidayOccurrence]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        region = self.region

        date = self.date.isoformat()

        weekday = self.weekday

        is_weekend = self.is_weekend

        is_business_day = self.is_business_day

        holidays = []
        for holidays_item_data in self.holidays:
            holidays_item = holidays_item_data.to_dict()
            holidays.append(holidays_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "region": region,
                "date": date,
                "weekday": weekday,
                "is_weekend": is_weekend,
                "is_business_day": is_business_day,
                "holidays": holidays,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.holiday_occurrence import HolidayOccurrence  # noqa: PLC0415

        d = dict(src_dict)
        region = d.pop("region")

        date = datetime.date.fromisoformat(d.pop("date"))

        weekday = d.pop("weekday")

        is_weekend = d.pop("is_weekend")

        is_business_day = d.pop("is_business_day")

        holidays = []
        _holidays = d.pop("holidays")
        for holidays_item_data in _holidays:
            holidays_item = HolidayOccurrence.from_dict(holidays_item_data)

            holidays.append(holidays_item)

        date_info = cls(
            region=region,
            date=date,
            weekday=weekday,
            is_weekend=is_weekend,
            is_business_day=is_business_day,
            holidays=holidays,
        )

        date_info.additional_properties = d
        return date_info

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
