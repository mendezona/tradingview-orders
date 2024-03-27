from datetime import timedelta
from typing import Any

from chalicelib.src.exchanges.bybit.bybit_account_utils import (
    bybit_get_credentials,
)
from chalicelib.src.exchanges.bybit.bybit_constants import (
    bybit_default_product_category,
    bybit_preferred_stablecoin,
    bybit_trading_account_name_live,
)
from chalicelib.src.exchanges.bybit.bybit_types import BybitAccountCredentials
from pybit.unified_trading import HTTP
from requests.structures import CaseInsensitiveDict


def bybit_get_most_recent_inverse_fill_to_stablecoin(
    bybit_pair_symbol: str,
    stablecoin: str = bybit_preferred_stablecoin,
    account_name: str = bybit_trading_account_name_live,
) -> bool:
    """
    Check if the most recent inverse fill to a stablecoin was a buy or a sell

    Parameters:
    - bybit_pair_symbol: Pair symbol to search for information without hyphen
    - stablecoin: Stablecoin pair to check
    - account_name: Account to trade with

    Returns:
    - A boolean, True if last trade was a sell to a stablecoin
    """

    credentials: BybitAccountCredentials = bybit_get_credentials(account_name)
    session: HTTP = HTTP(
        testnet=credentials["testnet"],
        api_key=credentials["api_key"],
        api_secret=credentials["api_secret"],
    )

    executed_orders: (
        tuple[Any, timedelta, CaseInsensitiveDict[str]]
        | tuple[Any, timedelta]
        | Any
    ) = session.get_executions(
        symbol=bybit_pair_symbol,
        category=bybit_default_product_category,
        limit=10,
    )

    if (
        not executed_orders
        or "result" not in executed_orders
        or "list" not in executed_orders["result"]
        or len(executed_orders["result"]["list"]) == 0
    ):
        return False

    orders = [
        order
        for order in executed_orders["result"]["list"]
        if order["symbol"] == bybit_pair_symbol
    ]
    last_trade = orders[0]
    is_sell_to_stablecoin: bool = (
        last_trade["symbol"].endswith(stablecoin)
        and last_trade["side"] == "Sell"
    )

    print("Last trade was a sell to stablecoin:", is_sell_to_stablecoin)
    return is_sell_to_stablecoin
