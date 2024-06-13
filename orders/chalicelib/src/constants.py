from decimal import Decimal

import pytz

# Developer Constants
development_mode: bool = False

# General finance constants

# Used for calculating tax on crypto assets
country_personal_income_tax_rate: Decimal = Decimal(0.42)

# Used for calculating tax on stocks
capital_gains_tax_rate: Decimal = Decimal(0.26375)

capital_to_deploy_percentage: Decimal = Decimal(1)

# TradingView Constants
tradingview_ticker: str = "ticker"

# Timezone constants
local_tz = pytz.timezone("Europe/Berlin")
