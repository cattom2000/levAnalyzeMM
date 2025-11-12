# -*- coding: utf-8 -*-
"""
pn!W - çDYù:ê˚ﬂ
Data Processing Module for Margin Debt Market Analysis System

#pnå¡lbå<
Handles data cleaning, validation, transformation, and formatting.

H,: 1.0.0
Â: 2025-11-12
û∞: Phase 2 - ˙@æΩpn∑÷ (T013)
"""

from typing import Dict, List, Optional, Tuple, Union
import pandas as pd
import numpy as np
import os
import sys
import logging
from datetime import datetime, timedelta

# Add src to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config


class DataProcessor:
    """
    pnh
    #pnå¡lbå<
    """

    def __init__(self) -> None:
        """Àpnh"""
        self.logger = logging.getLogger(__name__)
        self._setup_logging()

    def _setup_logging(self) -> None:
        """ænÂ◊"""
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    # ==================== pn ====================

    def clean_market_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        :pn

        Args:
            df: üÀ:pnDataFrame

        Returns:
            ÑDataFrame

        Õ\e§:
        1. ˚dÕÂ
        2. :1<
        3. Ócpn{ã
        4. å¡p<Ù
        5. íèpn
        """
        self.logger.info("Àpn...")
        cleaned_df = df.copy()

        # 1. Â
        if 'date' in cleaned_df.columns:
            cleaned_df['date'] = pd.to_datetime(cleaned_df['date'])
            # ˚dÕÂ›Y,*	
            cleaned_df = cleaned_df.drop_duplicates(subset=['date'], keep='first')
            cleaned_df = cleaned_df.set_index('date').sort_index()
        else:
            # Gæ"1/Â
            if not isinstance(cleaned_df.index, pd.DatetimeIndex):
                cleaned_df.index = pd.to_datetime(cleaned_df.index)

        # 2. p<
        numeric_columns = cleaned_df.select_dtypes(include=[np.number]).columns

        for col in numeric_columns:
            # lbp<{ã
            cleaned_df[col] = pd.to_numeric(cleaned_df[col], errors='coerce')

            # å¡pnÙvÓc8<
            cleaned_df[col] = self._validate_numeric_range(cleaned_df[col], col)

        # 3. :1<
        # H(MkEçkE(-MpkE
        for col in numeric_columns:
            if cleaned_df[col].isnull().any():
                # MkE
                cleaned_df[col] = cleaned_df[col].fillna(method='ffill')
                # kE
                cleaned_df[col] = cleaned_df[col].fillna(method='bfill')
                # iY:1<(-MpkE
                if cleaned_df[col].isnull().any():
                    median_val = cleaned_df[col].median()
                    cleaned_df[col] = cleaned_df[col].fillna(median_val)

        # 4. pnåt'å¡
        cleaned_df = self._validate_data_completeness(cleaned_df)

        self.logger.info(f"pnå: {len(cleaned_df)} a∞U")
        return cleaned_df

    def _validate_numeric_range(self, series: pd.Series, col_name: str) -> pd.Series:
        """
        å¡åÓcp<Ù

        Args:
            series: p<Series
            col_name: 

        Returns:
            å¡ÑSeries
        """
        # ˙éænÑp<Ù
        value_ranges = {
            'sp500_index': (100, 10000),
            'sp500_market_cap': (1, 100),
            'vix_index': (8, 80),
            'm2_money_supply': (1, 25),
            'federal_funds_rate': (-5, 50),
            'treasury_10y_rate': (-5, 50),
            'margin_debt': (0, 5),
            'finra_D': (0, 5),
            'finra_CC': (0, 5),
            'finra_CM': (0, 5)
        }

        if col_name in value_ranges:
            min_val, max_val = value_ranges[col_name]
            # ∞Ö˙ÙÑ<
            out_of_range = (series < min_val) | (series > max_val)

            if out_of_range.any():
                self.logger.warning(
                    f"—∞ {out_of_range.sum()} *8<( {col_name} "
                    f"Ö˙Ù [{min_val}, {max_val}]"
                )
                # 8<æ:NaNÌ
                series = series.copy()
                series.loc[out_of_range] = np.nan

        return series

    def _validate_data_completeness(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        å¡pnåt'

        Args:
            df: DataFrame

        Returns:
            å¡ÑDataFrame
        """
        # ¿Âs.Ñåt'
        required_columns = ['margin_debt', 'vix_index']
        available_required = [col for col in required_columns if col in df.columns]

        if available_required:
            completeness = df[available_required].notna().mean()
            min_completeness = completeness.min()

            if min_completeness < 0.7:
                self.logger.warning(
                    f"pnåt'Né70%: {completeness.to_dict()}"
                )

        return df

    # ==================== pnlb ====================

    def transform_to_monthly(self, df: pd.DataFrame, method: str = 'mean') -> pd.DataFrame:
        """
        lb:¶pn

        Args:
            df: Â¶˜ëápn
            method: Zπ’ ('mean', 'sum', 'last', 'first')

        Returns:
            ¶DataFrame
        """
        self.logger.info(f"lb:¶pnZπ’: {method}")

        # 	Zpn
        monthly_df = df.resample('M').agg(method)

        self.logger.info(f"¶lbå: {len(monthly_df)} *")
        return monthly_df

    def align_data_frequency(self, df: pd.DataFrame, target_freq: str = 'M') -> pd.DataFrame:
        """
        ˘Ppnëá

        Args:
            df: ìeDataFrame
            target_freq: Óëá ('D'=Â, 'W'=h, 'M'=, 'Q'=c)

        Returns:
            ˘PÑDataFrame
        """
        freq_map = {'D': 'D', 'W': 'W', 'M': 'M', 'Q': 'Q'}
        target = freq_map.get(target_freq, 'M')

        # Õ«70Óëá
        aligned_df = df.resample(target).last()

        # “<kE:1<
        numeric_cols = aligned_df.select_dtypes(include=[np.number]).columns
        aligned_df[numeric_cols] = aligned_df[numeric_cols].interpolate(method='time')

        self.logger.info(f"ëá˘På: {target_freq}")
        return aligned_df

    # ==================== pnå¡ ====================

    def validate_finra_fields(self, df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """
        å¡FINRAWµ

        Args:
            df: +FINRApnÑDataFrame

        Returns:
            Tuple[bool, List[str]]: (/&å¡«, Ô·oh)
        """
        errors = []
        required_fields = ['finra_D', 'finra_CC', 'finra_CM']

        # ¿ÂWµX('
        missing_fields = [field for field in required_fields if field not in df.columns]
        if missing_fields:
            errors.append(f":FINRAWµ: {missing_fields}")

        # å¡p<	H'
        for field in required_fields:
            if field in df.columns:
                # ¿Â<
                negative_count = (df[field] < 0).sum()
                if negative_count > 0:
                    errors.append(f"{field} + {negative_count} *<")

                # ¿ÂÅ<
                if df[field].notna().any():
                    max_val = df[field].max()
                    min_val = df[field].min()
                    if max_val > 10:  # GæøéCUM
                        errors.append(f"{field} '<8: {max_val:.2f}")

        is_valid = len(errors) == 0
        return is_valid, errors

    def validate_data_consistency(self, df: pd.DataFrame) -> Dict[str, any]:
        """
        å¡pnÙ'

        Args:
            df: DataFrame

        Returns:
            å¡”úWx
        """
        result = {
            'is_consistent': True,
            'checks': [],
            'warnings': [],
            'errors': []
        }

        # 1. ¿ÂÂﬁÌ'
        if 'date' in df.columns:
            df_sorted = df.sort_values('date')
            date_gaps = df_sorted['date'].diff()
            expected_gap = pd.Timedelta(days=30)  # ¶pn

            large_gaps = date_gaps[date_gaps > expected_gap * 2]
            if len(large_gaps) > 0:
                result['warnings'].append(f"—∞ {len(large_gaps)} *'Â:„")

        # 2. ¿Â;ëÙ'
        if 'margin_debt' in df.columns and 'finra_D' in df.columns:
            diff = (df['margin_debt'] - df['finra_D']).abs()
            max_diff = diff.max()
            if max_diff > 0.001:  # A∏ÆÓ
                result['warnings'].append(
                    f"margin_debt å finra_D X(Ó'Ó: {max_diff:.6f}"
                )

        # 3. ¿ÂpnÙ'
        reasonableness_checks = [
            ('vix_index', 8, 80, "VIXpÙ"),
            ('federal_funds_rate', -5, 50, "T¶˙—)á"),
            ('treasury_10y_rate', -5, 50, "10t˝:6 á"),
        ]

        for col, min_val, max_val, desc in reasonableness_checks:
            if col in df.columns and df[col].notna().any():
                out_of_range = ((df[col] < min_val) | (df[col] > max_val)).sum()
                if out_of_range > 0:
                    result['errors'].append(
                        f"{desc}: {out_of_range} *<Ö˙Ù [{min_val}, {max_val}]"
                    )

        # 4. ¿Âpnãø8
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if df[col].notna().sum() > 24:  # Û2tpn
                # °ó¶ÿá
                monthly_change = df[col].pct_change().abs()
                # ¿KÅÔÿÖ«50%Ñ¶ÿ	
                extreme_changes = (monthly_change > 0.5).sum()
                if extreme_changes > 0:
                    result['warnings'].append(
                        f"{col}: —∞ {extreme_changes} *ÅÔ¶ÿ (>50%)"
                    )

        result['is_consistent'] = len(result['errors']) == 0
        return result

    def generate_data_quality_report(self, df: pd.DataFrame) -> Dict[str, any]:
        """
        pn(œ•J

        Args:
            df: DataFrame

        Returns:
            (œ•JWx
        """
        report = {
            'timestamp': datetime.now().isoformat(),
            'record_count': len(df),
            'date_range': {
                'start': df.index.min().isoformat() if df.index.size > 0 else None,
                'end': df.index.max().isoformat() if df.index.size > 0 else None
            },
            'columns': {
                'total': len(df.columns),
                'numeric': len(df.select_dtypes(include=[np.number]).columns),
                'missing_data': {}
            },
            'statistics': {},
            'quality_score': 0.0,
            'issues': [],
            'recommendations': []
        }

        try:
            # °ó:1pnﬂ°
            missing_stats = df.isnull().sum()
            report['columns']['missing_data'] = {
                col: int(count) for col, count in missing_stats.items() if count > 0
            }

            # °óœ'ﬂ°
            numeric_df = df.select_dtypes(include=[np.number])
            if not numeric_df.empty:
                report['statistics'] = {
                    'summary': numeric_df.describe().to_dict(),
                    'correlations': numeric_df.corr().to_dict()
                }

            # °ó(œp
            score = 100.0
            total_cells = len(df) * len(df.columns)
            missing_cells = df.isnull().sum().sum()
            missing_pct = (missing_cells / total_cells * 100) if total_cells > 0 else 0
            score -= missing_pct * 0.3

            # ¿Âåt'
            required_cols = ['margin_debt', 'vix_index']
            available_required = [col for col in required_cols if col in df.columns]
            if len(available_required) < len(required_cols):
                score -= 20
                report['issues'].append(f":≈Å: {set(required_cols) - set(available_required)}")

            report['quality_score'] = max(0, min(100, score))

            # ˙Æ
            if missing_pct > 5:
                report['recommendations'].append(":1pn«˙Æ¿Âpnê")
            if report['quality_score'] < 70:
                report['recommendations'].append("pn(œÉN˙Æ€LÙ%<Ñpn")

            report['summary'] = f"pn(œp: {report['quality_score']:.1f}/100"

        except Exception as e:
            report['error'] = str(e)
            self.logger.error(f"pn(œ•J1%: {e}")

        return report

    # ==================== pn< ====================

    def format_for_export(self, df: pd.DataFrame, format_type: str = 'csv') -> Union[str, bytes]:
        """
        <pn(é¸˙

        Args:
            df: DataFrame
            format_type: <{ã ('csv', 'excel', 'json')

        Returns:
            <ÑpnW&2WÇ	
        """
        if format_type.lower() == 'csv':
            return df.to_csv(index=config.EXPORT_CONFIG.get('date_format', '%Y-%m-%d') == '%Y-%m-%d')
        elif format_type.lower() == 'excel':
            # ÄUExcel<+7	
            return df.to_excel()
        elif format_type.lower() == 'json':
            return df.to_json(orient='records', date_format='iso')
        else:
            raise ValueError(f"/Ñ<: {format_type}")

    def add_metadata_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        ˚†Cpn

        Args:
            df: ˙@DataFrame

        Returns:
            ˚†CpnÑDataFrame
        """
        result = df.copy()

        # ˚†°óˆÙ3
        result['calculation_date'] = datetime.now()

        # ˚†pn(œ∞
        result['data_quality_flag'] = 'VALIDATED'

        # ˚†pnê·oÄUH,	
        result['data_source'] = 'processed'

        return result

    # ==================== pnvÂw ====================

    def merge_with_validation(self, *dataframes, validation_rules: Optional[Dict] = None) -> pd.DataFrame:
        """
        &å¡Ñpnv

        Args:
            *dataframes: ÅvÑDataFrame
            validation_rules: å¡ƒWx

        Returns:
            vÑDataFrame
        """
        if not dataframes:
            raise ValueError("°	–õÅvÑDataFrame")

        if len(dataframes) == 1:
            return dataframes[0]

        # *vDataFrame
        result = dataframes[0]

        for i, df in enumerate(dataframes[1:], 1):
            try:
                result = pd.merge(
                    result, df,
                    left_index=True, right_index=True,
                    how='outer', suffixes=('', f'_df{i}')
                )
                self.logger.info(f"vDataFrame {i+1} ü")
            except Exception as e:
                self.logger.error(f"vDataFrame {i+1} 1%: {e}")
                raise

        return result

    def normalize_column_names(self, df: pd.DataFrame, naming_convention: str = 'snake_case') -> pd.DataFrame:
        """
        ∆

        Args:
            df: DataFrame
            naming_convention: }¶ö ('snake_case', 'camelCase')

        Returns:
            ∆ÑDataFrame
        """
        if naming_convention == 'snake_case':
            # lb:snake_case
            new_columns = []
            for col in df.columns:
                # ÄUÑsnake_caselb
                col = col.replace(' ', '_').replace('-', '_')
                col = ''.join('_' + c.lower() if c.isupper() and not new_columns else c for c in col)
                new_columns.append(col)
            df.columns = new_columns

        return df


# ==================== øw˝p ====================

def get_data_processor() -> DataProcessor:
    """
    ∑÷DataProcessorûãÑøw˝p

    Returns:
        DataProcessorûã
    """
    return DataProcessor()


def process_finra_data(file_path: str) -> Tuple[pd.DataFrame, Dict]:
    """
    øw˝pFINRApn

    Args:
        file_path: FINRApnáˆÔÑ

    Returns:
        Tuple[DataFrame, Dict]: (Ñpn, (œ•J)
    """
    from .fetcher import get_data_fetcher

    fetcher = get_data_fetcher(cache_enabled=False)
    processor = get_data_processor()

    # †}FINRApn
    df = fetcher.load_finra_data(file_path)

    # pn
    df_clean = processor.clean_market_data(df)

    # å¡
    is_valid, errors = processor.validate_finra_fields(df_clean)

    # •J
    quality_report = processor.generate_data_quality_report(df_clean)

    return df_clean, quality_report


# ==================== K’„ ====================

if __name__ == "__main__":
    # ÄUK’
    processor = DataProcessor()

    print("=== DataProcessor!WK’ ===")

    # K’pn(œ•J
    try:
        # ˙K’pn
        test_data = pd.DataFrame({
            'date': pd.date_range('2020-01-01', periods=12, freq='M'),
            'value1': np.random.randn(12).cumsum(),
            'value2': np.random.rand(12) * 100
        }).set_index('date')

        report = processor.generate_data_quality_report(test_data)
        print(f" pn(œ•Jü: {report['summary']}")

    except Exception as e:
        print(f" K’1%: {e}")
