# StatDay Python SDK

A typed Python client for the StatDay API, **generated** from the API's OpenAPI document with
[openapi-python-client](https://github.com/openapi-generators/openapi-python-client). Nothing in
`python/` is written by hand.

```bash
pip install ./sdk/python
python sdk/example.py
```

```python
from statday_client import Client
from statday_client.api.regions import next_holidays
from statday_client.models import RegionCode

with Client(base_url="https://statday.onrender.com") as client:
    nxt = next_holidays.sync(client=client, region=RegionCode.NS)
    print(nxt.data[0].name, nxt.data[0].date)
```

Every endpoint has `sync`, `sync_detailed` (status code and headers too), `asyncio` and
`asyncio_detailed`. Errors come back as `ProblemDetail` objects. To use an API key, pass
`headers={"X-API-Key": "sd_..."}` to `Client`.

## Regenerating

When the API changes (a backend test fails if `openapi.json` is out of date):

```bash
cd backend && python scripts/export_openapi.py        # writes sdk/openapi.json
cd ../sdk
pip install openapi-python-client ruff
openapi-python-client generate --path openapi.json --config config.yml --output-path python --overwrite
```
