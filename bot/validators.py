"""Input validation helpers for order requests."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Optional


SUPPORTED_SIDES = {"BUY", "SELL"}
SUPPORTED_ORDER_TYPES = {"MARKET", "LIMIT", "STOP_MARKET", "STOP_LIMIT"}


class ValidationError(Exception):
    """Raised when user input cannot become a valid order request."""


@dataclass(frozen=True)
class OrderRequest:
    """Validated order request values used by the CLI and order layer."""

    symbol: str
    side: str
    order_type: str
    quantity: str
    price: Optional[str] = None
    stop_price: Optional[str] = None


def validate_symbol(symbol: str | None) -> str:
    """Validate and normalize a Binance futures symbol."""
    if symbol is None or not symbol.strip():
        raise ValidationError("Symbol is required and cannot be empty.")

    normalized = symbol.strip().upper()
    if normalized != symbol.strip():
        raise ValidationError(
            "Symbol must be an uppercase string, for example BTCUSDT."
        )

    if not normalized.isalnum():
        raise ValidationError("Symbol can contain only letters and numbers.")

    return normalized


def validate_side(side: str | None) -> str:
    """Validate and normalize the order side."""
    if side is None or not side.strip():
        raise ValidationError("Side is required. Use BUY or SELL.")

    normalized = side.strip().upper()
    if normalized not in SUPPORTED_SIDES:
        raise ValidationError("Side must be BUY or SELL.")

    return normalized


def validate_order_type(order_type: str | None) -> str:
    """Validate and normalize the order type."""
    if order_type is None or not order_type.strip():
        raise ValidationError(
            "Type is required. Use MARKET, LIMIT, STOP_MARKET, or STOP_LIMIT."
        )

    normalized = order_type.strip().upper()
    if normalized not in SUPPORTED_ORDER_TYPES:
        raise ValidationError(
            "Type must be MARKET, LIMIT, STOP_MARKET, or STOP_LIMIT."
        )

    return normalized


def validate_positive_decimal(
    value: str | float | None,
    field_name: str,
) -> str:
    """Validate a positive decimal value and return it as a plain string."""
    if value is None:
        raise ValidationError(f"{field_name} is required.")

    try:
        decimal_value = Decimal(str(value).strip())
    except (InvalidOperation, AttributeError):
        raise ValidationError(
            f"{field_name} must be a valid positive number."
        ) from None

    if not decimal_value.is_finite() or decimal_value <= 0:
        raise ValidationError(f"{field_name} must be greater than 0.")

    return format(decimal_value, "f")


def validate_order_request(
    symbol: str | None,
    side: str | None,
    order_type: str | None,
    quantity: str | float | None,
    price: str | float | None = None,
    stop_price: str | float | None = None,
) -> OrderRequest:
    """Validate all CLI order inputs and return a normalized request."""
    normalized_type = validate_order_type(order_type)
    normalized_price: Optional[str] = None
    normalized_stop_price: Optional[str] = None

    if normalized_type in {"LIMIT", "STOP_LIMIT"}:
        normalized_price = validate_positive_decimal(price, "Price")
    elif price is not None:
        normalized_price = validate_positive_decimal(price, "Price")

    if normalized_type in {"STOP_MARKET", "STOP_LIMIT"}:
        normalized_stop_price = validate_positive_decimal(
            stop_price,
            "Stop price",
        )
    elif stop_price is not None:
        normalized_stop_price = validate_positive_decimal(
            stop_price,
            "Stop price",
        )

    return OrderRequest(
        symbol=validate_symbol(symbol),
        side=validate_side(side),
        order_type=normalized_type,
        quantity=validate_positive_decimal(quantity, "Quantity"),
        price=normalized_price,
        stop_price=normalized_stop_price,
    )
