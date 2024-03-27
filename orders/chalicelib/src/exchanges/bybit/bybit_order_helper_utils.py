from datetime import timedelta
from decimal import Decimal
from typing import Any, Literal

from chalicelib.src.exchanges.bybit.bybit_account_utils import (
    bybit_get_credentials,
)
from chalicelib.src.exchanges.bybit.bybit_constants import (
    bybit_default_product_category,
    bybit_trading_account_name_live,
)
from chalicelib.src.exchanges.bybit.bybit_types import (
    BybitAccountCredentials,
    BybitGetSymboIncrements,
)
from pybit.unified_trading import HTTP
from requests.structures import CaseInsensitiveDict


def bybit_get_symbol_increments(
    bybit_pair_symbol: str,
    account_name: str = bybit_trading_account_name_live,
    product_category: str = bybit_default_product_category,
) -> BybitGetSymboIncrements | str:
    """
    Retrieves information about required increments for an order

    Parameters:
    - pair_symbol: Pair symbol to search for information without hyphen
    - account_name: Account to use for search
    - product_category: Bybit product to search eg. spot, derivatives, etc

    Returns:
    - A BybitGetSymboIncrements object containing information about the
    increments for an order, or a string with an error
    """

    print("symbol", bybit_pair_symbol)

    # Initialise the HTTP client with Bybit's endpoint and API credentials
    credentials: BybitAccountCredentials = bybit_get_credentials(account_name)
    session: HTTP = HTTP(
        testnet=credentials["testnet"],
        api_key=credentials["api_key"],
        api_secret=credentials["api_secret"],
    )

    # Fetch the instrument information for desired product category
    response: (
        tuple[Any, timedelta, CaseInsensitiveDict[str]]
        | tuple[Any, timedelta]
        | Any
    ) = session.get_instruments_info(
        symbol=bybit_pair_symbol, category=product_category
    )
    print("response", response)

    # Iterate through each trading pair to find the matching symbol
    if response.get("retCode") == 0:
        # Iterate through each trading pair in the provided list
        for trading_pair in response["result"]["list"]:
            # Check if the current trading pair matches the desired symbol
            if trading_pair.get("symbol") == bybit_pair_symbol:
                # If the symbol matches, extract the increments information
                lot_size_filter = trading_pair.get("lotSizeFilter", {})
                price_filter = trading_pair.get("priceFilter", {})

                # Construct a result dictionary with the increments information
                increments: BybitGetSymboIncrements = {
                    "symbol": bybit_pair_symbol,
                    "basePrecision": lot_size_filter.get("basePrecision"),
                    "quotePrecision": lot_size_filter.get("quotePrecision"),
                    "minOrderQty": lot_size_filter.get("minOrderQty"),
                    "maxOrderQty": lot_size_filter.get("maxOrderQty"),
                    "minOrderAmt": lot_size_filter.get("minOrderAmt"),
                    "maxOrderAmt": lot_size_filter.get("maxOrderAmt"),
                    "tickSize": price_filter.get("tickSize"),
                }
                print("Increments found:", increments)
                return increments

        return f"Symbol {bybit_pair_symbol} not found."
    else:
        return f"Error: {response['retMsg']}"


def bybit_calculate_profit_loss(
    bybit_pair_symbol: str,
    account_name: str = bybit_trading_account_name_live,
) -> Decimal:
    """
    Calculates the profit/loss of the last order. Limitation is that last
    order needs to be made in the last 7 days

    Parameters:
    - bybit_pair_symbol: Pair symbol to search for information without hyphen
    - account_name: Account to use for search

    Returns:
    - A Decimal with the profit or loss amount
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
        print("Error - Invalid executed order data")
        return Decimal(0)

    # Filter orders for the specific symbol
    orders = [
        order
        for order in executed_orders["result"]["list"]
        if order["symbol"] == bybit_pair_symbol
    ]
    orders.reverse()

    # Find the last (most recent) order
    last_order = orders[0]  # The first order after reversing the list
    last_order_side = last_order["side"]
    opposite_side: Literal["Sell", "Buy"] = (
        "Sell" if last_order_side == "Buy" else "Buy"
    )

    last_order_qty: Decimal = Decimal(last_order["execQty"])
    last_order_exec_value: Decimal = Decimal(last_order["execValue"])

    total_opposite_qty: Decimal = Decimal(0)
    total_opposite_exec_value: Decimal = Decimal(0)

    for order in orders[1:]:  # Skip the first order since it's the last order
        if order["side"] == opposite_side:
            opposite_qty: Decimal = Decimal(order["execQty"])
            if total_opposite_qty + opposite_qty <= last_order_qty:
                total_opposite_qty += opposite_qty
                total_opposite_exec_value += Decimal(order["execValue"])
            else:
                portion_needed: Decimal = last_order_qty - total_opposite_qty
                total_opposite_qty += portion_needed
                value_portion: Decimal = (
                    portion_needed / opposite_qty * Decimal(order["execValue"])
                )
                total_opposite_exec_value += value_portion

            if total_opposite_qty >= last_order_qty:
                break

    if total_opposite_qty != last_order_qty:
        print(
            "Error - Could not match the last order quantity with opposite side orders"  # noqa: E501
        )
        return Decimal(0)

    profit_or_loss: Decimal = (
        Decimal(last_order_exec_value - total_opposite_exec_value)
        if last_order_side == "Sell"
        else Decimal(total_opposite_exec_value - last_order_exec_value)
    )

    print("Profit/loss:", profit_or_loss)
    return profit_or_loss
