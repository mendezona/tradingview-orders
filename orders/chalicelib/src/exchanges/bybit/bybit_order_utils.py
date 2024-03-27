from decimal import ROUND_DOWN, Decimal
from typing import Any

from chalicelib.src.constants import capital_to_deploy_percentage, tax_rate
from chalicelib.src.exchanges.bybit.bybit_account_utils import (
    bybit_get_coin_balance,
    bybit_get_credentials,
)
from chalicelib.src.exchanges.bybit.bybit_constants import (
    bybit_default_product_category,
    bybit_preferred_stablecoin,
    bybit_tax_pair,
    bybit_trading_account_name_live,
    tradingview_bybit_inverse_symbols,
    tradingview_bybit_symbols,
)
from chalicelib.src.exchanges.bybit.bybit_order_helper_utils import (
    bybit_calculate_profit_loss,
    bybit_get_symbol_increments,
)
from chalicelib.src.exchanges.bybit.bybit_order_history_utils import (
    bybit_get_most_recent_inverse_fill_to_stablecoin,
)
from chalicelib.src.exchanges.bybit.bybit_types import (
    BybitAccountCredentials,
    BybitGetSymboIncrements,
)
from chalicelib.src.exchanges.exchanges_utils import (
    get_base_and_quote_assets,
    remove_hyphen_from_pair_symbol,
)
from pybit.unified_trading import HTTP


def bybit_submit_pair_trade_order(
    tradingview_symbol: str,
    capital_to_deploy: Decimal = Decimal(capital_to_deploy_percentage),
    calculate_tax: bool = True,
    buy_alert: bool = True,
    account_name: str = bybit_trading_account_name_live,
):
    """
    Submit a pair trade order. Closes and calculates tax on inverse asset,
    then opens new order on asset

    Parameters:
    - tradingview_symbol: Tradingview symbol as formatted in TradingView
    - capital_to_deploy: Percentage of asset holdings to deploy
    - calculate_tax: Calculate and convert CGT tax to stablecoin holdings, and
    remove from capital deployment calculations
    - buy_alert: Set buy or sell alert (buy positively or buy negatively
    correlated asset)
    - account_name: Account to use for order
    """

    print("Bybit Order Begin - bybit_submit_pair_trade_order")

    # Search for asset name conversion
    pair_symbol = (
        tradingview_bybit_symbols[tradingview_symbol]
        if buy_alert
        else tradingview_bybit_inverse_symbols[tradingview_symbol]
    )
    pair_inverse_symbol = (
        tradingview_bybit_inverse_symbols[tradingview_symbol]
        if buy_alert
        else tradingview_bybit_symbols[tradingview_symbol]
    )

    # Check if you are holding the inverse asset, and sell it if you are
    # Assumes there is only one order open of an asset pair at a time
    # Sells all holdings of inverset asset, and converts CGT to tax stablecoin
    if not (
        bybit_get_most_recent_inverse_fill_to_stablecoin(
            pair_inverse_symbol, account_name=account_name
        )
    ):
        (
            base_asset,
            quote_asset,
        ) = get_base_and_quote_assets(pair_inverse_symbol)
        if (
            base_asset != bybit_preferred_stablecoin
            and quote_asset != bybit_preferred_stablecoin
        ):
            raise ValueError(
                "Error - Base stablecoin currency for calculatng profit/loss not found"  # noqa: E501
            )
        if base_asset == bybit_preferred_stablecoin:
            print("No stablecoin conversion found - submit buy order")
            bybit_submit_market_order_custom_percentage(
                pair_inverse_symbol,
                buy_side_order=True,
                asset_percentage_to_deploy=Decimal(1),
                account_name=account_name,
            )
        elif quote_asset == bybit_preferred_stablecoin:
            print("No stablecoin conversion found - submit sell order")
            bybit_submit_market_order_custom_percentage(
                pair_inverse_symbol,
                buy_side_order=False,
                asset_percentage_to_deploy=Decimal(1),
                account_name=account_name,
            )

        # Calculate tax to convert to preferred tax stablecoin
        if calculate_tax:
            profit_loss_amount: Decimal = bybit_calculate_profit_loss(
                pair_inverse_symbol, account_name
            )
            tax_amount: Decimal = Decimal(profit_loss_amount) * Decimal(
                tax_rate
            )
            print("Tax amount:", profit_loss_amount)

            if tax_amount > 0:
                bybit_submit_market_order_custom_amount(
                    bybit_tax_pair,
                    dollar_amount=tax_amount,
                    buy_side_order=True,
                    account_name=account_name,
                )

    # Submit market order for new asset, once inverse asset holdings are sold
    bybit_submit_market_order_custom_percentage(
        pair_symbol,
        buy_side_order=True,
        asset_percentage_to_deploy=capital_to_deploy,
        account_name=account_name,
    )


def bybit_submit_market_order_custom_percentage(
    pair_symbol: str,
    asset_percentage_to_deploy: Decimal = Decimal(1),
    buy_side_order: bool = True,
    account_name: str = bybit_trading_account_name_live,
    product_category: str = bybit_default_product_category,
):
    """
    Submit a market order for a custom percentage of total asset holdings

    Parameters:
    - pair_symbol: Pair symbol formatted with hypen eg. BTC-USDT
    - asset_percentage_to_deploy: Percentage of asset holdings to deploy
    - buy_side_order: Buy or sell side order
    - account_name: Account to use for order
    - product_category: Product category eg. spot, deraivatives, etc
    """

    print("Bybit Order Begin - bybit_submit_market_order_custom_percentage")

    # Get asset balance, and check if there is enough to execute order
    base_asset, quote_asset = get_base_and_quote_assets(pair_symbol)
    balance = (
        bybit_get_coin_balance(quote_asset, account_name)
        if buy_side_order
        else bybit_get_coin_balance(base_asset, account_name)
    )
    if Decimal(balance) <= Decimal(asset_percentage_to_deploy):
        print("Error - Insufficient funds to execute order")
        return "Error - Insufficient funds to execute order"

    # Get increment information to execute order
    increments_object: BybitGetSymboIncrements = bybit_get_symbol_increments(
        remove_hyphen_from_pair_symbol(pair_symbol), account_name
    )
    basePrecision: str | Any = increments_object.get("basePrecision")
    quotePrecision: str | Any = increments_object.get("quotePrecision")
    symbol_minimum_increment: Decimal = (
        Decimal(quotePrecision) if buy_side_order else Decimal(basePrecision)
    )

    # Calculate funds to deploy
    funds_to_deploy: Decimal = Decimal(balance) * Decimal(
        asset_percentage_to_deploy
    )
    quantity_to_deploy: Decimal = funds_to_deploy.quantize(
        symbol_minimum_increment, rounding=ROUND_DOWN
    )
    order_type = "Buy" if buy_side_order else "Sell"

    print("Order side: ", order_type)
    print("Capital to deploy (%): ", asset_percentage_to_deploy)
    print("Funds to deploy", funds_to_deploy, "\n")

    if funds_to_deploy > 0:
        # Initialise the HTTP client with Bybit's endpoint and API credentials
        credentials: BybitAccountCredentials = bybit_get_credentials(
            account_name
        )
        session: HTTP = HTTP(
            testnet=credentials["testnet"],
            api_key=credentials["api_key"],
            api_secret=credentials["api_secret"],
        )
        symbol: str = remove_hyphen_from_pair_symbol(pair_symbol)
        order_response = session.place_order(
            category=product_category,
            symbol=symbol,
            side=order_type,
            orderType="Market",
            qty=quantity_to_deploy,
        )
        print("Bybit market order submitted: \n", order_response, "\n")


def bybit_submit_market_order_custom_amount(
    pair_symbol: str,
    dollar_amount: Decimal,
    buy_side_order: bool = True,
    account_name: str = bybit_trading_account_name_live,
    product_category: str = bybit_default_product_category,
):
    """
    Submit a market order for a custom dollarised amount

    Parameters:
    - pair_symbol: Pair symbol formatted with hypen eg. BTC-USDT
    - dollar_amount: Dollar amount to deploy
    - buy_side_order: Buy or sell side order
    - account_name: Account to use for order
    - product_category: Product category eg. spot, deraivatives, etc
    """

    print("Bybit Order Begin - bybit_submit_market_order_custom_amount")

    # Get asset balance, and check if there is enough to execute order
    base_asset, quote_asset = get_base_and_quote_assets(pair_symbol)
    balance = (
        bybit_get_coin_balance(quote_asset, account_name)
        if buy_side_order
        else bybit_get_coin_balance(base_asset, account_name)
    )
    if Decimal(balance) <= Decimal(dollar_amount):
        print("Error - Insufficient funds to execute order")
        return "Error - Insufficient funds to execute order"

    # Get increment information to execute order
    increments_object: BybitGetSymboIncrements = bybit_get_symbol_increments(
        remove_hyphen_from_pair_symbol(pair_symbol), account_name
    )
    basePrecision: str | Any = increments_object.get("basePrecision")
    quotePrecision: str | Any = increments_object.get("quotePrecision")
    symbol_minimum_increment: Decimal = (
        Decimal(basePrecision) if buy_side_order else Decimal(quotePrecision)
    )

    # Calculate funds to deploy
    funds_to_deploy: Decimal = Decimal(dollar_amount)
    quantity_to_deploy: Decimal = funds_to_deploy.quantize(
        symbol_minimum_increment, rounding=ROUND_DOWN
    )
    order_type = "Buy" if buy_side_order else "Sell"

    print("Order side: ", order_type)
    print("Capital to deploy ($): ", dollar_amount)
    print("Funds to deploy", funds_to_deploy, "\n")

    if funds_to_deploy > 0:
        # Initialise the HTTP client with Bybit's endpoint and API credentials
        credentials: BybitAccountCredentials = bybit_get_credentials(
            account_name
        )
        session: HTTP = HTTP(
            testnet=credentials["testnet"],
            api_key=credentials["api_key"],
            api_secret=credentials["api_secret"],
        )
        symbol: str = remove_hyphen_from_pair_symbol(pair_symbol)
        order_response = session.place_order(
            category=product_category,
            symbol=symbol,
            side=order_type,
            orderType="Market",
            qty=quantity_to_deploy,
        )
        print("Bybit market order submitted: \n", order_response, "\n")
