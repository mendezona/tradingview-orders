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
