import pytest
from chalicelib.src.exchanges.kucoin.kucoin_utils import (
    get_base_and_quote_currencies,
)


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
