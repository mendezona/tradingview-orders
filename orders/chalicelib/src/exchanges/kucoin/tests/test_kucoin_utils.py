from unittest.mock import patch

import pytest
from chalicelib.src.exchanges.kucoin.kucoin_constants import (
    kucoin_account_names,
)
from chalicelib.src.exchanges.kucoin.kucoin_utils import (
    get_account_credentials,
    get_available_balance,
    get_base_and_quote_currencies,
    get_symbol_increments,
)
from mock_data_objects import (
    mock_account_list_response,
    mock_kucoin_accounts,
    mock_symbol_list_response,
)


@patch(
    "chalicelib.src.exchanges.kucoin.kucoin_utils.kucoin_accounts",
    mock_kucoin_accounts,
)
def test_get_account_credentials():
    # Call the function with different accounts
    result1 = get_account_credentials(
        kucoin_account_names[0], mock_kucoin_accounts
    )
    result2 = get_account_credentials(
        kucoin_account_names[1], mock_kucoin_accounts
    )
    result3 = get_account_credentials(
        kucoin_account_names[2], mock_kucoin_accounts
    )

    # Assertions
    assert result1 == (
        "mock_api_key1",
        "mock_api_secret1",
        "mock_api_passphrase1",
    )
    assert result2 == (
        "mock_api_key2",
        "mock_api_secret2",
        "mock_api_passphrase2",
    )
    assert result3 == (
        "mock_api_key3",
        "mock_api_secret3",
        "mock_api_passphrase3",
    )

    # Test for an account that doesn't exist
    result_nonexistent = get_account_credentials("nonexistent_account")
    assert result_nonexistent == (None, None, None)


def test_get_available_balance(mocker, capsys):
    # Mock the User class and its get_account_list method
    mocker.patch(
        "chalicelib.src.exchanges.kucoin.kucoin_utils.User.get_account_list",
        return_value=mock_account_list_response,
    )

    # Test for an existing currency (e.g., "BTC")
    available_balance = get_available_balance("BTC")
    captured = capsys.readouterr()
    assert available_balance == "10.0"
    assert "Trading account balance for BTC: 10.0" in captured.out


def test_get_symbol_increments(mocker):
    # Mock the Market class and its get_symbol_list_v2 method
    mocker.patch(
        "chalicelib.src.exchanges.kucoin.kucoin_utils.Market.get_symbol_list_v2",  # noqa
        return_value=mock_symbol_list_response,
    )

    # Test for an existing symbol (BTCUSDT)
    symbol_increments = get_symbol_increments("BTCUSDT")
    assert symbol_increments == ("0.001", "0.01")

    # Test for another existing symbol (ETHUSDT)
    symbol_increments = get_symbol_increments("ETHUSDT")
    assert symbol_increments == ("0.01", "0.1")

    # Test for a non-existing symbol (XYZUSDT)
    symbol_increments = get_symbol_increments("XYZUSDT")
    assert symbol_increments == (None, None)


def test_get_base_and_quote_currencies():
    # Correct symbol format
    kucoin_symbol_correct = "BTC-USDT"
    base_currency, quote_currency = get_base_and_quote_currencies(
        kucoin_symbol_correct
    )
    assert base_currency == "BTC"
    assert quote_currency == "USDT"

    # Incorrect symbol format with lowercase letters
    kucoin_symbol_lowercase = "btc-usdt"
    base_currency, quote_currency = get_base_and_quote_currencies(
        kucoin_symbol_lowercase
    )
    assert base_currency == "BTC"
    assert quote_currency == "USDT"

    # Incorrect symbol format with missing hyphen
    kucoin_symbol_missing_hyphen = "BTCUSDT"
    with pytest.raises(ValueError):
        get_base_and_quote_currencies(kucoin_symbol_missing_hyphen)

    # Incorrect symbol format with extra hyphen
    kucoin_symbol_extra_hyphen = "BTC--USDT"
    with pytest.raises(ValueError):
        get_base_and_quote_currencies(kucoin_symbol_extra_hyphen)

    # Incorrect symbol format with different separator
    kucoin_symbol_different_separator = "BTC_USDT"
    with pytest.raises(ValueError):
        get_base_and_quote_currencies(kucoin_symbol_different_separator)
