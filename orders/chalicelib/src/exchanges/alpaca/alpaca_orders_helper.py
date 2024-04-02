from decimal import ROUND_HALF_UP, Decimal
from typing import Any, Dict, List

from alpaca.common import RawData
from alpaca.data import Quote
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.models import BarSet, QuoteSet
from alpaca.data.requests import (
    StockBarsRequest,
    StockLatestQuoteRequest,
    StockQuotesRequest,
)
from alpaca.data.timeframe import TimeFrame
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
    AlpacaGetLatestQuote,
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


# TO DO - Add unit tests
def alpaca_get_latest_quote(
    symbol: str, account: str = alpaca_trading_account_name_live
) -> AlpacaGetLatestQuote | Dict[str, str]:
    """
    Get the latest quote data for an asset, with two additional backup methods

    Parameters:
    - symbol: Symbol to check if asset is fractionable
    - account: Account to use to check if asset if fractionable

    Returns:
    - A AlpacaGetLatestQuote object containing the ask price, bid price, ask
    size, and bid size
    """

    credentials: AlpacaAccountCredentials = alpaca_get_credentials(account)
    print("credentials", credentials)
    if credentials:
        client: StockHistoricalDataClient = StockHistoricalDataClient(
            api_key=credentials["key"], secret_key=credentials["secret"]
        )

        try:
            # Primary method: StockLatestQuoteRequest
            request_params_latest: StockLatestQuoteRequest = (
                StockLatestQuoteRequest(symbol_or_symbols=[symbol])
            )
            latest_quote: Dict[str, Quote] | RawData = (
                client.get_stock_latest_quote(request_params_latest)
            )

            print("latest quote", latest_quote)

            symbol_quote_latest: Quote | Any = latest_quote[symbol]
            if (
                symbol_quote_latest.bid_price > 0
                or symbol_quote_latest.ask_price > 0
            ):
                latest_quote: AlpacaGetLatestQuote = {
                    "ask_price": Decimal(
                        symbol_quote_latest.ask_price
                    ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
                    "bid_price": Decimal(
                        symbol_quote_latest.bid_price
                    ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
                    "ask_size": symbol_quote_latest.ask_size,
                    "bid_size": symbol_quote_latest.bid_size,
                }

                print("Quote Method 1 - Latest quote found:", latest_quote)
                return latest_quote

            # Backup method: StockQuotesRequest
            request_params_quotes: StockQuotesRequest = StockQuotesRequest(
                symbol_or_symbols=[symbol], limit=1
            )
            quotes: QuoteSet | RawData = client.get_stock_quotes(
                request_params_quotes
            )
            quote: Any = quotes[symbol][0]
            if quote.bid_price and quote.ask_price:
                latest_quote: AlpacaGetLatestQuote = {
                    "ask_price": Decimal(quote.ask_price).quantize(
                        Decimal("0.01"), rounding=ROUND_HALF_UP
                    ),
                    "bid_price": Decimal(quote.bid_price).quantize(
                        Decimal("0.01"), rounding=ROUND_HALF_UP
                    ),
                    "ask_size": quote.ask_size,
                    "bid_size": quote.bid_size,
                }

                print(
                    "Quote Method 2 - Latest quote not found, most recent Stock Quote:",  # noqa: E501
                    latest_quote,
                )
                return latest_quote

            # Secondary backup: StockBarsRequest
            bar_request_params: StockBarsRequest = StockBarsRequest(
                symbol_or_symbols=[symbol], timeframe=TimeFrame.Minute, limit=1
            )
            bars: BarSet | RawData = client.get_stock_bars(bar_request_params)
            bar: Any = bars[symbol][0]
            latest_quote: AlpacaGetLatestQuote = {
                "ask_price": Decimal(bar.close).quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP
                ),
                "bid_price": Decimal(bar.close).quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP
                ),
                "close_price": Decimal(bar.close),
                "volume": bar.volume,
            }

            print(
                "Quote Method 3 - Quote not found, latest historical bar close minute price:",  # noqa: E501
                latest_quote,
            )
            return latest_quote

        except Exception as e:
            print(f"An error occurred while fetching data for {symbol}: {e}")
            return {"error": str(e)}

    else:
        print("No credentials available.")
        return {"error": "No credentials"}


# TO DO: ADD DESCRIPTION AND TESTS
def alpaca_are_holdings_closed(
    symbol: str,
    account: str = alpaca_trading_account_name_live,
) -> bool:
    credentials: AlpacaAccountCredentials | None = alpaca_get_credentials(
        account
    )

    if credentials:
        trading_client = TradingClient(
            api_key=credentials["key"],
            secret_key=credentials["secret"],
            paper=credentials["paper"],
        )

        try:
            # Fetch the list of open positions
            open_positions = trading_client.get_all_positions()

            # Check if the specified symbol is in the list of open positions
            for position in open_positions:
                if position.symbol == symbol and float(position.qty) > 0:
                    return (
                        False  # There are still open positions for this symbol
                    )

            return True  # No open positions found for this symbol

        except Exception as e:
            print(
                f"An error occurred while checking holdings for {symbol}: {e}"
            )
            return False  # Assume holdings are not closed in case of error

    else:
        print("No credentials available.")
        return False  # Cannot check without credentials
