# -*- coding: utf-8 -*-
"""
pn∑÷!W - çDYù:ê˚ﬂ
Data Fetcher Module for Margin Debt Market Analysis System

#Œ*pnê∑÷:pnÏFREDYahoo FinanceFINRAI
Supports data collection from FRED, Yahoo Finance, FINRA, and other sources.

H,: 1.0.0
Â: 2025-11-12
û∞: Phase 2 - ˙@æΩpn∑÷ (T008-T012)
"""

from typing import Dict, List, Optional, Tuple, Union
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import yfinance as yf
import os
import sys
import logging
from pathlib import Path
import pickle
import hashlib
import time

# Add src to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from fredapi import Fred
except ImportError:
    Fred = None

import config


# ==================== 8{öI ====================

class DataSourceError(Exception):
    """pnêÔ"""
    pass


class RateLimitError(Exception):
    """APIáP6Ô"""
    pass


class DataFormatError(Exception):
    """pn<Ô"""
    pass


class MergeError(Exception):
    """pnvÔ"""
    pass


class SymbolNotFoundError(Exception):
    """°h„*~0Ô"""
    pass


class InsufficientDataError(Exception):
    """pn≥Ô"""
    pass


# ==================== pn∑÷hû∞ ====================

class DataFetcher:
    """
    pn∑÷h
    û∞Œ*pnê∑÷:pnÑü˝
    """

    def __init__(self, cache_enabled: bool = True) -> None:
        """
        Àpn∑÷h

        Args:
            cache_enabled: /&/(X
        """
        self.cache_enabled = cache_enabled
        self.cache_dir = Path("cache")
        self.cache_dir.mkdir(exist_ok=True)
        self.last_fetch: Optional[datetime] = None
        self._fred_client = None
        self._setup_logging()

    def _setup_logging(self) -> None:
        """ænÂ◊"""
        self.logger = logging.getLogger(__name__)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    @property
    def fred_client(self):
        """∑÷FRED¢7ÔˆﬂÀ	"""
        if self._fred_client is None:
            if Fred is None:
                raise ImportError("fredapi not installed. Run: pip install fredapi")
            api_key = config.FRED_CONFIG.get('api_key') or os.getenv('FRED_API_KEY')
            if not api_key:
                self.logger.warning("FRED API key not found. FRED data fetching will fail.")
            self._fred_client = Fred(api_key=api_key)
        return self._fred_client

    # ==================== T008: FINRApn†} ====================

    def load_finra_data(self, file_path: Optional[str] = None) -> pd.DataFrame:
        """
        T008: †}FINRAçDYùpn (,0CSVáˆ)

        Args:
            file_path: CSVáˆÔÑÿ§: 'datas/margin-statistics.csv'

        Returns:
            DataFrame+Â:
            - date: Â (YYYY-MM-DD)
            - finra_D: πYù (øéC)
            - finra_CC: ∞—&77πYù (øéC)
            - finra_CM: ›¡—&77πYù (øéC)
            - margin_debt: çDYù (+finra_D¯)

        Raises:
            FileNotFoundError: pnáˆX(
            DataFormatError: pn<cn
        """
        if file_path is None:
            file_path = config.FINRA_CONFIG['data_file']

        # ¿Âáˆ/&X(
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"FINRApnáˆX(: {file_path}")

        try:
            # ˚÷CSVáˆ
            df = pd.read_csv(file_path)

            # å¡
            expected_columns = list(config.FINRA_CONFIG['columns'].keys())
            missing_columns = [col for col in expected_columns if col not in df.columns]

            if missing_columns:
                raise DataFormatError(
                    f"FINRApnáˆ:≈Å: {missing_columns}"
                    f": {expected_columns}"
                )

            # Õ}Â9MMn
            df = df.rename(columns=config.FINRA_CONFIG['columns'])

            # lbÂ
            date_col = config.FINRA_CONFIG['date_column']
            df[date_col] = pd.to_datetime(df[date_col])
            df = df.rename(columns={date_col: 'date'})

            # ænÂ:"
            df = df.set_index('date').sort_index()

            # ˚†margin_debt+finra_D¯	
            df['margin_debt'] = df['finra_D']

            # lb:øéCUMÇúÅ	
            # FINRApn8Â~éC:UMÅlb
            df['finra_D'] = df['finra_D'] / 1000  # ~0ø
            df['finra_CC'] = df['finra_CC'] / 1000
            df['finra_CM'] = df['finra_CM'] / 1000
            df['margin_debt'] = df['margin_debt'] / 1000

            self.logger.info(f"ü†}FINRApn: {len(df)} a∞UˆÙÙ: {df.index.min()} 0 {df.index.max()}")

            return df

        except Exception as e:
            raise DataFormatError(f"˚÷FINRApnáˆ1%: {e}")

    # ==================== T009: VIXpn∑÷ ====================

    def fetch_vix_data(self, start_date: str, end_date: str) -> pd.Series:
        """
        T009: ∑÷VIXppn

        Args:
            start_date: ÀÂ (YYYY-MM-DD)
            end_date: ”_Â (YYYY-MM-DD)

        Returns:
            Series":Â<:VIXp¶sG	

        Raises:
            DataSourceError: pn∑÷1%
            RateLimitError: APIáP6
        """
        cache_key = f"vix_{start_date}_{end_date}"

        # ¿ÂX
        if self.cache_enabled:
            cached_data = self._get_from_cache(cache_key)
            if cached_data is not None:
                self.logger.info("ŒX†}VIXpn")
                return cached_data

        try:
            # ŒYahoo Finance∑÷VIXpnüÀ:Â¶pn	
            vix = yf.download("^VIX", start=start_date, end=end_date, progress=False)

            if vix.empty:
                raise DataSourceError("VIXpn:zÔ˝ÂÙÖ˙Ô(pnÙ")

            # °ó¶sGŒÂ¶l:¶	
            vix_monthly = vix['Close'].resample('M').mean()

            # lb:Seriesv}:vix_index
            vix_series = pd.Series(vix_monthly.values, index=vix_monthly.index, name='vix_index')

            # Xpn
            if self.cache_enabled:
                self._save_to_cache(cache_key, vix_series)

            self.logger.info(f"ü∑÷VIXpn: {len(vix_series)} *")
            return vix_series

        except Exception as e:
            raise DataSourceError(f"∑÷VIXpn1%: {e}")

    # ==================== T010: :<pn∑÷ ====================

    def fetch_market_cap_data(self, start_date: str, end_date: str) -> pd.DataFrame:
        """
        T010: ∑÷S&P500på<pn

        Args:
            start_date: ÀÂ (YYYY-MM-DD)
            end_date: ”_Â (YYYY-MM-DD)

        Returns:
            DataFrame+:
            - sp500_index: S&P500p
            - sp500_market_cap: S&P500;< (Wilshire 5000)

        Raises:
            DataSourceError: pn∑÷1%
        """
        cache_key = f"market_cap_{start_date}_{end_date}"

        # ¿ÂX
        if self.cache_enabled:
            cached_data = self._get_from_cache(cache_key)
            if cached_data is not None:
                self.logger.info("ŒX†}:<pn")
                return cached_data

        try:
            # ∑÷S&P500ppn
            sp500 = yf.download("^GSPC", start=start_date, end=end_date, progress=False)

            if sp500.empty:
                raise DataSourceError("S&P500ppn:z")

            # °ó¶sG
            sp500_monthly = sp500['Close'].resample('M').mean()

            # ˙”úDataFrame
            result = pd.DataFrame({
                'sp500_index': sp500_monthly
            }, index=sp500_monthly.index)

            # ∑÷Wilshire 5000<pnŒFRED	
            try:
                wilshire_data = self.fetch_fred_data(
                    series_id='WILL5000INDFC',
                    start_date=start_date,
                    end_date=end_date
                )
                result['sp500_market_cap'] = wilshire_data
            except Exception as e:
                self.logger.warning(f"∑÷Wilshire 5000pn1%: {e}")
                # Çú‡’∑÷<(0ó<æn:None
                result['sp500_market_cap'] = np.nan

            # Xpn
            if self.cache_enabled:
                self._save_to_cache(cache_key, result)

            self.logger.info(f"ü∑÷:<pn: {len(result)} *")
            return result

        except Exception as e:
            raise DataSourceError(f"∑÷:<pn1%: {e}")

    # ==================== T011: FREDpn∑÷ ====================

    def fetch_fred_data(self, series_id: str, start_date: str, end_date: str, frequency: str = "m") -> pd.Series:
        """
        T011: ŒFRED API∑÷œNpn

        Args:
            series_id: FRED˚ID (Ç 'M2SL', 'DFF', 'DGS10')
            start_date: ÀÂ (YYYY-MM-DD)
            end_date: ”_Â (YYYY-MM-DD)
            frequency: pnëá ('d'=Â, 'm'=, 'q'=c, 'a'=t)

        Returns:
            Series":Â<:pn

        Raises:
            ValueError: series_id‡H¬p<Ô
            ConnectionError: FRED APIﬁ•1%
            RateLimitError: APIáP6
        """
        cache_key = f"fred_{series_id}_{start_date}_{end_date}_{frequency}"

        # ¿ÂX
        if self.cache_enabled:
            cached_data = self._get_from_cache(cache_key)
            if cached_data is not None:
                self.logger.info(f"ŒX†}FREDpn: {series_id}")
                return cached_data

        try:
            # ŒFRED∑÷pn
            fred_series = self.fred_client.get_series(
                series_id,
                start=start_date,
                end=end_date
            )

            if fred_series.empty:
                raise DataSourceError(f"FREDpn:z: {series_id}")

            # lb:¶ÇúÅ	
            if frequency == 'm' and fred_series.index.freq is None:
                # pnÚœ/¶ÅZ
                fred_monthly = fred_series.resample('M').mean()
            else:
                fred_monthly = fred_series

            # lb:Seriesv}
            result_series = pd.Series(fred_monthly.values, index=fred_monthly.index, name=series_id)

            # Xpn
            if self.cache_enabled:
                self._save_to_cache(cache_key, result_series)

            self.logger.info(f"ü∑÷FREDpn {series_id}: {len(result_series)} a∞U")
            return result_series

        except Exception as e:
            if "Rate limit" in str(e) or "429" in str(e):
                raise RateLimitError(f"FRED APIáP6: {e}")
            else:
                raise DataSourceError(f"∑÷FREDpn1% {series_id}: {e}")

    # ==================== T012: pne˘P (vL˚°) ====================

    def sync_data_sources(self, df: pd.DataFrame, tolerance_days: int = 5) -> pd.DataFrame:
        """
        T012 [P]: e*pnêÑˆÙè

        Args:
            df: +*pnêÑDataFrame
            tolerance_days: ÂπÕ¶ ())

        Returns:
            ˘PÑDataFrameÂ"e

        Example:
            >>> # ìe: ÂÑpn
            >>> df = pd.DataFrame({
            ...     'date': ['2025-01-01', '2025-01-02', '2025-01-03'],
            ...     'sp500': [4500, None, 4510],
            ...     'margin_debt': [None, 0.82, 0.83]
            ... })
            >>> synced = fetcher.sync_data_sources(df)
            >>> # ì˙: Â˘P:1<∞
        """
        try:
            # Çú°	dateGæ"1/Â
            if 'date' in df.columns:
                df = df.set_index('date')

            # n›"/datetime{ã
            if not isinstance(df.index, pd.DatetimeIndex):
                df.index = pd.to_datetime(df.index)

            # ˙åtÑÂÙŒ0'Â	
            start_date = df.index.min()
            end_date = df.index.max()

            # åtÑ¶ÂÙ
            full_date_range = pd.date_range(
                start=start_date.replace(day=1),  # 
                end=end_date,
                freq='M'
            )

            # Õ∞"0åtÑÂÙ
            df_synced = df.reindex(full_date_range)

            # ˘Ppn(MkE{ÆÑÂÓ	
            # ˘éπÕ¶ÖÑpn€L“<
            df_synced = df_synced.interpolate(method='time', limit=tolerance_days)

            # ˚†:1<∞
            df_synced = df_synced.copy()
            for col in df_synced.columns:
                df_synced[f'{col}_missing'] = df_synced[col].isnull()

            # Õn"Â:
            df_synced.index.name = 'date'
            df_synced = df_synced.reset_index()

            self.logger.info(f"pneå: {len(df_synced)} *{len(df_synced.columns)} *Wµ")

            return df_synced

        except Exception as e:
            raise MergeError(f"pne1%: {e}")

    # ==================== pnv;˝p ====================

    def fetch_complete_market_dataset(self, start_date: str, end_date: str) -> pd.DataFrame:
        """
        ∑÷åt:pn∆ (@	pnêv)

        vÂpnê:
        - FINRA: çDYù (margin_debt)
        - FRED: M2'õîT¶˙—)á10t˝:6 á
        - Yahoo: S&P500pS&P500<VIX

        Args:
            start_date: ÀÂ (YYYY-MM-DD)
            end_date: ”_Â (YYYY-MM-DD)

        Returns:
            DataFrame+åt:pn
            : date, sp500_index, sp500_market_cap, vix_index, m2_money_supply,
                federal_funds_rate, treasury_10y_rate, margin_debt, finra_D, finra_CC, finra_CM

        Raises:
            DataSourceError: pnê∑÷1%
            MergeError: pnv1%
        """
        self.logger.info(f"À∑÷åt:pn∆: {start_date} 0 {end_date}")

        try:
            # 1. †}FINRApn
            finra_df = self.load_finra_data()
            finra_df = finra_df[(finra_df.index >= start_date) & (finra_df.index <= end_date)]

            # 2. ∑÷VIXpn
            vix_series = self.fetch_vix_data(start_date, end_date)

            # 3. ∑÷:<pn
            market_cap_df = self.fetch_market_cap_data(start_date, end_date)

            # 4. ∑÷FREDpn*˚	
            fred_series = {}
            fred_configs = [
                ('M2SL', 'm2_money_supply'),
                ('DFF', 'federal_funds_rate'),
                ('DGS10', 'treasury_10y_rate')
            ]

            for series_id, col_name in fred_configs:
                try:
                    fred_series[col_name] = self.fetch_fred_data(series_id, start_date, end_date)
                except Exception as e:
                    self.logger.warning(f"∑÷FREDpn1% {series_id}: {e}")
                    # ˙zSeries
                    fred_series[col_name] = pd.Series(dtype=float, name=col_name)

            # 5. v@	pn
            # ÂFINRApn:˙@‡:É	åtÑˆÙÙ	
            result = finra_df.copy()

            # ˚†v÷pnê
            for col_name, series in fred_series.items():
                if not series.empty:
                    # Serieslb:DataFramevÕ}
                    series_df = pd.DataFrame({col_name: series})
                    # 	Âv
                    result = result.join(series_df, how='outer')

            # ˚†VIXpn
            vix_df = pd.DataFrame({'vix_index': vix_series})
            result = result.join(vix_df, how='outer')

            # ˚†:<pn
            result = result.join(market_cap_df, how='outer')

            # 6. epnêÂ˘P	
            result = self.sync_data_sources(result)

            # 7. pn(œ¿Â
            quality_report = self.validate_market_data(result)
            self.logger.info(f"pn(œ¿Â: (œp {quality_report['quality_score']:.2f}")

            self.logger.info(f"åtpn∆∑÷ü: {len(result)} a∞U{len(result.columns)} *Wµ")
            return result

        except Exception as e:
            raise MergeError(f"∑÷åtpn∆1%: {e}")

    # ==================== X° ====================

    def _get_cache_key(self, key: str) -> str:
        """X."""
        return hashlib.md5(key.encode()).hexdigest()

    def _get_from_cache(self, cache_key: str, max_age_hours: int = 24) -> Optional[pd.DataFrame]:
        """ŒX∑÷pn"""
        try:
            cache_file = self.cache_dir / f"{self._get_cache_key(cache_key)}.pkl"
            if cache_file.exists():
                file_age = time.time() - cache_file.stat().st_mtime
                if file_age < max_age_hours * 3600:
                    with open(cache_file, 'rb') as f:
                        return pickle.load(f)
                else:
                    self.logger.info(f"X«: {cache_key}")
            return None
        except Exception as e:
            self.logger.warning(f"˚÷X1%: {e}")
            return None

    def _save_to_cache(self, cache_key: str, data: pd.DataFrame) -> bool:
        """›Xpn0X"""
        try:
            cache_file = self.cache_dir / f"{self._get_cache_key(cache_key)}.pkl"
            with open(cache_file, 'wb') as f:
                pickle.dump(data, f)
            self.logger.debug(f"pnÚX: {cache_key}")
            return True
        except Exception as e:
            self.logger.warning(f"›XX1%: {e}")
            return False

    def clear_cache(self, pattern: Optional[str] = None) -> int:
        """
        X

        Args:
            pattern: X.9M!Noneh:hË

        Returns:
            ÑXaÓp
        """
        try:
            cleared_count = 0
            for cache_file in self.cache_dir.glob("*.pkl"):
                if pattern is None or pattern in cache_file.name:
                    cache_file.unlink()
                    cleared_count += 1
            self.logger.info(f"X: {cleared_count} *áˆ")
            return cleared_count
        except Exception as e:
            self.logger.warning(f"X1%: {e}")
            return 0

    # ==================== pn(œ¿Â ====================

    def validate_market_data(self, df: pd.DataFrame) -> Dict[str, any]:
        """
        å¡:pn(œ

        Args:
            df: :pnDataFrame

        Returns:
            å¡”úWx
        """
        result = {
            'is_valid': True,
            'missing_data_pct': 0.0,
            'outliers_count': 0,
            'data_gaps': [],
            'quality_score': 100.0
        }

        try:
            # °ó:1pn~‘
            total_cells = len(df) * len(df.columns)
            missing_cells = df.isnull().sum().sum()
            result['missing_data_pct'] = (missing_cells / total_cells) * 100 if total_cells > 0 else 0

            # ¿K8<(3-sigmaƒ	
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            outliers = 0
            for col in numeric_cols:
                if df[col].notna().sum() > 0:
                    mean = df[col].mean()
                    std = df[col].std()
                    if std > 0:
                        col_outliers = ((df[col] - mean).abs() > 3 * std).sum()
                        outliers += col_outliers

            result['outliers_count'] = outliers

            # ¿Kpn:„
            if 'date' in df.columns:
                df_sorted = df.sort_values('date')
                date_diffs = df_sorted['date'].diff()
                expected_month_diff = pd.Timedelta(days=30)
                gaps = date_diffs[date_diffs > expected_month_diff * 1.5]
                result['data_gaps'] = [(str(gap[0]), str(gap[1])) for gap in gaps.items()]

            # °ó(œp
            score = 100.0
            score -= result['missing_data_pct'] * 0.5  # :1pnc
            score -= min(outliers / len(df), 0.1) * 100  # 8<c
            score -= len(result['data_gaps']) * 5  # pn:„c

            result['quality_score'] = max(0, min(100, score))
            result['is_valid'] = result['quality_score'] >= 70

            return result

        except Exception as e:
            self.logger.error(f"pn(œ¿Â1%: {e}")
            result['is_valid'] = False
            result['error'] = str(e)
            return result

    # ==================== pn∞ú¶¿Â ====================

    def check_data_freshness(self, df: pd.DataFrame) -> Dict[str, str]:
        """
        ¿Âpn∞ú¶

        Args:
            df: Å¿ÂÑDataFrame

        Returns:
            Wx+pnêÑ∞ú¶∂
        """
        freshness = {}

        try:
            if 'date' in df.columns:
                latest_date = pd.to_datetime(df['date']).max()
                days_old = (datetime.now() - latest_date).days

                if days_old <= 30:
                    freshness['overall'] = 'fresh'
                elif days_old <= 90:
                    freshness['overall'] = 'warning'
                else:
                    freshness['overall'] = 'stale'

                # 	pnê¿Â
                if 'finra_D' in df.columns:
                    freshness['finra'] = freshness['overall']
                if any(col in df.columns for col in ['m2_money_supply', 'federal_funds_rate']):
                    freshness['fred'] = freshness['overall']
                if any(col in df.columns for col in ['sp500_index', 'vix_index']):
                    freshness['yahoo'] = freshness['overall']
            else:
                freshness['overall'] = 'unknown'

        except Exception as e:
            self.logger.error(f"pn∞ú¶¿Â1%: {e}")
            freshness['overall'] = 'error'
            freshness['error'] = str(e)

        return freshness

    # ==================== Õ’:6 ====================

    def retry_api_call(self, func, max_retries: int = 3, backoff_factor: float = 2.0, *args, **kwargs):
        """
        API(Õ’≈ph

        Args:
            func: ÅÕ’Ñ˝p
            max_retries: 'Õ’!p
            backoff_factor: ‡P
            *args, **kwargs: ˝p¬p

        Returns:
            ˝pgL”ú
        """
        last_exception = None

        for attempt in range(max_retries + 1):
            try:
                return func(*args, **kwargs)
            except (DataSourceError, RateLimitError, ConnectionError) as e:
                last_exception = e
                if attempt < max_retries:
                    wait_time = backoff_factor ** attempt
                    self.logger.warning(f"API(1%{wait_time:.1f}“Õ’ (’ {attempt + 1}/{max_retries + 1}): {e}")
                    time.sleep(wait_time)
                else:
                    self.logger.error(f"API(»1%ÚÕ’ {max_retries} !: {e}")

        raise last_exception

    def detect_data_anomalies(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        ¿Kpn8

        Args:
            df: :pnDataFrame

        Returns:
            ∞8ÑDataFrame˚† anomaly_flag 
        """
        result = df.copy()
        result['anomaly_flag'] = False

        try:
            # ¿Kp<8Ö˙Ù	
            numeric_cols = result.select_dtypes(include=[np.number]).columns

            for col in numeric_cols:
                if col != 'anomaly_flag':
                    # (IQRπ’¿K8<
                    Q1 = result[col].quantile(0.25)
                    Q3 = result[col].quantile(0.75)
                    IQR = Q3 - Q1
                    lower_bound = Q1 - 1.5 * IQR
                    upper_bound = Q3 + 1.5 * IQR

                    anomalies = (result[col] < lower_bound) | (result[col] > upper_bound)
                    result.loc[anomalies, 'anomaly_flag'] = True

            self.logger.info(f"¿K0 {result['anomaly_flag'].sum()} *pn8π")

        except Exception as e:
            self.logger.error(f"8¿K1%: {e}")

        return result


# ==================== øw˝p ====================

def get_data_fetcher(cache_enabled: bool = True) -> DataFetcher:
    """
    ∑÷DataFetcherûãÑøw˝p

    Args:
        cache_enabled: /&/(X

    Returns:
        DataFetcherûã
    """
    return DataFetcher(cache_enabled=cache_enabled)


# ==================== K’„ ====================

if __name__ == "__main__":
    # ÄUK’
    fetcher = DataFetcher(cache_enabled=True)

    print("=== DataFetcher!WK’ ===")

    # K’FINRApn†}
    try:
        finra_data = fetcher.load_finra_data()
        print(f" FINRApn†}ü: {len(finra_data)} a∞U")
    except Exception as e:
        print(f" FINRApn†}1%: {e}")

    # K’pn(œ¿Â
    try:
        if 'finra_data' in locals():
            quality = fetcher.validate_market_data(finra_data)
            print(f" pn(œ¿Â: p {quality['quality_score']:.1f}")
    except Exception as e:
        print(f" pn(œ¿Â1%: {e}")
