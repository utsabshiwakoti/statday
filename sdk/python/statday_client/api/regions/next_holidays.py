import datetime
from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx2

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.next_holidays import NextHolidays
from ...models.problem_detail import ProblemDetail
from ...models.region_code import RegionCode
from ...types import UNSET, Response, Unset


def _get_kwargs(
    region: RegionCode,
    *,
    after: datetime.date | None | Unset = UNSET,
    count: int | Unset = 1,
    include_optional: bool | Unset = False,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    json_after: None | str | Unset
    if isinstance(after, Unset):
        json_after = UNSET
    elif isinstance(after, datetime.date):
        json_after = after.isoformat()
    else:
        json_after = after
    params["after"] = json_after

    params["count"] = count

    params["include_optional"] = include_optional

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/regions/{region}/holidays/next".format(
            region=quote(str(region), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx2.Response
) -> Any | NextHolidays | ProblemDetail | None:
    if response.status_code == 200:
        response_200 = NextHolidays.from_dict(response.json())

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
) -> Response[Any | NextHolidays | ProblemDetail]:
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
    after: datetime.date | None | Unset = UNSET,
    count: int | Unset = 1,
    include_optional: bool | Unset = False,
) -> Response[Any | NextHolidays | ProblemDetail]:
    """Next holidays in a region

     The next holidays strictly after a date. Statutory only unless `include_optional=true`.

    Args:
        region (RegionCode):
        after (datetime.date | None | Unset): Defaults to today in the region.
        count (int | Unset):  Default: 1.
        include_optional (bool | Unset): Include holidays that aren't statutory. Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | NextHolidays | ProblemDetail]
    """

    kwargs = _get_kwargs(
        region=region,
        after=after,
        count=count,
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
    after: datetime.date | None | Unset = UNSET,
    count: int | Unset = 1,
    include_optional: bool | Unset = False,
) -> Any | NextHolidays | ProblemDetail | None:
    """Next holidays in a region

     The next holidays strictly after a date. Statutory only unless `include_optional=true`.

    Args:
        region (RegionCode):
        after (datetime.date | None | Unset): Defaults to today in the region.
        count (int | Unset):  Default: 1.
        include_optional (bool | Unset): Include holidays that aren't statutory. Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | NextHolidays | ProblemDetail
    """

    return sync_detailed(
        region=region,
        client=client,
        after=after,
        count=count,
        include_optional=include_optional,
    ).parsed


async def asyncio_detailed(
    region: RegionCode,
    *,
    client: AuthenticatedClient,
    after: datetime.date | None | Unset = UNSET,
    count: int | Unset = 1,
    include_optional: bool | Unset = False,
) -> Response[Any | NextHolidays | ProblemDetail]:
    """Next holidays in a region

     The next holidays strictly after a date. Statutory only unless `include_optional=true`.

    Args:
        region (RegionCode):
        after (datetime.date | None | Unset): Defaults to today in the region.
        count (int | Unset):  Default: 1.
        include_optional (bool | Unset): Include holidays that aren't statutory. Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | NextHolidays | ProblemDetail]
    """

    kwargs = _get_kwargs(
        region=region,
        after=after,
        count=count,
        include_optional=include_optional,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    region: RegionCode,
    *,
    client: AuthenticatedClient,
    after: datetime.date | None | Unset = UNSET,
    count: int | Unset = 1,
    include_optional: bool | Unset = False,
) -> Any | NextHolidays | ProblemDetail | None:
    """Next holidays in a region

     The next holidays strictly after a date. Statutory only unless `include_optional=true`.

    Args:
        region (RegionCode):
        after (datetime.date | None | Unset): Defaults to today in the region.
        count (int | Unset):  Default: 1.
        include_optional (bool | Unset): Include holidays that aren't statutory. Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | NextHolidays | ProblemDetail
    """

    return (
        await asyncio_detailed(
            region=region,
            client=client,
            after=after,
            count=count,
            include_optional=include_optional,
        )
    ).parsed
