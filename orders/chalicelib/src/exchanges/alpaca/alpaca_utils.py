from typing import Any, Literal, Optional

from alpaca.trading.client import TradingClient
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
def test_alpaca_function():
    get_alpaca_account_balance()


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
