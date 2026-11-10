from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.holiday_type import HolidayType
from ..types import UNSET, Unset

T = TypeVar("T", bound="HolidayOccurrence")


@_attrs_define
class HolidayOccurrence:
    """A holiday in one region.

    Attributes:
        id (str):
        name (str): The name used in this region.
        name_en (str):
        name_fr (str):
        date (datetime.date):
        observed_date (datetime.date): The day off when the holiday falls on a weekend (otherwise `date`).
        weekday (str):
        type_ (HolidayType):
        note (None | str | Unset):
    """

    id: str
    name: str
    name_en: str
    name_fr: str
    date: datetime.date
    observed_date: datetime.date
    weekday: str
    type_: HolidayType
    note: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        name_en = self.name_en

        name_fr = self.name_fr

        date = self.date.isoformat()

        observed_date = self.observed_date.isoformat()

        weekday = self.weekday

        type_ = self.type_.value

        note: None | str | Unset
        if isinstance(self.note, Unset):
            note = UNSET
        else:
            note = self.note

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "name_en": name_en,
                "name_fr": name_fr,
                "date": date,
                "observed_date": observed_date,
                "weekday": weekday,
                "type": type_,
            }
        )
        if note is not UNSET:
            field_dict["note"] = note

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        name_en = d.pop("name_en")

        name_fr = d.pop("name_fr")

        date = datetime.date.fromisoformat(d.pop("date"))

        observed_date = datetime.date.fromisoformat(d.pop("observed_date"))

        weekday = d.pop("weekday")

        type_ = HolidayType(d.pop("type"))

        def _parse_note(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        note = _parse_note(d.pop("note", UNSET))

        holiday_occurrence = cls(
            id=id,
            name=name,
            name_en=name_en,
            name_fr=name_fr,
            date=date,
            observed_date=observed_date,
            weekday=weekday,
            type_=type_,
            note=note,
        )

        holiday_occurrence.additional_properties = d
        return holiday_occurrence

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
