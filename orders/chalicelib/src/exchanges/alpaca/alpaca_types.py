from typing import TypedDict


class AlpacaAccountCredentials(TypedDict):
    endpoint: str
    key: str
    secret: str | None
    paper: bool


class MockAsset:
    def __init__(self, fractionable):
        self.fractionable = fractionable
