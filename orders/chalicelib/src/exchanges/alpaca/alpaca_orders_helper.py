from decimal import Decimal
from typing import List

from alpaca.common import RawData
from alpaca.trading.client import TradingClient
from alpaca.trading.enums import OrderSide, QueryOrderStatus
from alpaca.trading.models import Asset, Order
from alpaca.trading.requests import GetOrdersRequest
from chalicelib.src.exchanges.alpaca.alpaca_account_utils import (
    alpaca_get_credentials,
)
from chalicelib.src.exchanges.alpaca.alpaca_constants import (
    alpaca_trading_account_name_live,
)
from chalicelib.src.exchanges.alpaca.alpaca_types import (
    AlpacaAccountCredentials,
)


def alpaca_is_asset_fractionable(
    symbol: str,
    account: str = alpaca_trading_account_name_live,
) -> bool:
    """
    Checks if asset is fractionable, or if only whole orders can be submitted

    Parameters:
    - symbol: Symbol to check if asset is fractionable
    - account: Account to use to check if asset if fractionable

    Returns:
    - A Boolean, true being asset is fractionable (eg 0.10 quantity is
    accepted)
    """

    credentials: AlpacaAccountCredentials = alpaca_get_credentials(account)
    if credentials:
        client = TradingClient(
            api_key=credentials["key"],
            secret_key=credentials["secret"],
            paper=credentials["paper"],
        )
        try:
            asset: Asset | RawData = client.get_asset(symbol)
            print("asset fractionable:", asset.fractionable)
            return asset.fractionable
        except Exception as e:
            print(f"Error fetching asset information: {e}")


def alpaca_calculate_profit_loss(
    symbol: str, account: str = alpaca_trading_account_name_live
) -> Decimal:
    """
    Calculate the profit/loss amount on an asset's last trade. Looks at last
    open and close of an asset

    Parameters:
    - symbol: Symbol to check if asset is fractionable
    - account: Account to use to check if asset if fractionable

    Returns:
    - A Decimal, a negative or positive number based on profit or loss
    calculation
    """

    credentials: AlpacaAccountCredentials = alpaca_get_credentials(account)
    trading_client = TradingClient(
        api_key=credentials["key"],
        secret_key=credentials["secret"],
        paper=credentials["paper"],
    )

    # Fetch the most recent orders, considering a reasonable limit
    orders_request = GetOrdersRequest(
        status=QueryOrderStatus.CLOSED, symbols=[symbol], limit=5
    )
    orders: List[Order] = trading_client.get_orders(filter=orders_request)

    # Find the most recent sell order
    recent_sell_order = next(
        (order for order in reversed(orders) if order.side == OrderSide.SELL),
        None,
    )
    if not recent_sell_order:
        raise ValueError("No recent sell order found.")

    sell_quantity_needed = Decimal(recent_sell_order.filled_qty)
    sell_price = Decimal(recent_sell_order.filled_avg_price)
    accumulated_buy_quantity = Decimal("0")
    total_buy_cost = Decimal("0")

    print("ordersordersorders", orders)
    # Accumulate buy orders starting from the most recent
    for order in reversed(orders):
        if order.side == OrderSide.BUY:
            buy_quantity = Decimal(order.filled_qty)
            buy_price = Decimal(order.filled_avg_price)

            # Determine how much of this order to use
            quantity_to_use = min(
                buy_quantity,
                sell_quantity_needed - accumulated_buy_quantity,
            )
            total_buy_cost += quantity_to_use * buy_price
            accumulated_buy_quantity += quantity_to_use

            if accumulated_buy_quantity >= sell_quantity_needed:
                break

    if accumulated_buy_quantity < sell_quantity_needed:
        raise ValueError("Not enough buy orders to match the sell quantity.")

    # Calculate profit or loss
    average_buy_price = total_buy_cost / accumulated_buy_quantity
    profit_loss = (sell_price - average_buy_price) * sell_quantity_needed

    print(f"Profit/loss: {profit_loss}")
    return profit_loss
