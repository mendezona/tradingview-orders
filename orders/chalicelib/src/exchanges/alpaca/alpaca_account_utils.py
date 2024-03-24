from decimal import Decimal
from typing import Any, Literal

from alpaca.common import RawData
from alpaca.trading.client import TradingClient
from alpaca.trading.models import TradeAccount
from chalicelib.src.aws.aws_constants import dynamodb_table_names_instance
from chalicelib.src.aws.aws_utils import get_last_running_total
from chalicelib.src.constants import development_mode
from chalicelib.src.exchanges.alpaca.alpaca_constants import (
    alpaca_accounts,
    alpaca_trading_account_name_live,
    alpaca_trading_account_name_paper,
)
from chalicelib.src.exchanges.alpaca.alpaca_types import (
    AlpacaAccountCredentials,
)


def alpaca_get_credentials(
    account_name: str = alpaca_trading_account_name_live,
    development_mode_toggle: bool = development_mode,
) -> AlpacaAccountCredentials:
    """
    Retrieves the account credentials for trading (most likely paper trading
    account or live account)

    Parameters:
    - account_name: The name of the account to trade with
    - development_mode_toggle: Forcely enable development mode

    Returns:
    - A AlpacaAccountCredentials object containing the endpoint, key, secret,
    and paper,
    to pass to the Bybit SDK API
    """

    account_info: AlpacaAccountCredentials = (
        alpaca_accounts.get(account_name)
        if not development_mode_toggle
        else alpaca_accounts[alpaca_trading_account_name_paper]
    )

    if account_info:
        print("Alpaca account credentials found")
        return AlpacaAccountCredentials(
            endpoint=account_info["endpoint"],
            key=account_info["key"],
            secret=account_info["secret"],
            paper=account_info["paper"],
        )


def get_alpaca_account_balance(
    account_name: str = alpaca_trading_account_name_live,
    development_mode_toggle: bool = development_mode,
) -> dict[str, Any] | Literal["Account not found"]:
    """
    Retrieves the account balance

    Parameters:
    - account_name: The name of the account to trade with
    - development_mode_toggle: Forcely enable development mode

    Returns:
    - A AlpacaAccountCredentials object containing the endpoint, key, secret,
    and paper, to pass to the Alpaca SDK API
    """

    account_credentials: AlpacaAccountCredentials | None = (
        alpaca_get_credentials(account_name)
    )

    if account_credentials:
        trading_client: TradingClient = (
            TradingClient(
                api_key=account_credentials["key"],
                secret_key=account_credentials["secret"],
                paper=account_credentials["paper"],
            )
            if not development_mode_toggle
            else TradingClient(
                api_key=account_credentials["key"],
                secret_key=account_credentials["secret"],
                paper=account_credentials["paper"],
            )
        )

        # Get account details
        account: TradeAccount | RawData = trading_client.get_account()

        last_running_total: Decimal = get_last_running_total(
            table_name=dynamodb_table_names_instance.alpaca_markets_profits
        )

        running_total_of_taxable_profits: Decimal = (
            last_running_total
            if last_running_total is not None
            else Decimal(0)
        )
        equity: Decimal = (
            Decimal(account.equity) - running_total_of_taxable_profits
        )
        cash: Decimal = (
            Decimal(account.cash) - running_total_of_taxable_profits
        )

        print("account", account)
        print("equity:", equity)
        print("cash:", cash)

        return {
            "account": account,
            "account_equity": equity,
            "account_cash": cash,
        }

    print("Account balance not found")
    return "Account balance not found"
