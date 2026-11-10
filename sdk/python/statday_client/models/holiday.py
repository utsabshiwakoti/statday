from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.observance import Observance


T = TypeVar("T", bound="Holiday")


@_attrs_define
class Holiday:
    """A holiday in one year, with every region that observes it.

    Attributes:
        id (str):
        name_en (str):
        name_fr (str):
        date (datetime.date):
        weekday (str):
        rule (str): How the date is worked out each year.
        regions (list[Observance]):
    """

    id: str
    name_en: str
    name_fr: str
    date: datetime.date
    weekday: str
    rule: str
    regions: list[Observance]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name_en = self.name_en

        name_fr = self.name_fr

        date = self.date.isoformat()

        weekday = self.weekday

        rule = self.rule

        regions = []
        for regions_item_data in self.regions:
            regions_item = regions_item_data.to_dict()
            regions.append(regions_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name_en": name_en,
                "name_fr": name_fr,
                "date": date,
                "weekday": weekday,
                "rule": rule,
                "regions": regions,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.observance import Observance  # noqa: PLC0415

        d = dict(src_dict)
        id = d.pop("id")

        name_en = d.pop("name_en")

        name_fr = d.pop("name_fr")

        date = datetime.date.fromisoformat(d.pop("date"))

        weekday = d.pop("weekday")

        rule = d.pop("rule")

        regions = []
        _regions = d.pop("regions")
        for regions_item_data in _regions:
            regions_item = Observance.from_dict(regions_item_data)

            regions.append(regions_item)

        holiday = cls(
            id=id,
            name_en=name_en,
            name_fr=name_fr,
            date=date,
            weekday=weekday,
            rule=rule,
            regions=regions,
        )

        holiday.additional_properties = d
        return holiday

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
