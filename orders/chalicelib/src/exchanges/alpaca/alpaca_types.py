from typing import TypedDict


class AlpacaAccountCredentials(TypedDict):
    endpoint: str
    key: str
    secret: str | None
