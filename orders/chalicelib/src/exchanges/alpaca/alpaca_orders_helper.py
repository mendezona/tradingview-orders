from alpaca.common import RawData
from alpaca.trading.client import TradingClient
from alpaca.trading.models import Asset
from chalicelib.src.exchanges.alpaca.alpaca_account_utils import (
    alpaca_get_credentials,
)
from chalicelib.src.exchanges.alpaca.alpaca_constants import (
    alpaca_trading_account_name_live,
)
from chalicelib.src.exchanges.alpaca.alpaca_types import (
    AlpacaAccountCredentials,
)


def alpaca_is_asset_fractionable(
    symbol: str,
    account: str = alpaca_trading_account_name_live,
) -> bool:
    credentials: AlpacaAccountCredentials = alpaca_get_credentials(account)
    if credentials:
        client = TradingClient(
            api_key=credentials["key"],
            secret_key=credentials["secret"],
            paper=credentials["paper"],
        )
        try:
            asset: Asset | RawData = client.get_asset(symbol)
            print("assetreturn", asset)
            print("asset fractionable: ", asset.fractionable)
            return asset.fractionable
        except Exception as e:
            print(f"Error fetching asset information: {e}")
