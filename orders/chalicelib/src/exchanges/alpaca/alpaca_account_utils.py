from typing import Optional
from chalicelib.src.constants import (
    development_mode,
)
from chalicelib.src.exchanges.alpaca.alpaca_constants import (
    alpaca_accounts,
    alpaca_trading_account_name_paper,
)
from chalicelib.src.exchanges.alpaca.alpaca_types import (
    AlpacaAccountCredentials,
)


def alpaca_get_credentials(
    account_name: str, development_mode_toggle: bool = development_mode
) -> Optional[AlpacaAccountCredentials]:
    """
    Retrieves the account credentials for trading (most likely paper trading
    account or live account)

    Parameters:
    - account_name: The name of the account to trade with
    - development_mode_toggle: Forcely enable development mode

    Returns:
    - A AlpacaAccountCredentials object containing the endpoint, key, secret, and paper,
    to pass to the Bybit SDK API
    """
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
