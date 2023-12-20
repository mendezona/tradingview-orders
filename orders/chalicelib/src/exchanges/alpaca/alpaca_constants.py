from chalicelib.src.exchanges.alpaca.alpaca_types import (
    AlpacaAccountCredentials,
)

# Alpaca Credentials
alpaca_trading_endpoint: str = "https://api.alpaca.markets"

alpaca_paper_trading_endpoint: str = "https://paper-api.alpaca.markets"

alpaca_trading_account_name_live: str = "live"

alpaca_trading_account_name_paper: str = "paper"

# Testing / Github
alpaca_accounts: dict[str, dict[AlpacaAccountCredentials]] = {
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
        "paper": True,
    },
}


# Pairs
tradingview_alpaca_symbols: dict[str, str] = {
    "<insert>": "<insert>",
}

# Inverse pairs
tradingview_alpaca_inverse_pairs: dict[str, str] = {
    "<insert>": "<insert>",
}
