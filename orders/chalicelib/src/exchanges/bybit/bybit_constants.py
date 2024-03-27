from chalicelib.src.exchanges.bybit.bybit_types import BybitAccountCredentials

# Bybit Credentials
bybit_trading_account_name_live: str = "live"

bybit_trading_account_name_paper: str = "paper"

bybit_account_type: str = "UNIFIED"

bybit_accounts: dict[str, dict[BybitAccountCredentials]] = {
    bybit_trading_account_name_live: {
        "api_key": "<insert>",
        "api_secret": "<insert>",
        "testnet": False,
    },
    bybit_trading_account_name_paper: {
        "api_key": "<insert>",
        "api_secret": "<insert>",
        "testnet": True,
    },
}

bybit_default_product_category: str = "spot"

# Bybit trading information
bybit_preferred_stablecoin: str = "USDT"

bybit_tax_pair: str = "USDC-USDT"

# Pairs
tradingview_bybit_symbols: dict[str, str] = {
    "<insert>": "<insert>",
}

# Inverse pairs
tradingview_bybit_inverse_symbols: dict[str, str] = {
    "<insert>": "<insert>",
}
