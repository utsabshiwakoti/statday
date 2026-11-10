import datetime
from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx2

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.business_day_add import BusinessDayAdd
from ...models.problem_detail import ProblemDetail
from ...models.region_code import RegionCode
from ...types import UNSET, Response


def _get_kwargs(
    region: RegionCode,
    *,
    start: datetime.date,
    days: int,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    json_start = start.isoformat()
    params["start"] = json_start

    params["days"] = days

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/regions/{region}/business-days/add".format(
            region=quote(str(region), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx2.Response
) -> Any | BusinessDayAdd | ProblemDetail | None:
    if response.status_code == 200:
        response_200 = BusinessDayAdd.from_dict(response.json())

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
) -> Response[Any | BusinessDayAdd | ProblemDetail]:
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
    start: datetime.date,
    days: int,
) -> Response[Any | BusinessDayAdd | ProblemDetail]:
    """Add business days

     The date `days` business days after `start`, e.g. a deadline of "10 business days from today".

    Args:
        region (RegionCode):
        start (datetime.date):
        days (int): Negative to count backwards.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | BusinessDayAdd | ProblemDetail]
    """

    kwargs = _get_kwargs(
        region=region,
        start=start,
        days=days,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    region: RegionCode,
    *,
    client: AuthenticatedClient,
    start: datetime.date,
    days: int,
) -> Any | BusinessDayAdd | ProblemDetail | None:
    """Add business days

     The date `days` business days after `start`, e.g. a deadline of "10 business days from today".

    Args:
        region (RegionCode):
        start (datetime.date):
        days (int): Negative to count backwards.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | BusinessDayAdd | ProblemDetail
    """

    return sync_detailed(
        region=region,
        client=client,
        start=start,
        days=days,
    ).parsed


async def asyncio_detailed(
    region: RegionCode,
    *,
    client: AuthenticatedClient,
    start: datetime.date,
    days: int,
) -> Response[Any | BusinessDayAdd | ProblemDetail]:
    """Add business days

     The date `days` business days after `start`, e.g. a deadline of "10 business days from today".

    Args:
        region (RegionCode):
        start (datetime.date):
        days (int): Negative to count backwards.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | BusinessDayAdd | ProblemDetail]
    """

    kwargs = _get_kwargs(
        region=region,
        start=start,
        days=days,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    region: RegionCode,
    *,
    client: AuthenticatedClient,
    start: datetime.date,
    days: int,
) -> Any | BusinessDayAdd | ProblemDetail | None:
    """Add business days

     The date `days` business days after `start`, e.g. a deadline of "10 business days from today".

    Args:
        region (RegionCode):
        start (datetime.date):
        days (int): Negative to count backwards.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | BusinessDayAdd | ProblemDetail
    """

    return (
        await asyncio_detailed(
            region=region,
            client=client,
            start=start,
            days=days,
        )
    ).parsed
