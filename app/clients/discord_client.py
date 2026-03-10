from __future__ import annotations

from typing import cast

import httpx

from app.models import DestinationResult, JsonValue


def _get_response_body(response: httpx.Response) -> JsonValue:
    content_type = response.headers.get("content-type", "")
    if "application/json" in content_type:
        parsed = response.json()
        return cast(JsonValue, parsed)

    text = response.text
    return text if text else None


async def forward_to_discord(
    webhook_url: str,
    payload: dict[str, JsonValue],
    timeout_seconds: float,
) -> DestinationResult:
    try:
        async with httpx.AsyncClient(timeout=timeout_seconds) as client:
            response = await client.post(webhook_url, json=payload)
        return DestinationResult(
            destination="discord",
            success=response.is_success,
            status_code=response.status_code,
            error=None if response.is_success else f"Discord returned {response.status_code}",
            response_body=_get_response_body(response),
        )
    except httpx.HTTPError as exc:
        return DestinationResult(
            destination="discord",
            success=False,
            status_code=None,
            error=f"Discord request failed: {exc}",
            response_body=None,
        )
