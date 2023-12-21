from decimal import ROUND_DOWN, Decimal
from typing import Any, Literal, Optional

from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestQuoteRequest
from alpaca.trading.client import TradingClient
from alpaca.trading.enums import (
    OrderSide,
    OrderStatus,
    QueryOrderStatus,
    TimeInForce,
)
from alpaca.trading.requests import (
    GetOrdersRequest,
    MarketOrderRequest,
    OrderRequest,
)
from chalicelib.src.constants import (
    capital_to_deploy_percentage,
    development_mode,
    tax_rate,
)
from chalicelib.src.exchanges.alpaca.alpaca_constants import (
    alpaca_accounts,
    alpaca_trading_account_name_live,
    alpaca_trading_account_name_paper,
    tradingview_alpaca_inverse_pairs,
    tradingview_alpaca_symbols,
)
from chalicelib.src.exchanges.alpaca.alpaca_types import (
    AlpacaAccountCredentials,
)


# Developer function, for testing
def test_alpaca_function():
    # get_latest_quote(tradingview_symbol)

    # get_available_asset_balance(tradingview_symbol)

    # submit_market_order_custom_percentage(
    #     alpaca_symbol="AAPL",
    #     buy_side_order=False,
    #     capital_percentage_to_deploy=0.05,
    #     account=alpaca_trading_account_name_paper,
    # )

    get_latest_quote(symbol="TSLT", account=alpaca_trading_account_name_paper)

    # close_all_holdings_of_asset(
    #     "AAPL", account=alpaca_trading_account_name_paper
    # )


# Get Alpaca Credentials (usually Live or Paper)
def get_alpaca_credentials(
    account_name: str, development_mode_toggle: bool = development_mode
) -> Optional[AlpacaAccountCredentials]:
    account_info: dict[AlpacaAccountCredentials] = (
        alpaca_accounts.get(account_name)
        if not development_mode_toggle
        else alpaca_accounts[alpaca_trading_account_name_paper]
    )

    if account_info:
        return AlpacaAccountCredentials(
            endpoint=account_info["endpoint"],
            key=account_info["key"],
            secret=account_info["secret"],
            paper=account_info["paper"],
        )
    else:
        return None


# Get current account balance
def get_alpaca_account_balance(
    account_name: str = alpaca_trading_account_name_live,
    development_mode_toggle: bool = development_mode,
) -> dict[str, Any] | Literal["Account not found"]:
    account: AlpacaAccountCredentials | None = get_alpaca_credentials(
        account_name
    )

    if account:
        trading_client = (
            TradingClient(api_key=account["key"], secret_key=account["secret"])
            if not development_mode_toggle
            else TradingClient(
                api_key=account["key"],
                secret_key=account["secret"],
                paper=True,
            )
        )

        # Get account details
        account: Any | AlpacaAccountCredentials | None = (
            trading_client.get_account()
        )

        print("account", account)
        print("equity:", account.equity)
        print("cash:", account.cash)

        return {
            "account": account,
            "account_equity": account.equity,
            "account_cash": account.cash,
        }

    return "Account not found"


# Submit market order for inversely paired assets
def alpaca_submit_pair_trade_order(
    tradingview_symbol,
    capital_to_deploy=capital_to_deploy_percentage,
    calculate_tax=True,
    buy_alert=True,
    account=alpaca_trading_account_name_live,
):
    # Check if there is an inverse order open
    alpaca_symbol = (
        tradingview_alpaca_symbols[tradingview_symbol]
        if buy_alert
        else tradingview_alpaca_inverse_pairs[tradingview_symbol]
    )
    alpaca_inverse_symbol = (
        tradingview_alpaca_inverse_pairs[tradingview_symbol]
        if buy_alert
        else tradingview_alpaca_symbols[tradingview_symbol]
    )

    # If there is no sell order found for inverse pair symbol,
    # sell all holdings of the inverse pair and convert CGT to USDC.
    # Assumes there is only one order open at a time
    if (
        check_last_filled_order_type(
            symbol=alpaca_inverse_symbol, account=account
        )
    ) == OrderSide.BUY:
        close_all_holdings_of_asset(alpaca_inverse_symbol, account)

        # if calculate_tax:
        #     profit_loss_amount = calculate_profit_loss(
        #         kucoin_inverse_symbol, account
        #     )
        #     tax_amount = profit_loss_amount * tax_rate
        #     print("tax_amount", profit_loss_amount, "\n")

        #     if tax_amount > 0:
        #         submit_market_order_custom_amount(
        #             tax_pair, True, tax_amount, account
        #         )

    submit_market_order_custom_percentage(
        alpaca_symbol,
        True,
        capital_percentage_to_deploy=capital_to_deploy,
        account=account,
    )


# Submit market order based on custom percentage of entire portfolio value
def submit_market_order_custom_percentage(
    alpaca_symbol: str,
    buy_side_order: bool = True,
    capital_percentage_to_deploy: float = 1.0,
    account: str = alpaca_trading_account_name_live,
    time_in_force: TimeInForce = TimeInForce.DAY,
) -> None:
    credentials: AlpacaAccountCredentials | None = get_alpaca_credentials(
        account
    )

    if credentials:
        trading_client = TradingClient(
            api_key=credentials["key"],
            secret_key=credentials["secret"],
            paper=credentials["paper"],
        )

        account_info: dict[str, Any] | Literal[
            "Account not found"
        ] = get_alpaca_account_balance(account_name=account)
        account_equity: Any | str = account_info["account_equity"]
        account_cash: Any | str = account_info["account_cash"]

        # Get account balance
        account_value = Decimal(account_equity)
        capital_percentage_to_deploy = Decimal(capital_percentage_to_deploy)
        funds_to_deploy = (
            account_value * capital_percentage_to_deploy
        ).quantize(Decimal("0.01"), rounding=ROUND_DOWN)

        # Check if funds are sufficient
        if funds_to_deploy <= 0:
            print("Insufficient funds to deploy")
            return

        # If funds are less that funds to deploy, deploy all cash
        # Can be useful if funds are still settling
        if funds_to_deploy > Decimal(account_cash):
            funds_to_deploy = Decimal(account_cash)

        # Set the order side
        order_side: OrderSide = "buy" if buy_side_order else "sell"

        # Check if asset is fractionable
        fractionable: bool = is_asset_fractionable(
            alpaca_symbol, trading_client
        )

        # Prepare order parameters
        if fractionable:
            # For fractionable assets, use the notional value
            order_request = MarketOrderRequest(
                symbol=alpaca_symbol,
                notional=round(funds_to_deploy, 2),
                side=order_side,
                time_in_force=time_in_force,
            )
        else:
            # For non-fractionable assets, calculate quantity using latest
            # quote
            latest_quote = get_latest_quote(alpaca_symbol, account)
            price: Decimal = Decimal(
                latest_quote["bid_price"]
                if latest_quote["bid_price"] > 0
                else latest_quote["ask_price"]
            )
            quantity = funds_to_deploy / price

            order_request = MarketOrderRequest(
                symbol=alpaca_symbol,
                qty=quantity.quantize(Decimal("1"), rounding=ROUND_DOWN),
                side=order_side,
                time_in_force=time_in_force,
            )

        # Create and submit the market order
        try:
            order_response = trading_client.submit_order(order_request)
            print(f"Market {order_side} order submitted: \n", order_response)
        except Exception as e:
            print(f"An error occurred while submitting the order: {e}")


# Check if you can buy fractionalable portions of an asset
def is_asset_fractionable(
    symbol: str,
    account: str = alpaca_trading_account_name_live,
) -> bool:
    credentials: AlpacaAccountCredentials | None = get_alpaca_credentials(
        account
    )

    if credentials:
        client = TradingClient(
            api_key=credentials["key"],
            secret_key=credentials["secret"],
            paper=credentials["paper"],
        )
        try:
            asset = client.get_asset(symbol)
            print("asset fractionable: ", asset.fractionable)
            return asset.fractionable
        except Exception as e:
            print(f"Error fetching asset information: {e}")
            return False


# Get the latest quote data for an asset
def get_latest_quote(
    symbol: str, account: str = alpaca_trading_account_name_live
) -> dict:
    credentials: AlpacaAccountCredentials | None = get_alpaca_credentials(
        account
    )

    if credentials:
        client = StockHistoricalDataClient(
            api_key=credentials["key"], secret_key=credentials["secret"]
        )

        try:
            request_params = StockLatestQuoteRequest(
                symbol_or_symbols=[symbol]
            )
            latest_quote = client.get_stock_latest_quote(request_params)
            symbol_quote = latest_quote[symbol]
            print("symbol_quote", symbol_quote)
            print(
                {
                    "ask_price": Decimal(symbol_quote.ask_price),
                    "bid_price": Decimal(symbol_quote.bid_price),
                    "ask_size": symbol_quote.ask_size,
                    "bid_size": symbol_quote.bid_size,
                }
            )
            return {
                "ask_price": Decimal(symbol_quote.ask_price),
                "bid_price": Decimal(symbol_quote.bid_price),
                "ask_size": symbol_quote.ask_size,
                "bid_size": symbol_quote.bid_size,
            }
        except Exception as e:
            print(
                f"An error occurred while fetching the latest quote for {symbol}: {e}"  # noqa: E501
            )
            return {
                "ask_price": Decimal(0),
                "bid_price": Decimal(0),
                "ask_size": 0,
                "bid_size": 0,
            }

    else:
        print("No credentials available.")
        return {
            "ask_price": Decimal(0),
            "bid_price": Decimal(0),
            "ask_size": 0,
            "bid_size": 0,
        }


# Get the amount of assets you own available to trade for one symbol
def get_available_asset_balance(
    symbol: str, account: str = alpaca_trading_account_name_live
) -> Decimal:
    credentials: AlpacaAccountCredentials | None = get_alpaca_credentials(
        account
    )

    if credentials:
        trading_client = TradingClient(
            api_key=credentials["key"],
            secret_key=credentials["secret"],
            paper=credentials["paper"],
        )

        try:
            position = trading_client.get_open_position(symbol)

            print(f"Position for {symbol}: {position}")
            print(f"Quantity of {symbol}: {position.qty}")
            print(f"Market value for {symbol}: {position.market_value}")

            return {
                "position": position,
                "position_qty": position.qty,
                "position_market_value": position.market_value,
            }

        except Exception as e:
            print(f"Error getting position for {symbol}: {e}")

            return None


# Submit a market order with a custom $ amount
def submit_market_order_custom_amount(
    alpaca_symbol: str,
    dollar_amount: float,
    buy_side_order: bool = True,
    account: str = alpaca_trading_account_name_live,
    time_in_force: TimeInForce = TimeInForce.DAY,
) -> None:
    credentials: AlpacaAccountCredentials | None = get_alpaca_credentials(
        account
    )

    if credentials:
        trading_client = TradingClient(
            api_key=credentials["key"],
            secret_key=credentials["secret"],
            paper=credentials["paper"],
        )

        # Check if asset is fractionable
        fractionable: bool = is_asset_fractionable(alpaca_symbol)

        # Convert dollar amount to Decimal
        funds_to_deploy: Decimal = Decimal(dollar_amount).quantize(
            Decimal("0.01"), rounding=ROUND_DOWN
        )

        # Set the order side
        order_side: OrderSide = "buy" if buy_side_order else "sell"

        # Prepare order parameters
        # If fractionable, any amount will be okay rounded to 2 decimals
        if fractionable:
            order_params: OrderRequest = OrderRequest(
                symbol=alpaca_symbol,
                notional=round(funds_to_deploy, 2),
                side=order_side,
                type="market",
                time_in_force=time_in_force,
            )

        # If non fractionable, calculate the quantity available to buy from
        # the fund amount
        else:
            latest_quote = get_latest_quote(alpaca_symbol, account)
            price: Decimal = Decimal(latest_quote["ask_price"])

            quantity: Decimal = funds_to_deploy / price

            order_params: OrderRequest = OrderRequest(
                symbol=alpaca_symbol,
                qty=quantity.quantize(Decimal("1"), rounding=ROUND_DOWN),
                side=order_side,
                type="market",
                time_in_force=time_in_force,
            )

        # Create and submit the market order
        try:
            order_response = trading_client.submit_order(
                order_data=order_params
            )
            print(f"Market {order_side} order submitted: \n", order_response)
        except Exception as e:
            print(f"An error occurred while submitting the order: {e}")


# Find if last order filled order for an asset was buy or a sell
def check_last_filled_order_type(
    symbol: str,
    account: str = alpaca_trading_account_name_live,
) -> str:
    credentials: AlpacaAccountCredentials | None = get_alpaca_credentials(
        account
    )

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
        closed_orders = trading_client.get_orders(filters)

        # Filter out only filled orders
        filled_orders = [
            order
            for order in closed_orders
            if order.status is OrderStatus.FILLED
        ]

        print("filled orders", filled_orders)

        # Check if there are any filled orders
        if not filled_orders:
            return "none"

        # Get the most recent filled order
        last_filled_order = filled_orders[0]

        # Return 'buy' or 'sell' based on the side of the last filled order
        order_side: Literal["buy", "sell"] = (
            "buy" if last_filled_order.side == OrderSide.BUY else "sell"
        )
        print("Last order was a", order_side)
        return order_side


# Sells all holdings of an asset
def close_all_holdings_of_asset(
    symbol: str,
    account: str = alpaca_trading_account_name_live,
) -> None:
    credentials: AlpacaAccountCredentials | None = get_alpaca_credentials(
        account
    )

    if credentials:
        trading_client = TradingClient(
            api_key=credentials["key"],
            secret_key=credentials["secret"],
            paper=credentials["paper"],
        )

        try:
            trading_client.close_position(symbol)
            print(f"Submitted request to close all holdings of {symbol}")

        except Exception as e:
            print(f"An error occurred: {e}")
