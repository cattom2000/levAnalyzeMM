# -*- coding: utf-8 -*-
"""
Configuration file for Margin Debt Market Analysis System
Project: levAnalyzeMM
Version: 1.0.0

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

# FRED (Federal Reserve Economic Data) API Configuration
FRED_CONFIG = {
    'api_key': None,  # Set your FRED API key here or via environment variable
    'base_url': 'https://api.stlouisfed.org/fred/series/observations',
    'series_ids': {
        'M2SL': 'M2 Money Stock',
        'DFF': 'Federal Funds Rate',
        'DGS10': '10-Year Treasury Constant Maturity Rate',
        'WILL5000INDFC': 'Wilshire 5000 Total Market Index'
    }
}

# Yahoo Finance Configuration
YAHOO_CONFIG = {
    'base_url': 'https://query1.finance.yahoo.com/v8/finance/chart',
    'symbols': {
        '^VIX': 'CBOE Volatility Index',
        '^GSPC': 'S&P 500 Index'
    }
}

# ============================================================================
# VULNERABILITY INDEX CONFIGURATION
# ============================================================================

# Risk Threshold Configuration
RISK_THRESHOLDS = {
    'extreme_high': 3.0,    # Vulnerability > 3: Extremely high risk
    'high': 1.5,            # Vulnerability > 1.5: High risk
    'medium': 0.5,          # Vulnerability > 0.5: Medium risk
    'low': -3.0,            # Vulnerability < -3: Extremely low risk
    'watch': 1.0            # Vulnerability > 1.0: Watch for risks
}

# Z-Score Calculation Parameters
ZSCORE_CONFIG = {
    'window_size': 252,     # 252 trading days ≈ 12 months
    'min_periods': 63,      # Minimum periods (≈ 3 months)
    'method': 'rolling'     # 'rolling' or 'expanding'
}

# Vulnerability Index Calculation Parameters
VULNERABILITY_CONFIG = {
    'calculation_method': 'difference',  # 'difference', 'ratio', 'weighted'
    'leverage_weight': 0.7,              # For weighted method
    'vix_weight': 0.3,                   # For weighted method
    'max_value': 10.0,                   # Maximum allowed vulnerability value
    'min_value': -10.0                   # Minimum allowed vulnerability value
}

# Crisis Detection Parameters
CRISIS_CONFIG = {
    'crisis_threshold': 2.0,      # Minimum vulnerability for crisis detection
    'min_duration_days': 30,      # Minimum crisis duration
    'early_warning_days': 30      # Days before crisis for early warning
}

# ============================================================================
# VISUALIZATION CONFIGURATION
# ============================================================================

# Chart Colors
CHART_COLORS = {
    'primary': '#1f77b4',        # Blue
    'secondary': '#ff7f0e',      # Orange
    'success': '#2ca02c',        # Green
    'danger': '#d62728',         # Red
    'warning': '#ff7f0e',        # Orange
    'info': '#17a2b8',           # Cyan
    'light': '#f8f9fa',          # Light gray
    'dark': '#343a40'            # Dark gray
}

# Risk Level Colors
RISK_LEVEL_COLORS = {
    '极低风险': '#2ca02c',       # Green
    '低风险': '#8bc34a',         # Light green
    '正常': '#17a2b8',           # Cyan
    '中风险': '#ff9800',         # Orange
    '高风险': '#ff5722',         # Deep orange
    '极高风险': '#d32f2f'        # Red
}

# Chart Configuration
CHART_CONFIG = {
    'figure_size': (12, 8),
    'dpi': 100,
    'style': 'seaborn-v0_8',
    'font_size': 12,
    'title_font_size': 16,
    'legend_font_size': 10
}

# ============================================================================
# BACKTESTING CONFIGURATION
# ============================================================================

# Backtest Parameters
BACKTEST_CONFIG = {
    'initial_capital': 100000.0,      # Initial capital for backtesting
    'transaction_cost': 0.001,        # Transaction cost (0.1%)
    'entry_threshold': 1.5,           # Default entry threshold
    'exit_threshold': 0.5,            # Default exit threshold
    'max_position': 1.0,              # Maximum position size
    'min_position': 0.0               # Minimum position size
}

# Performance Metrics
PERFORMANCE_CONFIG = {
    'risk_free_rate': 0.02,           # Risk-free rate (2%)
    'benchmark_symbol': '^GSPC',      # S&P 500 as benchmark
    'rebalance_frequency': 'M'        # Monthly rebalancing
}

# ============================================================================
# SYSTEM CONFIGURATION
# ============================================================================

# Logging Configuration
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': 'logs/levAnalyzeMM.log',
    'max_size_mb': 100,
    'backup_count': 5
}

# Cache Configuration
CACHE_CONFIG = {
    'enabled': True,
    'ttl_hours': 24,
    'directory': 'cache',
    'max_size_mb': 500
}

# Database Configuration (if needed)
DATABASE_CONFIG = {
    'type': 'sqlite',                 # 'sqlite', 'postgresql', 'mysql'
    'path': 'data/levAnalyzeMM.db',
    'backup_enabled': True,
    'backup_interval_hours': 24
}

# ============================================================================
# APPLICATION CONFIGURATION
# ============================================================================

# Streamlit Configuration
APP_CONFIG = {
    'title': 'Margin Debt Market Analysis System',
    'description': 'Advanced Market Risk Analysis via Vulnerability Index',
    'version': '1.0.0',
    'author': 'levAnalyzeMM Team',
    'page_icon': '📊',
    'layout': 'wide',
    'initial_sidebar_state': 'expanded'
}

# Export Configuration
EXPORT_CONFIG = {
    'formats': ['csv', 'xlsx', 'json'],
    'default_format': 'csv',
    'include_metadata': True,
    'date_format': '%Y-%m-%d',
    'decimal_places': 4
}

# ============================================================================
# VALIDATION CONFIGURATION
# ============================================================================

# Data Validation Rules
VALIDATION_CONFIG = {
    'max_data_gap_days': 90,          # Maximum allowed data gap
    'min_data_points': 50,            # Minimum data points required
    'outlier_threshold': 3.0,         # Standard deviations for outlier detection
    'data_freshness_days': 30         # Maximum data age in days
}

# Algorithm Validation Parameters
ALGORITHM_CONFIG = {
    'max_execution_time': 10.0,       # Maximum algorithm execution time (seconds)
    'min_test_coverage': 0.8,         # Minimum test coverage (80%)
    'performance_tolerance': 0.05,    # Performance tolerance (5%)
    'accuracy_threshold': 0.95        # Accuracy threshold (95%)
}

# ============================================================================
# END OF CONFIGURATION
# ============================================================================

# Export all configuration dictionaries
__all__ = [
    'FINRA_CONFIG',
    'FRED_CONFIG',
    'YAHOO_CONFIG',
    'RISK_THRESHOLDS',
    'ZSCORE_CONFIG',
    'VULNERABILITY_CONFIG',
    'CRISIS_CONFIG',
    'CHART_COLORS',
    'RISK_LEVEL_COLORS',
    'CHART_CONFIG',
    'BACKTEST_CONFIG',
    'PERFORMANCE_CONFIG',
    'LOGGING_CONFIG',
    'CACHE_CONFIG',
    'DATABASE_CONFIG',
    'APP_CONFIG',
    'EXPORT_CONFIG',
    'VALIDATION_CONFIG',
    'ALGORITHM_CONFIG'
]
