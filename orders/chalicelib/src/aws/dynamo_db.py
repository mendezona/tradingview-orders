import datetime

import boto3
from boto3.dynamodb.conditions import Attr, Key

dynamodb = boto3.resource("dynamodb")


# Developer function, create DynamoDB instance
def create_new_dynamodb_instance(table_name: str):
    dynamodb = boto3.resource("dynamodb")

    # Create a new DynamoDB table with a Global Secondary Index
    table = dynamodb.create_table(
        TableName=table_name,
        KeySchema=[
            {
                "AttributeName": "Asset",
                "KeyType": "HASH",
            },  # Partition key: Stock symbol
            {
                "AttributeName": "TransactionDate",
                "KeyType": "RANGE",
            },  # Sort key: Date of the transaction
        ],
        AttributeDefinitions=[
            {
                "AttributeName": "Asset",
                "AttributeType": "S",
            },  # String type for stock symbol
            {
                "AttributeName": "TransactionDate",
                "AttributeType": "S",
            },  # String type for transaction date
            {
                "AttributeName": "DateKey",
                "AttributeType": "S",
            },  # Additional attribute for GSI
        ],
        GlobalSecondaryIndexes=[
            {
                "IndexName": "DateIndex",
                "KeySchema": [
                    {
                        "AttributeName": "DateKey",
                        "KeyType": "HASH",  # Partition key for the GSI
                    },
                    {
                        "AttributeName": "TransactionDate",
                        "KeyType": "RANGE",  # Sort key for the GSI
                    },
                ],
                "Projection": {"ProjectionType": "ALL"},
                "ProvisionedThroughput": {
                    "ReadCapacityUnits": 5,
                    "WriteCapacityUnits": 5,
                },
            }
        ],
        ProvisionedThroughput={
            "ReadCapacityUnits": 5,
            "WriteCapacityUnits": 5,
        },
    )

    # Wait until the table exists.
    table.meta.client.get_waiter("table_exists").wait(TableName=table_name)

    return f"DynamoDB table '{table_name}' created"


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
