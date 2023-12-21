from typing import TypedDict


class AlpacaAccountCredentials(TypedDict):
    endpoint: str
    key: str
    secret: str | None
    paper: bool


class MockAsset:
    def __init__(self, fractionable):
        self.fractionable = fractionable


class MockTradingClient:
    def __init__(self, *args, **kwargs):
        pass

    def get_orders(self, filters):
        return []

    def close_position(self, symbol):
        pass
