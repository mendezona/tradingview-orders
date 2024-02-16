from typing import Any
from chalicelib.src.constants import development_mode
from chalicelib.src.exchanges.bybit.bybit_constants import (
    bybit_key,
    bybit_secret,
    bybit_account_type,
)
from pybit.unified_trading import HTTP


def bybit_get_coin_balance(
    coin: str,
    api_key: str = bybit_key,
    api_secret: str = bybit_secret,
    testnet: bool = development_mode,
) -> Any | str:
    """
    Retrieves the account balance for a specific coin from Bybit.

    Parameters:
    - coin: The coin symbol (e.g., "BTC").
    - api_key: Your Bybit API key.
    - api_secret: Your Bybit API secret.
    - testnet: Boolean indicating whether to use the testnet (default False).

    Returns:
    - The account balance for the specified coin or an error message.
    """
    # Initialize the HTTP client with Bybit's endpoint and your API credentials
    session = HTTP(api_key=api_key, api_secret=api_secret, testnet=testnet)

    # Fetch the wallet balance for the specified coin
    response = session.get_wallet_balance(
        accountType=bybit_account_type, coin=coin
    )
    print("bybit_get_coin_balance response: ", response)

    # Check if the request was successful
    if response["retCode"] == 0:
        for item in response["result"]["list"]:
            for coin_info in item["coin"]:
                if coin_info["coin"] == coin:
                    return coin_info["walletBalance"]
        return f"Coin {coin} balance not found."
    else:
        return f"Error: {response['retMsg']}"
