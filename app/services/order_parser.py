from __future__ import annotations

import json
from json import JSONDecodeError
from typing import cast

from pydantic import ValidationError

from app.models import JsonValue, TraderPostOrder


class OrderParsingError(ValueError):
    pass


def parse_order_from_content(content: str | None) -> TraderPostOrder:
    if content is None or content.strip() == "":
        raise OrderParsingError("Payload content is required and must contain JSON order data.")

    try:
        raw_data = json.loads(content)
    except JSONDecodeError as exc:
        raise OrderParsingError(f"Invalid JSON in content: {exc}") from exc

    if not isinstance(raw_data, dict):
        raise OrderParsingError("Order JSON must be an object.")

    typed_data = cast(dict[str, JsonValue], raw_data)
    try:
        return TraderPostOrder.model_validate(typed_data)
    except ValidationError as exc:
        raise OrderParsingError(f"Order validation failed: {exc}") from exc
