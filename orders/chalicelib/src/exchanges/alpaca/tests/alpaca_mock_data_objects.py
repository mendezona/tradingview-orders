from typing import List
from unittest.mock import MagicMock

from alpaca.trading.models import Order
from chalicelib.src.exchanges.alpaca.alpaca_constants import (
    alpaca_paper_trading_endpoint,
    alpaca_trading_account_name_live,
    alpaca_trading_account_name_paper,
    alpaca_trading_endpoint,
)
from chalicelib.src.exchanges.alpaca.alpaca_types import (
    AlpacaAccountCredentials,
)

# Mock response for bybit_get_credentials
mock_alpaca_accounts: dict[str, dict[AlpacaAccountCredentials]] = {
    alpaca_trading_account_name_live: {
        "endpoint": alpaca_trading_endpoint,
        "key": "live_key",
        "secret": "live_secret",
        "paper": False,
    },
    alpaca_trading_account_name_paper: {
        "endpoint": alpaca_paper_trading_endpoint,
        "key": "paper_key",
        "secret": "paper_secret",
        "paper": False,
    },
}

mock_alpaca_get_stock_latest_quote = MagicMock()
mock_alpaca_get_stock_latest_quote.__getitem__.return_value = {
    "ask_exchange": "V",
    "ask_price": 171.39,
    "ask_size": 3.0,
    "bid_exchange": "V",
    "bid_price": 171.38,
    "bid_size": 1.0,
    "conditions": ["R"],
    "symbol": "AAPL",
    "tape": "C",
}

mock_alpaca_get_stock_quotes = MagicMock()
mock_alpaca_get_stock_quotes.__getitem__.return_value = [
    {
        "ask_exchange": "P",
        "ask_price": 174.37,
        "ask_size": 1.0,
        "bid_exchange": "P",
        "bid_price": 167.06,
        "bid_size": 2.0,
        "conditions": ["R"],
        "symbol": "AAPL",
        "tape": "C",
    }
]

mock_alpaca_get_stock_bars = MagicMock()
mock_alpaca_get_stock_bars.__getitem__.return_value = [
    {
        "close": 172.14,
        "high": 172.2,
        "low": 172.14,
        "open": 172.2,
        "symbol": "AAPL",
        "trade_count": 180.0,
        "volume": 1283.0,
        "vwap": 172.174739,
    }
]


mock_alpaca_get_orders_return: List[Order] = [
    {
        "asset_class": "us_equity",
        "asset_id": "9067979a-40eb-49ef-b8e9-c43fa950e9c7",
        "canceled_at": None,
        "client_order_id": "24e727f3-b07a-45a3-8d1d-51a17c4ef2a1",
        "expired_at": None,
        "extended_hours": False,
        "failed_at": None,
        "filled_avg_price": "39.705",
        "filled_qty": "13",
        "hwm": None,
        "id": "7e7dd7b4-c2fc-4817-ad5b-093b57728d3b",
        "legs": None,
        "limit_price": None,
        "notional": None,
        "order_class": "simple",
        "order_type": "market",
        "qty": "13",
        "replaced_at": None,
        "replaced_by": None,
        "replaces": None,
        "side": "sell",
        "status": "filled",
        "stop_price": None,
        "symbol": "AAPL",
        "time_in_force": "day",
        "trail_percent": None,
        "trail_price": None,
        "type": "market",
    },
]
