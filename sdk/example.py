"""Using the generated SDK.

    pip install ./sdk/python
    python sdk/example.py                       # against the live API
    STATDAY_URL=http://localhost:8000 python sdk/example.py
"""

import os
from datetime import date

from statday_client import Client
from statday_client.api.business_days import add_business_days
from statday_client.api.holidays import list_holidays
from statday_client.api.regions import next_holidays, region_holidays
from statday_client.models import HolidayType, ProblemDetail, RegionCode

BASE_URL = os.getenv("STATDAY_URL", "https://statday.onrender.com")
API_KEY = os.getenv("STATDAY_API_KEY")  # optional: raises the rate limit

# Keys are optional, so send the X-API-Key header only when there is one.
client = Client(base_url=BASE_URL, headers={"X-API-Key": API_KEY} if API_KEY else {})

with client:
    # Every holiday in Nova Scotia this year.
    ns = region_holidays.sync(client=client, region=RegionCode.NS, include_optional=False)
    print(f"{ns.region.name_en}, {ns.year}:")
    for h in ns.data:
        moved = f" (observed {h.observed_date})" if h.observed_date != h.date else ""
        print(f"  {h.date}  {h.name}{moved}")

    # The next statutory holiday in Ontario.
    upcoming = next_holidays.sync(client=client, region=RegionCode.ON)
    print("\nNext in Ontario:", upcoming.data[0].name, upcoming.data[0].date)

    # A deadline 10 business days from today in Quebec.
    deadline = add_business_days.sync(client=client, region=RegionCode.QC, start=date.today(), days=10)
    print("10 business days from today in Quebec:", deadline.result)

    # Statutory holidays shared by every region.
    page = list_holidays.sync(client=client, type_=HolidayType.STATUTORY, per_page=50)
    everywhere = [h.name_en for h in page.data if len(h.regions) == 14]
    print("\nStatutory everywhere:", ", ".join(everywhere))

    # Errors come back as typed problem details.
    error = region_holidays.sync(client=client, region=RegionCode.NS, year=1999)
    if isinstance(error, ProblemDetail):
        print(f"\n{error.status} {error.title}: {error.detail}")
