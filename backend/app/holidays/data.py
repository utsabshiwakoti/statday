"""The holiday table. Plain data so it can be reviewed against the law line by line.

"statutory" = a paid general/public holiday under that region's employment standards law.
"optional"  = widely observed (government offices, many employers, banks) but not guaranteed.
"CA" means federally regulated workplaces (banks, airlines, telecoms...) under the Canada Labour Code.

Checked November 2026 against federal, provincial and territorial employment standards pages.
Regions decide their own holidays, so treat this as a reference, not legal advice.
"""

from dataclasses import dataclass, field

from .rules import (
    MONDAY,
    EasterOffset,
    Fixed,
    FridayBeforeLastSunday,
    NearestWeekday,
    NthWeekday,
    Rule,
    WeekdayBefore,
)

FIRST_YEAR = 2023  # every current rule was in force by 2023 (e.g. Sept 30 in B.C., Manitoba, Yukon)
LAST_YEAR = 2050  # later years are projections of today's law

REGIONS = {
    "CA": ("Federal (Canada Labour Code)", "Fédéral (Code canadien du travail)", "federal"),
    "AB": ("Alberta", "Alberta", "province"),
    "BC": ("British Columbia", "Colombie-Britannique", "province"),
    "MB": ("Manitoba", "Manitoba", "province"),
    "NB": ("New Brunswick", "Nouveau-Brunswick", "province"),
    "NL": ("Newfoundland and Labrador", "Terre-Neuve-et-Labrador", "province"),
    "NS": ("Nova Scotia", "Nouvelle-Écosse", "province"),
    "ON": ("Ontario", "Ontario", "province"),
    "PE": ("Prince Edward Island", "Île-du-Prince-Édouard", "province"),
    "QC": ("Quebec", "Québec", "province"),
    "SK": ("Saskatchewan", "Saskatchewan", "province"),
    "NT": ("Northwest Territories", "Territoires du Nord-Ouest", "territory"),
    "NU": ("Nunavut", "Nunavut", "territory"),
    "YT": ("Yukon", "Yukon", "territory"),
}
ALL = frozenset(REGIONS)

# Used for "today" in each region (e.g. which holiday is next). Regions with more than one
# time zone use the capital's; federal uses Ottawa's.
REGION_TIMEZONES = {
    "CA": "America/Toronto", "AB": "America/Edmonton", "BC": "America/Vancouver",
    "MB": "America/Winnipeg", "NB": "America/Moncton", "NL": "America/St_Johns",
    "NS": "America/Halifax", "ON": "America/Toronto", "PE": "America/Halifax",
    "QC": "America/Toronto", "SK": "America/Regina", "NT": "America/Yellowknife",
    "NU": "America/Iqaluit", "YT": "America/Whitehorse",
}


@dataclass(frozen=True)
class Holiday:
    id: str
    name_en: str
    name_fr: str
    rule: Rule
    statutory: frozenset[str]
    optional: frozenset[str] = frozenset()
    # How a weekend date is moved to a day off: "weekend" (Sat/Sun -> next free weekday),
    # "sunday" (only Sunday moves, to Monday), or "none" (never moved).
    shift: str = "weekend"
    shift_overrides: dict[str, str] = field(default_factory=dict)
    local_names: dict[str, str] = field(default_factory=dict)  # region -> name used there
    notes: dict[str, str] = field(default_factory=dict)  # region -> caveat

    def shift_for(self, region: str) -> str:
        return self.shift_overrides.get(region, self.shift)

    def name_in(self, region: str) -> str:
        return self.local_names.get(region, self.name_en)


def regions(*codes: str) -> frozenset[str]:
    return frozenset(codes)


HOLIDAYS: list[Holiday] = [
    Holiday("new-years-day", "New Year's Day", "Jour de l'An", Fixed(1, 1), ALL),
    Holiday("family-day", "Family Day", "Fête de la famille", NthWeekday(3, MONDAY, 2),
            regions("AB", "BC", "NB", "ON", "SK")),
    Holiday("louis-riel-day", "Louis Riel Day", "Journée Louis-Riel", NthWeekday(3, MONDAY, 2), regions("MB")),
    Holiday("nova-scotia-heritage-day", "Nova Scotia Heritage Day", "Fête du patrimoine de la Nouvelle-Écosse",
            NthWeekday(3, MONDAY, 2), regions("NS")),
    Holiday("islander-day", "Islander Day", "Fête des Insulaires", NthWeekday(3, MONDAY, 2), regions("PE")),
    Holiday("yukon-heritage-day", "Yukon Heritage Day", "Journée du patrimoine du Yukon",
            FridayBeforeLastSunday(2), frozenset(), regions("YT"), shift="none"),
    Holiday("st-patricks-day", "St. Patrick's Day", "Saint-Patrick", NearestWeekday(MONDAY, 3, 17),
            frozenset(), regions("NL"), notes={"NL": "Provincial government holiday."}),
    Holiday("good-friday", "Good Friday", "Vendredi saint", EasterOffset(-2), ALL,
            notes={"QC": "Employers may give Easter Monday instead of Good Friday."}),
    Holiday("easter-monday", "Easter Monday", "Lundi de Pâques", EasterOffset(1), frozenset(), regions("CA", "QC"),
            notes={"CA": "Federal public service holiday; not in the Canada Labour Code.",
                   "QC": "Statutory instead of Good Friday if the employer chooses."}),
    Holiday("st-georges-day", "St. George's Day", "Saint-Georges", NearestWeekday(MONDAY, 4, 23),
            frozenset(), regions("NL"), notes={"NL": "Provincial government holiday."}),
    Holiday("victoria-day", "Victoria Day", "Fête de la Reine", WeekdayBefore(MONDAY, 5, 25),
            regions("CA", "AB", "BC", "MB", "ON", "SK", "NT", "NU", "YT"), regions("NB", "NL", "NS", "PE")),
    Holiday("national-patriots-day", "National Patriots' Day", "Journée nationale des patriotes",
            WeekdayBefore(MONDAY, 5, 25), regions("QC")),
    Holiday("national-indigenous-peoples-day", "National Indigenous Peoples Day",
            "Journée nationale des peuples autochtones", Fixed(6, 21), regions("NT", "YT")),
    Holiday("discovery-day-nl", "Discovery Day", "Jour de la Découverte", NearestWeekday(MONDAY, 6, 24),
            frozenset(), regions("NL"), notes={"NL": "Provincial government holiday."}),
    Holiday("fete-nationale", "Fête nationale du Québec", "Fête nationale du Québec", Fixed(6, 24),
            regions("QC"), shift="sunday", local_names={"QC": "Fête nationale (St-Jean-Baptiste Day)"}),
    Holiday("canada-day", "Canada Day", "Fête du Canada", Fixed(7, 1), ALL,
            shift_overrides={"QC": "sunday"}, local_names={"NL": "Memorial Day / Canada Day"}),
    Holiday("nunavut-day", "Nunavut Day", "Jour du Nunavut", Fixed(7, 9), regions("NU")),
    Holiday("orangemens-day", "Orangemen's Day", "Fête des Orangistes", NearestWeekday(MONDAY, 7, 12),
            frozenset(), regions("NL"), notes={"NL": "Provincial government holiday."}),
    Holiday("bc-day", "British Columbia Day", "Jour de la Colombie-Britannique",
            NthWeekday(1, MONDAY, 8), regions("BC")),
    Holiday("saskatchewan-day", "Saskatchewan Day", "Fête de la Saskatchewan", NthWeekday(1, MONDAY, 8), regions("SK")),
    Holiday("new-brunswick-day", "New Brunswick Day", "Fête du Nouveau-Brunswick",
            NthWeekday(1, MONDAY, 8), regions("NB")),
    Holiday("civic-holiday", "Civic Holiday", "Congé civique", NthWeekday(1, MONDAY, 8),
            regions("NT", "NU"), regions("CA", "AB", "MB", "NS", "ON", "PE"),
            local_names={"AB": "Heritage Day", "MB": "Terry Fox Day", "NS": "Natal Day"},
            notes={"CA": "Federal public service holiday; not in the Canada Labour Code."}),
    Holiday("discovery-day-yukon", "Discovery Day", "Jour de la Découverte", NthWeekday(3, MONDAY, 8), regions("YT")),
    Holiday("labour-day", "Labour Day", "Fête du travail", NthWeekday(1, MONDAY, 9), ALL),
    Holiday("truth-and-reconciliation", "National Day for Truth and Reconciliation",
            "Journée nationale de la vérité et de la réconciliation", Fixed(9, 30),
            regions("CA", "BC", "MB", "PE", "NT", "NU", "YT")),
    Holiday("thanksgiving", "Thanksgiving", "Action de grâce", NthWeekday(2, MONDAY, 10),
            regions("CA", "AB", "BC", "MB", "ON", "QC", "SK", "NT", "NU", "YT"), regions("NB", "NL", "NS", "PE")),
    Holiday("remembrance-day", "Remembrance Day", "Jour du Souvenir", Fixed(11, 11),
            regions("CA", "AB", "BC", "NB", "NL", "NS", "PE", "SK", "NT", "NU", "YT"),
            shift="none",
            notes={"NS": "Covered by Nova Scotia's Remembrance Day Act rather than the Labour Standards Code."}),
    Holiday("christmas-day", "Christmas Day", "Noël", Fixed(12, 25), ALL),
    Holiday("boxing-day", "Boxing Day", "Lendemain de Noël", Fixed(12, 26),
            regions("CA", "ON"), regions("AB", "BC", "MB", "NB", "NL", "NS", "PE", "SK", "NT", "NU", "YT")),
]

BY_ID = {h.id: h for h in HOLIDAYS}

