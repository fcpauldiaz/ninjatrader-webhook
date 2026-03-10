from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

JsonPrimitive = str | int | float | bool | None
JsonValue = JsonPrimitive | list["JsonValue"] | dict[str, "JsonValue"]
EmbedPayload = dict[str, JsonValue]


class WebhookPayload(BaseModel):
    content: str | None = None
    embeds: list[EmbedPayload] | None = None

    model_config = ConfigDict(extra="allow")


class TraderPostOrder(BaseModel):
    symbol: str
    side: Literal["buy", "sell"]
    quantity: float = Field(gt=0)
    order_type: str = "market"
    time_in_force: str | None = None
    limit_price: float | None = None
    stop_price: float | None = None
    take_profit_price: float | None = None
    strategy_id: str | None = None
    account_id: str | None = None
    note: str | None = None


class DestinationResult(BaseModel):
    destination: str
    success: bool
    status_code: int | None = None
    error: str | None = None
    response_body: JsonValue | None = None


class WebhookResponse(BaseModel):
    success: bool
    discord: DestinationResult
    traderpost: DestinationResult
    parsed_order: TraderPostOrder | None = None
