from decimal import Decimal

import pytz

# Developer Constants
development_mode = False

# General finance constants
country_personal_tax_rate: Decimal = 0.42  # "<insert> tax rate"

tax_rate: Decimal = country_personal_tax_rate

capital_to_deploy_percentage: Decimal = 0.33

# TradingView Constants
tradingview_ticker: str = "ticker"

# Timezone constants
berlin_tz = pytz.timezone("Europe/Berlin")
