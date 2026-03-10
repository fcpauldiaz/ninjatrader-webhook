from __future__ import annotations

from typing import cast

import httpx

from app.models import DestinationResult, JsonValue, TraderPostOrder


def _build_orders_url(base_url: str, orders_path: str) -> str:
    return f"{base_url.rstrip('/')}/{orders_path.lstrip('/')}"


def _get_response_body(response: httpx.Response) -> JsonValue:
    content_type = response.headers.get("content-type", "")
    if "application/json" in content_type:
        parsed = response.json()
        return cast(JsonValue, parsed)

    text = response.text
    return text if text else None


async def send_order_to_traderpost(
    base_url: str,
    orders_path: str,
    api_key: str,
    order: TraderPostOrder,
    timeout_seconds: float,
) -> DestinationResult:
    url = _build_orders_url(base_url=base_url, orders_path=orders_path)
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = cast(dict[str, JsonValue], order.model_dump(exclude_none=True))

    try:
        async with httpx.AsyncClient(timeout=timeout_seconds) as client:
            response = await client.post(url, json=payload, headers=headers)
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
