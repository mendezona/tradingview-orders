import json
import os
from datetime import datetime, timedelta, timezone

from upstash_qstash import Client


def alpaca_schedule_price_check_at_next_interval_cron_job(
    ticker: str, price: str, interval_minutes: str
):
    """
    Schedules a cron job to check the price at the next defined interval

    Parameters:
    - ticker: The stock ticker symbol
    - price: Price of the TradingView alert
    - interval_minutes: The interval in minutes defined by the TradingView
    alert
    """

    print(
        f"Beginning cron job with ticker: {ticker}, price: {price}, and interval: {interval_minutes} minutes"  # noqa: E501
    )

    # Convert price and interval_minutes to appropriate types
    try:
        price = float(price)
        interval_minutes = int(interval_minutes)
    except ValueError as e:
        print(f"Error converting inputs: {e}")
        raise

    print(
        f"Scheduling cron job with ticker: {ticker}, price: {price}, and interval: {interval_minutes} minutes"  # noqa: E501
    )

    QSTASH_TOKEN: str | None = os.getenv("QSTASH_TOKEN")
    AWS_LAMBDA_ENDPOINT: str | None = os.getenv("AWS_LAMBDA_ENDPOINT")

    # Current UTC time
    now: datetime = datetime.now(timezone.utc)
    print(f"Current UTC time: {now}")

    # Get the next interval time
    next_time: datetime = alpaca_get_next_interval_time(now, interval_minutes)

    print(f"Next scheduled time: {next_time}")

    # Schedule the job using qstash
    client = Client(token=QSTASH_TOKEN)
    job_data: dict[str, str] = {"ticker": ticker, "price": price}

    response = client.schedule(
        destination=f"{AWS_LAMBDA_ENDPOINT}/compare-price",
        body=json.dumps(job_data),
        delay=(next_time - now).total_seconds(),  # Delay in seconds
        method="POST",
        headers={"Content-Type": "application/json"},
    )

    if response.status_code == 201:
        print("Cron job scheduled successfully")
    else:
        print(
            f"Failed to schedule cron job: {response.status_code}, {response.text}"  # noqa: E501
        )
        raise Exception("Failed to schedule cron job")


def alpaca_get_next_interval_time(
    now: datetime, interval_minutes: int
) -> datetime:
    """
    Finds the next interval time for a cron job for extended hours trading

    Parameters:
    - now: The time of the current execution
    - interval_minutes: The interval in minutes defined by the TradingView
    alert

    Returns:
    - A datetime object representing the next time to schedule the cron job
    """

    # Extended US trading hours in Eastern Time (ET)
    trading_start = 4 * 60  # 4:00 AM in minutes
    trading_end = 19 * 60 + 45  # 7:45 PM in minutes

    print(
        f"Trading start: {trading_start} minutes, Trading end: {trading_end} minutes"  # noqa: E501
    )

    # Calculate the next interval time within the trading day
    for minutes in range(trading_start, trading_end, interval_minutes):
        hours: int = minutes // 60
        mins: int = minutes % 60
        interval_time = now.replace(
            hour=hours, minute=mins, second=0, microsecond=0
        )

        # If the interval time is after the current time, it is a valid
        # next interval
        if interval_time > now:
            print(f"Next interval time: {interval_time}")
            return interval_time

    # If all times have passed today, schedule for the first interval
    # tomorrow at 4:15 AM
    next_time: datetime = now.replace(
        hour=4, minute=15, second=0, microsecond=0
    ) + timedelta(days=1)
    print("All times have passed today, scheduling for 4:15 AM tomorrow")
    return next_time
