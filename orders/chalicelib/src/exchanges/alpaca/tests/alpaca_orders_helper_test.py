import uuid

import pytest
import requests_mock
from alpaca.trading.client import TradingClient


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


def test_get_asset_success(asset_api_response, mock_requests):
    asset_symbol = "AAPL"
    api_url = f"https://paper-api.alpaca.markets/v2/assets/{asset_symbol}"
    mock_requests.get(api_url, json=asset_api_response)

    client = TradingClient(api_key="dummy", secret_key="dummy", paper=True)
    asset = client.get_asset(asset_symbol)

    assert asset.symbol == asset_api_response["symbol"]
    assert asset.fractionable is asset_api_response["fractionable"]
