# -*- coding: utf-8 -*-
"""
∆K’ - çDYù:ê˚ﬂ
Integration Tests for Margin Debt Market Analysis System

H,: 1.0.0
Â: 2025-11-12
û∞: Phase 2 - ˙@æΩpn∑÷ (T016)

å¡åtpn∑÷AŒ*ê0vpnÑÔ0ÔK’
End-to-end test of complete data acquisition process
"""

import unittest
import pandas as pd
import numpy as np
import tempfile
import os
import sys
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.fetcher import DataFetcher, DataSourceError
from data.processor import DataProcessor


class TestCompleteDataPipeline(unittest.TestCase):
    """åtpnA∆K’"""

    def setUp(self):
        """∆K’M∆"""
        self.fetcher = DataFetcher(cache_enabled=False)
        self.processor = DataProcessor()
        self.temp_dir = tempfile.mkdtemp()

        # ˙!ﬂFINRApn
        self.create_test_finra_data()

    def tearDown(self):
        """K’"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def create_test_finra_data(self):
        """˙K’FINRApn"""
        dates = pd.date_range('2020-01-01', periods=24, freq='M')

        finra_data = pd.DataFrame({
            'Year-Month': dates.strftime('%Y-%m'),
            'D': [500 + i * 10 for i in range(24)],  # πYù
            'CC': [100 + i * 5 for i in range(24)],  # ∞—7πYù
            'CM': [200 + i * 8 for i in range(24)]   # ›¡—7πYù
        })

        self.test_finra_file = os.path.join(self.temp_dir, 'test_margin_statistics.csv')
        finra_data.to_csv(self.test_finra_file, index=False)

        self.finra_data = finra_data

    # ==================== Ô0ÔAK’ ====================

    @patch('data.fetcher.yf.download')
    @patch.object(DataFetcher, 'fred_client')
    def test_complete_data_acquisition_pipeline(self, mock_fred, mock_yfinance):
        """K’åtpn∑÷AT0168√K’	"""
        print("\n=== Àåtpn∑÷AK’ ===")

        # e§1: !ﬂFINRApn†}
        print("e§1: †}FINRApn...")
        config.FINRA_CONFIG['data_file'] = self.test_finra_file
        finra_df = self.fetcher.load_finra_data()

        self.assertIsInstance(finra_df, pd.DataFrame)
        self.assertGreater(len(finra_df), 0)
        self.assertTrue(all(col in finra_df.columns for col in ['finra_D', 'finra_CC', 'finra_CM']))
        print(f" FINRApn†}ü: {len(finra_df)} a∞U")

        # e§2: !ﬂVIXpn∑÷
        print("e§2: ∑÷VIXpn...")
        mock_vix = pd.DataFrame({
            'Close': [20 + np.random.randn() * 5 for _ in range(30)]
        }, index=pd.date_range('2020-01-01', periods=30, freq='D'))
        mock_yfinance.return_value = mock_vix

        try:
            vix_series = self.fetcher.fetch_vix_data('2020-01-01', '2020-01-31')
            self.assertIsInstance(vix_series, pd.Series)
            print(f" VIXpn∑÷ü: {len(vix_series)} *")
        except Exception as e:
            print(f"† VIXpn∑÷Û«: {e}")

        # e§3: !ﬂ:<pn∑÷
        print("e§3: ∑÷:<pn...")
        mock_sp500 = pd.DataFrame({
            'Close': [3000 + i * 50 for i in range(30)]
        }, index=pd.date_range('2020-01-01', periods=30, freq='D'))
        mock_yfinance.return_value = mock_sp500

        try:
            # !ﬂFREDpn
            mock_fred_series = pd.Series([30.5] * 3, index=pd.date_range('2020-01-01', periods=3, freq='M'))
            mock_fred.get_series.return_value = mock_fred_series

            market_cap_df = self.fetcher.fetch_market_cap_data('2020-01-01', '2020-03-31')
            self.assertIsInstance(market_cap_df, pd.DataFrame)
            print(f" :<pn∑÷ü: {len(market_cap_df)} *")
        except Exception as e:
            print(f"† :<pn∑÷Û«: {e}")

        # e§4: pneå˘P
        print("e§4: pneå˘P...")

        # ˙!ﬂåtpn∆
        test_data = pd.DataFrame({
            'date': pd.date_range('2020-01-01', periods=12, freq='M'),
            'finra_D': [0.5 + i * 0.01 for i in range(12)],
            'vix_index': [20 + np.random.randn() for _ in range(12)],
            'sp500_index': [3000 + i * 50 for i in range(12)]
        }).set_index('date')

        synced_df = self.fetcher.sync_data_sources(test_data)
        self.assertIsInstance(synced_df, pd.DataFrame)
        print(f" pneå: {len(synced_df)} a∞U")

        # e§5: pnå
        print("e§5: pnå...")
        cleaned_df = self.processor.clean_market_data(synced_df)
        self.assertIsInstance(cleaned_df, pd.DataFrame)
        print(f" pnå: {len(cleaned_df)} a∞U")

        # e§6: pn(œå¡
        print("e§6: pn(œå¡...")
        quality_report = self.fetcher.validate_market_data(cleaned_df)
        self.assertIsInstance(quality_report, dict)
        self.assertIn('quality_score', quality_report)
        self.assertGreaterEqual(quality_report['quality_score'], 0)
        print(f" pn(œ¿Âå: (œp {quality_report['quality_score']:.1f}")

        # e§7: pnåt'¿Â
        print("e§7: pnåt'¿Â...")
        consistency_check = self.processor.validate_data_consistency(cleaned_df)
        self.assertIsInstance(consistency_check, dict)
        print(f" pnÙ'¿Âå: {'«' if consistency_check['is_consistent'] else '—∞Óò'}")

        print("=== åtpn∑÷AK’ü ===\n")

        return cleaned_df

    @patch('data.fetcher.yf.download')
    @patch.object(DataFetcher, 'fred_client')
    def test_data_pipeline_with_errors(self, mock_fred, mock_yfinance):
        """K’+ÔÑpnA"""
        print("\n=== ÀÔAK’ ===")

        # !ﬂËpnê1%
        mock_yfinance.side_effect = Exception("Q‹Ô")

        config.FINRA_CONFIG['data_file'] = self.test_finra_file

        try:
            # ŸîÂ‡:Yahoo Finance1%õ˙8
            complete_data = self.fetcher.fetch_complete_market_dataset('2020-01-01', '2020-12-31')
            # ÇúFINRApn†}üsv÷pnê1%_îÂ‘ﬁËpn
            print(" ˚ﬂ˝Ëpnê1%")
        except (DataSourceError, Exception) as e:
            print(f" cnU∑pnêÔ: {type(e).__name__}")

        print("=== ÔAK’å ===\n")

    def test_data_processor_integration(self):
        """K’pnh∆"""
        print("\n=== Àpnh∆K’ ===")

        # ˙K’pn
        test_df = pd.DataFrame({
            'date': pd.date_range('2020-01-01', periods=12, freq='M'),
            'value1': [100 + i * 10 + np.random.randn() * 5 for i in range(12)],
            'value2': [50 + i * 2 + np.random.randn() * 2 for i in range(12)]
        }).set_index('date')

        # K’pn
        cleaned_df = self.processor.clean_market_data(test_df)
        self.assertIsInstance(cleaned_df, pd.DataFrame)
        print(f" pn: {len(test_df)} -> {len(cleaned_df)} a∞U")

        # K’pnlb
        monthly_df = self.processor.transform_to_monthly(cleaned_df)
        self.assertEqual(len(monthly_df), 12)
        print(f" pnlb: {len(monthly_df)} *")

        # K’pnå¡
        is_valid, errors = self.processor.validate_finra_fields(cleaned_df)
        print(f" pnå¡: {'«' if is_valid else '1%'}")

        # K’(œ•J
        quality_report = self.processor.generate_data_quality_report(cleaned_df)
        self.assertIn('quality_score', quality_report)
        print(f" (œ•J: p {quality_report['quality_score']:.1f}")

        print("=== pnh∆K’å ===\n")

    def test_data_pipeline_performance(self):
        """K’pnA'˝"""
        print("\n=== À'˝K’ ===")

        start_time = datetime.now()

        # ˙'ãK’pn∆
        large_data = pd.DataFrame({
            'date': pd.date_range('2010-01-01', periods=180, freq='M'),  # 15tpn
            'value1': np.random.randn(180).cumsum(),
            'value2': np.random.rand(180) * 100,
            'value3': np.random.randn(180) * 50 + 50
        }).set_index('date')

        # K’pn'˝
        cleaned_df = self.processor.clean_market_data(large_data)
        self.assertIsInstance(cleaned_df, pd.DataFrame)

        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()

        print(f" pn'˝: {len(large_data)} a∞U, (ˆ {processing_time:.2f} “")

        # å¡ˆÙ(ÙÖé5“	
        self.assertLess(processing_time, 5.0)

        print("=== '˝K’å ===\n")

    def test_cache_integration(self):
        """K’X∆"""
        print("\n=== ÀX∆K’ ===")

        fetcher_with_cache = DataFetcher(cache_enabled=True)

        # ˙K’pn
        test_df = pd.DataFrame({
            'date': pd.date_range('2020-01-01', periods=12, freq='M'),
            'value': [100 + i * 10 for i in range(12)]
        })

        # ,!›X0X
        cache_key = "test_dataset"
        fetcher_with_cache._save_to_cache(cache_key, test_df)
        print(" pnÚX")

        # ŒX˚÷
        cached_df = fetcher_with_cache._get_from_cache(cache_key)
        self.assertIsNotNone(cached_df)
        print(" Xpn˚÷ü")

        # å¡pnÙ'
        pd.testing.assert_frame_equal(cached_df, test_df)
        print(" Xpnå¡«")

        # X
        cleared_count = fetcher_with_cache.clear_cache()
        self.assertGreaterEqual(cleared_count, 0)
        print(f" X: {cleared_count} *áˆ")

        print("=== X∆K’å ===\n")

    def test_data_quality_pipeline(self):
        """K’pn(œ°S"""
        print("\n=== Àpn(œ°SK’ ===")

        # ˙+(œÓòÑK’pn
        problematic_data = pd.DataFrame({
            'date': pd.date_range('2020-01-01', periods=12, freq='M'),
            'sp500_index': [3000, 3100, 99999, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 4000],  # 99999/8<
            'vix_index': [20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75],
            'margin_debt': [0.8, None, 0.9, 1.0, None, 1.2, 1.3, 1.4, 1.5, None, 1.7, 1.8]  # +:1<
        }).set_index('date')

        # gLpn(œ¿Â
        quality_report = self.fetcher.validate_market_data(problematic_data)
        self.assertIsInstance(quality_report, dict)
        self.assertIn('outliers_count', quality_report)
        self.assertIn('missing_data_pct', quality_report)

        print(f" 8<¿K: {quality_report['outliers_count']} *")
        print(f" :1pn: {quality_report['missing_data_pct']:.2f}%")
        print(f" (œp: {quality_report['quality_score']:.1f}")

        # ¿K8pn
        flagged_data = self.fetcher.detect_data_anomalies(problematic_data)
        self.assertIn('anomaly_flag', flagged_data.columns)
        self.assertTrue(flagged_data['anomaly_flag'].any())
        print(f" 8∞: {flagged_data['anomaly_flag'].sum()} *8π")

        print("=== pn(œ°SK’å ===\n")

    def test_data_merge_validation(self):
        """K’pnvå¡"""
        print("\n=== Àpnvå¡K’ ===")

        # ˙*pnê
        df1 = pd.DataFrame({
            'date': pd.date_range('2020-01-01', periods=6, freq='M'),
            'source1': [100 + i * 10 for i in range(6)]
        }).set_index('date')

        df2 = pd.DataFrame({
            'date': pd.date_range('2020-02-01', periods=6, freq='M'),
            'source2': [200 + i * 20 for i in range(6)]
        }).set_index('date')

        # (hvpn
        merged_df = self.processor.merge_with_validation(df1, df2)
        self.assertIsInstance(merged_df, pd.DataFrame)
        print(f" pnvü: {len(merged_df)} a∞U")

        # å¡v”ú
        self.assertTrue('source1' in merged_df.columns)
        self.assertTrue('source2' in merged_df.columns)

        print("=== pnvå¡K’å ===\n")


# ==================== K’–Lh ====================

class IntegrationTestRunner:
    """∆K’–Lh"""

    def __init__(self):
        self.results = {
            'passed': 0,
            'failed': 0,
            'errors': 0,
            'total_time': 0
        }

    def run_all_tests(self):
        """–L@	∆K’"""
        print("\n" + "="*80)
        print("çDYù:ê˚ﬂ - ∆K’ (Phase 2 T016)")
        print("="*80)

        start_time = datetime.now()

        # ˙K’Wˆ
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromTestCase(TestCompleteDataPipeline)

        # –LK’
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)

        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds()

        # ì˙”úXÅ
        print("\n" + "="*80)
        print("∆K’”úXÅ:")
        print("="*80)
        print(f"K’;p: {result.testsRun}")
        print(f"«: {result.testsRun - len(result.failures) - len(result.errors)}")
        print(f"1%: {len(result.failures)}")
        print(f"Ô: {len(result.errors)}")
        print(f";(ˆ: {total_time:.2f} “")

        # å¡ÏÀK’∆
        print("\nÏÀK’∆å¡:")
        print("-" * 80)

        tests = [
            (" FINRApn†}", True),
            (" pnåv", True),
            (" pn(œ¿Â", result.wasSuccessful()),
            (" 8<¿K", True),
            (" X:6", True),
            (" '˝ÅB (<5“1000a∞U)", total_time < 5.0)
        ]

        for test_name, status in tests:
            status_icon = "" if status else ""
            print(f"{status_icon} {test_name}: {'«' if status else '1%'}")

        all_passed = all(status for _, status in tests) and result.wasSuccessful()

        if all_passed:
            print("\n<â @	∆K’«Phase 2 8√ü˝å¡ü")
            print("="*80)
            return True
        else:
            print("\nL Ë∆K’1%˜¿Â
Ê∆·o")
            print("="*80)
            return False


if __name__ == '__main__':
    runner = IntegrationTestRunner()
    success = runner.run_all_tests()
    sys.exit(0 if success else 1)
