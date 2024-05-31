from typing import Any, Dict, List

from alpaca.trading.client import TradingClient
from alpaca.trading.enums import OrderSide, OrderStatus, QueryOrderStatus
from alpaca.trading.models import Order
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


def alpaca_check_last_filled_order_type(
    symbol: str,
    account: str = alpaca_trading_account_name_live,
) -> OrderSide | str:
    """
    Check if last filled order for an asset was a buy or a sell

    Parameters:
    - symbol: The symbol to check if it was a by or sell eg. APPL
    - account: Account to check the history of

    Returns:
    - A an OrderSide object ("buy" or "sell") or string "none"
    """

    credentials: AlpacaAccountCredentials = alpaca_get_credentials(account)
    if credentials:
        trading_client = TradingClient(
            api_key=credentials["key"],
            secret_key=credentials["secret"],
            paper=credentials["paper"],
        )

        # Create filter to get last filled order of an asset
        filters = GetOrdersRequest(
            status=QueryOrderStatus.CLOSED, limit=10, symbols=[symbol]
        )

        # Fetch the list of closed orders for the specified symbol
        closed_orders: List[Order] | Dict[str, Any] = (
            trading_client.get_orders(filters)
        )

        print("Closed orders:", closed_orders)

        # Filter out only filled orders
        filled_orders: List[Order | str] = [
            order
            for order in closed_orders
            if order.status is OrderStatus.FILLED
        ]

        print("Filled orders:", filled_orders)

        # Check if there are any filled orders
        if not filled_orders:
            return "none"

        # Get the most recent filled order
        last_filled_order: Order | str = filled_orders[0]

        # Return 'buy' or 'sell' based on the side of the last filled order
        order_side: OrderSide = (
            OrderSide.BUY
            if last_filled_order.side == OrderSide.BUY
            else OrderSide.SELL
        )

        print("Last order was a", order_side)
        return order_side
