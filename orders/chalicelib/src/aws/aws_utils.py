from decimal import Decimal
import boto3
from boto3.dynamodb.conditions import Key


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
