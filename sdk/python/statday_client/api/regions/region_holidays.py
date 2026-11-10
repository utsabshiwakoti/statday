from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx2

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.problem_detail import ProblemDetail
from ...models.region_code import RegionCode
from ...models.region_holidays import RegionHolidays
from ...types import UNSET, Response, Unset


def _get_kwargs(
    region: RegionCode,
    *,
    year: int | None | Unset = UNSET,
    include_optional: bool | Unset = True,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    json_year: int | None | Unset
    if isinstance(year, Unset):
        json_year = UNSET
    else:
        json_year = year
    params["year"] = json_year

    params["include_optional"] = include_optional

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/regions/{region}/holidays".format(
            region=quote(str(region), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx2.Response
) -> Any | ProblemDetail | RegionHolidays | None:
    if response.status_code == 200:
        response_200 = RegionHolidays.from_dict(response.json())

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
) -> Response[Any | ProblemDetail | RegionHolidays]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    region: RegionCode,
    *,
    client: AuthenticatedClient,
    year: int | None | Unset = UNSET,
    include_optional: bool | Unset = True,
) -> Response[Any | ProblemDetail | RegionHolidays]:
    """Holidays in a region

     Every holiday in one region for a year, in date order, with the observed day off for weekend dates.

    Args:
        region (RegionCode):
        year (int | None | Unset): Defaults to the current year.
        include_optional (bool | Unset): Include holidays that aren't statutory. Default: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ProblemDetail | RegionHolidays]
    """

    kwargs = _get_kwargs(
        region=region,
        year=year,
        include_optional=include_optional,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    region: RegionCode,
    *,
    client: AuthenticatedClient,
    year: int | None | Unset = UNSET,
    include_optional: bool | Unset = True,
) -> Any | ProblemDetail | RegionHolidays | None:
    """Holidays in a region

     Every holiday in one region for a year, in date order, with the observed day off for weekend dates.

    Args:
        region (RegionCode):
        year (int | None | Unset): Defaults to the current year.
        include_optional (bool | Unset): Include holidays that aren't statutory. Default: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | ProblemDetail | RegionHolidays
    """

    return sync_detailed(
        region=region,
        client=client,
        year=year,
        include_optional=include_optional,
    ).parsed


async def asyncio_detailed(
    region: RegionCode,
    *,
    client: AuthenticatedClient,
    year: int | None | Unset = UNSET,
    include_optional: bool | Unset = True,
) -> Response[Any | ProblemDetail | RegionHolidays]:
    """Holidays in a region

     Every holiday in one region for a year, in date order, with the observed day off for weekend dates.

    Args:
        region (RegionCode):
        year (int | None | Unset): Defaults to the current year.
        include_optional (bool | Unset): Include holidays that aren't statutory. Default: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ProblemDetail | RegionHolidays]
    """

    kwargs = _get_kwargs(
        region=region,
        year=year,
        include_optional=include_optional,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    region: RegionCode,
    *,
    client: AuthenticatedClient,
    year: int | None | Unset = UNSET,
    include_optional: bool | Unset = True,
) -> Any | ProblemDetail | RegionHolidays | None:
    """Holidays in a region

     Every holiday in one region for a year, in date order, with the observed day off for weekend dates.

    Args:
        region (RegionCode):
        year (int | None | Unset): Defaults to the current year.
        include_optional (bool | Unset): Include holidays that aren't statutory. Default: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | ProblemDetail | RegionHolidays
    """

    return (
        await asyncio_detailed(
            region=region,
            client=client,
            year=year,
            include_optional=include_optional,
        )
    ).parsed
