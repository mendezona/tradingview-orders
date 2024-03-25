from decimal import Decimal
from typing import TypedDict


class AWSDynamoDbItem(TypedDict):
    Asset: str
    TransactionDate: str
    Profit: Decimal
    RunningTotal: Decimal
    DateKey: str
