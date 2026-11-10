import datetime
from http import HTTPStatus
from typing import Any, cast

import httpx2

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.holiday_page import HolidayPage
from ...models.holiday_type import HolidayType
from ...models.problem_detail import ProblemDetail
from ...models.region_code import RegionCode
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    year: int | None | Unset = UNSET,
    start: datetime.date | None | Unset = UNSET,
    end: datetime.date | None | Unset = UNSET,
    region: None | RegionCode | Unset = UNSET,
    type_: HolidayType | None | Unset = UNSET,
    q: None | str | Unset = UNSET,
    page: int | Unset = 1,
    per_page: int | Unset = 20,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    json_year: int | None | Unset
    if isinstance(year, Unset):
        json_year = UNSET
    else:
        json_year = year
    params["year"] = json_year

    json_start: None | str | Unset
    if isinstance(start, Unset):
        json_start = UNSET
    elif isinstance(start, datetime.date):
        json_start = start.isoformat()
    else:
        json_start = start
    params["start"] = json_start

    json_end: None | str | Unset
    if isinstance(end, Unset):
        json_end = UNSET
    elif isinstance(end, datetime.date):
        json_end = end.isoformat()
    else:
        json_end = end
    params["end"] = json_end

    json_region: None | str | Unset
    if isinstance(region, Unset):
        json_region = UNSET
    elif isinstance(region, RegionCode):
        json_region = region.value
    else:
        json_region = region
    params["region"] = json_region

    json_type_: None | str | Unset
    if isinstance(type_, Unset):
        json_type_ = UNSET
    elif isinstance(type_, HolidayType):
        json_type_ = type_.value
    else:
        json_type_ = type_
    params["type"] = json_type_

    json_q: None | str | Unset
    if isinstance(q, Unset):
        json_q = UNSET
    else:
        json_q = q
    params["q"] = json_q

    params["page"] = page

    params["per_page"] = per_page

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/holidays",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx2.Response
) -> Any | HolidayPage | ProblemDetail | None:
    if response.status_code == 200:
        response_200 = HolidayPage.from_dict(response.json())

        return response_200

    if response.status_code == 304:
        response_304 = cast(Any, None)
        return response_304

    if response.status_code == 401:
        response_401 = ProblemDetail.from_dict(response.json())

        return response_401

    if response.status_code == 422:
        response_422 = ProblemDetail.from_dict(response.json())

        return response_422

    if response.status_code == 429:
        response_429 = ProblemDetail.from_dict(response.json())

        return response_429

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx2.Response
) -> Response[Any | HolidayPage | ProblemDetail]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    year: int | None | Unset = UNSET,
    start: datetime.date | None | Unset = UNSET,
    end: datetime.date | None | Unset = UNSET,
    region: None | RegionCode | Unset = UNSET,
    type_: HolidayType | None | Unset = UNSET,
    q: None | str | Unset = UNSET,
    page: int | Unset = 1,
    per_page: int | Unset = 20,
) -> Response[Any | HolidayPage | ProblemDetail]:
    """Search holidays

     Holidays across Canada between two dates, with the regions observing each one.

    Filters narrow both the holidays and their `regions` list (e.g. `region=ON&type=statutory`).
    Results are paginated: see `pagination` in the body, or the `Link` and `X-Total-Count` headers.

    Args:
        year (int | None | Unset): Shorthand for `start` and `end` covering one year.
        start (datetime.date | None | Unset): Defaults to January 1 of the current year.
        end (datetime.date | None | Unset): Defaults to December 31 of `start`'s year.
        region (None | RegionCode | Unset):
        type_ (HolidayType | None | Unset):
        q (None | str | Unset): Search English and French names.
        page (int | Unset):  Default: 1.
        per_page (int | Unset):  Default: 20.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HolidayPage | ProblemDetail]
    """

    kwargs = _get_kwargs(
        year=year,
        start=start,
        end=end,
        region=region,
        type_=type_,
        q=q,
        page=page,
        per_page=per_page,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    year: int | None | Unset = UNSET,
    start: datetime.date | None | Unset = UNSET,
    end: datetime.date | None | Unset = UNSET,
    region: None | RegionCode | Unset = UNSET,
    type_: HolidayType | None | Unset = UNSET,
    q: None | str | Unset = UNSET,
    page: int | Unset = 1,
    per_page: int | Unset = 20,
) -> Any | HolidayPage | ProblemDetail | None:
    """Search holidays

     Holidays across Canada between two dates, with the regions observing each one.

    Filters narrow both the holidays and their `regions` list (e.g. `region=ON&type=statutory`).
    Results are paginated: see `pagination` in the body, or the `Link` and `X-Total-Count` headers.

    Args:
        year (int | None | Unset): Shorthand for `start` and `end` covering one year.
        start (datetime.date | None | Unset): Defaults to January 1 of the current year.
        end (datetime.date | None | Unset): Defaults to December 31 of `start`'s year.
        region (None | RegionCode | Unset):
        type_ (HolidayType | None | Unset):
        q (None | str | Unset): Search English and French names.
        page (int | Unset):  Default: 1.
        per_page (int | Unset):  Default: 20.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HolidayPage | ProblemDetail
    """

    return sync_detailed(
        client=client,
        year=year,
        start=start,
        end=end,
        region=region,
        type_=type_,
        q=q,
        page=page,
        per_page=per_page,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    year: int | None | Unset = UNSET,
    start: datetime.date | None | Unset = UNSET,
    end: datetime.date | None | Unset = UNSET,
    region: None | RegionCode | Unset = UNSET,
    type_: HolidayType | None | Unset = UNSET,
    q: None | str | Unset = UNSET,
    page: int | Unset = 1,
    per_page: int | Unset = 20,
) -> Response[Any | HolidayPage | ProblemDetail]:
    """Search holidays

     Holidays across Canada between two dates, with the regions observing each one.

    Filters narrow both the holidays and their `regions` list (e.g. `region=ON&type=statutory`).
    Results are paginated: see `pagination` in the body, or the `Link` and `X-Total-Count` headers.

    Args:
        year (int | None | Unset): Shorthand for `start` and `end` covering one year.
        start (datetime.date | None | Unset): Defaults to January 1 of the current year.
        end (datetime.date | None | Unset): Defaults to December 31 of `start`'s year.
        region (None | RegionCode | Unset):
        type_ (HolidayType | None | Unset):
        q (None | str | Unset): Search English and French names.
        page (int | Unset):  Default: 1.
        per_page (int | Unset):  Default: 20.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HolidayPage | ProblemDetail]
    """

    kwargs = _get_kwargs(
        year=year,
        start=start,
        end=end,
        region=region,
        type_=type_,
        q=q,
        page=page,
        per_page=per_page,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    year: int | None | Unset = UNSET,
    start: datetime.date | None | Unset = UNSET,
    end: datetime.date | None | Unset = UNSET,
    region: None | RegionCode | Unset = UNSET,
    type_: HolidayType | None | Unset = UNSET,
    q: None | str | Unset = UNSET,
    page: int | Unset = 1,
    per_page: int | Unset = 20,
) -> Any | HolidayPage | ProblemDetail | None:
    """Search holidays

     Holidays across Canada between two dates, with the regions observing each one.

    Filters narrow both the holidays and their `regions` list (e.g. `region=ON&type=statutory`).
    Results are paginated: see `pagination` in the body, or the `Link` and `X-Total-Count` headers.

    Args:
        year (int | None | Unset): Shorthand for `start` and `end` covering one year.
        start (datetime.date | None | Unset): Defaults to January 1 of the current year.
        end (datetime.date | None | Unset): Defaults to December 31 of `start`'s year.
        region (None | RegionCode | Unset):
        type_ (HolidayType | None | Unset):
        q (None | str | Unset): Search English and French names.
        page (int | Unset):  Default: 1.
        per_page (int | Unset):  Default: 20.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HolidayPage | ProblemDetail
    """

    return (
        await asyncio_detailed(
            client=client,
            year=year,
            start=start,
            end=end,
            region=region,
            type_=type_,
            q=q,
            page=page,
            per_page=per_page,
        )
    ).parsed
