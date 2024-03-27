from unittest.mock import patch

import pytest
from chalicelib.src.exchanges.bybit.bybit_account_utils import (
    bybit_get_coin_balance,
    bybit_get_credentials,
)
from chalicelib.src.exchanges.bybit.bybit_constants import (
    bybit_accounts,
    bybit_trading_account_name_live,
    bybit_trading_account_name_paper,
)
from chalicelib.src.exchanges.bybit.bybit_types import BybitAccountCredentials
from chalicelib.src.exchanges.bybit.tests.bybit_mock_data_objects import (
    mock_bybit_accounts,
    mock_coin_balance_response,
)


@pytest.mark.parametrize(
    "account_name, development_mode_toggle, expected",
    [
        (
            bybit_trading_account_name_live,
            False,
            mock_bybit_accounts[bybit_trading_account_name_live],
        ),
        (
            bybit_trading_account_name_paper,
            True,
            mock_bybit_accounts[bybit_trading_account_name_paper],
        ),
        ("non_existent_account", False, None),
    ],
)
def test_bybit_get_credentials(
    account_name, development_mode_toggle, expected
):
    with patch(
        "chalicelib.src.exchanges.bybit.bybit_constants.bybit_accounts",
        bybit_accounts,
    ):
        # Call the function with the mocked data
        result: BybitAccountCredentials = bybit_get_credentials(
            account_name, development_mode_toggle
        )

        # Check if the function returns the expected result
        assert result == expected


@pytest.mark.parametrize(
    "coin,expected",
    [("USDC", "1.25"), ("USDT", "3.74775")],
)
def test_bybit_get_coin_balance(mocker, coin, expected):
    # Mock the HTTP client's get_wallet_balance method
    mocker.patch(
        "pybit.unified_trading.HTTP.get_wallet_balance",
        return_value=mock_coin_balance_response,
    )

    # Call the function with the mocked response
    result: str = bybit_get_coin_balance(coin=coin)

    # Assert the expected outcome
    assert result == expected
