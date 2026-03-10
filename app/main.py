from __future__ import annotations

import asyncio
import logging
from typing import cast

from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

from app.clients.discord_client import forward_to_discord
from app.clients.traderpost_client import send_order_to_traderpost
from app.config import get_settings
from app.models import DestinationResult, JsonValue, WebhookPayload, WebhookResponse
from app.services.order_parser import OrderParsingError, parse_order_from_content

app = FastAPI(title="Ninja Webhook Relay")
logger = logging.getLogger(__name__)


@app.on_event("startup")
async def on_startup() -> None:
    settings = get_settings()
    logging.basicConfig(level=settings.log_level)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/webhook", response_model=WebhookResponse)
async def webhook(payload: WebhookPayload) -> JSONResponse:
    settings = get_settings()
    raw_payload = cast(
        dict[str, JsonValue],
        payload.model_dump(mode="json", exclude_none=False),
    )
    logger.info("Incoming payload: %s", raw_payload)

    discord_task = asyncio.create_task(
        forward_to_discord(
            webhook_url=settings.discord_webhook_url,
            payload=raw_payload,
            timeout_seconds=settings.request_timeout_seconds,
        )
    )

    parsed_order = None
    try:
        parsed_order = parse_order_from_content(payload.content)
        traderpost_result = await send_order_to_traderpost(
            base_url=settings.traderpost_base_url,
            orders_path=settings.traderpost_orders_path,
            api_key=settings.traderpost_api_key,
            order=parsed_order,
            timeout_seconds=settings.request_timeout_seconds,
        )
    except OrderParsingError as exc:
        traderpost_result = DestinationResult(
            destination="traderpost",
            success=False,
            status_code=None,
            error=str(exc),
            response_body=None,
        )

    discord_result = await discord_task
    overall_success = discord_result.success or traderpost_result.success

    if discord_result.success and traderpost_result.success:
        response_status = status.HTTP_200_OK
    elif not discord_result.success and not traderpost_result.success:
        response_status = status.HTTP_502_BAD_GATEWAY
    else:
        response_status = status.HTTP_207_MULTI_STATUS

    response_payload = WebhookResponse(
        success=overall_success,
        discord=discord_result,
        traderpost=traderpost_result,
        parsed_order=parsed_order,
    )
    return JSONResponse(
        status_code=response_status,
        content=response_payload.model_dump(mode="json"),
    )
