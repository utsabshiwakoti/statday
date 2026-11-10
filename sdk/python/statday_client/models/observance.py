from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.holiday_type import HolidayType
from ..types import UNSET, Unset

T = TypeVar("T", bound="Observance")


@_attrs_define
class Observance:
    """How one region observes a holiday.

    Attributes:
        region (str):
        type_ (HolidayType):
        name (str):
        observed_date (datetime.date):
        note (None | str | Unset):
    """

    region: str
    type_: HolidayType
    name: str
    observed_date: datetime.date
    note: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        region = self.region

        type_ = self.type_.value

        name = self.name

        observed_date = self.observed_date.isoformat()

        note: None | str | Unset
        if isinstance(self.note, Unset):
            note = UNSET
        else:
            note = self.note

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "region": region,
                "type": type_,
                "name": name,
                "observed_date": observed_date,
            }
        )
        if note is not UNSET:
            field_dict["note"] = note

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        region = d.pop("region")

        type_ = HolidayType(d.pop("type"))

        name = d.pop("name")

        observed_date = datetime.date.fromisoformat(d.pop("observed_date"))

        def _parse_note(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        note = _parse_note(d.pop("note", UNSET))

        observance = cls(
            region=region,
            type_=type_,
            name=name,
            observed_date=observed_date,
            note=note,
        )

        observance.additional_properties = d
        return observance

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
