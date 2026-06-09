"""Binance Futures Testnet REST API client wrapper."""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import time
from typing import Any, Mapping
from urllib.parse import urlencode

import requests
from requests import Response
from requests.exceptions import RequestException, Timeout


BASE_URL = "https://testnet.binancefuture.com"
ORDER_ENDPOINT = "/fapi/v1/order"
REQUEST_TIMEOUT_SECONDS = 10
RETRY_DELAY_SECONDS = 2


class BinanceClientError(Exception):
    """Base exception raised for Binance client failures."""


class BinanceAPIError(BinanceClientError):
    """Raised when Binance returns an API error response."""

    def __init__(
        self,
        status_code: int,
        code: int | str | None,
        message: str,
    ) -> None:
        self.status_code = status_code
        self.code = code
        self.message = message
        code_text = f"code {code}, " if code is not None else ""
        super().__init__(
            f"Binance API error ({code_text}status {status_code}): {message}"
        )


class BinanceAuthenticationError(BinanceAPIError):
    """Raised when Binance rejects the API credentials or signature."""


class BinanceNetworkError(BinanceClientError):
    """Raised when the request fails due to network or timeout errors."""


class BinanceFuturesClient:
    """Client for signed Binance Futures Testnet REST requests."""

    def __init__(
        self,
        api_key: str,
        api_secret: str,
        base_url: str = BASE_URL,
        logger: logging.Logger | None = None,
    ) -> None:
        if not api_key:
            raise ValueError("API key cannot be empty.")
        if not api_secret:
            raise ValueError("API secret cannot be empty.")

        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url.rstrip("/")
        self.logger = logger or logging.getLogger("trading_bot")
        self.session = requests.Session()
        self.session.headers.update({"X-MBX-APIKEY": self.api_key})

    def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: str | float,
        price: str | float | None = None,
        stop_price: str | float | None = None,
    ) -> dict[str, Any]:
        """Place a Binance Futures order and return the raw API response."""
        params: dict[str, Any] = {
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "quantity": quantity,
        }

        if price is not None:
            params["price"] = price
        if stop_price is not None:
            params["stopPrice"] = stop_price
        if order_type in {"LIMIT", "STOP"}:
            params["timeInForce"] = "GTC"

        return self._signed_request("POST", ORDER_ENDPOINT, params)

    def _signed_request(
        self,
        method: str,
        endpoint: str,
        params: Mapping[str, Any],
    ) -> dict[str, Any]:
        request_params = dict(params)
        request_params["timestamp"] = int(time.time() * 1000)
        query_string = urlencode(request_params, doseq=True)
        signature = self._sign(query_string)
        signed_params = {**request_params, "signature": signature}

        return self._request_with_retry(method, endpoint, signed_params)

    def _request_with_retry(
        self,
        method: str,
        endpoint: str,
        params: Mapping[str, Any],
    ) -> dict[str, Any]:
        last_error: RequestException | None = None

        for attempt in range(2):
            try:
                return self._send_request(method, endpoint, params)
            except (Timeout, RequestException) as exc:
                last_error = exc
                self.logger.exception(
                    "Network error during %s %s request on attempt %s.",
                    method,
                    endpoint,
                    attempt + 1,
                )
                if attempt == 0:
                    time.sleep(RETRY_DELAY_SECONDS)
                    continue
                break

        raise BinanceNetworkError(
            "Network or timeout error after retry. "
            "Please check your connection and try again."
        ) from last_error

    def _send_request(
        self,
        method: str,
        endpoint: str,
        params: Mapping[str, Any],
    ) -> dict[str, Any]:
        url = f"{self.base_url}{endpoint}"
        sanitized_params = self._sanitize_params(params)
        self.logger.debug(
            "API request: method=%s endpoint=%s params=%s",
            method,
            endpoint,
            sanitized_params,
        )

        response = self.session.request(
            method=method,
            url=url,
            params=params,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        self._log_response(response)

        try:
            response_body = response.json()
        except ValueError:
            response_body = {"msg": response.text}

        if response.status_code >= 400:
            self._raise_api_error(response.status_code, response_body)

        if not isinstance(response_body, dict):
            raise BinanceClientError("Unexpected Binance response format.")

        return response_body

    def _sign(self, payload: str) -> str:
        return hmac.new(
            self.api_secret.encode("utf-8"),
            payload.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    def _sanitize_params(self, params: Mapping[str, Any]) -> dict[str, Any]:
        sanitized = dict(params)
        if "signature" in sanitized:
            sanitized["signature"] = "<redacted>"
        return sanitized

    def _log_response(self, response: Response) -> None:
        body = response.text
        if len(body) > 500:
            body = f"{body[:500]}..."

        self.logger.debug(
            "API response: status_code=%s body=%s",
            response.status_code,
            body,
        )

    def _raise_api_error(self, status_code: int, response_body: Any) -> None:
        code: int | str | None = None
        message = "Unknown Binance API error."

        if isinstance(response_body, dict):
            code = response_body.get("code")
            message = str(response_body.get("msg", message))
        else:
            message = json.dumps(response_body)

        if status_code in {401, 403} or code in {-1022, -2014, -2015}:
            raise BinanceAuthenticationError(status_code, code, message)

        raise BinanceAPIError(status_code, code, message)
