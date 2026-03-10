from __future__ import annotations

from typing import cast

import httpx

from app.models import DestinationResult, TraderPostOrder


def _get_response_body(response: httpx.Response) -> object:
    content_type = response.headers.get("content-type", "")
    if "application/json" in content_type:
        return response.json()

    text = response.text
    return text if text else None


async def send_order_to_traderpost(
    webhook_url: str,
    order: TraderPostOrder,
    timeout_seconds: float,
) -> DestinationResult:
    payload = cast(dict[str, object], order.model_dump(exclude_none=True))
    headers = {"Content-Type": "application/json"}

    try:
        async with httpx.AsyncClient(timeout=timeout_seconds) as client:
            response = await client.post(webhook_url, json=payload, headers=headers)
        return DestinationResult(
            destination="traderpost",
            success=response.is_success,
            status_code=response.status_code,
            error=None if response.is_success else f"TraderPost returned {response.status_code}",
            response_body=_get_response_body(response),
        )
    except httpx.HTTPError as exc:
        return DestinationResult(
            destination="traderpost",
            success=False,
            status_code=None,
            error=f"TraderPost request failed: {exc}",
            response_body=None,
        )
