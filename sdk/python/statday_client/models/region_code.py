from enum import StrEnum


class RegionCode(StrEnum):
    AB = "AB"
    BC = "BC"
    CA = "CA"
    MB = "MB"
    NB = "NB"
    NL = "NL"
    NS = "NS"
    NT = "NT"
    NU = "NU"
    ON = "ON"
    PE = "PE"
    QC = "QC"
    SK = "SK"
    YT = "YT"

    def __str__(self) -> str:
        return str(self.value)
