from chalice import Chalice
from src.exchanges.kucoin.kucoin_utils import submit_pair_trade_order

app = Chalice(app_name="orders")


@app.route("/")
def index():
    return {"hello": "world"}


@app.route("/pairtradealerts", methods=["POST"])
def index():
    request = app.current_request
    tradingViewWebhookMessage = request.json_body
    print("tradingViewWebhookMessage", tradingViewWebhookMessage, "\n")
    submit_pair_trade_order(tradingViewWebhookMessage["ticker"])

    return {
        "message": "alert received",
        "tradingViewWebhookMessage": tradingViewWebhookMessage,
    }
