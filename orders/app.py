from chalice import Chalice
from chalicelib.src.aws.aws_constants import dynamodb_table_names_instance
from chalicelib.src.aws.dynamo_db import (
    create_new_dynamodb_instance,
    save_item_to_dynamodb_table,
)
from chalicelib.src.exchanges.alpaca.alpaca_utils import test_alpaca_function
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


@app.route("/alpacatest")
def hello():
    test_alpaca_function()

    return {"hello": "world"}


# Developer function, convert assets in Kucoin subaccount to a stablecoin
@app.route("/converttostablecoin")
def transfer_funds_to_stablecoin():
    # set to sub account 1
    submit_market_order_custom_percentage(
        tax_pair, False, account=kucoin_account_names[2]
    )

    return {"message": "market order executed"}


# Developer function, reset Kucoin account to all Stablecoins
@app.route("/resettostablecoin")
def reset_funds_to_stablecoin():
    # SET ACCOUNT AND BASE AND QUOTE CURRENCIES
    pairToReset: str = "BASE-QUOTE"
    account: str = kucoin_account_names[1]
    submit_market_order_custom_percentage(
        pairToReset,
        False,
        account=account,
    )

    return {"message": "market order executed"}


"""
Save historical Tradingview Alerts
"""


# Developer function, create new DynamoDB instance with desired
# table name
@app.route("/createnewdynamodbinstance")
def create_new_db():
    create_new_dynamodb_instance(
        dynamodb_table_names_instance.ptos_signal_alerts
    )

    return {"dynamodb": "new table created"}


@app.route("/saveptosmodelalerts", methods=["POST"])
def save_tradingview_ptos_model_alerts():
    request = app.current_request
    tradingViewWebhookMessage = request.json_body
    table_name = dynamodb_table_names_instance.ptos_model_alerts

    response = save_item_to_dynamodb_table(
        table_name=table_name, item=tradingViewWebhookMessage
    )

    print("response: ", response)
    return {"saved": "ptos model alert"}


@app.route("/saveptossignalalerts", methods=["POST"])
def save_tradingview_ptos_signal_alerts():
    request = app.current_request
    tradingViewWebhookMessage = request.json_body
    table_name: str = dynamodb_table_names_instance.ptos_signal_alerts

    response = save_item_to_dynamodb_table(
        table_name=table_name, item=tradingViewWebhookMessage
    )

    print("response: ", response)
    return {"saved": "ptos signal alert"}


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
