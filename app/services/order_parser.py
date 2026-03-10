from __future__ import annotations

import re
from typing import Literal

from app.models import TraderPostOrder

EXECUTION_PATTERN = re.compile(
    r"\*\*EXECUTION\*\*:\s*(Long|Short)\s+(\d+)\s+(.+?)\s+@\s+([\d.]+)\s*\|\s*Account:\s*(\S+)",
    re.IGNORECASE,
)


def parse_execution_from_content(content: str | None) -> TraderPostOrder | None:
    if content is None or not content.strip():
        return None
    match = EXECUTION_PATTERN.search(content.strip())
    if not match:
        return None
    direction, qty_str, symbol, price_str, _ = match.groups()
    side: Literal["buy", "sell"] = "buy" if direction.lower() == "long" else "sell"
    quantity = float(qty_str)
    price = float(price_str)
    symbol = symbol.strip()
    return TraderPostOrder(
        symbol=symbol,
        side=side,
        quantity=quantity,
        order_type="market",
        limit_price=price,
    )
