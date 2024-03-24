from decimal import Decimal
from unittest import TestCase, mock
from chalicelib.src.aws.aws_utils import (
    get_last_running_total,
)


class TestGetLastRunningTotal(TestCase):
    @mock.patch("boto3.resource")
    def test_get_last_running_total_specific_asset(self, mock_boto3_resource):
        # Mock DynamoDB Table and response
        mock_table = mock.MagicMock()
        mock_boto3_resource.return_value.Table.return_value = mock_table
        mock_response = {"Items": [{"Asset": "BTC", "RunningTotal": "100.50"}]}
        mock_table.query.return_value = mock_response

        # Call the function
        result = get_last_running_total(table_name="Assets", asset="BTC")

        # Assertions
        mock_table.query.assert_called_once()
        self.assertEqual(result, Decimal("100.50"))

    @mock.patch("boto3.resource")
    def test_get_last_running_total_all_assets(self, mock_boto3_resource):
        # Mock DynamoDB Table and response
        mock_table = mock.MagicMock()
        mock_boto3_resource.return_value.Table.return_value = mock_table
        mock_response = {
            "Items": [{"DateKey": "ALL", "RunningTotal": "1000.75"}]
        }
        mock_table.query.return_value = mock_response

        # Call the function without specifying an asset
        result = get_last_running_total(table_name="Assets")

        # Assertions
        mock_table.query.assert_called_once()
        self.assertEqual(result, Decimal("1000.75"))

    @mock.patch("boto3.resource")
    def test_get_last_running_total_no_items(self, mock_boto3_resource):
        # Mock DynamoDB Table and response for no items found
        mock_table = mock.MagicMock()
        mock_boto3_resource.return_value.Table.return_value = mock_table
        mock_response = {"Items": []}
        mock_table.query.return_value = mock_response

        # Call the function
        result = get_last_running_total(table_name="Assets", asset="BTC")

        # Assertions
        mock_table.query.assert_called_once()
        self.assertEqual(result, Decimal("0"))
