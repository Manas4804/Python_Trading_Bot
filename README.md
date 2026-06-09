# Binance Futures Testnet Trading Bot

Python CLI for placing signed orders on the Binance USD-M Futures Testnet.
The bot validates requests before sending them, keeps credentials in `.env`,
and writes logs without exposing API secrets.

## Highlights

- MARKET, LIMIT, STOP_MARKET, and STOP_LIMIT order support
- Binance Futures Testnet REST integration with HMAC SHA256 signing
- Input validation for symbol, side, quantity, price, and stop price
- Rotating console/file logging with sensitive values redacted
- Clean CLI structure built with `argparse`

## Tech stack

- Python 3
- `requests`
- `python-dotenv`

## Project structure

```text
trading_bot/
├── bot/
│   ├── __init__.py
│   ├── client.py
│   ├── orders.py
│   ├── validators.py
│   └── logging_config.py
├── cli.py
├── logs/
├── README.md
└── requirements.txt
```

## Getting started

Clone the repo and install dependencies:

```bash
git clone <your-repository-url>
cd trading_bot
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```env
BINANCE_API_KEY=your_testnet_api_key
BINANCE_API_SECRET=your_testnet_api_secret
```

## Getting Binance Futures Testnet API credentials

1. Go to https://testnet.binancefuture.com
2. Click **Create** to register a testnet account
3. Log in and scroll down to the **API Key** tab
4. Click **Generate HMAC_SHA256 Key**
5. Copy both the API Key and Secret Key immediately. The Secret Key is shown only once
6. Paste them into your `.env` file

## Usage

Run commands from the `trading_bot` directory.

### MARKET order

```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

### LIMIT order

```bash
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 30000
```

### STOP_MARKET order

```bash
python cli.py --symbol BTCUSDT --side SELL --type STOP_MARKET --quantity 0.001 --stop-price 29000
```

### STOP_LIMIT order

```bash
python cli.py --symbol BTCUSDT --side SELL --type STOP_LIMIT --quantity 0.001 --price 28950 --stop-price 29000
```

## Behaviour

- `MARKET` orders ignore `--price` if it is passed.
- `STOP_MARKET` and `STOP_LIMIT` require `--stop-price`.
- `STOP_LIMIT` maps to Binance API order type `STOP`.
- The bot is configured for Binance Futures Testnet only.

## Logging

Logs are written to `logs/trading_bot.log`. The directory is created on first
run, and logs rotate automatically.
