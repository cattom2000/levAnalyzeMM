# -*- coding: utf-8 -*-
"""
数据获取模块合同
Data Fetcher Module Contract

负责从多个数据源获取市场数据，包括FRED、Yahoo Finance、FINRA等。
Supports data collection from FRED, Yahoo Finance, FINRA, and other sources.

版本: 1.0.0
日期: 2025-11-08
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime
import pandas as pd


class DataFetcher:
    """
    数据获取器基类
    Base data fetcher for market data sources
    """

    def __init__(self, cache_enabled: bool = True) -> None:
        """
        初始化数据获取器

        Args:
            cache_enabled: 是否启用缓存
        """
        self.cache_enabled = cache_enabled
        self.last_fetch: Optional[datetime] = None

    # ==================== FRED数据获取 ====================

    def fetch_fred_data(
        self,
        series_id: str,
        start_date: str,
        end_date: str,
        frequency: str = "m"
    ) -> pd.Series:
        """
        从FRED API获取经济数据

        Args:
            series_id: FRED系列ID (如 'M2SL', 'FEDFUNDS')
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            frequency: 数据频率 ('d'=日, 'm'=月, 'q'=季, 'a'=年)

        Returns:
            pandas Series，索引为日期，值为数据

        Raises:
            ValueError: series_id无效或参数格式错误
            ConnectionError: FRED API连接失败
            RateLimitError: API速率限制
        """
        raise NotImplementedError

    def fetch_multiple_fred_series(
        self,
        series_config: Dict[str, Dict],
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """
        批量获取FRED多个系列数据

        Args:
            series_config: 系列配置字典
                {
                    'series_id': {
                        'frequency': 'm',
                        'description': 'M2 Money Supply'
                    }
                }
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            DataFrame，列为各系列，索引为日期

        Example:
            >>> config = {
            ...     'M2SL': {'frequency': 'm', 'description': 'M2'},
            ...     'FEDFUNDS': {'frequency': 'm', 'description': 'Fed Funds'}
            ... }
            >>> df = fetcher.fetch_multiple_fred_series(config, '2020-01-01', '2025-09-30')
        """
        raise NotImplementedError

    # ==================== Yahoo Finance数据获取 ====================

    def fetch_yahoo_data(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        interval: str = "1d"
    ) -> pd.DataFrame:
        """
        从Yahoo Finance获取股票/指数数据

        Args:
            symbol: 股票代码 (如 '^GSPC', 'BTC-USD', 'GC=F')
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            interval: 数据间隔 ('1d', '1wk', '1mo')

        Returns:
            DataFrame，包含 ['Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close']列

        Raises:
            SymbolNotFoundError: 股票代码不存在
            InsufficientDataError: 数据不足
        """
        raise NotImplementedError

    def fetch_multiple_yahoo_symbols(
        self,
        symbols: List[str],
        start_date: str,
        end_date: str,
        interval: str = "1d"
    ) -> Dict[str, pd.DataFrame]:
        """
        批量获取Yahoo Finance多个股票数据

        Args:
            symbols: 股票代码列表 ['^GSPC', '^VIX', 'GC=F', 'BTC-USD']
            start_date: 开始日期
            end_date: 结束日期
            interval: 数据间隔

        Returns:
            字典，键为股票代码，值为对应的DataFrame

        Example:
            >>> symbols = ['^GSPC', '^VIX', 'GC=F']
            >>> data = fetcher.fetch_multiple_yahoo_symbols(symbols, '2020-01-01', '2025-09-30')
        """
        raise NotImplementedError

    # ==================== FINRA数据加载 ====================

    def load_finra_data(self, file_path: Optional[str] = None) -> pd.DataFrame:
        """
        加载FINRA融资余额数据 (本地CSV文件)

        Args:
            file_path: CSV文件路径，默认为 'datas/margin-statistics.csv'

        Returns:
            DataFrame，包含以下列:
            - date: 日期
            - margin_debt: 融资余额 (万亿美元)
            - cash_balance: 现金余额 (如果包含)
            - debit_balance: 借方余额 (如果包含)

        Raises:
            FileNotFoundError: 数据文件不存在
            DataFormatError: 数据格式不正确
        """
        raise NotImplementedError

    def validate_finra_data(self, df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """
        验证FINRA数据质量

        Args:
            df: FINRA数据DataFrame

        Returns:
            Tuple[bool, List[str]]: (是否验证通过, 错误信息列表)
        """
        raise NotImplementedError

    # ==================== 数据合并与对齐 ====================

    def fetch_complete_market_dataset(
        self,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """
        获取完整市场数据集 (所有数据源合并)

        合并以下数据源:
        - FINRA: 融资余额 (margin_debt)
        - FRED: M2货币供应、联邦基金利率、10年期国债收益率
        - Yahoo: S&P500指数、S&P500市值、VIX、黄金、BTC

        Args:
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)

        Returns:
            DataFrame，包含完整市场数据
            列: date, sp500_index, sp500_market_cap, vix_index, m2_money_supply,
                federal_funds_rate, treasury_10y_rate, margin_debt

        Raises:
            DataSourceError: 数据源获取失败
            MergeError: 数据合并失败
        """
        raise NotImplementedError

    def sync_data_sources(
        self,
        df: pd.DataFrame,
        tolerance_days: int = 5
    ) -> pd.DataFrame:
        """
        同步多个数据源的时间序列

        Args:
            df: 包含多个数据源的DataFrame
            tolerance_days: 日期容忍度 (天)

        Returns:
            对齐后的DataFrame，日期索引同步

        Example:
            >>> # 输入: 不同日期的数据
            >>> df = pd.DataFrame({
            ...     'date': ['2025-01-01', '2025-01-02', '2025-01-03'],
            ...     'sp500': [4500, None, 4510],
            ...     'margin_debt': [None, 0.82, 0.83]
            ... })
            >>> synced = fetcher.sync_data_sources(df)
            >>> # 输出: 日期对齐，缺失值标记
        """
        raise NotImplementedError

    # ==================== 错误处理与重试 ====================

    def retry_api_call(
        self,
        func,
        max_retries: int = 3,
        backoff_factor: float = 2.0,
        *args,
        **kwargs
    ):
        """
        API调用重试装饰器

        Args:
            func: 要重试的函数
            max_retries: 最大重试次数
            backoff_factor: 退避因子
            *args, **kwargs: 函数参数

        Returns:
            函数执行结果
        """
        raise NotImplementedError

    def check_data_freshness(self, df: pd.DataFrame) -> Dict[str, str]:
        """
        检查数据新鲜度

        Args:
            df: 要检查的DataFrame

        Returns:
            字典，包含各数据源的新鲜度状态
            {
                'finra': 'fresh|warning|stale',
                'fred': 'fresh|warning|stale',
                'yahoo': 'fresh|warning|stale'
            }
        """
        raise NotImplementedError

    # ==================== 缓存管理 ====================

    def get_cached_data(
        self,
        cache_key: str,
        max_age_hours: int = 24
    ) -> Optional[pd.DataFrame]:
        """
        获取缓存数据

        Args:
            cache_key: 缓存键
            max_age_hours: 最大缓存时间 (小时)

        Returns:
            缓存的DataFrame或None (如果过期)
        """
        raise NotImplementedError

    def set_cache_data(
        self,
        cache_key: str,
        data: pd.DataFrame,
        ttl_hours: int = 24
    ) -> bool:
        """
        设置缓存数据

        Args:
            cache_key: 缓存键
            data: 要缓存的数据
            ttl_hours: 生存时间 (小时)

        Returns:
            是否成功缓存
        """
        raise NotImplementedError

    def clear_cache(self, pattern: Optional[str] = None) -> int:
        """
        清理缓存

        Args:
            pattern: 缓存键匹配模式，None表示清理全部

        Returns:
            清理的缓存条目数
        """
        raise NotImplementedError

    # ==================== 数据质量检查 ====================

    def validate_market_data(self, df: pd.DataFrame) -> Dict[str, any]:
        """
        验证市场数据质量

        Args:
            df: 市场数据DataFrame

        Returns:
            验证结果字典
            {
                'is_valid': bool,
                'missing_data_pct': float,
                'outliers_count': int,
                'data_gaps': List[Tuple[str, str]],
                'quality_score': float (0-100)
            }
        """
        raise NotImplementedError

    def detect_data_anomalies(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        检测数据异常

        Args:
            df: 市场数据DataFrame

        Returns:
            标记异常的DataFrame，添加 anomaly_flag 列
        """
        raise NotImplementedError


# ==================== 异常类定义 ====================

class DataSourceError(Exception):
    """数据源错误"""
    pass


class RateLimitError(Exception):
    """API速率限制错误"""
    pass


class DataFormatError(Exception):
    """数据格式错误"""
    pass


class MergeError(Exception):
    """数据合并错误"""
    pass


class SymbolNotFoundError(Exception):
    """股票代码未找到错误"""
    pass


class InsufficientDataError(Exception):
    """数据不足错误"""
    pass


# ==================== 合同版本信息 ====================

CONTRACT_VERSION = "1.0.0"
LAST_UPDATED = "2025-11-08"
API_COMPATIBILITY = "Python 3.11+"
