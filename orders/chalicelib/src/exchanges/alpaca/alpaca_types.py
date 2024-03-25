from decimal import Decimal
from typing import TypedDict

from alpaca.common import RawData
from alpaca.trading.models import TradeAccount


class AlpacaAccountCredentials(TypedDict):
    endpoint: str
    key: str
    secret: str | None
    paper: bool


class AlpacaGetAccountBalance(TypedDict):
    account: TradeAccount | RawData
    account_equity: Decimal
    account_cash: Decimal


class AlpacaAvailableAssetBalance(TypedDict):
    position: str
    position_qty: float
    position_market_value: float


class AlpacaGetLatestQuote(TypedDict):
    ask_price: Decimal
    bid_price: Decimal
    ask_size: float
    bid_size: float
