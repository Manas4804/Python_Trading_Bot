"""Command-line interface for placing Binance Futures Testnet orders."""

from __future__ import annotations

import argparse
import logging
import os
import sys
from pathlib import Path
from typing import Any, Sequence

from dotenv import load_dotenv

from bot.client import (
    BinanceAPIError,
    BinanceAuthenticationError,
    BinanceFuturesClient,
    BinanceNetworkError,
)
from bot.logging_config import setup_logging
from bot.orders import place_order
from bot.validators import (
    OrderRequest,
    ValidationError,
    validate_order_request,
)


SEPARATOR = "─" * 29
MARKET_PRICE_WARNING = (
    "⚠️  Price was provided for a MARKET order and will be ignored."
)
STOP_PRICE_WARNING = (
    "⚠️  Stop price was provided for this order type and will be ignored."
)


class FriendlyArgumentParser(argparse.ArgumentParser):
    """Argument parser that prints friendly errors and exits with code 1."""

    def error(self, message: str) -> None:
        print(f"❌ Invalid input: {message}", file=sys.stderr)
        print(f"Use --help to see valid options.", file=sys.stderr)
        raise SystemExit(1)


def build_parser() -> argparse.ArgumentParser:
    """Build the trading bot CLI parser."""
    parser = FriendlyArgumentParser(
        description="Place orders on the Binance Futures Testnet (USDT-M)."
    )
    parser.add_argument(
        "--symbol",
        required=True,
        help="Trading symbol, for example BTCUSDT.",
    )
    parser.add_argument(
        "--side",
        required=True,
        help="Order side: BUY or SELL.",
    )
    parser.add_argument(
        "--type",
        required=True,
        dest="order_type",
        help="Order type: MARKET, LIMIT, STOP_MARKET, or STOP_LIMIT.",
    )
    parser.add_argument(
        "--quantity",
        required=True,
        help="Positive order quantity.",
    )
    parser.add_argument(
        "--price",
        help="Positive limit price. Required for LIMIT/STOP_LIMIT.",
    )
    parser.add_argument(
        "--stop-price",
        dest="stop_price",
        help="Positive trigger price. Required for STOP_MARKET/STOP_LIMIT.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the CLI application."""
    logger = setup_logging()
    parser = build_parser()

    try:
        args = parser.parse_args(argv)
        order_request = validate_order_request(
            symbol=args.symbol,
            side=args.side,
            order_type=args.order_type,
            quantity=args.quantity,
            price=args.price,
            stop_price=args.stop_price,
        )

        if (
            order_request.order_type == "MARKET"
            and order_request.price is not None
        ):
            print(MARKET_PRICE_WARNING)
            logger.warning(
                "Price was provided for a MARKET order and will be ignored."
            )

        if (
            order_request.order_type in {"MARKET", "LIMIT"}
            and order_request.stop_price is not None
        ):
            print(STOP_PRICE_WARNING)
            logger.warning(
                "Stop price was provided for %s and will be ignored.",
                order_request.order_type,
            )

        load_environment()
        api_key = os.getenv("BINANCE_API_KEY", "").strip()
        api_secret = os.getenv("BINANCE_API_SECRET", "").strip()

        if not api_key or not api_secret:
            print(
                "❌ Order failed: Missing BINANCE_API_KEY or "
                "BINANCE_API_SECRET in .env."
            )
            return 1

        print_order_request_summary(order_request)
        client = BinanceFuturesClient(
            api_key=api_key,
            api_secret=api_secret,
            logger=logger,
        )
        response = place_order(client, order_request)
        print_order_response(response)
        print("✅ Order placed successfully!")
        return 0

    except ValidationError as exc:
        logger.exception("Invalid CLI input.")
        print(f"❌ Invalid input: {exc}")
        return 1
    except BinanceAuthenticationError as exc:
        logger.exception("Binance authentication failed.")
        print(
            "❌ Order failed: Authentication error "
            f"({format_api_error(exc)})."
        )
        return 1
    except BinanceAPIError as exc:
        logger.exception("Binance API error.")
        print(f"❌ Order failed: {format_api_error(exc)}.")
        return 1
    except BinanceNetworkError as exc:
        logger.exception("Binance network error.")
        print(f"❌ Order failed: {exc}")
        return 1
    except KeyboardInterrupt:
        print("\n❌ Order failed: Operation cancelled by user.")
        return 1
    except Exception:
        logger.exception("Unexpected error while placing order.")
        print(
            "❌ Order failed: An unexpected error occurred. "
            "Check logs/trading_bot.log for details."
        )
        return 1


def load_environment() -> None:
    """Load environment variables from common .env locations."""
    project_env = Path(__file__).resolve().parent / ".env"
    load_dotenv(project_env)
    load_dotenv()


def print_order_request_summary(order_request: OrderRequest) -> None:
    """Print the order request summary before placing an order."""
    print(SEPARATOR)
    print("Order Request Summary")
    print(SEPARATOR)
    print(f"Symbol   : {order_request.symbol}")
    print(f"Side     : {order_request.side}")
    print(f"Type     : {order_request.order_type}")
    print(f"Quantity : {order_request.quantity}")
    if (
        order_request.price is not None
        and order_request.order_type in {"LIMIT", "STOP_LIMIT"}
    ):
        print(f"Price    : {order_request.price}")
    if (
        order_request.stop_price is not None
        and order_request.order_type in {"STOP_MARKET", "STOP_LIMIT"}
    ):
        print(f"Stop     : {order_request.stop_price}")
    print(SEPARATOR)


def print_order_response(response: dict[str, Any]) -> None:
    """Print a concise Binance order response summary."""
    print(SEPARATOR)
    print("Order Response")
    print(SEPARATOR)
    print(f"Order ID     : {response.get('orderId', 'N/A')}")
    print(f"Symbol       : {response.get('symbol', 'N/A')}")
    print(f"Status       : {response.get('status', 'N/A')}")
    print(f"Side         : {response.get('side', 'N/A')}")
    order_type = response.get("type", response.get("origType", "N/A"))
    print(f"Type         : {order_type}")
    print(f"Orig Qty     : {response.get('origQty', 'N/A')}")
    print(f"Executed Qty : {response.get('executedQty', 'N/A')}")
    print(f"Avg Price    : {response.get('avgPrice', 'N/A')}")
    print(SEPARATOR)


def format_api_error(exc: BinanceAPIError) -> str:
    """Format a Binance API exception for terminal output."""
    if exc.code is not None:
        return f"code {exc.code}: {exc.message}"
    return exc.message


if __name__ == "__main__":
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    sys.exit(main())
