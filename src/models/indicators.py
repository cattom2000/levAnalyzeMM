# -*- coding: utf-8 -*-
"""
Market Indicators Module

Version: 2.0.0
Date: 2025-11-12
Phase: Phase 3 - Calculation Engine Development

Market indicators and vulnerability index calculations
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')


class VulnerabilityIndex:
    """
    Vulnerability Index Calculator

    Calculates market vulnerability based on margin debt and VIX indicators
    Formula: Vulnerability Index = Leverage_ZScore - VIX_ZScore
    """

    def __init__(self):
        """Initialize VulnerabilityIndex"""
        pass

    def calculate_zscore(self, series: pd.Series, window: int = 252,
                        min_periods: int = 63) -> pd.Series:
        """
        Calculate rolling Z-score

        Args:
            series: Input time series
            window: Rolling window size (default 252 days = 1 year)
            min_periods: Minimum periods required

        Returns:
            Z-score series
        """
        # Calculate rolling mean and std
        rolling_mean = series.rolling(window=window, min_periods=min_periods).mean()
        rolling_std = series.rolling(window=window, min_periods=min_periods).std()

        # Calculate Z-score
        zscore = (series - rolling_mean) / rolling_std

        return zscore

    def calculate_vulnerability_index(self, data: pd.DataFrame,
                                     leverage_ratio: pd.Series) -> pd.Series:
        """
        Calculate vulnerability index

        Formula: Vulnerability Index = Leverage_ZScore - VIX_ZScore

        Args:
            data: Market data DataFrame
            leverage_ratio: Market leverage ratio series

        Returns:
            Vulnerability index series
        """
        # Calculate Z-scores
        leverage_zscore = self.calculate_zscore(leverage_ratio)

        vix_zscore = None
        if 'vix_index' in data.columns:
            vix_zscore = self.calculate_zscore(data['vix_index'])
        else:
            # If VIX not available, use a constant or create dummy VIX
            vix_zscore = pd.Series(0, index=leverage_ratio.index)

        # Calculate vulnerability index
        vulnerability_index = leverage_zscore - vix_zscore

        return vulnerability_index

    def classify_risk_level(self, vulnerability_index: pd.Series,
                           thresholds: Optional[Dict] = None) -> pd.Series:
        """
        Classify risk levels based on vulnerability index

        Args:
            vulnerability_index: Vulnerability index series
            thresholds: Risk threshold dictionary

        Returns:
            Risk level series (low, medium, high, extreme_high)
        """
        if thresholds is None:
            thresholds = {
                'extreme_high': 3.0,
                'high': 1.5,
                'low': -3.0
            }

        # Create risk level classification
        risk_levels = pd.Series('medium', index=vulnerability_index.index)

        risk_levels[vulnerability_index >= thresholds['extreme_high']] = 'extreme_high'
        risk_levels[(vulnerability_index >= thresholds['high']) &
                   (vulnerability_index < thresholds['extreme_high'])] = 'high'
        risk_levels[vulnerability_index <= thresholds['low']] = 'low'

        return risk_levels

    def get_risk_summary(self, vulnerability_index: pd.Series,
                        risk_levels: pd.Series) -> Dict:
        """
        Get risk summary statistics

        Args:
            vulnerability_index: Vulnerability index series
            risk_levels: Risk level series

        Returns:
            Dictionary with risk summary
        """
        summary = {
            'mean_vulnerability': float(vulnerability_index.mean()),
            'std_vulnerability': float(vulnerability_index.std()),
            'min_vulnerability': float(vulnerability_index.min()),
            'max_vulnerability': float(vulnerability_index.max()),
            'current_vulnerability': float(vulnerability_index.iloc[-1]) if len(vulnerability_index) > 0 else 0,
            'current_risk_level': risk_levels.iloc[-1] if len(risk_levels) > 0 else 'medium',
            'risk_distribution': risk_levels.value_counts().to_dict(),
            'extreme_high_periods': int((risk_levels == 'extreme_high').sum()),
            'high_risk_periods': int((risk_levels == 'high').sum()),
            'low_risk_periods': int((risk_levels == 'low').sum()),
        }

        return summary

    def detect_crisis_periods(self, vulnerability_index: pd.Series,
                             threshold: float = 2.0,
                             min_duration: int = 3) -> pd.DataFrame:
        """
        Detect crisis periods from vulnerability index

        Args:
            vulnerability_index: Vulnerability index series
            threshold: Threshold for crisis detection
            min_duration: Minimum duration in periods

        Returns:
            DataFrame with crisis periods
        """
        # Identify crisis periods
        crisis_mask = vulnerability_index > threshold

        # Find start and end of crisis periods
        crisis_periods = []
        in_crisis = False
        start_idx = None

        for idx, is_crisis in crisis_mask.items():
            if is_crisis and not in_crisis:
                # Start of crisis
                in_crisis = True
                start_idx = idx
            elif not is_crisis and in_crisis:
                # End of crisis
                in_crisis = False
                end_idx = idx

                # Check if crisis is long enough
                duration = (end_idx - start_idx).days
                if duration >= min_duration:
                    max_vuln = vulnerability_index[start_idx:end_idx].max()
                    crisis_periods.append({
                        'start_date': start_idx,
                        'end_date': end_idx,
                        'duration_days': duration,
                        'max_vulnerability': max_vuln
                    })

        # Handle case where data ends during crisis
        if in_crisis and start_idx is not None:
            end_idx = vulnerability_index.index[-1]
            duration = (end_idx - start_idx).days
            max_vuln = vulnerability_index[start_idx:].max()
            crisis_periods.append({
                'start_date': start_idx,
                'end_date': end_idx,
                'duration_days': duration,
                'max_vulnerability': max_vuln
            })

        # Convert to DataFrame
        if crisis_periods:
            crisis_df = pd.DataFrame(crisis_periods)
            crisis_df.set_index('start_date', inplace=True)
            return crisis_df
        else:
            return pd.DataFrame()


class MarketIndicators:
    """
    Market Indicators Calculator

    Calculates various market health indicators
    """

    def __init__(self):
        """Initialize MarketIndicators"""
        pass

    def calculate_market_momentum(self, data: pd.DataFrame) -> pd.Series:
        """
        Calculate market momentum indicator

        Args:
            data: Market data DataFrame

        Returns:
            Momentum series
        """
        if 'sp500_index' in data.columns:
            # Calculate 12-month momentum
            momentum = data['sp500_index'].pct_change(periods=12)
            return momentum
        else:
            return pd.Series(index=data.index, dtype=float)

    def calculate_volatility_regime(self, data: pd.DataFrame,
                                   window: int = 63) -> pd.Series:
        """
        Calculate volatility regime (high/low volatility periods)

        Args:
            data: Market data DataFrame
            window: Rolling window for volatility calculation

        Returns:
            Volatility regime series
        """
        if 'vix_index' in data.columns:
            # Calculate rolling volatility
            rolling_vol = data['vix_index'].rolling(window=window).mean()

            # Classify as high/low volatility
            vol_threshold = rolling_vol.quantile(0.7)
            volatility_regime = pd.Series('low', index=data.index)
            volatility_regime[data['vix_index'] > vol_threshold] = 'high'

            return volatility_regime
        else:
            return pd.Series(index=data.index, dtype=str)

    def calculate_leverage_cycle(self, data: pd.DataFrame) -> Dict[str, pd.Series]:
        """
        Calculate leverage cycle indicators

        Args:
            data: Market data DataFrame

        Returns:
            Dictionary of leverage cycle indicators
        """
        indicators = {}

        if 'margin_debt' in data.columns:
            # Leverage acceleration (change in leverage)
            indicators['leverage_acceleration'] = data['margin_debt'].diff()

            # Leverage trend (12-month average)
            indicators['leverage_trend'] = data['margin_debt'].rolling(12).mean()

        return indicators


# ==================== 便捷函数 ====================

def get_vulnerability_index() -> VulnerabilityIndex:
    """
    获取VulnerabilityIndex实例的便捷函数

    Returns:
        VulnerabilityIndex实例
    """
    return VulnerabilityIndex()


def get_market_indicators() -> MarketIndicators:
    """
    获取MarketIndicators实例的便捷函数

    Returns:
        MarketIndicators实例
    """
    return MarketIndicators()
