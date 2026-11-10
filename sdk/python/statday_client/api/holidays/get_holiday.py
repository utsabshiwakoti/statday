from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx2

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.holiday import Holiday
from ...models.problem_detail import ProblemDetail
from ...types import UNSET, Response, Unset


def _get_kwargs(
    holiday_id: str,
    *,
    year: int | None | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    json_year: int | None | Unset
    if isinstance(year, Unset):
        json_year = UNSET
    else:
        json_year = year
    params["year"] = json_year

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/holidays/{holiday_id}".format(
            holiday_id=quote(str(holiday_id), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx2.Response
) -> Any | Holiday | ProblemDetail | None:
    if response.status_code == 200:
        response_200 = Holiday.from_dict(response.json())

        return response_200

    if response.status_code == 304:
        response_304 = cast(Any, None)
        return response_304

    if response.status_code == 401:
        response_401 = ProblemDetail.from_dict(response.json())

        return response_401

    if response.status_code == 404:
        response_404 = ProblemDetail.from_dict(response.json())

        return response_404

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
) -> Response[Any | Holiday | ProblemDetail]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    holiday_id: str,
    *,
    client: AuthenticatedClient,
    year: int | None | Unset = UNSET,
) -> Response[Any | Holiday | ProblemDetail]:
    """Get a holiday

     One holiday in a given year: its date, the rule behind it, and how each region observes it.

    Args:
        holiday_id (str):
        year (int | None | Unset): Defaults to the current year.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | Holiday | ProblemDetail]
    """

    kwargs = _get_kwargs(
        holiday_id=holiday_id,
        year=year,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    holiday_id: str,
    *,
    client: AuthenticatedClient,
    year: int | None | Unset = UNSET,
) -> Any | Holiday | ProblemDetail | None:
    """Get a holiday

     One holiday in a given year: its date, the rule behind it, and how each region observes it.

    Args:
        holiday_id (str):
        year (int | None | Unset): Defaults to the current year.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | Holiday | ProblemDetail
    """

    return sync_detailed(
        holiday_id=holiday_id,
        client=client,
        year=year,
    ).parsed


async def asyncio_detailed(
    holiday_id: str,
    *,
    client: AuthenticatedClient,
    year: int | None | Unset = UNSET,
) -> Response[Any | Holiday | ProblemDetail]:
    """Get a holiday

     One holiday in a given year: its date, the rule behind it, and how each region observes it.

    Args:
        holiday_id (str):
        year (int | None | Unset): Defaults to the current year.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | Holiday | ProblemDetail]
    """

    kwargs = _get_kwargs(
        holiday_id=holiday_id,
        year=year,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    holiday_id: str,
    *,
    client: AuthenticatedClient,
    year: int | None | Unset = UNSET,
) -> Any | Holiday | ProblemDetail | None:
    """Get a holiday

     One holiday in a given year: its date, the rule behind it, and how each region observes it.

    Args:
        holiday_id (str):
        year (int | None | Unset): Defaults to the current year.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | Holiday | ProblemDetail
    """

    return (
        await asyncio_detailed(
            holiday_id=holiday_id,
            client=client,
            year=year,
        )
    ).parsed
