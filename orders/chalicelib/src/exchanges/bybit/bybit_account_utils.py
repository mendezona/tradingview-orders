from chalicelib.src.constants import development_mode
from chalicelib.src.exchanges.bybit.bybit_constants import (
    bybit_account_type,
    bybit_accounts,
    bybit_trading_account_name_live,
    bybit_trading_account_name_paper,
)
from chalicelib.src.exchanges.bybit.bybit_types import BybitAccountCredentials
from pybit.unified_trading import HTTP


def bybit_get_credentials(
    account_name: str = bybit_trading_account_name_live,
    development_mode_toggle: bool = development_mode,
) -> BybitAccountCredentials:
    """
    Retrieves the account credentials for trading (most likely paper trading
    account or live account)

    Parameters:
    - account_name: The name of the account to trade with
    - development_mode_toggle: Forcely enable development mode

    Returns:
    - A BybitAccountCredentials object containing the key, secret, and testnet
    to pass to the Bybit SDK API
    """

    account_info: BybitAccountCredentials = (
        bybit_accounts.get(account_name)
        if not development_mode_toggle
        else bybit_accounts[bybit_trading_account_name_paper]
    )

    if account_info:
        print("Account credentials found")
        return account_info
    else:
        print("Error: Account credentials not found")
        return None


def bybit_get_coin_balance(
    coin: str,
    account_name: str = bybit_trading_account_name_live,
) -> str:
    """
    Retrieves the account balance for a specific coin from Bybit

    Parameters:
    - coin: The coin symbol (e.g., "BTC").
    - api_key: Your Bybit API key.
    - api_secret: Your Bybit API secret.
    - testnet: Boolean indicating whether to use the testnet (default False).

    Returns:
    - The account balance for the specified coin as a string
    or an error message as a string.
    """

    # Initialise the HTTP client with Bybit's endpoint and API credentials
    credentials: BybitAccountCredentials = bybit_get_credentials(account_name)
    session: HTTP = HTTP(
        testnet=credentials["testnet"],
        api_key=credentials["api_key"],
        api_secret=credentials["api_secret"],
    )

    # Fetch the wallet balance for the specified coin
    response = session.get_wallet_balance(
        accountType=bybit_account_type, coin=coin
    )

    if response["retCode"] == 0:
        for item in response["result"]["list"]:
            for coin_info in item["coin"]:
                if coin_info["coin"] == coin:
                    print(coin, "balance:", coin_info["walletBalance"])
                    return coin_info["walletBalance"]
        return f"Coin {coin} balance not found."
    else:
        return f"Error: {response['retMsg']}"
