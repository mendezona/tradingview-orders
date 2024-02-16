import pytest
from chalicelib.src.exchanges.bybit.bybit_account_utils import (
    bybit_get_coin_balance,
)
from chalicelib.src.exchanges.bybit.tests.bybit_mock_data_objects import (
    mock_coin_balance_response,
)


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
    result = bybit_get_coin_balance(
        coin=coin, api_key="dummy_key", api_secret="dummy_secret", testnet=True
    )

    # Assert the expected outcome
    assert result == expected
