# import pytest
# import requests_mock
# from chalicelib.src.exchanges.alpaca.alpaca_order_history_utils import (
#     alpaca_check_last_filled_order_type,
# )
# from chalicelib.src.exchanges.alpaca.tests.alpaca_mock_data_objects import (
#     mock_alpaca_get_orders_return,
# )


# @pytest.fixture
# def mock_alpaca_get_credentials(mocker):
#     return mocker.patch(
#         "chalicelib.src.exchanges.alpaca.alpaca_account_utils.alpaca_get_credentials",  # noqa: E501
#         return_value={
#             "key": "dummy_key",
#             "secret": "dummy_secret",
#             "paper": True,
#         },
#     )


# @pytest.fixture
# def mock_account_response():
#     with requests_mock.Mocker() as m:
#         m.get(
#             "https://paper-api.alpaca.markets/v2/orders",
#             json={mock_alpaca_get_orders_return},
#         )
#         yield


# @pytest.mark.parametrize(
#     "expected_result",
#     [
#         (
#             None,
#             None,
#         ),
#     ],
# )
# # def test_alpaca_check_last_filled_order_type(expected_result):
# #     symbol = "AAPL"
# #     account = "test_account"
# #     result: OrderSide | str = alpaca_check_last_filled_order_type(
# #         symbol, account
# #     )

# #     assert result == expected_result
