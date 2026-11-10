from enum import StrEnum


class HolidayType(StrEnum):
    OPTIONAL = "optional"
    STATUTORY = "statutory"

    def __str__(self) -> str:
        return str(self.value)
