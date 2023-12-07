from typing import Dict

from chalicelib.src.exchanges.kucoin.kucoin_constants import (
    kucoin_account_names,
)
from chalicelib.src.exchanges.kucoin.kucoin_types import (
    KucoinAccountCredentials,
)

mock_kucoin_accounts: Dict[str, KucoinAccountCredentials] = {
    kucoin_account_names[0]: {
        "api_key": "mock_api_key1",
        "api_secret": "mock_api_secret1",
        "api_passphrase": "mock_api_passphrase1",
    },
    kucoin_account_names[1]: {
        "api_key": "mock_api_key2",
        "api_secret": "mock_api_secret2",
        "api_passphrase": "mock_api_passphrase2",
    },
    kucoin_account_names[2]: {
        "api_key": "mock_api_key3",
        "api_secret": "mock_api_secret3",
        "api_passphrase": "mock_api_passphrase3",
    },
}

mock_symbol_list_response: list[dict[str, str]] = [
    {"symbol": "BTCUSDT", "baseIncrement": "0.001", "quoteIncrement": "0.01"},
    {"symbol": "ETHUSDT", "baseIncrement": "0.01", "quoteIncrement": "0.1"},
]

mock_account_list_response: list[dict[str, str]] = [
    {"type": "trade", "balance": "10.0"},
    {"type": "spot", "balance": "20.0"},
]
