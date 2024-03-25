import uuid
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest
import requests_mock
from alpaca.trading.client import TradingClient
from alpaca.trading.enums import OrderSide
from chalicelib.src.exchanges.alpaca.alpaca_orders_helper import (
    alpaca_calculate_profit_loss,
)
from chalicelib.src.exchanges.alpaca.alpaca_types import (
    AlpacaAccountCredentials,
)


@pytest.fixture
def asset_api_response():
    return {
        "id": str(uuid.UUID("b0b6dd9d-8b9b-48a9-ba46-b9d54906e415")),
        "class": "us_equity",
        "exchange": "NASDAQ",
        "symbol": "AAPL",
        "name": "Apple Inc. Common Stock",
        "status": "active",
        "tradable": True,
        "marginable": True,
        "shortable": True,
        "easy_to_borrow": True,
        "fractionable": True,
        "attributes": ["fractional_eh_enabled", "options_enabled"],
    }


@pytest.fixture
def mock_requests():
    with requests_mock.Mocker() as m:
        yield m


def test_is_asset_fractionable(asset_api_response, mock_requests):
    asset_symbol = "AAPL"
    api_url = f"https://paper-api.alpaca.markets/v2/assets/{asset_symbol}"
    mock_requests.get(api_url, json=asset_api_response)

    client = TradingClient(api_key="dummy", secret_key="dummy", paper=True)
    asset = client.get_asset(asset_symbol)

    assert asset.symbol == asset_api_response["symbol"]
    assert asset.fractionable is asset_api_response["fractionable"]


@pytest.fixture
def mock_credentials():
    """Fixture for mocking Alpaca credentials."""
    return AlpacaAccountCredentials(
        key="fake_key", secret="fake_secret", paper=True
    )


@pytest.fixture
def mock_orders():
    """Fixture for mocking a list of Order objects."""
    return [
        # Mock a sell order
        MagicMock(
            side=OrderSide.SELL, filled_qty="10", filled_avg_price="200"
        ),
        # Mock a buy order that matches the sell quantity
        MagicMock(side=OrderSide.BUY, filled_qty="10", filled_avg_price="150"),
    ]


@patch("alpaca.trading.client.TradingClient")
@patch(
    "chalicelib.src.exchanges.alpaca.alpaca_orders_helper.alpaca_get_credentials"  # noqa: E501
)
def alpaca_calculate_profit_loss_test_profit_scenario(
    mock_get_credentials, mock_TradingClient, mock_credentials, mock_orders
):
    mock_credentials = {
        "key": "fake_key",
        "paper": True,
        "secret": "fake_secret",
    }
    mock_get_credentials.return_value = mock_credentials
    mock_orders = [
        MagicMock(
            side=OrderSide.BUY,
            symbol="AAPL",
            filled_qty="10",
            filled_avg_price="150",
        ),
        MagicMock(
            side=OrderSide.SELL,
            symbol="AAPL",
            filled_qty="10",
            filled_avg_price="200",
        ),
    ]
    mock_TradingClient.return_value.get_orders.return_value = mock_orders

    profit_loss = alpaca_calculate_profit_loss("AAPL")
    assert profit_loss == Decimal("500"), "Expected profit of 500 not met"


@patch("alpaca.trading.client.TradingClient")
@patch(
    "chalicelib.src.exchanges.alpaca.alpaca_orders_helper.alpaca_get_credentials"  # noqa: E501
)
def alpaca_calculate_profit_loss_test_loss_scenario(
    mock_get_credentials, mock_TradingClient, mock_credentials, mock_orders
):
    """Test case for a loss scenario."""
    # Adjust the mock_orders for a loss scenario
    mock_orders[1].filled_avg_price = "250"
    mock_get_credentials.return_value = mock_credentials
    mock_TradingClient.return_value.get_orders.return_value = mock_orders

    profit_loss = alpaca_calculate_profit_loss("AAPL")
    assert profit_loss == Decimal(
        "-500"
    ), "Loss should be -500 for the given orders"


@patch("alpaca.trading.client.TradingClient")
@patch(
    "chalicelib.src.exchanges.alpaca.alpaca_orders_helper.alpaca_get_credentials"  # noqa: E501
)
def alpaca_calculate_profit_loss_test_no_sell_order_found(
    mock_get_credentials, mock_TradingClient, mock_credentials
):
    """Test case for no sell order found."""
    mock_get_credentials.return_value = mock_credentials
    # Return only buy orders
    mock_orders = [
        MagicMock(side=OrderSide.BUY, filled_qty="10", filled_avg_price="150")
    ]
    mock_TradingClient.return_value.get_orders.return_value = mock_orders

    with pytest.raises(ValueError, match="No recent sell order found."):
        alpaca_calculate_profit_loss("AAPL")


@patch("alpaca.trading.client.TradingClient")
@patch(
    "chalicelib.src.exchanges.alpaca.alpaca_orders_helper.alpaca_get_credentials"  # noqa: E501
)
def alpaca_calculate_profit_loss_test_not_enough_buy_orders(
    mock_get_credentials, mock_TradingClient, mock_credentials
):
    """
    Test case for not having enough buy orders to match the sell
    quantity.
    """
    mock_get_credentials.return_value = mock_credentials
    # Return one sell order and not enough buy quantity
    mock_orders = [
        MagicMock(
            side=OrderSide.SELL, filled_qty="10", filled_avg_price="200"
        ),
        MagicMock(side=OrderSide.BUY, filled_qty="5", filled_avg_price="150"),
    ]
    mock_TradingClient.return_value.get_orders.return_value = mock_orders

    with pytest.raises(
        ValueError, match="Not enough buy orders to match the sell quantity."
    ):
        alpaca_calculate_profit_loss("AAPL")
