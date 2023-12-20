from typing import Any, Literal
from unittest.mock import MagicMock, patch

import pytest
from chalicelib.src.exchanges.alpaca.alpaca_constants import (
    alpaca_paper_trading_endpoint,
    alpaca_trading_account_name_live,
    alpaca_trading_endpoint,
)
from chalicelib.src.exchanges.alpaca.alpaca_types import (
    AlpacaAccountCredentials,
    MockAsset,
)
from chalicelib.src.exchanges.alpaca.alpaca_utils import (
    get_alpaca_account_balance,
    get_alpaca_credentials,
    is_asset_fractionable,
    submit_market_order_custom_percentage,
)
from chalicelib.src.exchanges.alpaca.tests.alpaca_mock_data_objects import (
    mock_account_details,
    mock_account_info,
    mock_credentials,
)


# tests for get_alpaca_credentials helper function
class TestGetAlpacaCredentials:
    # Test that live trading credentials can be accessed
    def test_get_alpaca_credentials_valid_account(self):
        account_name: str = alpaca_trading_account_name_live
        credentials: AlpacaAccountCredentials | None = get_alpaca_credentials(
            account_name, False
        )
        assert credentials is not None
        assert credentials["endpoint"] == alpaca_trading_endpoint
        assert credentials["key"] == "live_key"
        assert credentials["secret"] == "live_secret"
        assert credentials["paper"] is False

    # Test that credentials cannot be accessed if incorrect
    # account passed
    def test_get_alpaca_credentials_invalid_account(self):
        account_name: str = "non_existing_account"
        credentials: AlpacaAccountCredentials | None = get_alpaca_credentials(
            account_name, False
        )
        assert credentials is None

    # Test that if development is turned on paper
    # trading credentials are accessed
    def test_get_alpaca_credentials_development_mode(self):
        account_name: str = alpaca_trading_account_name_live
        credentials: AlpacaAccountCredentials | None = get_alpaca_credentials(
            account_name, True
        )

        assert credentials["endpoint"] == alpaca_paper_trading_endpoint
        assert credentials["key"] == "paper_key"
        assert credentials["secret"] == "paper_secret"
        assert credentials["paper"] is True


# tests for get_alpaca_account_balance helper function
@pytest.fixture
def mock_trading_client():
    with patch(
        "chalicelib.src.exchanges.alpaca.alpaca_utils.TradingClient"
    ) as mock_client:
        client_instance = MagicMock()
        client_instance.get_account.return_value = mock_account_details
        mock_client.return_value = client_instance
        yield client_instance


class TestGetAlpacaAccountBalance:
    def test_valid_account(self, mock_trading_client):
        account_balance: dict[str, Any] | Literal[
            "Account not found"
        ] = get_alpaca_account_balance()

        # Asserting the structure of the returned data
        assert account_balance["account_equity"] == mock_account_details.equity
        assert account_balance["account_cash"] == mock_account_details.cash


# tests for submit_market_order_custom_amount helper function
@pytest.fixture
def mock_get_alpaca_credentials():
    with patch(
        "chalicelib.src.exchanges.alpaca.alpaca_utils.get_alpaca_credentials",
        return_value=mock_credentials,
    ) as mock:
        yield mock


@pytest.fixture
def mock_get_alpaca_account_balance():
    with patch(
        "chalicelib.src.exchanges.alpaca.alpaca_utils.get_alpaca_account_balance",  # noqa: E501
        return_value=mock_account_info,
    ) as mock:
        yield mock


@pytest.fixture
def mock_is_asset_fractionable():
    with patch(
        "chalicelib.src.exchanges.alpaca.alpaca_utils.is_asset_fractionable",
        return_value=True,
    ) as mock:
        yield mock


class TestSubmitMarketOrderCustomPercentage:
    def test_valid_order(
        self,
        mock_get_alpaca_credentials,
        mock_get_alpaca_account_balance,
        mock_trading_client,
        mock_is_asset_fractionable,
    ):
        submit_market_order_custom_percentage(
            "AAPL", True, 0.5, "test_account"
        )
        mock_trading_client.submit_order.assert_called_once()

    def test_no_credentials(
        self,
        mock_get_alpaca_credentials,
        mock_get_alpaca_account_balance,
        mock_trading_client,
        mock_is_asset_fractionable,
    ):
        mock_get_alpaca_credentials.return_value = None
        submit_market_order_custom_percentage(
            "AAPL", True, 0.5, "test_account"
        )
        mock_trading_client.submit_order.assert_not_called()

    def test_insufficient_funds(
        self,
        mock_get_alpaca_credentials,
        mock_get_alpaca_account_balance,
        mock_trading_client,
        mock_is_asset_fractionable,
    ):
        mock_get_alpaca_account_balance.return_value = {"account_cash": "0"}
        submit_market_order_custom_percentage(
            "AAPL", True, 0.5, "test_account"
        )
        mock_trading_client.submit_order.assert_not_called()

    def test_error_handling(
        self,
        mock_get_alpaca_credentials,
        mock_get_alpaca_account_balance,
        mock_trading_client,
        mock_is_asset_fractionable,
    ):
        mock_trading_client.submit_order.side_effect = Exception("Test error")
        submit_market_order_custom_percentage(
            "AAPL", True, 0.5, "test_account"
        )


# tests for is_asset_fractionable helper function
@pytest.fixture
def mock_trading_client_assets(
    mock_fractionable_asset, mock_non_fractionable_asset
):
    with patch(
        "chalicelib.src.exchanges.alpaca.alpaca_utils.TradingClient"
    ) as mock_client:
        mock_client.return_value.get_asset.side_effect = (
            lambda symbol: mock_fractionable_asset
            if symbol == "AAPL"
            else mock_non_fractionable_asset
        )
        yield mock_client


class TestIsAssetFractionable:
    @pytest.fixture
    def mock_fractionable_asset(self):
        return MockAsset(fractionable=True)

    @pytest.fixture
    def mock_non_fractionable_asset(self):
        return MockAsset(fractionable=False)

    def test_asset_is_fractionable(
        self, mock_get_alpaca_credentials, mock_trading_client_assets
    ):
        assert is_asset_fractionable("AAPL") is True

    def test_asset_is_not_fractionable(
        self, mock_get_alpaca_credentials, mock_trading_client_assets
    ):
        assert is_asset_fractionable("TSLA") is False
