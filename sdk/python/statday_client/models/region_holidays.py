from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.holiday_occurrence import HolidayOccurrence
    from ..models.region import Region


T = TypeVar("T", bound="RegionHolidays")


@_attrs_define
class RegionHolidays:
    """
    Attributes:
        region (Region):
        year (int):
        data (list[HolidayOccurrence]):
    """

    region: Region
    year: int
    data: list[HolidayOccurrence]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        region = self.region.to_dict()

        year = self.year

        data = []
        for data_item_data in self.data:
            data_item = data_item_data.to_dict()
            data.append(data_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "region": region,
                "year": year,
                "data": data,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.holiday_occurrence import HolidayOccurrence  # noqa: PLC0415
        from ..models.region import Region  # noqa: PLC0415

        d = dict(src_dict)
        region = Region.from_dict(d.pop("region"))

        year = d.pop("year")

        data = []
        _data = d.pop("data")
        for data_item_data in _data:
            data_item = HolidayOccurrence.from_dict(data_item_data)

            data.append(data_item)

        region_holidays = cls(
            region=region,
            year=year,
            data=data,
        )

        region_holidays.additional_properties = d
        return region_holidays

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
