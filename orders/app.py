from chalice import Chalice
from chalicelib.src.exchanges.kucoin.kucoin_constants import (
    kucoin_account_names,
    tax_pair,
)
from chalicelib.src.exchanges.kucoin.kucoin_utils import (
    submit_market_order_custom_percentage,
    submit_pair_trade_order,
)

app = Chalice(app_name="orders")

"""
Utility / testing routes
"""


@app.route("/")
def hello():
    return {"hello": "world"}


@app.route("/converttostablecoin")
def transferFundsToStablecoin():
    # set to sub account 1
    submit_market_order_custom_percentage(
        tax_pair, False, account=kucoin_account_names[1]
    )

    return {"message": "market order executed"}


@app.route("/resettostablecoin")
def resetFundsToStablecoin():
    # set to sub account 1 and SOL3S-USDT
    pairToReset = "SOL3S-USDT"
    account = kucoin_account_names[1]
    submit_market_order_custom_percentage(
        pairToReset,
        False,
        account=account,
    )

    return {"message": "market order executed"}


"""
Main Account routes
"""


@app.route("/pairtradebuyalert", methods=["POST"])
def pair_trade_buy_alert():
    request = app.current_request
    tradingViewWebhookMessage = request.json_body
    print("tradingViewWebhookMessage", tradingViewWebhookMessage, "\n")
    submit_pair_trade_order(tradingViewWebhookMessage["ticker"])

    return {
        "message": "alert received",
        "tradingViewWebhookMessage": tradingViewWebhookMessage,
    }


@app.route("/pairtradesellalert", methods=["POST"])
def pair_trade_sell_alert():
    request = app.current_request
    tradingViewWebhookMessage = request.json_body
    print("tradingViewWebhookMessage", tradingViewWebhookMessage, "\n")
    submit_pair_trade_order(
        tradingViewWebhookMessage["ticker"],
        buy_alert=False,
    )

    return {
        "message": "alert received",
        "tradingViewWebhookMessage": tradingViewWebhookMessage,
    }


@app.route("/pairtradebuyalertnotax", methods=["POST"])
def pair_trade_buy_alert_no_tax():
    request = app.current_request
    tradingViewWebhookMessage = request.json_body
    print("tradingViewWebhookMessage", tradingViewWebhookMessage, "\n")
    submit_pair_trade_order(
        tradingview_symbol=tradingViewWebhookMessage["ticker"],
        calculate_tax=False,
    )

    return {
        "message": "alert received",
        "tradingViewWebhookMessage": tradingViewWebhookMessage,
    }


@app.route("/pairtradesellalertnotax", methods=["POST"])
def pair_trade_sell_alert_no_tax():
    request = app.current_request
    tradingViewWebhookMessage = request.json_body
    print("tradingViewWebhookMessage", tradingViewWebhookMessage, "\n")
    submit_pair_trade_order(
        tradingview_symbol=tradingViewWebhookMessage["ticker"],
        calculate_tax=False,
        buy_alert=False,
    )

    return {
        "message": "alert received",
        "tradingViewWebhookMessage": tradingViewWebhookMessage,
    }


"""
Sub Account 1 routes
"""


@app.route("/sub1pairtradebuyalert", methods=["POST"])
def sub_1_pair_trade_buy_alert():
    request = app.current_request
    tradingViewWebhookMessage = request.json_body
    print("tradingViewWebhookMessage", tradingViewWebhookMessage, "\n")
    submit_pair_trade_order(
        tradingViewWebhookMessage["ticker"],
        account=kucoin_account_names[1],
    )

    return {
        "message": "alert received",
        "tradingViewWebhookMessage": tradingViewWebhookMessage,
    }


@app.route("/sub1pairtradesellalert", methods=["POST"])
def sub_1_pair_trade_sell_alert():
    request = app.current_request
    tradingViewWebhookMessage = request.json_body
    print("tradingViewWebhookMessage", tradingViewWebhookMessage, "\n")
    submit_pair_trade_order(
        tradingViewWebhookMessage["ticker"],
        buy_alert=False,
        account=kucoin_account_names[1],
    )

    return {
        "message": "alert received",
        "tradingViewWebhookMessage": tradingViewWebhookMessage,
    }


@app.route("/sub1pairtradebuyalertnotax", methods=["POST"])
def sub_1_pair_trade_buy_alert_no_tax():
    request = app.current_request
    tradingViewWebhookMessage = request.json_body
    print("tradingViewWebhookMessage", tradingViewWebhookMessage, "\n")
    submit_pair_trade_order(
        tradingview_symbol=tradingViewWebhookMessage["ticker"],
        calculate_tax=False,
        account=kucoin_account_names[1],
    )

    return {
        "message": "alert received",
        "tradingViewWebhookMessage": tradingViewWebhookMessage,
    }


@app.route("/sub1pairtradesellalertnotax", methods=["POST"])
def sub_1_pair_trade_sell_alert_no_tax():
    request = app.current_request
    tradingViewWebhookMessage = request.json_body
    print("tradingViewWebhookMessage", tradingViewWebhookMessage, "\n")
    submit_pair_trade_order(
        tradingview_symbol=tradingViewWebhookMessage["ticker"],
        calculate_tax=False,
        buy_alert=False,
        account=kucoin_account_names[1],
    )

    return {
        "message": "alert received",
        "tradingViewWebhookMessage": tradingViewWebhookMessage,
    }


"""
Sub Account 2 routes
"""


@app.route("/sub2pairtradebuyalert", methods=["POST"])
def sub_2_pair_trade_buy_alert():
    request = app.current_request
    tradingViewWebhookMessage = request.json_body
    print("tradingViewWebhookMessage", tradingViewWebhookMessage, "\n")
    submit_pair_trade_order(
        tradingViewWebhookMessage["ticker"],
        account=kucoin_account_names[2],
    )

    return {
        "message": "alert received",
        "tradingViewWebhookMessage": tradingViewWebhookMessage,
    }


@app.route("/sub2pairtradesellalert", methods=["POST"])
def sub_2_pair_trade_sell_alert():
    request = app.current_request
    tradingViewWebhookMessage = request.json_body
    print("tradingViewWebhookMessage", tradingViewWebhookMessage, "\n")
    submit_pair_trade_order(
        tradingViewWebhookMessage["ticker"],
        buy_alert=False,
        account=kucoin_account_names[2],
    )

    return {
        "message": "alert received",
        "tradingViewWebhookMessage": tradingViewWebhookMessage,
    }


@app.route("/sub2pairtradebuyalertnotax", methods=["POST"])
def sub_2_pair_trade_buy_alert_no_tax():
    request = app.current_request
    tradingViewWebhookMessage = request.json_body
    print("tradingViewWebhookMessage", tradingViewWebhookMessage, "\n")
    submit_pair_trade_order(
        tradingview_symbol=tradingViewWebhookMessage["ticker"],
        calculate_tax=False,
        account=kucoin_account_names[2],
    )

    return {
        "message": "alert received",
        "tradingViewWebhookMessage": tradingViewWebhookMessage,
    }


@app.route("/sub2pairtradesellalertnotax", methods=["POST"])
def sub_2_pair_trade_sell_alert_no_tax():
    request = app.current_request
    tradingViewWebhookMessage = request.json_body
    print("tradingViewWebhookMessage", tradingViewWebhookMessage, "\n")
    submit_pair_trade_order(
        tradingview_symbol=tradingViewWebhookMessage["ticker"],
        calculate_tax=False,
        buy_alert=False,
        account=kucoin_account_names[2],
    )

    return {
        "message": "alert received",
        "tradingViewWebhookMessage": tradingViewWebhookMessage,
    }
