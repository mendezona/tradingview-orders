from decimal import Decimal
from typing import Any, Literal
from unittest.mock import MagicMock, patch

import pytest
from alpaca.trading.enums import OrderSide, OrderStatus
from chalicelib.src.exchanges.alpaca.alpaca_constants import (
    alpaca_paper_trading_endpoint,
    alpaca_trading_account_name_live,
    alpaca_trading_endpoint,
)
from chalicelib.src.exchanges.alpaca.alpaca_types import (
    AlpacaAccountCredentials,
    MockAsset,
    MockTradingClient,
)
from chalicelib.src.exchanges.alpaca.alpaca_utils import (
    check_last_filled_order_type,
    get_alpaca_account_balance,
    get_alpaca_credentials,
    get_available_asset_balance,
    get_latest_quote,
    is_asset_fractionable,
    submit_market_order_custom_amount,
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


# class TestSubmitMarketOrderCustomPercentage:
#     def test_valid_order(
#         self,
#         mock_get_alpaca_credentials,
#         mock_get_alpaca_account_balance,
#         mock_trading_client,
#         mock_is_asset_fractionable,
#     ):
#         submit_market_order_custom_percentage(
#             "AAPL", True, 0.5, "test_account"
#         )
#         mock_trading_client.submit_order.assert_called_once()

#     def test_no_credentials(
#         self,
#         mock_get_alpaca_credentials,
#         mock_get_alpaca_account_balance,
#         mock_trading_client,
#         mock_is_asset_fractionable,
#     ):
#         mock_get_alpaca_credentials.return_value = None
#         submit_market_order_custom_percentage(
#             "AAPL", True, 0.5, "test_account"
#         )
#         mock_trading_client.submit_order.assert_not_called()

#     def test_insufficient_funds(
#         self,
#         mock_get_alpaca_credentials,
#         mock_get_alpaca_account_balance,
#         mock_trading_client,
#         mock_is_asset_fractionable,
#     ):
#         mock_get_alpaca_account_balance.return_value = {"account_cash": "0"}
#         submit_market_order_custom_percentage(
#             "AAPL", True, 0.5, "test_account"
#         )
#         mock_trading_client.submit_order.assert_not_called()

#     def test_error_handling(
#         self,
#         mock_get_alpaca_credentials,
#         mock_get_alpaca_account_balance,
#         mock_trading_client,
#         mock_is_asset_fractionable,
#     ):
#         mock_trading_client.submit_order.side_effect = Exception("Test error") # noqa: E501
#         submit_market_order_custom_percentage(
#             "AAPL", True, 0.5, "test_account"
#         )


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


# tests for submit_market_order_custom_amount helper function
# Mock for get_latest_quote
@pytest.fixture
def mock_get_latest_quote(monkeypatch):
    monkeypatch.setattr(
        "chalicelib.src.exchanges.alpaca.alpaca_utils.get_latest_quote",
        lambda symbol, account: {
            "ask_price": Decimal("150"),
            "bid_price": Decimal("149"),
        },
    )


class TestSubmitMarketOrderCustomAmount:
    def test_submit_order_fractional_asset(
        self,
        mock_get_alpaca_credentials,
        mock_trading_client,
        mock_is_asset_fractionable,
        mock_get_latest_quote,
    ):
        submit_market_order_custom_amount("AAPL", 100, True)
        assert mock_trading_client.submit_order.called

    def test_submit_order_non_fractional_asset(
        self,
        mock_get_alpaca_credentials,
        mock_trading_client,
        monkeypatch,
        mock_get_latest_quote,
    ):
        # Mock is_asset_fractionable to return False
        monkeypatch.setattr(
            "chalicelib.src.exchanges.alpaca.alpaca_utils.is_asset_fractionable",  # noqa: E501
            lambda symbol, account=None: False,
        )
        submit_market_order_custom_amount("AAPL", 100, True)
        assert mock_trading_client.submit_order.called


# tests for helper function get_available_asset_balance
@pytest.fixture
def mock_trading_client_success(monkeypatch):
    mock_position = MagicMock(qty=100, market_value=5000)
    mock_client_instance = MagicMock()
    mock_client_instance.get_open_position.return_value = mock_position
    monkeypatch.setattr(
        "chalicelib.src.exchanges.alpaca.alpaca_utils.TradingClient",
        lambda *args, **kwargs: mock_client_instance,
    )


@pytest.fixture
def mock_trading_client_failure(monkeypatch):
    mock_client_instance = MagicMock()
    mock_client_instance.get_open_position.side_effect = Exception("API Error")
    monkeypatch.setattr(
        "chalicelib.src.exchanges.alpaca.alpaca_utils.TradingClient",
        lambda *args, **kwargs: mock_client_instance,
    )


class TestGetAvailableAssetBalance:
    def test_get_available_asset_balance_success(
        self, mock_get_alpaca_credentials, mock_trading_client_success
    ):
        result = get_available_asset_balance("AAPL")
        assert result is not None
        assert result["position_qty"] == 100
        assert result["position_market_value"] == 5000

    def test_get_available_asset_balance_no_credentials(
        self, mock_get_alpaca_credentials, monkeypatch
    ):
        monkeypatch.setattr(
            "chalicelib.src.exchanges.alpaca.alpaca_utils.get_alpaca_credentials",  # noqa: E501
            lambda _: None,
        )
        result = get_available_asset_balance("AAPL")
        assert result is None

    def test_get_available_asset_balance_api_error(
        self, mock_get_alpaca_credentials, mock_trading_client_failure
    ):
        result = get_available_asset_balance("AAPL")
        assert result is None


# tests for get_latest_quote helper function
@pytest.fixture
def mock_stock_historical_data_client(monkeypatch):
    mock_client = MagicMock()
    mock_client.get_stock_latest_quote.return_value = {
        "AAPL": MagicMock(
            ask_price=150.50, bid_price=150.00, ask_size=100, bid_size=200
        )
    }
    monkeypatch.setattr(
        "chalicelib.src.exchanges.alpaca.alpaca_utils.StockHistoricalDataClient",  # noqa: E501
        lambda *args, **kwargs: mock_client,
    )


class TestGetLatestQuote:
    def test_get_latest_quote_success(
        self, mock_get_alpaca_credentials, mock_stock_historical_data_client
    ):
        result = get_latest_quote("AAPL")
        assert result == {
            "ask_price": Decimal(150.50),
            "bid_price": Decimal(150.00),
            "ask_size": 100,
            "bid_size": 200,
        }

    def test_get_latest_quote_failure(
        self, mock_get_alpaca_credentials, monkeypatch
    ):
        monkeypatch.setattr(
            "chalicelib.src.exchanges.alpaca.alpaca_utils.StockHistoricalDataClient",  # noqa: E501
            lambda *args, **kwargs: MagicMock(
                side_effect=Exception("API Error")
            ),
        )
        result = get_latest_quote("AAPL")
        assert result == {
            "ask_price": Decimal(0),
            "bid_price": Decimal(0),
            "ask_size": 0,
            "bid_size": 0,
        }


# tests for check_last_filled_order_type helper function
mock_filled_buy_order = MagicMock(
    status=OrderStatus.FILLED, side=OrderSide.BUY
)
mock_filled_sell_order = MagicMock(
    status=OrderStatus.FILLED, side=OrderSide.SELL
)


class TestCheckLastFilledOrderType:
    @pytest.fixture(autouse=True)
    def setup_mocks(self, monkeypatch):
        monkeypatch.setattr(
            "chalicelib.src.exchanges.alpaca.alpaca_utils.get_alpaca_credentials",  # noqa: E501
            lambda x: mock_credentials,
        )
        monkeypatch.setattr(
            "chalicelib.src.exchanges.alpaca.alpaca_utils.TradingClient",
            MockTradingClient,
        )

    def test_last_order_none(self, monkeypatch):
        monkeypatch.setattr(
            "chalicelib.src.exchanges.alpaca.alpaca_utils.TradingClient.get_orders",  # noqa: E501
            MagicMock(return_value=[]),
        )
        assert check_last_filled_order_type("AAPL") == "none"

    def test_last_order_buy(self, monkeypatch):
        monkeypatch.setattr(
            "chalicelib.src.exchanges.alpaca.alpaca_utils.TradingClient.get_orders",  # noqa: E501
            MagicMock(return_value=[mock_filled_buy_order]),
        )
        assert check_last_filled_order_type("AAPL") == "buy"

    def test_last_order_sell(self, monkeypatch):
        monkeypatch.setattr(
            "chalicelib.src.exchanges.alpaca.alpaca_utils.TradingClient.get_orders",  # noqa: E501
            MagicMock(return_value=[mock_filled_sell_order]),
        )
        assert check_last_filled_order_type("AAPL") == "sell"
