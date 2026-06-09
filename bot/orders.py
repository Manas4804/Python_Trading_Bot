"""Order placement logic for Binance Futures Testnet orders."""

from __future__ import annotations

from typing import Any

from bot.client import BinanceFuturesClient
from bot.validators import OrderRequest


def place_order(
    client: BinanceFuturesClient,
    order_request: OrderRequest,
) -> dict[str, Any]:
    """Place an order using a validated order request."""
    api_order_type = _to_binance_order_type(order_request.order_type)

    return client.place_order(
        symbol=order_request.symbol,
        side=order_request.side,
        order_type=api_order_type,
        quantity=order_request.quantity,
        price=(
            order_request.price
            if order_request.order_type in {"LIMIT", "STOP_LIMIT"}
            else None
        ),
        stop_price=order_request.stop_price
        if order_request.order_type in {"STOP_MARKET", "STOP_LIMIT"}
        else None,
    )


def _to_binance_order_type(order_type: str) -> str:
    """Map CLI order type names to Binance Futures API order type names."""
    if order_type == "STOP_LIMIT":
        return "STOP"
    return order_type
