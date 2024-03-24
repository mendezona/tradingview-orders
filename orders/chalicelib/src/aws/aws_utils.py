from decimal import ROUND_DOWN, Decimal
from typing import Dict

import boto3
from boto3.dynamodb.conditions import Key
from chalicelib.src.aws.aws_types import AWSDynamoDbItem


def get_last_running_total(
    table_name: str, asset: str = None, gsi_name: str = "DateIndex"
) -> Decimal:
    """
    Calculate the Capital Gains Tax using the running total in the database

    Parameters:
    - table_name: Forcely enable development mode
    - asset: The name of the account to trade with
    - gsi_name: Index name for DynamoDb table

    Returns:
    - A Decimal which is the running total of the CGT amount stored in the
    database for a single asset or an entire trading database
    """

    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(table_name)

    if asset:
        # Query for a specific asset
        response = table.query(
            KeyConditionExpression=Key("Asset").eq(asset),
            ScanIndexForward=False,
            Limit=1,
        )
    else:
        # Query the GSI for the last entry across all assets
        response = table.query(
            IndexName=gsi_name,
            KeyConditionExpression=Key("DateKey").eq("ALL"),
            ScanIndexForward=False,
            Limit=1,
        )

    if response["Items"]:
        last_item = response["Items"][0]
        running_total = Decimal(last_item.get("RunningTotal", 0))
        print("Last running total:", running_total)
        return running_total
    else:
        return Decimal(0)


def save_CGT_amount_to_dynamoDB(
    asset: str,
    transaction_date: str,
    profit: float,
    table_name: str,
    gsi_name: str = "DateIndex",
) -> Dict:
    """
    Add new item to DynamoDb database

    Parameters:
    - asset: The name of the asset
    - transaction_date: Transaction date of trade
    - profit: Profit made from closing trade
    - table_name: DynamoDb table name to save to
    - gsi_name: Index column of DynamoDb database

    Returns:
    - A Decimal which is the running total of the CGT amount stored in the
    database for a single asset or an entire trading database
    """

    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(table_name)

    # Fetch the last entry across all assets using the GSI
    response = table.query(
        IndexName=gsi_name,
        KeyConditionExpression=Key("DateKey").eq("ALL"),
        ScanIndexForward=False,
        Limit=1,
    )

    # Calculate the new running total
    if response["Items"]:
        last_item = response["Items"][0]
        running_total = Decimal(last_item.get("RunningTotal", 0)) + Decimal(
            profit
        )
    else:
        running_total = Decimal(profit)

    # Round to two decimal places
    rounded_profit = Decimal(profit).quantize(
        Decimal("0.01"), rounding=ROUND_DOWN
    )
    rounded_running_total = running_total.quantize(
        Decimal("0.01"), rounding=ROUND_DOWN
    )

    # Prepare the new item with DateKey for the GSI
    new_item: AWSDynamoDbItem = {
        "Asset": asset,
        "TransactionDate": transaction_date,
        "Profit": rounded_profit,
        "RunningTotal": rounded_running_total,
        "DateKey": "ALL",  # Constant value for all items for the GSI
    }

    # Add the new item to the table
    table.put_item(Item=new_item)

    print("New item added to DynamoDB table", new_item)
    return new_item
