import time
from datetime import datetime
from datetime import time as datetime_module_time

import pytz
from chalicelib.src.constants import local_tz


# TO DO - Add unit tests
def is_outside_nasdaq_trading_hours() -> bool:
    """
    Check if current time is outside of normal NASDAQ trading hours (9:30 AM
    to 4:00 PM ET)

    Returns:
    - Boolean, true if outside of normal trading hours
    """
    # Define NASDAQ trading hours (9:30 AM to 4:00 PM ET)
    nasdaq_open_time: time = datetime_module_time(9, 30, 0)
    nasdaq_close_time: time = datetime_module_time(16, 0, 0)

    # Get the current time in ET
    eastern = pytz.timezone("US/Eastern")
    current_time_et: datetime_module_time = datetime.now(eastern).time()

    # Check if current time is outside trading hours
    if (
        current_time_et < nasdaq_open_time
        or current_time_et > nasdaq_close_time
    ):
        print("Outside normal NASDAQ trading hours")
        return True
    else:
        print("Inside normal NASDAQ trading hours")
        return False


# TO DO - Add unit tests
def log_times_in_new_york_and_local_timezone(
    local_timezone=local_tz,
):
    timezone_new_york = pytz.timezone("America/New_York")
    now_utc: datetime = datetime.now(pytz.utc)
    time_in_new_york: datetime = now_utc.astimezone(timezone_new_york)
    time_in_local_timezone: datetime = now_utc.astimezone(local_timezone)

    print(
        f"Current time in New York: {time_in_new_york.strftime('%Y-%m-%d %H:%M:%S')}"  # noqa: E501
    )
    print(
        f"Current time in Berlin: {time_in_local_timezone.strftime('%Y-%m-%d %H:%M:%S')}"  # noqa: E501
    )
    return time_in_new_york, time_in_local_timezone
