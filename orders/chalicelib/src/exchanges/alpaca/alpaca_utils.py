from decimal import ROUND_DOWN, Decimal
from typing import Any, Literal, Optional

from alpaca.trading.client import TradingClient
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.trading.requests import MarketOrderRequest
from chalicelib.src.constants import development_mode
from chalicelib.src.exchanges.alpaca.alpaca_constants import (
    alpaca_accounts,
    alpaca_trading_account_name_live,
    alpaca_trading_account_name_paper,
)
from chalicelib.src.exchanges.alpaca.alpaca_types import (
    AlpacaAccountCredentials,
)


# Developer function, for testing
def test_alpaca_function(tradingview_symbol):
    submit_market_order_custom_percentage(
        alpaca_symbol=tradingview_symbol,
        buy_side_order=True,
        capital_percentage_to_deploy=0.3,
        account=alpaca_trading_account_name_paper,
    )


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


# Submit market order based on custom percentage
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

        # Check if asset is fractionable
        fractionable: bool = is_asset_fractionable(
            alpaca_symbol, trading_client
        )

        # Get account balance
        account_info: dict[str, Any] | Literal[
            "Account not found"
        ] = get_alpaca_account_balance()
        balance: Decimal = Decimal(account_info["account_cash"])
        capital_percentage_to_deploy = Decimal(
            str(capital_percentage_to_deploy)
        )
        funds_to_deploy: Decimal = (
            balance * capital_percentage_to_deploy
        ).quantize(Decimal("0.01"), rounding=ROUND_DOWN)

        # Check if funds are sufficient
        if funds_to_deploy <= 0:
            print("Insufficient funds to deploy")
            return

        # Set the order side
        order_side = OrderSide.BUY if buy_side_order else OrderSide.SELL

        # Create and submit a market order
        try:
            order_request = MarketOrderRequest(
                symbol=alpaca_symbol,
                notional=round(funds_to_deploy, 2)
                if fractionable
                else int(funds_to_deploy),
                side=order_side,
                time_in_force=time_in_force,
            )
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
            return asset.fractionable
        except Exception as e:
            print(f"Error fetching asset information: {e}")
            return False
