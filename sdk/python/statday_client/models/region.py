from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.region_type import RegionType

T = TypeVar("T", bound="Region")


@_attrs_define
class Region:
    """
    Attributes:
        code (str):
        name_en (str):
        name_fr (str):
        type_ (RegionType):
        timezone (str): Used to work out 'today' in the region.
    """

    code: str
    name_en: str
    name_fr: str
    type_: RegionType
    timezone: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        code = self.code

        name_en = self.name_en

        name_fr = self.name_fr

        type_ = self.type_.value

        timezone = self.timezone

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "code": code,
                "name_en": name_en,
                "name_fr": name_fr,
                "type": type_,
                "timezone": timezone,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        code = d.pop("code")

        name_en = d.pop("name_en")

        name_fr = d.pop("name_fr")

        type_ = RegionType(d.pop("type"))

        timezone = d.pop("timezone")

        region = cls(
            code=code,
            name_en=name_en,
            name_fr=name_fr,
            type_=type_,
            timezone=timezone,
        )

        region.additional_properties = d
        return region

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
