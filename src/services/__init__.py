# Services module - Note: The following classes are now in models/:
# - VulnerabilityIndex: models.indicators.VulnerabilityIndex
# - MarginDebtCalculator: models.margin_debt_calculator.MarginDebtCalculator

# Import available services from models directory
from ..models.margin_debt_calculator import MarginDebtCalculator, get_margin_debt_calculator
from ..models.indicators import (
    VulnerabilityIndex,
    MarketIndicators,
    get_vulnerability_index,
    get_market_indicators
)

__all__ = [
    'MarginDebtCalculator',
    'get_margin_debt_calculator',
    'VulnerabilityIndex',
    'MarketIndicators',
    'get_vulnerability_index',
    'get_market_indicators'
]
