# Mock response for a successful balance retrieval
mock_coin_balance_response: dict[str, any] = {
    "retCode": 0,
    "retMsg": "OK",
    "result": {
        "list": [
            {
                "totalEquity": "4.99938662",
                "accountIMRate": "0",
                "totalMarginBalance": "4.99938662",
                "totalInitialMargin": "0",
                "accountType": "UNIFIED",
                "totalAvailableBalance": "4.99938662",
                "accountMMRate": "0",
                "totalPerpUPL": "0",
                "totalWalletBalance": "4.99938662",
                "accountLTV": "0",
                "totalMaintenanceMargin": "0",
                "coin": [
                    {
                        "availableToBorrow": "",
                        "bonus": "0",
                        "accruedInterest": "0",
                        "availableToWithdraw": "1.25",
                        "totalOrderIM": "0",
                        "equity": "1.25",
                        "totalPositionMM": "0",
                        "usdValue": "1.25018625",
                        "unrealisedPnl": "0",
                        "collateralSwitch": True,
                        "spotHedgingQty": "0",
                        "borrowAmount": "0.000000000000000000",
                        "totalPositionIM": "0",
                        "walletBalance": "1.25",
                        "cumRealisedPnl": "0",
                        "locked": "0",
                        "marginCollateral": True,
                        "coin": "USDC",
                    },
                    {
                        "availableToBorrow": "",
                        "bonus": "0",
                        "accruedInterest": "0",
                        "availableToWithdraw": "3.74775",
                        "totalOrderIM": "0",
                        "equity": "3.74775",
                        "totalPositionMM": "0",
                        "usdValue": "3.74920037",
                        "unrealisedPnl": "0",
                        "collateralSwitch": True,
                        "spotHedgingQty": "0",
                        "borrowAmount": "0.000000000000000000",
                        "totalPositionIM": "0",
                        "walletBalance": "3.74775",
                        "cumRealisedPnl": "0",
                        "locked": "0",
                        "marginCollateral": True,
                        "coin": "USDT",
                    },
                ],
            }
        ]
    },
    "retExtInfo": {},
    "time": 1708100506934,
}