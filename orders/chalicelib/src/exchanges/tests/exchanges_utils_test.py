# from datetime import datetime
# from datetime import time as datetime_module_time
# from unittest.mock import MagicMock, patch

# import pytest
# import pytz
# from chalicelib.src.exchanges.exchanges_utils import (
#     is_outside_nasdaq_trading_hours,
#     log_times_in_new_york_and_local_timezone,
# )


# # Helper function to create a datetime object in the US/Eastern timezone
# def create_eastern_time(hour, minute=0, second=0):
#     return datetime_module_time(hour, minute, second)


# # @pytest.mark.parametrize(
# #     "mock_time, expected_result",
# #     [
# #         # Time before NASDAQ opens
# #         (create_eastern_time(9, 29), True),
# #         # Time when NASDAQ is open
# #         (create_eastern_time(10, 0), False),
# #         (create_eastern_time(15, 59), False),
# #         # Time after NASDAQ closes
# #         (create_eastern_time(16, 1), True),
# #     ],
# # )
# # def test_is_outside_nasdaq_trading_hours(mock_time, expected_result):
# #     # Mock datetime to return the specified mock_time
# #     with patch(
# #         "datetime.datetime",
# #         autospec=True,
# #     ) as mock_datetime:
# #         # Create a mock datetime object in the US/Eastern timezone
# #         eastern = pytz.timezone("US/Eastern")
# #         mock_now = datetime(
# #             2023,
# #             1,
# #             1,
# #             mock_time.hour,
# #             mock_time.minute,
# #             mock_time.second,
# #             tzinfo=eastern,
# #         )

# #         # Configure the mock to return our mock_now when now() is called
# #         mock_datetime.now.return_value = mock_now

# #         # Run the function under test
# #         result = is_outside_nasdaq_trading_hours()

# #         # Assert that the result matches our expectation
# #         assert result == expected_result


# @pytest.mark.parametrize(
#     "mock_now,expected_new_york_time,expected_berlin_time",
#     [
#         (
#             datetime(2023, 1, 1, 12, 0, tzinfo=pytz.utc),
#             "Current time in New York: 2023-01-01 07:00:00",
#             "Current time in Berlin: 2023-01-01 13:00:00",
#         ),
#     ],
# )
# @patch(
#     "chalicelib.src.exchanges.exchanges_utils.datetime", autospec=True
# )  # Adjust the path to where datetime is used
# def test_log_times_in_new_york_and_localtimezone(
#     mock_datetime, mock_now, expected_new_york_time, expected_berlin_time
# ):
#     mock_datetime.now.return_value = mock_now
#     new_york_time, berlin_time = log_times_in_new_york_and_local_timezone()

#     assert expected_new_york_time in new_york_time
#     assert expected_berlin_time in berlin_time


# # Assuming log_times_in_new_york_and_berlin now returns the strings instead
# of printing them
# def test_log_times_in_new_york_and_local_timezone(mocker):
#     mock_now = datetime(2023, 1, 1, 12, 0, 0, tzinfo=pytz.utc)
#     mocker.patch("datetime.datetime", autospec=True)
#     mocker.patch(
#         "datetime.datetime.now",
#         return_value=mock_now,
#     )

#     times = log_times_in_new_york_and_local_timezone()
#     expected_new_york_time = "Current time in New York: 2023-01-01 07:00:00"
#     expected_berlin_time = "Current time in Berlin: 2023-01-01 13:00:00"

#     assert expected_new_york_time in times[0]
#     assert expected_berlin_time in times[1]
