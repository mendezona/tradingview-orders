from decimal import Decimal

from chalicelib.src.exchanges.alpaca.alpaca_types import (
    AlpacaAccountCredentials,
)

# Alpaca Credentials
alpaca_trading_endpoint: str = "https://api.alpaca.markets"

alpaca_paper_trading_endpoint: str = "https://paper-api.alpaca.markets"

alpaca_trading_account_name_live: str = "live"

alpaca_trading_account_name_paper: str = "paper"

alpaca_tolerated_aftermarket_slippage: Decimal = 0.06

# Real credentials
alpaca_accounts: dict[str, dict[AlpacaAccountCredentials]] = {
    alpaca_trading_account_name_live: {
        "endpoint": alpaca_trading_endpoint,
        "key": "<insert>",
        "secret": "<insert>",
        "paper": False,
    },
    alpaca_trading_account_name_paper: {
        "endpoint": alpaca_paper_trading_endpoint,
        "key": "<insert>",
        "secret": "<insert>",
        "paper": True,
    },
}

# Pairs
alpaca_tradingview_symbols: dict[str, str] = {
    "<insert>": "<insert>",
}

# Inverse pairs
alpaca_tradingview_inverse_pairs: dict[str, str] = {
    "<insert>": "<insert>",
}
