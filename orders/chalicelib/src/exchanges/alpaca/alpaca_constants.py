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
        "key": "AKDAJQ0U9SY7KMUJMT4J",
        "secret": "vKaqYxPoN7N3j3YcnlMvuedQuzHqY1Jz4tPl92J9",
        "paper": False,
    },
    alpaca_trading_account_name_paper: {
        "endpoint": alpaca_paper_trading_endpoint,
        "key": "PK2CINT9YPZTHZVNONEO",
        "secret": "XqeVqCpbf0P0c8tef62Qdfu11ZdmUGRCVEfQuiCA",
        "paper": True,
    },
}

# Pairs
tradingview_alpaca_symbols: dict[str, str] = {
    "TSLT": "TSLT",
    "TSLZ": "TSLZ",
    "FNGU": "FNGU",
    "FNGD": "FNGD",
    "SOXL": "SOXL",
    "SOXS": "SOXS",
}

# Inverse pairs
tradingview_alpaca_inverse_pairs: dict[str, str] = {
    "TSLT": "TSLZ",
    "TSLZ": "TSLT",
    "FNGU": "FNGD",
    "FNGD": "FNGU",
    "SOXL": "SOXS",
    "SOXS": "SOXL",
}
