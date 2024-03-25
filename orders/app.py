from chalice import Chalice

# from chalicelib.src.aws.aws_constants import dynamodb_table_names_instance
# from chalicelib.src.aws.dynamo_db import create_new_dynamodb_instance
# from chalicelib.src.exchanges.alpaca.alpaca_orders_helper import (
#     alpaca_get_latest_quote,
# )
from chalicelib.src.exchanges.alpaca.alpaca_orders_utils import (
    alpaca_submit_pair_trade_order,
)

app = Chalice(app_name="orders")

"""
Developer / Utility Routes
"""


# @app.route("/")
# def hello():
#     alpaca_get_latest_quote("AAPL")
#     return {"hello": "world"}


# Developer function, create new DynamoDB instance with desired
# table name
# @app.route("/createnewdynamodbinstance")
# def create_new_db():
#     create_new_dynamodb_instance(
#         dynamodb_table_names_instance.alpaca_markets_profits
#     )

#     return {"dynamodb": "new table created"}


"""
Alpaca Routes
"""


# @app.route("/alpacatest")
# def alpaca_test():
#     # request = app.current_request
#     # tradingViewWebhookMessage = request.json_body
#     # print("tradingViewWebhookMessage", tradingViewWebhookMessage, "\n")
#     test_alpaca_function()

#     return {"hello": "world"}


@app.route("/alpacapairtradebuyalert", methods=["POST"])
def alpaca_pair_trade_buy_alert():
    request = app.current_request
    tradingViewWebhookMessage = request.json_body
    print("tradingViewWebhookMessage", tradingViewWebhookMessage, "\n")
    alpaca_submit_pair_trade_order(tradingViewWebhookMessage["ticker"])

    return {"message": "market order executed"}


@app.route("/alpacapairtradesellalert", methods=["POST"])
def alpaca_pair_trade_sell_alert():
    request = app.current_request
    tradingViewWebhookMessage = request.json_body
    print("tradingViewWebhookMessage", tradingViewWebhookMessage, "\n")
    alpaca_submit_pair_trade_order(
        tradingViewWebhookMessage["ticker"], buy_alert=False
    )

    return {
        "message": "alert received",
        "tradingViewWebhookMessage": tradingViewWebhookMessage,
    }


@app.route("/alpacapairtradebuyalertnotax", methods=["POST"])
def alpaca_pair_trade_buy_alert_no_tax():
    request = app.current_request
    tradingViewWebhookMessage = request.json_body
    print("tradingViewWebhookMessage", tradingViewWebhookMessage, "\n")
    alpaca_submit_pair_trade_order(
        tradingview_symbol=tradingViewWebhookMessage["ticker"],
        calculate_tax=False,
    )

    return {
        "message": "alert received",
        "tradingViewWebhookMessage": tradingViewWebhookMessage,
    }


@app.route("/alpacapairtradesellalertnotax", methods=["POST"])
def alpaca_pair_trade_sell_alert_no_tax():
    request = app.current_request
    tradingViewWebhookMessage = request.json_body
    print("tradingViewWebhookMessage", tradingViewWebhookMessage, "\n")
    alpaca_submit_pair_trade_order(
        tradingview_symbol=tradingViewWebhookMessage["ticker"],
        calculate_tax=False,
        buy_alert=False,
    )

    return {
        "message": "alert received",
        "tradingViewWebhookMessage": tradingViewWebhookMessage,
    }


# """
# Kucoin Routes
# """


# # Developer function, convert assets in Kucoin subaccount to a stablecoin
# @app.route("/converttostablecoin")
# def transfer_funds_to_stablecoin():
#     # set to sub account 1
#     submit_market_order_custom_percentage(
#         tax_pair, False, account=kucoin_account_names[2]
#     )

#     return {"message": "market order executed"}


# # Developer function, reset Kucoin account to all Stablecoins
# @app.route("/resettostablecoin")
# def reset_funds_to_stablecoin():
#     # SET BASE AND QUOTE CURRENCIES
#     # SET ACCOUNT OR SUBACCOUNT
#     # SET TRUE OR FALSE BUY
#     # SET BUY PERCENTAGE CAPITAL
#     pairToReset: str = "RNDRUP-USDT"
#     account: str = kucoin_account_names[2]
#     submit_market_order_custom_percentage(
#         pairToReset,
#         False,
#         capital_percentage_to_deploy=1,
#         account=account,
#     )

#     return {"message": "market order executed"}


# """
# Save historical Tradingview Alerts
# """


# @app.route("/saveptosmodelalerts", methods=["POST"])
# def save_tradingview_ptos_model_alerts():
#     request = app.current_request
#     tradingViewWebhookMessage = request.json_body
#     table_name = dynamodb_table_names_instance.ptos_model_alerts

#     response = save_item_to_dynamodb_table(
#         table_name=table_name, item=tradingViewWebhookMessage
#     )

#     print("response: ", response)
#     return {"saved": "ptos model alert"}


# @app.route("/saveptossignalalerts", methods=["POST"])
# def save_tradingview_ptos_signal_alerts():
#     request = app.current_request
#     tradingViewWebhookMessage = request.json_body
#     table_name: str = dynamodb_table_names_instance.ptos_signal_alerts

#     response = save_item_to_dynamodb_table(
#         table_name=table_name, item=tradingViewWebhookMessage
#     )

#     print("response: ", response)
#     return {"saved": "ptos signal alert"}


# """
# Main Account routes
# """


# @app.route("/pairtradebuyalert", methods=["POST"])
# def pair_trade_buy_alert():
#     request = app.current_request
#     tradingViewWebhookMessage = request.json_body
#     print("tradingViewWebhookMessage", tradingViewWebhookMessage, "\n")
#     submit_pair_trade_order(
#         tradingViewWebhookMessage["ticker"],
#         capital_to_deploy=0.98,
#     )

#     return {
#         "message": "alert received",
#         "tradingViewWebhookMessage": tradingViewWebhookMessage,
#     }


# @app.route("/pairtradesellalert", methods=["POST"])
# def pair_trade_sell_alert():
#     request = app.current_request
#     tradingViewWebhookMessage = request.json_body
#     print("tradingViewWebhookMessage", tradingViewWebhookMessage, "\n")
#     submit_pair_trade_order(
#         tradingViewWebhookMessage["ticker"],
#         capital_to_deploy=0.98,
#         buy_alert=False,
#     )

#     return {
#         "message": "alert received",
#         "tradingViewWebhookMessage": tradingViewWebhookMessage,
#     }


# @app.route("/pairtradebuyalertnotax", methods=["POST"])
# def pair_trade_buy_alert_no_tax():
#     request = app.current_request
#     tradingViewWebhookMessage = request.json_body
#     print("tradingViewWebhookMessage", tradingViewWebhookMessage, "\n")
#     submit_pair_trade_order(
#         tradingview_symbol=tradingViewWebhookMessage["ticker"],
#         capital_to_deploy=0.98,
#         calculate_tax=False,
#     )

#     return {
#         "message": "alert received",
#         "tradingViewWebhookMessage": tradingViewWebhookMessage,
#     }


# """
# Sub Account 1 routes
# """


# @app.route("/sub1pairtradebuyalert", methods=["POST"])
# def sub_1_pair_trade_buy_alert():
#     request = app.current_request
#     tradingViewWebhookMessage = request.json_body
#     print("tradingViewWebhookMessage", tradingViewWebhookMessage, "\n")
#     submit_pair_trade_order(
#         tradingViewWebhookMessage["ticker"],
#         capital_to_deploy=0.98,
#         account=kucoin_account_names[1],
#     )

#     return {
#         "message": "alert received",
#         "tradingViewWebhookMessage": tradingViewWebhookMessage,
#     }


# @app.route("/sub1pairtradesellalert", methods=["POST"])
# def sub_1_pair_trade_sell_alert():
#     request = app.current_request
#     tradingViewWebhookMessage = request.json_body
#     print("tradingViewWebhookMessage", tradingViewWebhookMessage, "\n")
#     submit_pair_trade_order(
#         tradingViewWebhookMessage["ticker"],
#         capital_to_deploy=0.98,
#         buy_alert=False,
#         account=kucoin_account_names[1],
#     )

#     return {
#         "message": "alert received",
#         "tradingViewWebhookMessage": tradingViewWebhookMessage,
#     }


# @app.route("/sub1pairtradebuyalertnotax", methods=["POST"])
# def sub_1_pair_trade_buy_alert_no_tax():
#     request = app.current_request
#     tradingViewWebhookMessage = request.json_body
#     print("tradingViewWebhookMessage", tradingViewWebhookMessage, "\n")
#     submit_pair_trade_order(
#         tradingview_symbol=tradingViewWebhookMessage["ticker"],
#         capital_to_deploy=0.98,
#         calculate_tax=False,
#         account=kucoin_account_names[1],
#     )

#     return {
#         "message": "alert received",
#         "tradingViewWebhookMessage": tradingViewWebhookMessage,
#     }


# @app.route("/sub1pairtradesellalertnotax", methods=["POST"])
# def sub_1_pair_trade_sell_alert_no_tax():
#     request = app.current_request
#     tradingViewWebhookMessage = request.json_body
#     print("tradingViewWebhookMessage", tradingViewWebhookMessage, "\n")
#     submit_pair_trade_order(
#         tradingview_symbol=tradingViewWebhookMessage["ticker"],
#         capital_to_deploy=0.98,
#         calculate_tax=False,
#         buy_alert=False,
#         account=kucoin_account_names[1],
#     )

#     return {
#         "message": "alert received",
#         "tradingViewWebhookMessage": tradingViewWebhookMessage,
#     }


# """
# Sub Account 2 routes
# """


# @app.route("/sub2pairtradebuyalert", methods=["POST"])
# def sub_2_pair_trade_buy_alert():
#     request = app.current_request
#     tradingViewWebhookMessage = request.json_body
#     print("tradingViewWebhookMessage", tradingViewWebhookMessage, "\n")
#     submit_pair_trade_order(
#         tradingViewWebhookMessage["ticker"],
#         capital_to_deploy=0.98,
#         account=kucoin_account_names[2],
#     )

#     return {
#         "message": "alert received",
#         "tradingViewWebhookMessage": tradingViewWebhookMessage,
#     }


# @app.route("/sub2pairtradesellalert", methods=["POST"])
# def sub_2_pair_trade_sell_alert():
#     request = app.current_request
#     tradingViewWebhookMessage = request.json_body
#     print("tradingViewWebhookMessage", tradingViewWebhookMessage, "\n")
#     submit_pair_trade_order(
#         tradingViewWebhookMessage["ticker"],
#         capital_to_deploy=0.98,
#         buy_alert=False,
#         account=kucoin_account_names[2],
#     )

#     return {
#         "message": "alert received",
#         "tradingViewWebhookMessage": tradingViewWebhookMessage,
#     }


# @app.route("/sub2pairtradebuyalertnotax", methods=["POST"])
# def sub_2_pair_trade_buy_alert_no_tax():
#     request = app.current_request
#     tradingViewWebhookMessage = request.json_body
#     print("tradingViewWebhookMessage", tradingViewWebhookMessage, "\n")
#     submit_pair_trade_order(
#         tradingview_symbol=tradingViewWebhookMessage["ticker"],
#         capital_to_deploy=0.98,
#         calculate_tax=False,
#         account=kucoin_account_names[2],
#     )

#     return {
#         "message": "alert received",
#         "tradingViewWebhookMessage": tradingViewWebhookMessage,
#     }


# @app.route("/sub2pairtradesellalertnotax", methods=["POST"])
# def sub_2_pair_trade_sell_alert_no_tax():
#     request = app.current_request
#     tradingViewWebhookMessage = request.json_body
#     print("tradingViewWebhookMessage", tradingViewWebhookMessage, "\n")
#     submit_pair_trade_order(
#         tradingview_symbol=tradingViewWebhookMessage["ticker"],
#         capital_to_deploy=0.98,
#         calculate_tax=False,
#         buy_alert=False,
#         account=kucoin_account_names[2],
#     )

#     return {
#         "message": "alert received",
#         "tradingViewWebhookMessage": tradingViewWebhookMessage,
#     }


# @app.route("/sub3pairtradebuyalertnotax", methods=["POST"])
# def sub_3_pair_trade_buy_alert_no_tax():
#     request = app.current_request
#     tradingViewWebhookMessage = request.json_body
#     print("tradingViewWebhookMessage", tradingViewWebhookMessage, "\n")
#     submit_pair_trade_order(
#         tradingview_symbol=tradingViewWebhookMessage["ticker"],
#         capital_to_deploy=0.98,
#         calculate_tax=False,
#         account=kucoin_account_names[3],
#     )

#     return {
#         "message": "alert received",
#         "tradingViewWebhookMessage": tradingViewWebhookMessage,
#     }


# @app.route("/sub3pairtradesellalertnotax", methods=["POST"])
# def sub_3_pair_trade_sell_alert_no_tax():
#     request = app.current_request
#     tradingViewWebhookMessage = request.json_body
#     print("tradingViewWebhookMessage", tradingViewWebhookMessage, "\n")
#     submit_pair_trade_order(
#         tradingview_symbol=tradingViewWebhookMessage["ticker"],
#         capital_to_deploy=0.98,
#         calculate_tax=False,
#         buy_alert=False,
#         account=kucoin_account_names[3],
#     )

#     return {
#         "message": "alert received",
#         "tradingViewWebhookMessage": tradingViewWebhookMessage,
#     }


# @app.route("/sub4pairtradebuyalertnotax", methods=["POST"])
# def sub_4_pair_trade_buy_alert_no_tax():
#     request = app.current_request
#     tradingViewWebhookMessage = request.json_body
#     print("tradingViewWebhookMessage", tradingViewWebhookMessage, "\n")
#     submit_pair_trade_order(
#         tradingview_symbol=tradingViewWebhookMessage["ticker"],
#         capital_to_deploy=0.98,
#         calculate_tax=False,
#         account=kucoin_account_names[4],
#     )

#     return {
#         "message": "alert received",
#         "tradingViewWebhookMessage": tradingViewWebhookMessage,
#     }


# @app.route("/sub4pairtradesellalertnotax", methods=["POST"])
# def sub_4_pair_trade_sell_alert_no_tax():
#     request = app.current_request
#     tradingViewWebhookMessage = request.json_body
#     print("tradingViewWebhookMessage", tradingViewWebhookMessage, "\n")
#     submit_pair_trade_order(
#         tradingview_symbol=tradingViewWebhookMessage["ticker"],
#         capital_to_deploy=0.98,
#         calculate_tax=False,
#         buy_alert=False,
#         account=kucoin_account_names[4],
#     )

#     return {
#         "message": "alert received",
#         "tradingViewWebhookMessage": tradingViewWebhookMessage,
#     }
