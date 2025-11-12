"""
Configuration file for Margin Debt Market Analysis System
yÓ: levAnalyzeMM
H,: 1.0.0

This module contains all configuration settings for data sources,
vulnerability index calculations, and visualization parameters.
"""

# ============================================================================
# DATA SOURCE CONFIGURATION
# ============================================================================

# FINRA Margin Debt Data (provided by user)
FINRA_CONFIG = {
    'data_file': 'datas/margin-statistics.csv',
    'date_column': 'Year-Month',
    'columns': {
        'D': 'finra_D',        # Debit Balances
        'CC': 'finra_CC',      # Cash Credit
        'CM': 'finra_CM'       # Margin Credit
    }
}

# FRED (Federal Reserve Economic Data) Configuration
FRED_CONFIG = {
    'api_key': None,  # Set your FRED API key here or via environment variable
    'series_id': {
        'm2_money_supply': 'M2SL',
        'federal_funds_rate': 'DFF',
        'treasury_10y_rate': 'DGS10',
        'wilshire5000': 'WILL5000INDFC'  # For market cap normalization
    },
    'date_format': '%Y-%m-%d'
}

# Yahoo Finance Configuration
YAHOO_FINANCE_CONFIG = {
    'symbols': {
        'sp500_index': '^GSPC',  # S&P 500 Index
        'vix_index': '^VIX'      # VIX Index
    },
    'date_range': {
        'start': '1997-01-01',
        'end': '2025-09-30'
    },
    'interval': '1mo'  # Monthly data
}

# Data Processing Configuration
DATA_CONFIG = {
    'start_date': '1997-01-01',
    'end_date': '2025-09-30',
    'date_column': 'date',
    'cache_enabled': True,
    'cache_ttl_hours': 24,
    'data_coverage_threshold': 0.95  # 95% minimum coverage
}

# ============================================================================
# VULNERABILITY INDEX CONFIGURATION
# ============================================================================

# Z-Score Calculation Parameters
ZSCORE_CONFIG = {
    'window': 252,  # 252 trading days H 12 months
    'min_periods': 126,  # Minimum half-window for calculation
    'standardization_method': 'rolling'
}

# Risk Level Thresholds
RISK_THRESHOLDS = {
    'extreme_high': 3.0,    # Vulnerability > 3: ÿŒi (·´/Í·)
    'high': 1.0,            # Vulnerability > 1: ÿŒi
    'neutral_high': 0.0,    # Vulnerability > 0: -'Oc
    'neutral_low': -1.0,    # Vulnerability < -1: -'O
    'low': -3.0,            # Vulnerability < -3: NŒi (PL/ª`F)
    'extreme_low': -5.0     # Vulnerability < -5: ÅNŒi
}

# Risk Color Mapping (for visualizations)
RISK_COLORS = {
    'N': '#28a745',      # Green
    '-': '#ffc107',      # Yellow
    'ÿ': '#fd7e14',      # Orange
    'Åÿ': '#dc3545'     # Red
}

# Vulnerability Index Configuration
VULNERABILITY_CONFIG = {
    'zscore_window': ZSCORE_CONFIG['window'],
    'risk_thresholds': RISK_THRESHOLDS,
    'risk_colors': RISK_COLORS,
    'calculation_method': 'leverage_z_minus_vix_z',
    'description': 'Vulnerability = Leverage_ZScore - VIX_ZScore'
}

# ============================================================================
# VISUALIZATION CONFIGURATION
# ============================================================================

# Chart Display Options
VIZ_CONFIG = {
    'theme': 'plotly_white',
    'default_height': 600,
    'default_width': 1200,
    'show_confidence_bands': True,
    'show_data_source': True,
    'color_palette': {
        'primary': '#1f77b4',
        'secondary': '#ff7f0e',
        'accent': '#2ca02c',
        'warning': '#d62728'
    }
}

# Interactive Chart Features
INTERACTIVE_CONFIG = {
    'hover_mode': 'x unified',
    'zoom_enabled': True,
    'pan_enabled': True,
    'select_enabled': True,
    'showlegend': True,
    'hoverlabel': {
        'bgcolor': 'rgba(255, 255, 255, 0.9)',
        'bordercolor': 'rgba(0, 0, 0, 0.5)',
        'font_size': 12
    }
}

# Historical Crisis Periods
CRISIS_PERIODS = {
    'íTQ·´': {
        'start': '1999-01-01',
        'end': '2003-12-31',
        'color': 'rgba(255, 0, 0, 0.1)',
        'description': 'dot-com bubble burst'
    },
    '—çq:': {
        'start': '2006-01-01',
        'end': '2010-12-31',
        'color': 'rgba(255, 165, 0, 0.1)',
        'description': 'global financial crisis'
    },
    '´≈≤˚': {
        'start': '2019-01-01',
        'end': '2023-12-31',
        'color': 'rgba(128, 0, 128, 0.1)',
        'description': 'COVID-19 pandemic impact'
    }
}

# ============================================================================
# PERFORMANCE & OPTIMIZATION
# ============================================================================

# Streamlit Configuration
STREAMLIT_CONFIG = {
    'page_title': 'çDYù:ê˚ﬂ',
    'page_icon': '= ',
    'layout': 'wide',
    'initial_sidebar_state': 'expanded',
    'server': {
        'port': 8501,
        'address': '0.0.0.0'
    }
}

# Memory Management
MEMORY_CONFIG = {
    'max_memory_usage_mb': 2048,  # 2GB limit
    'gc_threshold': 700,  # Trigger GC at 70% usage
    'chunk_size': 10000  # Process data in chunks
}

# API Rate Limiting
API_CONFIG = {
    'fred_rate_limit': 120,  # requests per minute
    'yahoo_rate_limit': 60,  # requests per minute
    'retry_attempts': 3,
    'retry_delay_seconds': 1.0
}

# ============================================================================
# CALCULATION METHODS
# ============================================================================

# Leverage Net Calculation: Leverage_Net = D - (CC + CM)
LEVERAGE_CALCULATION = {
    'formula': 'D - (CC + CM)',
    'description': 'Net leverage as difference between debit and credit balances'
}

# Market Leverage Ratio: Margin Debt / S&P500 Market Cap
MARKET_LEVERAGE = {
    'formula': 'margin_debt / sp500_market_cap',
    'threshold_high': 0.15,  # Alert if > 15%
    'description': 'Market leverage ratio'
}

# Money Supply Ratio: Margin Debt / M2
MONEY_SUPPLY_RATIO = {
    'formula': 'margin_debt / m2_money_supply',
    'description': 'Margin debt as percentage of M2 money supply'
}

# Change Rate Calculations
CHANGE_RATES = {
    'monthly_formula': '(value_t / value_{t-1}) - 1',
    'yearly_formula': '(value_t / value_{t-12}) - 1',
    'description': 'Month-over-month and year-over-year change rates'
}

# ============================================================================
# EXPORT & LOGGING
# ============================================================================

# Data Export Options
EXPORT_CONFIG = {
    'formats': ['CSV', 'Excel', 'JSON'],
    'default_format': 'CSV',
    'include_metadata': True,
    'date_format': '%Y-%m-%d'
}

# Logging Configuration
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': 'logs/market_analysis.log',
    'max_file_size_mb': 10,
    'backup_count': 5
}

# ============================================================================
# VALIDATION RULES
# ============================================================================

# Data Quality Thresholds
QUALITY_THRESHOLDS = {
    'missing_data_ratio': 0.05,  # Maximum 5% missing data
    'outlier_std': 3.0,          # Values beyond 3√ are outliers
    'correlation_threshold': 0.7, # Minimum correlation for validation
    'coverage_threshold': 0.95    # 95% data coverage required
}

# Validation Checks
VALIDATION_RULES = {
    'required_columns': ['date', 'margin_debt', 'vix_index'],
    'value_ranges': {
        'margin_debt': (0, None),        # Must be positive
        'vix_index': (8, 80),            # VIX typically 8-80
        'federal_funds_rate': (-5, 50)   # Federal funds rate range
    },
    'date_consistency': True,
    'duplicate_check': True
}

# ============================================================================
# USER INTERFACE SETTINGS
# ============================================================================

# UI Text and Labels
UI_LABELS = {
    'app_title': 'çDYù:ê˚ﬂ',
    'app_subtitle': 'Margin Debt Market Analysis System',
    'disclaimer': ',˚ﬂ≈õY≤åvÓÑÑïD˙Æ',
    'data_sources': 'pneê',
    'last_updated': ' Ù∞',
    'vulnerability_index': '1'p',
    'risk_level': 'ŒiIß',
    'historical_crises': 'ÜÚq:ˆ'
}

# ============================================================================
# CONSTANTS
# ============================================================================

# System Constants
CONSTANTS = {
    'TRADING_DAYS_PER_YEAR': 252,
    'MONTHS_PER_YEAR': 12,
    'WEEKS_PER_YEAR': 52,
    'DATETIME_FORMAT': '%Y-%m-%d',
    'MONTHLY_FREQUENCY': 'M'
}

# Error Messages
ERROR_MESSAGES = {
    'data_not_found': '*~0≈ÅÑpnáˆ˜¿ÂMn',
    'api_error': 'API(1%˜Õ’',
    'calculation_error': '°ó«-—Ô˜¿Âpn(œ',
    'visualization_error': 'Ô∆1%˜¿Âpn<'
}

# Success Messages
SUCCESS_MESSAGES = {
    'data_loaded': 'pn†}ü',
    'calculation_complete': '°óå',
    'visualization_ready': 'Ô∆Ú∆1Í',
    'export_complete': 'pn¸˙å'
}

# ============================================================================
# VERSION INFORMATION
# ============================================================================

__version__ = '1.0.0'
__author__ = 'Claude Code'
__project__ = 'levAnalyzeMM'
__description__ = 'Margin Debt Market Analysis System'

# Export all configuration dictionaries
__all__ = [
    'FINRA_CONFIG',
    'FRED_CONFIG',
    'YAHOO_FINANCE_CONFIG',
    'DATA_CONFIG',
    'VULNERABILITY_CONFIG',
    'VIZ_CONFIG',
    'CRISIS_PERIODS',
    'STREAMLIT_CONFIG',
    'MEMORY_CONFIG',
    'API_CONFIG',
    'LEVERAGE_CALCULATION',
    'MARKET_LEVERAGE',
    'MONEY_SUPPLY_RATIO',
    'CHANGE_RATES',
    'EXPORT_CONFIG',
    'LOGGING_CONFIG',
    'QUALITY_THRESHOLDS',
    'VALIDATION_RULES',
    'UI_LABELS',
    'CONSTANTS',
    'ERROR_MESSAGES',
    'SUCCESS_MESSAGES'
]
