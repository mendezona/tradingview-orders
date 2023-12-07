from typing import Dict

from chalicelib.src.exchanges.kucoin.kucoin_types import (
    KucoinAccountCredentials,
)

# Kucoin Credentials
base_url: str = "https://api.kucoin.com"
kucoin_account_names: list[str] = ["main", "sub_account_1", "sub_account_2"]
kucoin_accounts: Dict[str, KucoinAccountCredentials] = {
    kucoin_account_names[0]: {
        "api_key": "<insert>",
        "api_secret": "<insert>",
        "api_passphrase": "<insert>",
    },
    kucoin_account_names[1]: {
        "api_key": "<insert>",
        "api_secret": "<insert>",
        "api_passphrase": "<insert>",
    },
    kucoin_account_names[2]: {
        "api_key": "<insert>",
        "api_secret": "<insert>",
        "api_passphrase": "<insert>",
    },
}

# Trade information
trade_account: str = "trade"
buy: str = "buy"
sell: str = "sell"
tax_pair: str = "USDC-USDT"
preferred_stablecoin: str = "USDT"

# Pairs
tradingview_kucoin_symbols: dict[str, str] = {
    "<insert>": "<insert>",
}

# Inverse pairs
tradingview_kucoin_inverse_pairs: dict[str, str] = {
    "<insert>": "<insert>",
}
