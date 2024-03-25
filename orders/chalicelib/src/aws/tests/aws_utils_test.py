from decimal import ROUND_DOWN, Decimal
from unittest import TestCase, mock
from unittest.mock import MagicMock, patch

import pytest
from chalicelib.src.aws.aws_utils import (
    get_last_running_total,
    save_CGT_amount_to_dynamoDB,
)


class TestGetLastRunningTotal(TestCase):
    @mock.patch("boto3.resource")
    def test_get_last_running_total_specific_asset(self, mock_boto3_resource):
        # Mock DynamoDB Table and response
        mock_table = mock.MagicMock()
        mock_boto3_resource.return_value.Table.return_value = mock_table
        mock_response = {"Items": [{"Asset": "BTC", "RunningTotal": "100.50"}]}
        mock_table.query.return_value = mock_response
        result = get_last_running_total(table_name="Assets", asset="BTC")
        mock_table.query.assert_called_once()
        self.assertEqual(result, Decimal("100.50"))

    @mock.patch("boto3.resource")
    def test_get_last_running_total_all_assets(self, mock_boto3_resource):
        mock_table = mock.MagicMock()
        mock_boto3_resource.return_value.Table.return_value = mock_table
        mock_response = {
            "Items": [{"DateKey": "ALL", "RunningTotal": "1000.75"}]
        }
        mock_table.query.return_value = mock_response
        result = get_last_running_total(table_name="Assets")

        mock_table.query.assert_called_once()
        self.assertEqual(result, Decimal("1000.75"))

    @mock.patch("boto3.resource")
    def test_get_last_running_total_no_items(self, mock_boto3_resource):
        mock_table = mock.MagicMock()
        mock_boto3_resource.return_value.Table.return_value = mock_table
        mock_response = {"Items": []}
        mock_table.query.return_value = mock_response
        result = get_last_running_total(table_name="Assets", asset="BTC")

        mock_table.query.assert_called_once()
        self.assertEqual(result, Decimal("0"))


@pytest.fixture
def mock_dynamodb_resource():
    with patch("boto3.resource") as mock_resource:
        mock_table = MagicMock()
        mock_resource.return_value.Table.return_value = mock_table

        mock_query_response = {
            "Items": [
                {
                    "Asset": "AAPL",
                    "TransactionDate": "2024-03-24",
                    "RunningTotal": "100.00",
                }
            ]
        }

        mock_table.query.return_value = mock_query_response
        mock_table.put_item.return_value = None

        yield mock_table


@pytest.fixture
def create_table(mock_dynamodb_resource):
    """Mocked create_table method. In this context, it's just for setup and
    does not perform any action."""
    table_name = "TestTable"
    return table_name


def test_save_CGT_amount_to_dynamoDB(create_table, mock_dynamodb_resource):
    asset = "AAPL"
    transaction_date = "2024-03-24"
    profit = 200.00
    table_name = create_table

    result = save_CGT_amount_to_dynamoDB(
        asset=asset,
        transaction_date=transaction_date,
        profit=profit,
        table_name=table_name,
    )

    expected_item = {
        "Asset": asset,
        "TransactionDate": transaction_date,
        "Profit": Decimal(profit).quantize(
            Decimal("0.01"), rounding=ROUND_DOWN
        ),
        "RunningTotal": Decimal(300).quantize(
            Decimal("0.01"), rounding=ROUND_DOWN
        ),
        "DateKey": "ALL",
    }
    assert result == expected_item

    mock_dynamodb_resource.put_item.assert_called_once_with(Item=expected_item)
