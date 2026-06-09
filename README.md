# Binance Futures Testnet Trading Bot

A production-quality Python command-line trading bot for the Binance USD-M
Futures Testnet. The bot places signed testnet orders through Binance's REST
API, validates all CLI inputs before submission, logs API activity safely, and
handles Binance, network, authentication, and unexpected errors gracefully.

This project was built for a Python Developer Intern assignment.

## Project Highlights

- Direct Binance Futures Testnet REST integration using `requests`
- HMAC SHA256 request signing
- `.env`-based credential loading with `python-dotenv`
- `argparse` command-line interface
- MARKET, LIMIT, STOP_MARKET, and STOP_LIMIT order support
- STOP_LIMIT CLI support mapped to Binance Futures API order type `STOP`
- User-friendly validation and error messages
- Rotating file logs plus console logging
- API request/response logging with sanitized sensitive values
- Clean modular project structure with type hints and module docstrings

## Project Structure

```text
trading_bot/
├── bot/
│   ├── __init__.py
│   ├── client.py          # Binance Futures Testnet API client wrapper
│   ├── orders.py          # Order placement logic
│   ├── validators.py      # Input validation logic
│   └── logging_config.py  # Logging setup
├── cli.py                 # CLI entry point
├── logs/                  # Auto-created at runtime
├── README.md
└── requirements.txt
```

## Requirements

- Python 3.x
- pip
- Binance Futures Testnet or Demo Trading API credentials

## Installation

Clone the repository:

```bash
git clone <your-repository-url>
cd trading_bot
```

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Environment Variables

Create a `.env` file in the `trading_bot` directory:

```env
BINANCE_API_KEY=your_testnet_api_key
BINANCE_API_SECRET=your_testnet_api_secret
```

Never commit `.env` to GitHub. The included `.gitignore` excludes it.

## Getting Binance Futures Testnet Credentials

1. Open Binance Demo Trading API management:
   https://demo.binance.com/en/my/settings/api-management
2. Create a new API key for the testnet/demo environment.
3. Enable futures trading permissions for the key.
4. If IP restrictions are enabled, whitelist the machine running this bot.
5. Copy the API key and API secret into `.env`.

The bot is configured for this Futures Testnet base URL:

```text
https://testnet.binancefuture.com
```

## Usage

Run all commands from the `trading_bot` directory.

### MARKET Order

```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

### LIMIT Order

```bash
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 30000
```

### STOP_MARKET Order

```bash
python cli.py --symbol BTCUSDT --side SELL --type STOP_MARKET --quantity 0.001 --stop-price 29000
```

### STOP_LIMIT Order

```bash
python cli.py --symbol BTCUSDT --side SELL --type STOP_LIMIT --quantity 0.001 --price 28950 --stop-price 29000
```

## Example Terminal Output

Before placing an order, the bot prints a request summary:

```text
─────────────────────────────
Order Request Summary
─────────────────────────────
Symbol   : BTCUSDT
Side     : BUY
Type     : LIMIT
Quantity : 0.002
Price    : 30000
─────────────────────────────
```

After a successful order, it prints the Binance response summary:

```text
─────────────────────────────
Order Response
─────────────────────────────
Order ID     : 123456789
Symbol       : BTCUSDT
Status       : NEW
Side         : BUY
Type         : LIMIT
Orig Qty     : 0.0020
Executed Qty : 0.0000
Avg Price    : N/A
─────────────────────────────
✅ Order placed successfully!
```

On failure:

```text
❌ Order failed: code -1121: Invalid symbol.
```

## Validation Rules

The CLI validates inputs before sending any API request:

- `--symbol` must be a non-empty uppercase string, for example `BTCUSDT`.
- `--side` accepts `BUY` or `SELL`, case-insensitive.
- `--type` accepts `MARKET`, `LIMIT`, `STOP_MARKET`, or `STOP_LIMIT`,
  case-insensitive.
- `--quantity` must be a positive number.
- `--price` must be positive and is required for `LIMIT` and `STOP_LIMIT`.
- `--stop-price` must be positive and is required for `STOP_MARKET` and
  `STOP_LIMIT`.
- If `--price` is supplied for a `MARKET` order, the bot warns that it will be
  ignored.

Invalid input exits with code `1` and a clear user-facing message.

## Error Handling

The bot handles:

- Missing or invalid CLI arguments
- Missing `.env` credentials
- Binance authentication failures
- Binance API errors such as invalid symbol, bad parameters, insufficient
  margin, or minimum notional failures
- Network and timeout errors with one retry after 2 seconds
- Unexpected exceptions with full traceback logging

## Logging

Logs are written to:

```text
logs/trading_bot.log
```

The `logs/` directory is created automatically at runtime.

Logging behavior:

- Console logging: INFO-level user-facing messages
- File logging: DEBUG-level detailed logs
- Rotating file handler: 5 MB max file size, 3 backups
- Request logs include method, endpoint, and sanitized parameters
- Response logs include status code and response body truncated after 500
  characters
- API secrets are never logged

## Testing Performed

The project was checked with:

```bash
python3 -B -c "import cli; import bot.client; import bot.orders; import bot.validators; import bot.logging_config; print('imports OK')"
```

Manual CLI validation tests covered:

- Missing required arguments
- Invalid side
- Invalid order type
- Non-positive quantity
- Missing LIMIT price
- Missing STOP_MARKET and STOP_LIMIT stop price
- MARKET order with ignored price warning
- Signed Binance API error parsing with an invalid symbol
- Successful Binance Futures Testnet LIMIT order placement after account funding

## Assignment Requirement Coverage

| Requirement | Status |
| --- | --- |
| Python 3 project | Complete |
| Mandatory folder structure | Complete |
| Binance Futures Testnet base URL | Complete |
| `.env` credential loading | Complete |
| `argparse` CLI | Complete |
| MARKET and LIMIT orders | Complete |
| STOP_MARKET bonus | Complete |
| STOP_LIMIT bonus | Complete |
| Friendly validation errors | Complete |
| Request and response terminal summaries | Complete |
| Rotating file logging | Complete |
| Sanitized API request logging | Complete |
| Binance API error parsing | Complete |
| Network retry once after 2 seconds | Complete |
| Type hints and module docstrings | Complete |
| README and requirements file | Complete |

## Security Notes

- API keys are loaded from `.env`; they are not hardcoded.
- `.env` is ignored by Git and should never be committed.
- Logs redact request signatures and never include the API secret.
- This bot is configured for Binance Futures Testnet only.

## Assumptions and Known Limitations

- This project places orders only; it does not manage leverage, margin mode,
  balances, or open positions.
- Exchange-specific precision, tick size, lot size, and notional checks are
  delegated to Binance and displayed from the API response.
- `STOP_LIMIT` is a CLI convenience name; Binance receives API order type
  `STOP`.
- Commands in this README use `python`; on systems where only `python3` is
  available, use `python3 cli.py ...`.
