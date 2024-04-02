import time
from datetime import datetime
from decimal import ROUND_DOWN, ROUND_HALF_UP, Decimal
from typing import Any, Dict, Literal

from alpaca.common import RawData
from alpaca.trading.client import TradingClient
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.trading.models import Order
from alpaca.trading.requests import (
    LimitOrderRequest,
    MarketOrderRequest,
    OrderRequest,
)
from chalicelib.src.aws.aws_constants import dynamodb_table_names_instance
from chalicelib.src.aws.aws_utils import save_CGT_amount_to_dynamoDB
from chalicelib.src.constants import (
    capital_gains_tax_rate,
    capital_to_deploy_percentage,
    local_tz,
)
from chalicelib.src.exchanges.alpaca.alpaca_account_utils import (
    alpaca_get_account_balance,
    alpaca_get_available_asset_balance,
    alpaca_get_credentials,
)
from chalicelib.src.exchanges.alpaca.alpaca_constants import (
    alpaca_tolerated_aftermarket_slippage,
    alpaca_trading_account_name_live,
    alpaca_tradingview_inverse_pairs,
    alpaca_tradingview_symbols,
)
from chalicelib.src.exchanges.alpaca.alpaca_order_history_utils import (
    alpaca_check_last_filled_order_type,
)
from chalicelib.src.exchanges.alpaca.alpaca_orders_helper import (
    alpaca_are_holdings_closed,
    alpaca_calculate_profit_loss,
    alpaca_get_latest_quote,
    alpaca_is_asset_fractionable,
)
from chalicelib.src.exchanges.alpaca.alpaca_types import (
    AlpacaAccountCredentials,
    AlpacaGetLatestQuote,
)
from chalicelib.src.exchanges.exchanges_utils import (
    is_outside_nasdaq_trading_hours,
    log_times_in_new_york_and_local_timezone,
)

# TO DO ADD PRINT TIMES IN NEW YORK AND BERLIN TO THIS FUNCTION ALONG WITH
# EACH TYPE OF ORDER TO THE TOP SO WE CAN SEE WHAT IS ADDED TO THE LOGS FOR
# EASIER TROUBLESHOOTING EG> SUBMIT PAIR TRADE ORDER AND PRINT TIMES

# TO DO - Refactor and add tests
# TO DO - Check all types
# TO DO - Improve error logs


def alpaca_submit_pair_trade_order(
    tradingview_symbol: str,
    capital_to_deploy: Decimal = capital_to_deploy_percentage,
    calculate_tax: bool = True,
    buy_alert: bool = True,
    account: str = alpaca_trading_account_name_live,
):
    print("Alpaca Order Begin - alpaca_submit_pair_trade_order")
    log_times_in_new_york_and_local_timezone()

    # Check if there is an inverse order open
    alpaca_symbol: str = (
        alpaca_tradingview_symbols[tradingview_symbol]
        if buy_alert
        else alpaca_tradingview_inverse_pairs[tradingview_symbol]
    )
    alpaca_inverse_symbol: str = (
        alpaca_tradingview_inverse_pairs[tradingview_symbol]
        if buy_alert
        else alpaca_tradingview_symbols[tradingview_symbol]
    )

    isOutsideNormalTradingHours: bool = is_outside_nasdaq_trading_hours()

    # If there is no sell order found for inverse pair symbol,
    # sell all holdings of the inverse pair and save CGT to DynamoDB
    # Assumes there is only one order open at a time
    if (
        alpaca_check_last_filled_order_type(
            symbol=alpaca_inverse_symbol, account=account
        )
        == OrderSide.BUY
    ):
        if isOutsideNormalTradingHours:
            asset_balance: float | Any = alpaca_get_available_asset_balance(
                alpaca_inverse_symbol
            )["position_qty"]
            alpaca_submit_limit_order_custom_quantity(
                alpaca_inverse_symbol,
                asset_balance,
                buy_side_order=False,
                setSlippagePercentage=alpaca_tolerated_aftermarket_slippage,
            )
        else:
            alpaca_close_all_holdings_of_asset(alpaca_inverse_symbol, account)

        # Wait for up to 10 seconds for holdings to close
        timeout: int = 10  # timeout in seconds
        start_time: float = time.time()
        while time.time() - start_time < timeout:
            if alpaca_are_holdings_closed(alpaca_inverse_symbol, account):
                break
            time.sleep(1)  # Wait for 1 second before checking again

        # Calculate and save tax, if applicable
        if calculate_tax:
            profit_loss_amount: Decimal = alpaca_calculate_profit_loss(
                alpaca_inverse_symbol, account
            )
            tax_amount: Decimal = Decimal(profit_loss_amount) * Decimal(
                capital_gains_tax_rate
            )
            print("tax_amount", profit_loss_amount, "\n")

            if tax_amount > 0:
                timestamp: str = datetime.now(local_tz).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                save_CGT_amount_to_dynamoDB(
                    asset=alpaca_inverse_symbol,
                    profit=tax_amount,
                    transaction_date=timestamp,
                    table_name=dynamodb_table_names_instance.alpaca_markets_profits,  # noqa: E501
                )

    (
        alpaca_submit_limit_order_custom_percentage(
            alpaca_symbol,
            True,
            capital_percentage_to_deploy=capital_to_deploy,
            account=account,
            setSlippagePercentage=alpaca_tolerated_aftermarket_slippage,
        )
        if isOutsideNormalTradingHours
        else alpaca_submit_market_order_custom_percentage(  # noqa: E501
            alpaca_symbol,
            True,
            capital_percentage_to_deploy=capital_to_deploy,
            account=account,
        )
    )


# Submit a limit order for the custom quantity of a stock
def alpaca_submit_limit_order_custom_quantity(
    alpaca_symbol: str,
    quantity: float,
    limit_price: Decimal = None,
    buy_side_order: bool = True,
    account: str = alpaca_trading_account_name_live,
    time_in_force: TimeInForce = TimeInForce.DAY,
    setSlippagePercentage: Decimal = 0,
) -> None:
    print("Alpaca Order Begin - alpaca_submit_limit_order_custom_quantity")
    log_times_in_new_york_and_local_timezone()
    credentials: AlpacaAccountCredentials | None = alpaca_get_credentials(
        account
    )

    if credentials:
        trading_client: TradingClient = TradingClient(
            api_key=credentials["key"],
            secret_key=credentials["secret"],
            paper=credentials["paper"],
        )

        # Check if the asset is fractionable
        fractionable: bool = alpaca_is_asset_fractionable(
            alpaca_symbol, account
        )

        # Set the default limit price using the latest quote
        if limit_price is None:
            latest_quote: AlpacaGetLatestQuote | Dict[str, str] = (
                alpaca_get_latest_quote(alpaca_symbol, account)
            )
            if buy_side_order:
                quote_price: Decimal = (
                    Decimal(latest_quote["ask_price"])
                    if latest_quote["ask_price"] != Decimal(0)
                    else Decimal(latest_quote["bid_price"])
                )
                limit_price = Decimal(
                    Decimal(quote_price)
                    + (Decimal(quote_price) * Decimal(setSlippagePercentage))
                ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            else:
                quote_price: Decimal = (
                    Decimal(latest_quote["bid_price"])
                    if latest_quote["bid_price"] != Decimal(0)
                    else Decimal(latest_quote["ask_price"])
                )
                limit_price = Decimal(
                    Decimal(quote_price)
                    + (Decimal(quote_price) * Decimal(setSlippagePercentage))
                ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        # Set the order side
        order_side: OrderSide = "buy" if buy_side_order else "sell"

        # Prepare limit order parameters
        if fractionable:
            order_request: LimitOrderRequest = LimitOrderRequest(
                symbol=alpaca_symbol,
                notional=round(Decimal(quantity) * limit_price, 2),
                side=order_side,
                time_in_force=time_in_force,
                limit_price=limit_price,
            )
        else:
            order_request: LimitOrderRequest = LimitOrderRequest(
                symbol=alpaca_symbol,
                qty=Decimal(quantity).quantize(
                    Decimal("1"), rounding=ROUND_DOWN
                ),
                side=order_side,
                time_in_force=time_in_force,
                limit_price=limit_price,
            )

        # Create and submit the limit order
        try:
            order_response: Order | RawData = trading_client.submit_order(
                order_request
            )
            print(f"Limit {order_side} order submitted: \n", order_response)
        except Exception as e:
            print(f"An error occurred while submitting the order: {e}")


# Submit limit order based on custom percentage of entire portfolio value
def alpaca_submit_limit_order_custom_percentage(
    alpaca_symbol: str,
    buy_side_order: bool = True,
    capital_percentage_to_deploy: float = 1.0,
    account: str = alpaca_trading_account_name_live,
    time_in_force: TimeInForce = TimeInForce.DAY,
    limit_price: Decimal = None,
    setSlippagePercentage: Decimal = 0,
) -> None:
    print("Alpaca Order Begin - alpaca_submit_limit_order_custom_percentage")
    log_times_in_new_york_and_local_timezone()
    credentials: AlpacaAccountCredentials | None = alpaca_get_credentials(
        account
    )

    if credentials:
        trading_client: TradingClient = TradingClient(
            api_key=credentials["key"],
            secret_key=credentials["secret"],
            paper=credentials["paper"],
        )

        account_info: dict[str, Any] | Literal["Account not found"] = (
            alpaca_get_account_balance(account_name=account)
        )
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
            funds_to_deploy: Decimal = Decimal(account_cash)

        if limit_price is None:
            latest_quote: AlpacaGetLatestQuote | Dict[str, str] = (
                alpaca_get_latest_quote(alpaca_symbol, account)
            )
            if buy_side_order:
                quote_price: Decimal = (
                    Decimal(latest_quote["ask_price"])
                    if latest_quote["ask_price"] != Decimal(0)
                    else Decimal(latest_quote["bid_price"])
                )
                limit_price = Decimal(
                    Decimal(quote_price)
                    + (Decimal(quote_price) * Decimal(setSlippagePercentage))
                ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            else:
                quote_price: Decimal = (
                    Decimal(latest_quote["bid_price"])
                    if latest_quote["bid_price"] != Decimal(0)
                    else Decimal(latest_quote["ask_price"])
                )
                limit_price = Decimal(
                    Decimal(quote_price)
                    + (Decimal(quote_price) * Decimal(setSlippagePercentage))
                ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        # Set the order side
        order_side: OrderSide = "buy" if buy_side_order else "sell"

        # Check if asset is fractionable
        fractionable: bool = alpaca_is_asset_fractionable(
            alpaca_symbol, account
        )

        # Prepare order parameters
        if fractionable:
            order_request: LimitOrderRequest = LimitOrderRequest(
                symbol=alpaca_symbol,
                notional=round(funds_to_deploy, 2),
                side=order_side,
                time_in_force=time_in_force,
                limit_price=limit_price,
            )
        else:
            # For non-fractionable assets, calculate quantity using latest
            # quote
            latest_quote: AlpacaGetLatestQuote | Dict[str, str] = (
                alpaca_get_latest_quote(alpaca_symbol, account)
            )
            price: Decimal = Decimal(
                latest_quote["ask_price"]
                if latest_quote["bid_price"] == Decimal(0)
                else latest_quote["bid_price"]
            )
            quantity: Decimal = (
                Decimal(funds_to_deploy)
                * Decimal(
                    0.97
                )  # 3% margin of error for latest quote unreliabiity
            ) / price

            order_request = LimitOrderRequest(
                symbol=alpaca_symbol,
                qty=quantity.quantize(Decimal("1"), rounding=ROUND_DOWN),
                side=order_side,
                time_in_force=time_in_force,
                limit_price=limit_price,
            )

        # Create and submit the limit order
        try:
            order_response: Order | RawData = trading_client.submit_order(
                order_request
            )
            print(f"Limit {order_side} order submitted: \n", order_response)
        except Exception as e:
            print(f"An error occurred while submitting the order: {e}")


# Submit market order based on custom percentage of entire portfolio value
def alpaca_submit_market_order_custom_percentage(
    alpaca_symbol: str,
    buy_side_order: bool = True,
    capital_percentage_to_deploy: float = 1.0,
    account: str = alpaca_trading_account_name_live,
    time_in_force: TimeInForce = TimeInForce.DAY,
) -> None:
    print("Alpaca Order Begin - alpaca_submit_market_order_custom_percentage")
    log_times_in_new_york_and_local_timezone()
    credentials: AlpacaAccountCredentials | None = alpaca_get_credentials(
        account
    )

    if credentials:
        trading_client: TradingClient = TradingClient(
            api_key=credentials["key"],
            secret_key=credentials["secret"],
            paper=credentials["paper"],
        )

        account_info: dict[str, Any] | Literal["Account not found"] = (
            alpaca_get_account_balance(account_name=account)
        )
        account_equity: Any | str = account_info["account_equity"]
        account_cash: Any | str = account_info["account_cash"]

        # Get account balance
        account_value: Decimal = Decimal(account_equity)
        capital_percentage_to_deploy = Decimal(capital_percentage_to_deploy)
        funds_to_deploy: Decimal = Decimal(
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
        fractionable: bool = alpaca_is_asset_fractionable(
            alpaca_symbol, account
        )

        # Prepare order parameters
        if fractionable:
            # For fractionable assets, use the notional value
            order_request: MarketOrderRequest = MarketOrderRequest(
                symbol=alpaca_symbol,
                notional=round(funds_to_deploy, 2),
                side=order_side,
                time_in_force=time_in_force,
            )
        else:
            # For non-fractionable assets, calculate quantity using latest
            # quote
            latest_quote: AlpacaGetLatestQuote | Dict[str, str] = (
                alpaca_get_latest_quote(alpaca_symbol, account)
            )
            price: Decimal = Decimal(
                latest_quote["ask_price"]
                if latest_quote["bid_price"] == Decimal(0)
                else latest_quote["bid_price"]
            )
            quantity: Decimal = (
                Decimal(funds_to_deploy)
                * Decimal(
                    0.97
                )  # 3% margin of error for latest quote unreliabiity
            ) / price

            order_request: MarketOrderRequest = MarketOrderRequest(
                symbol=alpaca_symbol,
                qty=quantity.quantize(Decimal("1"), rounding=ROUND_DOWN),
                side=order_side,
                time_in_force=time_in_force,
            )

        # Create and submit the market order
        try:
            order_response: Order | RawData = trading_client.submit_order(
                order_request
            )
            print(f"Market {order_side} order submitted: \n", order_response)
        except Exception as e:
            print(f"An error occurred while submitting the order: {e}")


# Submit a market order with a custom $ amount
def alpaca_submit_market_order_custom_amount(
    alpaca_symbol: str,
    dollar_amount: float,
    buy_side_order: bool = True,
    account: str = alpaca_trading_account_name_live,
    time_in_force: TimeInForce = TimeInForce.DAY,
) -> None:
    print("Alpaca Order Begin - alpaca_submit_market_order_custom_amount")
    log_times_in_new_york_and_local_timezone()
    credentials: AlpacaAccountCredentials | None = alpaca_get_credentials(
        account
    )

    if credentials:
        trading_client: TradingClient = TradingClient(
            api_key=credentials["key"],
            secret_key=credentials["secret"],
            paper=credentials["paper"],
        )

        # Check if asset is fractionable
        fractionable: bool = alpaca_is_asset_fractionable(
            alpaca_symbol, account
        )

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
            latest_quote: AlpacaGetLatestQuote | Dict[str, str] = (
                alpaca_get_latest_quote(alpaca_symbol, account)
            )
            price: Decimal = Decimal(
                latest_quote["ask_price"]
                if latest_quote["bid_price"] == Decimal(0)
                else latest_quote["bid_price"]
            )

            quantity: Decimal = (
                Decimal(funds_to_deploy)
                * Decimal(
                    0.97
                )  # 3% margin of error for latest quote unreliabiity
            ) / price

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


# Sells all holdings of an asset
def alpaca_close_all_holdings_of_asset(
    symbol: str,
    account: str = alpaca_trading_account_name_live,
) -> None:
    print("Alpaca Order Begin - alpaca_close_all_holdings_of_asset")
    log_times_in_new_york_and_local_timezone()
    credentials: AlpacaAccountCredentials | None = alpaca_get_credentials(
        account
    )

    if credentials:
        trading_client: TradingClient = TradingClient(
            api_key=credentials["key"],
            secret_key=credentials["secret"],
            paper=credentials["paper"],
        )

        try:
            trading_client.close_position(symbol)
            print(f"Submitted request to close all holdings of {symbol}")

        except Exception as e:
            print(f"An error occurred: {e}")
