from enum import StrEnum


class RegionType(StrEnum):
    FEDERAL = "federal"
    PROVINCE = "province"
    TERRITORY = "territory"

    def __str__(self) -> str:
        return str(self.value)
