import datetime
from decimal import Decimal
from unittest.mock import patch

import pytest
import requests_mock
from chalicelib.src.exchanges.alpaca.alpaca_account_utils import (
    alpaca_get_credentials,
    get_alpaca_account_balance,
)
from chalicelib.src.exchanges.alpaca.alpaca_constants import (
    alpaca_trading_account_name_live,
    alpaca_trading_account_name_paper,
)
from chalicelib.src.exchanges.alpaca.alpaca_types import (
    AlpacaAccountCredentials,
)
from chalicelib.src.exchanges.alpaca.tests.alpaca_mock_data_objects import (
    mock_alpaca_accounts,
)
from click import UUID


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
    result: AlpacaAccountCredentials = alpaca_get_credentials(
        account_name, development_mode_toggle
    )
    assert result == expected


@pytest.fixture
def mock_alpaca_get_credentials(mocker):
    return mocker.patch(
        "chalicelib.src.exchanges.alpaca.alpaca_account_utils.alpaca_get_credentials",
        return_value={
            "key": "dummy_key",
            "secret": "dummy_secret",
            "paper": True,
        },
    )


@pytest.fixture
def mock_last_running_total(mocker):
    return mocker.patch(
        "chalicelib.src.aws.aws_utils.get_last_running_total",
        return_value=Decimal("10"),
    )


@pytest.fixture
def mock_account_response():
    with requests_mock.Mocker() as m:
        m.get(
            "https://paper-api.alpaca.markets/v2/account",
            json={
                "id": str(UUID("4bc7b5f3-32f3-47d6-b686-5442d89cc112")),
                "account_number": "352415595",
                "status": "ACTIVE",
                "crypto_status": "ACTIVE",
                "currency": "USD",
                "buying_power": "50.98",
                "regt_buying_power": "50.98",
                "daytrading_buying_power": "0",
                "non_marginable_buying_power": "50.98",
                "cash": "50.98",
                "accrued_fees": "0",
                "pending_transfer_out": None,
                "pending_transfer_in": "0",
                "portfolio_value": "627.36",
                "pattern_day_trader": False,
                "trading_blocked": False,
                "transfers_blocked": False,
                "account_blocked": False,
                "created_at": datetime.datetime(
                    2023, 12, 2, 12, 22, 5, 708765
                ).isoformat(),
                "trade_suspended_by_user": False,
                "multiplier": "1",
                "shorting_enabled": False,
                "equity": "627.36",
                "last_equity": "627.36",
                "long_market_value": "576.38",
                "short_market_value": "0",
                "initial_margin": "576.38",
                "maintenance_margin": "432.29",
                "last_maintenance_margin": "432.29",
                "sma": "630.94",
                "daytrade_count": 0,
            },
        )
        yield


def test_account_found_correct_balance():
    result = get_alpaca_account_balance()

    assert result["account_equity"] == Decimal("594.90")
    assert result["account_cash"] == Decimal("18.52")
