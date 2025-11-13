# -*- coding: utf-8 -*-
"""
Data Processor - Market Data Processing Module

Version: 2.0.0
Date: 2025-11-12
Phase: Phase 2 - Data Infrastructure & Acquisition

Clean version without encoding issues
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')


class DataProcessor:
    """
    Market data processor
    Handles data cleaning, transformation, and validation
    """

    def __init__(self):
        """Initialize DataProcessor"""
        pass

    def clean_market_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and preprocess market data

        Args:
            data: Raw market data DataFrame

        Returns:
            Cleaned DataFrame
        """
        cleaned_data = data.copy()

        # Handle missing values
        for col in cleaned_data.select_dtypes(include=[np.number]).columns:
            if cleaned_data[col].isnull().any():
                # Forward fill, then backward fill
                cleaned_data[col] = cleaned_data[col].fillna(method='ffill')
                cleaned_data[col] = cleaned_data[col].fillna(method='bfill')

        # Remove duplicates
        cleaned_data = cleaned_data[~cleaned_data.index.duplicated(keep='last')]

        # Sort by date
        cleaned_data = cleaned_data.sort_index()

        return cleaned_data

    def transform_to_monthly(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Transform daily data to monthly frequency

        Args:
            data: DataFrame with daily or irregular frequency

        Returns:
            DataFrame with monthly frequency
        """
        # Resample to monthly, using last value for each month
        monthly_data = data.resample('M').last()

        return monthly_data

    def validate_finra_fields(self, data: pd.DataFrame) -> Tuple[bool, List[str]]:
        """
        Validate FINRA-specific fields

        Args:
            data: DataFrame to validate

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        # Check required columns
        required_cols = ['finra_D', 'finra_CC', 'finra_CM']
        for col in required_cols:
            if col not in data.columns:
                errors.append(f"Missing required column: {col}")

        # Check for negative values
        for col in data.select_dtypes(include=[np.number]).columns:
            if (data[col] < 0).any():
                errors.append(f"Column {col} contains negative values")

        # Check for extreme outliers
        for col in data.select_dtypes(include=[np.number]).columns:
            if len(data[col].dropna()) > 0:
                q1 = data[col].quantile(0.25)
                q3 = data[col].quantile(0.75)
                iqr = q3 - q1
                lower_bound = q1 - 3 * iqr
                upper_bound = q3 + 3 * iqr

                outliers = data[(data[col] < lower_bound) | (data[col] > upper_bound)]
                if len(outliers) > len(data) * 0.1:  # More than 10% outliers
                    errors.append(f"Column {col} has too many outliers ({len(outliers)} points)")

        is_valid = len(errors) == 0
        return is_valid, errors

    def merge_with_validation(self, df1: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:
        """
        Merge two DataFrames with validation

        Args:
            df1: First DataFrame
            df2: Second DataFrame

        Returns:
            Merged DataFrame
        """
        # Ensure both DataFrames have datetime index
        if not isinstance(df1.index, pd.DatetimeIndex):
            df1 = df1.set_index(pd.to_datetime(df1.index))

        if not isinstance(df2.index, pd.DatetimeIndex):
            df2 = df2.set_index(pd.to_datetime(df2.index))

        # Merge on index
        merged_df = pd.merge(df1, df2, left_index=True, right_index=True, how='outer')

        # Sort by date
        merged_df = merged_df.sort_index()

        # Fill missing values
        merged_df = merged_df.fillna(method='ffill').fillna(method='bfill')

        return merged_df

    def generate_data_quality_report(self, data: pd.DataFrame) -> Dict:
        """
        Generate comprehensive data quality report

        Args:
            data: DataFrame to analyze

        Returns:
            Dictionary with quality metrics
        """
        report = {
            'total_rows': len(data),
            'total_columns': len(data.columns),
            'missing_data': {},
            'missing_data_pct': 0,
            'data_types': {},
            'numeric_columns': [],
            'date_columns': [],
            'quality_score': 0,
            'report_date': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        # Analyze missing data
        for col in data.columns:
            missing_count = data[col].isnull().sum()
            missing_pct = (missing_count / len(data)) * 100
            report['missing_data'][col] = {
                'count': int(missing_count),
                'percentage': round(missing_pct, 2)
            }

        report['missing_data_pct'] = round(
            (data.isnull().sum().sum() / (len(data) * len(data.columns))) * 100, 2
        )

        # Analyze data types
        for col in data.columns:
            dtype = str(data[col].dtype)
            report['data_types'][col] = dtype

            if np.issubdtype(data[col].dtype, np.number):
                report['numeric_columns'].append(col)
            elif np.issubdtype(data[col].dtype, np.datetime64):
                report['date_columns'].append(col)

        # Calculate quality score (0-100)
        quality_score = 100

        # Deduct for missing data
        quality_score -= report['missing_data_pct']

        # Deduct for columns with too many missing values
        for col, info in report['missing_data'].items():
            if info['percentage'] > 20:
                quality_score -= (info['percentage'] - 20) * 0.5

        report['quality_score'] = max(0, round(quality_score, 2))

        return report

    def detect_outliers(self, data: pd.DataFrame, method: str = 'zscore',
                       threshold: float = 3.0) -> pd.DataFrame:
        """
        Detect outliers in the data

        Args:
            data: DataFrame to analyze
            method: Outlier detection method ('zscore' or 'iqr')
            threshold: Threshold for outlier detection

        Returns:
            DataFrame with outlier flags
        """
        outlier_data = data.copy()

        for col in data.select_dtypes(include=[np.number]).columns:
            if method == 'zscore':
                # Z-score method
                mean = data[col].mean()
                std = data[col].std()
                z_scores = (data[col] - mean) / std
                outlier_data[f'{col}_outlier'] = np.abs(z_scores) > threshold

            elif method == 'iqr':
                # IQR method
                q1 = data[col].quantile(0.25)
                q3 = data[col].quantile(0.75)
                iqr = q3 - q1
                lower_bound = q1 - threshold * iqr
                upper_bound = q3 + threshold * iqr
                outlier_data[f'{col}_outlier'] = (
                    (data[col] < lower_bound) | (data[col] > upper_bound)
                )

        return outlier_data

    def calculate_moving_averages(self, data: pd.DataFrame,
                                 windows: List[int] = [30, 90, 252]) -> pd.DataFrame:
        """
        Calculate moving averages for numeric columns

        Args:
            data: DataFrame with numeric data
            windows: List of window sizes

        Returns:
            DataFrame with moving averages added
        """
        result_data = data.copy()

        for col in data.select_dtypes(include=[np.number]).columns:
            for window in windows:
                ma_col = f'{col}_ma_{window}'
                result_data[ma_col] = data[col].rolling(window=window, min_periods=1).mean()

        return result_data

    def normalize_data(self, data: pd.DataFrame,
                      method: str = 'zscore') -> pd.DataFrame:
        """
        Normalize data to standard scale

        Args:
            data: DataFrame to normalize
            method: Normalization method ('zscore', 'minmax')

        Returns:
            Normalized DataFrame
        """
        normalized_data = data.copy()

        for col in data.select_dtypes(include=[np.number]).columns:
            if method == 'zscore':
                # Z-score normalization
                mean = data[col].mean()
                std = data[col].std()
                if std > 0:
                    normalized_data[col] = (data[col] - mean) / std

            elif method == 'minmax':
                # Min-max normalization
                min_val = data[col].min()
                max_val = data[col].max()
                if max_val > min_val:
                    normalized_data[col] = (data[col] - min_val) / (max_val - min_val)

        return normalized_data

    def validate_data_consistency(self, data: pd.DataFrame) -> Dict:
        """
        Validate data consistency across columns

        Args:
            data: DataFrame to validate

        Returns:
            Dictionary with validation results
        """
        validation_result = {
            'is_consistent': True,
            'checks': [],
            'warnings': [],
            'errors': []
        }

        # Check 1: Index should be sorted
        if not data.index.is_monotonic_increasing:
            validation_result['warnings'].append('Index is not sorted by date')
            validation_result['checks'].append({
                'check': 'index_sorted',
                'status': 'warning'
            })

        # Check 2: No completely duplicate rows
        if data.index.duplicated().any():
            validation_result['errors'].append('Found duplicate rows')
            validation_result['is_consistent'] = False
            validation_result['checks'].append({
                'check': 'no_duplicates',
                'status': 'error'
            })

        # Check 3: Reasonable value ranges for known metrics
        if 'vix_index' in data.columns:
            vix_col = data['vix_index']
            if (vix_col < 0).any():
                validation_result['errors'].append('VIX index contains negative values')
                validation_result['is_consistent'] = False
            if (vix_col > 100).sum() > len(vix_col) * 0.1:
                validation_result['warnings'].append('VIX index has many extreme values (>100)')

        # Check 4: Positive values where expected
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if 'debt' in col.lower() or 'margin' in col.lower():
                if (data[col] < 0).any():
                    validation_result['errors'].append(f'{col} contains negative values')
                    validation_result['is_consistent'] = False

        return validation_result
