# -*- coding: utf-8 -*-
"""
Data Fetcher - Multi-Source Market Data Acquisition Module

Version: 2.0.0
Date: 2025-11-12
Phase: Phase 2 - Data Infrastructure & Acquisition

Clean version without encoding issues
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union
import yfinance as yf
from fredapi import Fred
from cachetools import TTLCache
import warnings
warnings.filterwarnings('ignore')

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

# Custom Exceptions
class DataSourceError(Exception):
    """Data source error"""
    pass

class DataFormatError(Exception):
    """Data format error"""
    pass


class DataFetcher:
    """
    Multi-source market data fetcher
    Supports FINRA, FRED, and Yahoo Finance
    """

    def __init__(self, cache_enabled: bool = True):
        """Initialize DataFetcher"""
        self.cache_enabled = cache_enabled
        self.cache = TTLCache(maxsize=100, ttl=3600)  # 1 hour cache

        # Initialize FRED client
        fred_api_key = os.getenv('FRED_API_KEY')
        if fred_api_key:
            self.fred_client = Fred(api_key=fred_api_key)
        else:
            self.fred_client = None
            print("Warning: FRED_API_KEY not set. FRED data will not be available.")

    def _get_cache_key(self, prefix: str, **kwargs) -> str:
        """Generate cache key"""
        return f"{prefix}_{hash(str(sorted(kwargs.items())))}"

    def _save_to_cache(self, key: str, data):
        """Save data to cache"""
        if self.cache_enabled:
            self.cache[key] = data

    def _get_from_cache(self, key: str):
        """Get data from cache"""
        if self.cache_enabled:
            return self.cache.get(key)
        return None

    def clear_cache(self) -> int:
        """Clear cache"""
        if self.cache_enabled:
            count = len(self.cache)
            self.cache.clear()
            return count
        return 0

    def load_finra_data(self) -> pd.DataFrame:
        """
        Load FINRA margin debt data from CSV file

        Returns:
            DataFrame with FINRA margin debt statistics
        """
        cache_key = self._get_cache_key("finra_data")
        cached_data = self._get_from_cache(cache_key)

        if cached_data is not None:
            return cached_data

        file_path = config.FINRA_CONFIG['data_file']

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"FINRA data file not found: {file_path}")

        try:
            # Load CSV file
            df = pd.read_csv(file_path)

            # Validate columns
            expected_columns = list(config.FINRA_CONFIG['columns'].keys())
            missing_columns = [col for col in expected_columns if col not in df.columns]

            if missing_columns:
                raise DataFormatError(
                    f"FINRA data missing columns: {missing_columns}"
                    f"Expected: {expected_columns}"
                )

            # Rename columns
            df = df.rename(columns=config.FINRA_CONFIG['columns'])

            # Parse Year-Month column
            if 'Year-Month' in df.columns:
                df['date'] = pd.to_datetime(df['Year-Month'], format='%Y-%m')
                df = df.set_index('date')
                df = df.drop('Year-Month', axis=1)

            # Ensure numeric types
            for col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

            # Save to cache
            self._save_to_cache(cache_key, df)

            return df

        except Exception as e:
            raise DataSourceError(f"Error loading FINRA data: {str(e)}")

    def fetch_vix_data(self, start_date: str, end_date: str) -> pd.Series:
        """
        Fetch VIX index data from Yahoo Finance

        Args:
            start_date: Start date in 'YYYY-MM-DD' format
            end_date: End date in 'YYYY-MM-DD' format

        Returns:
            Series with VIX index values
        """
        cache_key = self._get_cache_key("vix", start_date=start_date, end_date=end_date)
        cached_data = self._get_from_cache(cache_key)

        if cached_data is not None:
            return cached_data

        try:
            vix = yf.download("^VIX", start=start_date, end=end_date, progress=False)
            if vix.empty:
                raise DataSourceError("No VIX data retrieved")

            vix_series = vix['Close'].dropna()
            self._save_to_cache(cache_key, vix_series)
            return vix_series

        except Exception as e:
            raise DataSourceError(f"Error fetching VIX data: {str(e)}")

    def fetch_sp500_data(self, start_date: str, end_date: str) -> pd.Series:
        """
        Fetch S&P 500 index data from Yahoo Finance

        Args:
            start_date: Start date
            end_date: End date

        Returns:
            Series with S&P 500 index values
        """
        cache_key = self._get_cache_key("sp500", start_date=start_date, end_date=end_date)
        cached_data = self._get_from_cache(cache_key)

        if cached_data is not None:
            return cached_data

        try:
            sp500 = yf.download("^GSPC", start=start_date, end=end_date, progress=False)
            if sp500.empty:
                raise DataSourceError("No S&P 500 data retrieved")

            sp500_series = sp500['Close'].dropna()
            self._save_to_cache(cache_key, sp500_series)
            return sp500_series

        except Exception as e:
            raise DataSourceError(f"Error fetching S&P 500 data: {str(e)}")

    def fetch_m2_money_supply(self, start_date: str, end_date: str) -> pd.Series:
        """
        Fetch M2 money supply from FRED

        Args:
            start_date: Start date
            end_date: End date

        Returns:
            Series with M2 money supply values
        """
        if self.fred_client is None:
            raise DataSourceError("FRED client not initialized")

        cache_key = self._get_cache_key("m2", start_date=start_date, end_date=end_date)
        cached_data = self._get_from_cache(cache_key)

        if cached_data is not None:
            return cached_data

        try:
            m2_series = self.fred_client.get_series('M2SL', start=start_date, end=end_date)
            if m2_series.empty:
                raise DataSourceError("No M2 data retrieved")

            self._save_to_cache(cache_key, m2_series)
            return m2_series

        except Exception as e:
            raise DataSourceError(f"Error fetching M2 money supply: {str(e)}")

    def sync_data_sources(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Synchronize data from multiple sources

        Args:
            data: DataFrame with base data

        Returns:
            DataFrame with synchronized data
        """
        synced_data = data.copy()

        # Calculate derived metrics
        if 'margin_debt' in synced_data.columns and 'market_cap' in synced_data.columns:
            synced_data['leverage_ratio'] = synced_data['margin_debt'] / synced_data['market_cap']

        if 'vix_index' in synced_data.columns:
            synced_data['vix_zscore'] = (
                synced_data['vix_index'] - synced_data['vix_index'].rolling(252).mean()
            ) / synced_data['vix_index'].rolling(252).std()

        return synced_data

    def validate_market_data(self, data: pd.DataFrame) -> Dict:
        """
        Validate market data quality

        Args:
            data: DataFrame to validate

        Returns:
            Dictionary with validation results
        """
        validation_report = {
            'total_rows': len(data),
            'missing_data_pct': 0,
            'outliers_count': 0,
            'quality_score': 0,
            'validation_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        # Calculate missing data percentage
        missing_pct = (data.isnull().sum().sum() / (len(data) * len(data.columns))) * 100
        validation_report['missing_data_pct'] = missing_pct

        # Detect outliers (using 3-sigma rule)
        outlier_count = 0
        for col in data.select_dtypes(include=[np.number]).columns:
            mean = data[col].mean()
            std = data[col].std()
            outliers = ((data[col] - mean).abs() > 3 * std).sum()
            outlier_count += outliers

        validation_report['outliers_count'] = outlier_count

        # Calculate quality score (0-100)
        quality_score = 100
        quality_score -= missing_pct  # Deduct for missing data
        quality_score -= (outlier_count / len(data)) * 10  # Deduct for outliers
        validation_report['quality_score'] = max(0, quality_score)

        return validation_report

    def detect_data_anomalies(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Detect anomalies in market data

        Args:
            data: DataFrame to analyze

        Returns:
            DataFrame with anomaly flags
        """
        anomaly_data = data.copy()

        for col in data.select_dtypes(include=[np.number]).columns:
            # Calculate Z-score
            mean = data[col].mean()
            std = data[col].std()
            z_scores = (data[col] - mean) / std

            # Flag anomalies (|z-score| > 3)
            anomaly_data[f'{col}_anomaly'] = (z_scores.abs() > 3)

        # Overall anomaly flag
        anomaly_cols = [col for col in anomaly_data.columns if col.endswith('_anomaly')]
        anomaly_data['anomaly_flag'] = anomaly_data[anomaly_cols].any(axis=1)

        return anomaly_data

    def fetch_complete_market_dataset(self, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Fetch complete market dataset from all sources

        Args:
            start_date: Start date
            end_date: End date

        Returns:
            DataFrame with all market data
        """
        try:
            # Load FINRA data
            finra_df = self.load_finra_data()

            # Filter FINRA data by date range
            finra_df = finra_df[(finra_df.index >= start_date) & (finra_df.index <= end_date)]

            # Fetch other market data
            vix_data = self.fetch_vix_data(start_date, end_date)
            sp500_data = self.fetch_sp500_data(start_date, end_date)

            # Fetch M2 money supply if FRED is available
            m2_data = None
            if self.fred_client:
                try:
                    m2_data = self.fetch_m2_money_supply(start_date, end_date)
                except Exception as e:
                    print(f"Warning: Could not fetch M2 data: {e}")

            # Combine all data
            combined_data = finra_df.copy()

            # Add VIX data
            vix_monthly = vix_data.resample('M').last()
            combined_data['vix_index'] = vix_monthly

            # Add S&P 500 data
            sp500_monthly = sp500_data.resample('M').last()
            combined_data['sp500_index'] = sp500_monthly

            # Add M2 data if available
            if m2_data is not None:
                m2_monthly = m2_data.resample('M').last()
                combined_data['m2_money_supply'] = m2_monthly

            # Calculate market cap (approximate)
            combined_data['market_cap'] = combined_data['sp500_index'] * 400

            return combined_data

        except Exception as e:
            raise DataSourceError(f"Error fetching complete market dataset: {str(e)}")


def get_data_fetcher(cache_enabled: bool = True) -> DataFetcher:
    """
    Get a DataFetcher instance

    Args:
        cache_enabled: Whether to enable caching

    Returns:
        DataFetcher instance
    """
    return DataFetcher(cache_enabled=cache_enabled)
