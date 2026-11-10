import datetime
from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx2

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.date_info import DateInfo
from ...models.problem_detail import ProblemDetail
from ...models.region_code import RegionCode
from ...types import Response


def _get_kwargs(
    region: RegionCode,
    day: datetime.date,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/regions/{region}/dates/{day}".format(
            region=quote(str(region), safe=""),
            day=quote(str(day), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx2.Response
) -> Any | DateInfo | ProblemDetail | None:
    if response.status_code == 200:
        response_200 = DateInfo.from_dict(response.json())

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
) -> Response[Any | DateInfo | ProblemDetail]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    region: RegionCode,
    day: datetime.date,
    *,
    client: AuthenticatedClient,
) -> Response[Any | DateInfo | ProblemDetail]:
    """Check a date

     Is this date a business day in the region, and is it (or is it observed as) a holiday?

    Args:
        region (RegionCode):
        day (datetime.date):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | DateInfo | ProblemDetail]
    """

    kwargs = _get_kwargs(
        region=region,
        day=day,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    region: RegionCode,
    day: datetime.date,
    *,
    client: AuthenticatedClient,
) -> Any | DateInfo | ProblemDetail | None:
    """Check a date

     Is this date a business day in the region, and is it (or is it observed as) a holiday?

    Args:
        region (RegionCode):
        day (datetime.date):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | DateInfo | ProblemDetail
    """

    return sync_detailed(
        region=region,
        day=day,
        client=client,
    ).parsed


async def asyncio_detailed(
    region: RegionCode,
    day: datetime.date,
    *,
    client: AuthenticatedClient,
) -> Response[Any | DateInfo | ProblemDetail]:
    """Check a date

     Is this date a business day in the region, and is it (or is it observed as) a holiday?

    Args:
        region (RegionCode):
        day (datetime.date):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | DateInfo | ProblemDetail]
    """

    kwargs = _get_kwargs(
        region=region,
        day=day,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    region: RegionCode,
    day: datetime.date,
    *,
    client: AuthenticatedClient,
) -> Any | DateInfo | ProblemDetail | None:
    """Check a date

     Is this date a business day in the region, and is it (or is it observed as) a holiday?

    Args:
        region (RegionCode):
        day (datetime.date):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | DateInfo | ProblemDetail
    """

    return (
        await asyncio_detailed(
            region=region,
            day=day,
            client=client,
        )
    ).parsed
