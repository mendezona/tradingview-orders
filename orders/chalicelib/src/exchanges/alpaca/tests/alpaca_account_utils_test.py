import pytest
from chalicelib.src.exchanges.alpaca.alpaca_account_utils import (
    alpaca_get_credentials,
)
from chalicelib.src.exchanges.alpaca.alpaca_constants import (
    alpaca_trading_account_name_live,
    alpaca_trading_account_name_paper,
)
from chalicelib.src.exchanges.alpaca.tests.alpaca_mock_data_objects import (
    mock_alpaca_accounts,
)
from unittest.mock import patch
from chalicelib.src.exchanges.alpaca.alpaca_types import (
    AlpacaAccountCredentials,
)


@pytest.mark.parametrize(
    "account_name, development_mode_toggle, expected",
    [
        (
            alpaca_trading_account_name_live,
            False,
            mock_alpaca_accounts[alpaca_trading_account_name_live],
        ),
        (
            alpaca_trading_account_name_paper,
            True,
            mock_alpaca_accounts[alpaca_trading_account_name_paper],
        ),
        ("non_existent_account", False, None),
    ],
)
@patch(
    "chalicelib.src.exchanges.alpaca.alpaca_account_utils.alpaca_accounts",
    new=mock_alpaca_accounts,
)
def test_alpaca_get_credentials(
    account_name, development_mode_toggle, expected
):
    # Call the function with the mocked data
    result: AlpacaAccountCredentials = alpaca_get_credentials(
        account_name, development_mode_toggle
    )

    # Check if the function returns the expected result
    assert result == expected
