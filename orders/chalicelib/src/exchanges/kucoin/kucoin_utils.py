from decimal import ROUND_DOWN, Decimal
from typing import Any, Dict, Optional, Tuple

from chalicelib.src.constants import (
    capital_to_deploy_percentage,
    country_personal_income_tax_rate,
    development_mode,
)
from chalicelib.src.exchanges.exchanges_utils import get_base_and_quote_assets
from chalicelib.src.exchanges.kucoin.kucoin_constants import (
    base_url,
    kucoin_account_names,
    kucoin_accounts,
    preferred_stablecoin,
    tax_pair,
    trade_account,
    tradingview_kucoin_inverse_pairs,
    tradingview_kucoin_symbols,
)
from chalicelib.src.exchanges.kucoin.kucoin_types import (
    KucoinAccountCredentials,
)
from kucoin.client import Market, Trade, User


# Get account credentials, for main account or sub accounts to trade with
def get_account_credentials(
    account: str = kucoin_account_names[0],
    accounts: Dict[str, KucoinAccountCredentials] = kucoin_accounts,
) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    account_info = accounts.get(account)

    if account_info is not None:
        api_key: Optional[str] = account_info.get("api_key")
        api_secret: Optional[str] = account_info.get("api_secret")
        api_passphrase: Optional[str] = account_info.get("api_passphrase")
        return api_key, api_secret, api_passphrase
    else:
        return None, None, None


# Get current account balance
def get_account_balance(account: str = kucoin_account_names[0]) -> Any:
    api_key, api_secret, api_passphrase = get_account_credentials(account)
    client = (
        User(api_key, api_secret, api_passphrase)
        if not development_mode
        else User(
            api_key,
            api_secret,
            api_passphrase,
            is_sandbox=True,
            url=f"{base_url}/api/v1/accounts/test",
        )
    )
    balance = client.get_account_list()

    print("Account balance:", balance)
    return balance


# Submit market order for inversely paired assets
def submit_pair_trade_order(
    tradingview_symbol,
    capital_to_deploy=capital_to_deploy_percentage,
    calculate_tax=True,
    buy_alert=True,
    account=kucoin_account_names[0],
):
    # Check if there is an inverse order open
    kucoin_symbol = (
        tradingview_kucoin_symbols[tradingview_symbol]
        if buy_alert
        else tradingview_kucoin_inverse_pairs[tradingview_symbol]
    )
    kucoin_inverse_symbol = (
        tradingview_kucoin_inverse_pairs[tradingview_symbol]
        if buy_alert
        else tradingview_kucoin_symbols[tradingview_symbol]
    )

    # If there is no sell order found for inverse pair symbol,
    # sell all holdings of the inverse pair and convert CGT to USDC.
    # Assumes there is only one order open at a time
    if not (
        get_most_recent_inverse_fill_to_stablecoin(
            kucoin_inverse_symbol, account=account
        )
    ):
        (
            base_currency_inverse,
            quote_currency_inverse,
        ) = get_base_and_quote_assets(kucoin_inverse_symbol)
        if (
            base_currency_inverse != preferred_stablecoin
            and quote_currency_inverse != preferred_stablecoin
        ):
            raise ValueError(
                "Base stablecoin currency for calculatng profit/loss not found"
            )
        if base_currency_inverse == preferred_stablecoin:
            print("NO CONVERSION TO STABLECOIN FOUND - SUBMIT BUY ORDER")
            submit_market_order_custom_percentage(
                kucoin_inverse_symbol,
                True,
                capital_percentage_to_deploy=1,
                account=account,
            )
        elif quote_currency_inverse == preferred_stablecoin:
            print("NO CONVERSION TO STABLECOIN FOUND - SUBMIT SELL ORDER")
            submit_market_order_custom_percentage(
                kucoin_inverse_symbol,
                False,
                capital_percentage_to_deploy=1,
                account=account,
            )

        if calculate_tax:
            profit_loss_amount = calculate_profit_loss(
                kucoin_inverse_symbol, account
            )
            tax_amount = profit_loss_amount * country_personal_income_tax_rate
            print("tax_amount", profit_loss_amount, "\n")

            if tax_amount > 0:
                submit_market_order_custom_amount(
                    tax_pair, True, tax_amount, account
                )

    submit_market_order_custom_percentage(
        kucoin_symbol, True, capital_to_deploy, account
    )


# Check if last fill was a sell side order have been sold to USDT.
# Returns True if last order was Sell, False if last order was a Buy or
# no previous orders found
def get_most_recent_inverse_fill_to_stablecoin(
    kucoin_symbol,
    stablecoin=preferred_stablecoin,
    account=kucoin_account_names[0],
):
    base_currency, quote_currency = get_base_and_quote_assets(kucoin_symbol)
    buyOrSellToStablecoin: str = ""
    if base_currency != stablecoin and quote_currency != stablecoin:
        raise ValueError(
            "Base stablecoin currency for calculatng most recent fill not found"  # noqa: E501
        )
    if base_currency == stablecoin:
        buyOrSellToStablecoin: str = "sell"
    elif quote_currency == stablecoin:
        buyOrSellToStablecoin: str = "buy"
    buyOrSellToStablecoin = (
        "sell" if base_currency == stablecoin else "quote_currency"
    )
    api_key, api_secret, api_passphrase = get_account_credentials(account)
    client = (
        Trade(api_key, api_secret, api_passphrase)
        if not development_mode
        else Trade(
            api_key,
            api_secret,
            api_passphrase,
            is_sandbox=True,
            url=f"{base_url}/api/v1/fills/test",
        )
    )
    recent_fills = client.get_fill_list(
        tradeType=trade_account.upper(),
        symbol=kucoin_symbol,
    )

    if len(recent_fills["items"]) > 0:
        last_fill = recent_fills["items"][0]
        return True if last_fill["side"] == buyOrSellToStablecoin else False

    return False


# Sell all holdings of a symbol using a Market Order.
# Default is aSell Side Order
def submit_market_order_custom_percentage(
    kucoin_symbol,
    buy_side_order=True,
    capital_percentage_to_deploy=1,
    account=kucoin_account_names[0],
):
    base_currency, quote_currency = get_base_and_quote_assets(kucoin_symbol)
    print(
        "currency search", quote_currency if buy_side_order else base_currency
    )
    balance = (
        get_available_balance(quote_currency, account)
        if buy_side_order
        else get_available_balance(base_currency, account)
    )
    if not balance:
        return
    base_increment, quote_increment = get_symbol_increments(
        kucoin_symbol, account
    )
    funds_to_deploy = Decimal(balance) * Decimal(capital_percentage_to_deploy)
    order_type = "buy" if buy_side_order else "sell"
    symbol_minimum_increment = (
        Decimal(base_increment) if buy_side_order else Decimal(quote_increment)
    )
    # Round down the max order size to the nearest valid increment
    funds_to_deploy = funds_to_deploy.quantize(
        symbol_minimum_increment, rounding=ROUND_DOWN
    )
    print("order_side: ", order_type)
    print("capital %: ", capital_percentage_to_deploy)
    print("funds_to_deploy", funds_to_deploy, "\n")

    # Remember to use size instead of funds if you want denomination
    # in base currency
    if funds_to_deploy > 0:
        api_key, api_secret, api_passphrase = get_account_credentials(account)
        client_trade = (
            Trade(api_key, api_secret, api_passphrase)
            if not development_mode
            else Trade(
                api_key,
                api_secret,
                api_passphrase,
                is_sandbox=True,
                url=f"{base_url}/api/v1/orders/test",
            )
        )
        if buy_side_order:
            order_response = client_trade.create_market_order(
                symbol=str(kucoin_symbol),
                side="buy",
                funds=str(funds_to_deploy),
            )
            print("Market buy order submitted: \n", order_response, "\n")
        else:
            order_response = client_trade.create_market_order(
                symbol=str(kucoin_symbol),
                side="sell",
                size=str(funds_to_deploy),
            )
            print("Market sell order submitted: \n", order_response, "\n")


# Calculate the profit/loss made from previous trade
# (assuming Market Order for both)
# Change stablecoin to other stablecoin or pair
def calculate_profit_loss(
    kucoin_symbol,
    currency_to_convert_to=preferred_stablecoin,
    account=kucoin_account_names[0],
):
    api_key, api_secret, api_passphrase = get_account_credentials(account)
    client = (
        Trade(api_key, api_secret, api_passphrase)
        if not development_mode
        else Trade(
            api_key,
            api_secret,
            api_passphrase,
            is_sandbox=True,
            url=f"{base_url}/api/v1/fills/test",
        )
    )
    recent_fills = client.get_fill_list(
        tradeType=trade_account.upper(), symbol=kucoin_symbol
    )
    base_currency, quote_currency = get_base_and_quote_assets(kucoin_symbol)
    sell_funds = []
    buy_funds = []
    profitOrLoss = 0
    iterating_sell = True

    for item in recent_fills["items"]:
        if quote_currency == currency_to_convert_to:
            # Iterate over "sell" orders until the first "buy" order is found
            if item["side"] == "sell" and iterating_sell:
                sell_funds.append(float(item["funds"]))
            elif item["side"] == "buy" and iterating_sell:
                # Stop iterating over "sell" orders once a "buy" order is found
                iterating_sell = False
                buy_funds.append(float(item["funds"]))
            elif item["side"] == "sell" and not iterating_sell:
                # Stop iterating once the first "sell" order after a "buy"
                # order is found
                break
        elif base_currency == currency_to_convert_to:
            # Iterate over "buy" orders until the first "sell" order is found
            if item["side"] == "buy" and iterating_sell:
                buy_funds.append(float(item["funds"]))
            elif item["side"] == "sell" and iterating_sell:
                # Stop iterating over "buy" orders once a "sell" order is found
                iterating_sell = False
                sell_funds.append(float(item["funds"]))
            elif item["side"] == "buy" and not iterating_sell:
                # Stop iterating once the first "buy" order after a "sell"
                # order is found
                break
    print("buy_funds", buy_funds)
    print("sell_funds", sell_funds)
    sum_sell_funds = sum(sell_funds)
    sum_buy_funds = sum(buy_funds)
    profitOrLoss = sum_sell_funds - sum_buy_funds

    print("profit/loss:", profitOrLoss)
    return profitOrLoss


# Convert CGT to USDC for easier tracking, and manual withdrawal later
def submit_market_order_custom_amount(
    kucoin_symbol: str,
    buy_side_order: bool = True,
    capital_amount_to_deploy: int = 0,
    account: str = kucoin_account_names[0],
) -> None:
    base_currency, quote_currency = get_base_and_quote_assets(kucoin_symbol)
    print(
        "currency search", quote_currency if buy_side_order else base_currency
    )
    balance = (
        get_available_balance(quote_currency, account)
        if buy_side_order
        else get_available_balance(base_currency, account)
    )
    if not float(balance) <= float(capital_amount_to_deploy):
        return
    base_increment, quote_increment = get_symbol_increments(
        kucoin_symbol, account
    )
    funds_to_deploy: Decimal = Decimal(capital_amount_to_deploy)
    order_type = "buy" if buy_side_order else "sell"
    symbol_minimum_increment: Decimal = (
        Decimal(base_increment) if buy_side_order else Decimal(quote_increment)
    )
    # Round down the max order size to the nearest valid increment
    funds_to_deploy: Decimal = funds_to_deploy.quantize(
        symbol_minimum_increment, rounding=ROUND_DOWN
    )
    print("order_side: ", order_type)
    print("capital %: ", capital_amount_to_deploy)
    print("funds_to_deploy", funds_to_deploy, "\n")

    # Remember to use size instead of funds if you want denomination
    # in base currency
    if funds_to_deploy > 0:
        api_key, api_secret, api_passphrase = get_account_credentials(account)
        client_trade = (
            Trade(api_key, api_secret, api_passphrase)
            if not development_mode
            else Trade(
                api_key,
                api_secret,
                api_passphrase,
                is_sandbox=True,
                url=f"{base_url}/api/v1/orders/test",
            )
        )
        if buy_side_order:
            order_response = client_trade.create_market_order(
                symbol=str(kucoin_symbol),
                side="buy",
                funds=str(funds_to_deploy),
            )
            print("Market buy order submitted: \n", order_response, "\n")
        else:
            order_response = client_trade.create_market_order(
                symbol=str(kucoin_symbol),
                side="sell",
                size=str(funds_to_deploy),
            )
            print("Market sell order submitted: \n", order_response, "\n")


# Get available coin balance, can specify base or quote symbol
def get_available_balance(
    currency: str,
    account: str = kucoin_account_names[0],
) -> Optional[str]:
    api_key, api_secret, api_passphrase = get_account_credentials(account)
    client = User(api_key, api_secret, api_passphrase)
    accounts = client.get_account_list(currency=currency)

    # Handle the case where the structure is different
    if not isinstance(accounts, list):
        print(f"Unexpected accounts structure: {accounts}")
        return None

    available_balance = next(
        (
            item["balance"]
            for item in accounts
            if item.get("type") == trade_account
        ),
        None,
    )

    if available_balance:
        print(f"Trading account balance for {currency}: {available_balance}")
        return str(available_balance)

    return None


# Get minimum increment that a coin pair accepts. Returns base increment
# of the base currency (first currency in the trading pair), and the quote
# increment of the quote currency (second currency in the trading pair)
def get_symbol_increments(
    symbol: str,
    account: str = kucoin_account_names[0],
) -> Tuple[Optional[str], Optional[str]]:
    api_key, api_secret, api_passphrase = get_account_credentials(account)
    client = Market(api_key, api_secret, api_passphrase)
    symbols = client.get_symbol_list_v2()

    # Iterate through the symbols to find the one
    # matching the provided symbol
    for s in symbols:
        if s["symbol"] == symbol:
            # Return base increment and quote increment
            return s.get("baseIncrement"), s.get("quoteIncrement")

    # Return None if the symbol is not found
    return None, None
