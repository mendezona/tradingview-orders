from datetime import datetime

import pytest
import pytz
from chalicelib.src.exchanges.exchanges_utils import (
    is_outside_nasdaq_trading_hours,
)
from requests import patch


@pytest.mark.parametrize(
    "mock_now, expected",
    [
        # Before NASDAQ opens
        (
            datetime(2022, 1, 1, 8, 29, tzinfo=pytz.timezone("US/Eastern")),
            True,
        ),
        # During NASDAQ trading hours
        (
            datetime(2022, 1, 1, 10, 0, tzinfo=pytz.timezone("US/Eastern")),
            False,
        ),
        # After NASDAQ closes
        (
            datetime(2022, 1, 1, 16, 1, tzinfo=pytz.timezone("US/Eastern")),
            True,
        ),
    ],
)
def test_is_outside_nasdaq_trading_hours(mock_now, expected):
    with patch("datetime.datetime") as mock_datetime:
        mock_datetime.now.return_value = mock_now
        mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)

        result = is_outside_nasdaq_trading_hours()
        assert result == expected
