import datetime

import boto3
from boto3.dynamodb.conditions import Attr, Key

dynamodb = boto3.resource("dynamodb")


# Developer function, create DynamoDB instance
def create_new_dynamodb_instance(table_name):
    dynamodb.create_table(
        TableName=table_name,
        KeySchema=[
            {"AttributeName": "ticker", "KeyType": "HASH"},
            {
                "AttributeName": "interval_alertType_time",
                "KeyType": "RANGE",
            },
        ],
        AttributeDefinitions=[
            {
                "AttributeName": "ticker",
                "AttributeType": "S",
            },
            {
                "AttributeName": "interval_alertType_time",
                "AttributeType": "S",
            },
        ],
        ProvisionedThroughput={
            "ReadCapacityUnits": 5,
            "WriteCapacityUnits": 5,
        },
    )

    return "Dynamodb ", table_name, "created"


# Get DynamoDB instance by table name
def get_dynamodb_table(table_name):
    table = dynamodb.Table(table_name)
    return table


# Add concatenated property interval, alert type, and time for querying
def add_interval_alert_type_time(item):
    # Assuming 'interval' and 'alertType' are already present in the item
    interval_alert_type_time = (
        f"{item['interval']}_{item['alertType']}_{item['time']}"
    )
    item["interval_alertType_time"] = interval_alert_type_time
    return item


# Save item to DynamoDB instance
def save_item_to_dynamodb_table(table_name, item):
    modified_item = add_interval_alert_type_time(item)
    table = get_dynamodb_table(table_name)
    table.put_item(Item=modified_item)

    return "Item saved in DynamoDB"


# Query DynamoDb to find instances based on the arguements below
def query_dynamodb_table(
    table_name,
    interval,
    tradingview_ticker,
    alert_type,
    time_range_hours=36,
    limit=20,
):
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(table_name)

    # Calculate the timestamp for the start of the time range (36 hours ago)
    start_timestamp = (
        datetime.datetime.now() - datetime.timedelta(hours=time_range_hours)
    ).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Construct the filter expression
    filter_expression = (
        Key("interval").eq(str(interval))
        & Key("ticker").eq(tradingview_ticker)
        & Key("alertType").eq(alert_type)
        & Attr("time").between(
            start_timestamp,
            datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        )
    )

    # Execute the query without specifying an index
    response = table.scan(
        FilterExpression=filter_expression,
        Limit=limit,  # Adjust the limit as needed
    )

    return response["Items"]
