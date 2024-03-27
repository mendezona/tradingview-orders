from typing import TypedDict


class BybitAccountCredentials(TypedDict):
    api_key: str
    api_secret: str
    testnet: bool


class BybitGetSymboIncrements(TypedDict):
    symbol: str
    basePrecision: str
    quotePrecision: str
    minOrderQty: str
    maxOrderQty: str
    minOrderAmt: str
    maxOrderAmt: str
    tickSize: str
