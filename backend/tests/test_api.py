from app.config import settings
from tests.conftest import create_key, signup


def test_regions(client):
    res = client.get("/v1/regions")
    assert res.status_code == 200
    codes = [r["code"] for r in res.json()["data"]]
    assert codes[0] == "CA" and len(codes) == 14


def test_region_holidays(client):
    res = client.get("/v1/regions/ON/holidays", params={"year": 2026, "include_optional": False})
    body = res.json()
    assert body["region"]["name_en"] == "Ontario"
    boxing = body["data"][-1]
    assert boxing["id"] == "boxing-day"
    assert (boxing["date"], boxing["observed_date"], boxing["weekday"]) == ("2026-12-26", "2026-12-28", "Saturday")


def test_year_defaults_to_this_year(client):
    assert client.get("/v1/regions/NS/holidays").json()["year"] == 2026


def test_next_holiday_defaults_to_today(client):
    body = client.get("/v1/regions/NS/holidays/next").json()
    assert body["after"] == "2026-11-10"
    assert [h["id"] for h in body["data"]] == ["remembrance-day"]


def test_check_date(client):
    body = client.get("/v1/regions/ON/dates/2026-12-28").json()
    assert body["is_business_day"] is False
    assert body["holidays"][0]["id"] == "boxing-day"
    assert client.get("/v1/regions/ON/dates/2026-12-29").json()["is_business_day"] is True


def test_business_day_endpoints(client):
    body = client.get("/v1/regions/NS/business-days", params={"start": "2026-12-01", "end": "2026-12-31"}).json()
    assert (body["calendar_days"], body["business_days"]) == (31, 22)
    assert [h["id"] for h in body["days_off"]] == ["christmas-day"]

    body = client.get("/v1/regions/ON/business-days/add", params={"start": "2026-12-23", "days": 3}).json()
    assert body["result"] == "2026-12-30"
    assert [h["id"] for h in body["days_off"]] == ["christmas-day", "boxing-day"]


def test_holiday_search_filters_and_pagination(client):
    res = client.get("/v1/holidays", params={"year": 2026, "region": "ON", "type": "statutory", "per_page": 4})
    body = res.json()
    assert body["pagination"] == {"page": 1, "per_page": 4, "total": 9, "pages": 3}
    assert res.headers["X-Total-Count"] == "9"
    assert 'page=2>; rel="next"' in res.headers["Link"]
    assert 'page=3>; rel="last"' in res.headers["Link"]
    assert all(r["region"] == "ON" for h in body["data"] for r in h["regions"])

    last = client.get("/v1/holidays", params={"year": 2026, "region": "ON", "type": "statutory",
                                               "per_page": 4, "page": 3})
    assert [h["id"] for h in last.json()["data"]] == ["boxing-day"]
    assert 'rel="next"' not in last.headers["Link"]


def test_holiday_search_across_years_and_by_name(client):
    body = client.get("/v1/holidays", params={"start": "2026-01-01", "end": "2030-12-31", "q": "christmas"}).json()
    assert [h["date"] for h in body["data"]] == [f"{y}-12-25" for y in range(2026, 2031)]
    # French names are searched too: "Noël" also finds Boxing Day ("Lendemain de Noël").
    body = client.get("/v1/holidays", params={"year": 2026, "q": "noël"}).json()
    assert [h["id"] for h in body["data"]] == ["christmas-day", "boxing-day"]


def test_get_holiday(client):
    body = client.get("/v1/holidays/canada-day", params={"year": 2028}).json()
    assert body["rule"] == "July 1"
    by_region = {r["region"]: r for r in body["regions"]}
    assert by_region["ON"]["observed_date"] == "2028-07-03"
    assert by_region["NL"]["name"] == "Memorial Day / Canada Day"


# ---------- errors ----------


def assert_problem(res, status, slug):
    assert res.status_code == status
    assert res.headers["content-type"] == "application/problem+json"
    body = res.json()
    assert body["type"] == f"/guide#{slug}" and body["status"] == status
    assert body["title"] and body["detail"] and body["instance"]
    return body


def test_errors_are_problem_json(client):
    assert_problem(client.get("/v1/holidays/not-a-holiday"), 404, "unknown-holiday")
    assert_problem(client.get("/v1/regions/NS/holidays", params={"year": 1999}), 422, "out-of-range")
    body = assert_problem(client.get("/v1/regions/XX/holidays"), 422, "invalid-parameters")
    assert body["errors"][0]["location"] == "path.region"
    assert_problem(client.get("/v1/regions/NS/business-days", params={"start": "2026-12-31", "end": "2026-01-01"}),
                   422, "invalid-range")
    assert_problem(client.get("/v1/holidays", params={"start": "2026-01-01", "end": "2035-01-01"}),
                   422, "invalid-range")


def test_unknown_routes_are_problem_json_too(client):
    res = client.get("/v1/nothing-here")
    assert res.status_code == 404
    assert res.headers["content-type"] == "application/problem+json"


# ---------- caching ----------


def test_etag_and_304(client):
    first = client.get("/v1/regions/NS/holidays", params={"year": 2026})
    etag = first.headers["ETag"]
    assert first.headers["Cache-Control"].startswith("public, max-age=")

    again = client.get("/v1/regions/NS/holidays", params={"year": 2026}, headers={"If-None-Match": etag})
    assert again.status_code == 304 and again.content == b""
    assert again.headers["ETag"] == etag

    weak_list = client.get("/v1/regions/NS/holidays", params={"year": 2026},
                           headers={"If-None-Match": f'"other", W/{etag}'})
    assert weak_list.status_code == 304

    other_year = client.get("/v1/regions/NS/holidays", params={"year": 2027}, headers={"If-None-Match": etag})
    assert other_year.status_code == 200 and other_year.headers["ETag"] != etag


# ---------- rate limits and keys ----------


def test_anonymous_rate_limit(client, monkeypatch, fake_time):
    monkeypatch.setattr(settings, "anonymous_limit", 3)
    remaining = [client.get("/v1/regions").headers["RateLimit-Remaining"] for _ in range(3)]
    assert remaining == ["2", "1", "0"]

    blocked = client.get("/v1/regions")
    assert_problem(blocked, 429, "rate-limited")
    assert blocked.headers["Retry-After"] == blocked.headers["RateLimit-Reset"] == "1800"

    fake_time.value += 1800  # the next window
    assert client.get("/v1/regions").status_code == 200


def test_a_key_gets_its_own_bigger_allowance(client, monkeypatch):
    monkeypatch.setattr(settings, "anonymous_limit", 1)
    key = create_key(client, signup(client))["key"]
    client.get("/v1/regions")
    assert client.get("/v1/regions").status_code == 429
    res = client.get("/v1/regions", headers={"X-API-Key": key})
    assert res.status_code == 200
    assert res.headers["RateLimit-Limit"] == str(settings.key_limit)


def test_bad_key_is_rejected_not_ignored(client):
    assert_problem(client.get("/v1/regions", headers={"X-API-Key": "sd_nope"}), 401, "invalid-key")


def test_openapi_documents_only_the_public_api(client):
    paths = client.get("/openapi.json").json()["paths"]
    assert all(path.startswith("/v1/") for path in paths)
    assert "/v1/regions/{region}/business-days/add" in paths


def test_committed_openapi_spec_is_current():
    """sdk/openapi.json feeds the generated SDK; regenerate it when the API changes."""
    import json
    from pathlib import Path

    from app.main import app

    committed = json.loads((Path(__file__).resolve().parents[2] / "sdk" / "openapi.json").read_text(encoding="utf-8"))
    assert committed == app.openapi(), "run: python scripts/export_openapi.py, then regenerate the SDK"


def test_error_schemas_use_problem_json(client):
    spec = client.get("/openapi.json").json()
    content = spec["paths"]["/v1/regions"]["get"]["responses"]["429"]["content"]
    assert list(content) == ["application/problem+json"]
