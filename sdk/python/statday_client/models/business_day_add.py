from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.holiday_occurrence import HolidayOccurrence


T = TypeVar("T", bound="BusinessDayAdd")


@_attrs_define
class BusinessDayAdd:
    """
    Attributes:
        region (str):
        start (datetime.date):
        days (int):
        result (datetime.date):
        days_off (list[HolidayOccurrence]): Statutory holidays skipped on the way.
    """

    region: str
    start: datetime.date
    days: int
    result: datetime.date
    days_off: list[HolidayOccurrence]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        region = self.region

        start = self.start.isoformat()

        days = self.days

        result = self.result.isoformat()

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
                "days": days,
                "result": result,
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

        days = d.pop("days")

        result = datetime.date.fromisoformat(d.pop("result"))

        days_off = []
        _days_off = d.pop("days_off")
        for days_off_item_data in _days_off:
            days_off_item = HolidayOccurrence.from_dict(days_off_item_data)

            days_off.append(days_off_item)

        business_day_add = cls(
            region=region,
            start=start,
            days=days,
            result=result,
            days_off=days_off,
        )

        business_day_add.additional_properties = d
        return business_day_add

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
