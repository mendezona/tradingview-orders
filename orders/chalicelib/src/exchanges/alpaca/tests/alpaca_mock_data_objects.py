from unittest.mock import MagicMock

from chalicelib.src.exchanges.alpaca.alpaca_types import (
    AlpacaAccountCredentials,
)

mock_account_details = MagicMock()
mock_account_details.equity = 10000
mock_account_details.cash = 5000
mock_credentials = AlpacaAccountCredentials(
    key="test_key", secret="test_secret", paper=True
)
mock_account_info: dict[str, str] = {"account_cash": "10000"}
