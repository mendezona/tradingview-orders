from chalice import Chalice
from src.exchanges.kucoin.kucoin_utils import submit_pair_trade_order

app = Chalice(app_name="orders")


@app.route("/")
def index():
    return {"hello": "world"}


@app.route("/pairtradebuyalert", methods=["POST"])
def index():
    request = app.current_request
    tradingViewWebhookMessage = request.json_body
    print("tradingViewWebhookMessage", tradingViewWebhookMessage, "\n")
    submit_pair_trade_order(tradingViewWebhookMessage["ticker"])

    return {
        "message": "alert received",
        "tradingViewWebhookMessage": tradingViewWebhookMessage,
    }


@app.route("/pairtradesellalert", methods=["POST"])
def index():
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
def index():
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
def index():
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
