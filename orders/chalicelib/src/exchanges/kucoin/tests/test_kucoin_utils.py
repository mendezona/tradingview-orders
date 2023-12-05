import pytest
from chalicelib.src.exchanges.kucoin.kucoin_utils import (
    get_base_and_quote_currencies,
    get_symbol_increments,
)
from mock_data_objects import mock_symbol_list_response


def test_get_symbol_increments(mocker):
    # Mock the Market class and its get_symbol_list_v2 method
    mocker.patch(
        "chalicelib.src.exchanges.kucoin.kucoin_utils.Market.get_symbol_list_v2",
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
