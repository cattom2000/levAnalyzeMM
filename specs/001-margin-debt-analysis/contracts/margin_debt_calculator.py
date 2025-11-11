# -*- coding: utf-8 -*-
"""
融资余额指标计算模块合同
Margin Debt Indicators Calculation Module Contract

负责计算Part1和Part2的核心指标，包括市场杠杆率、货币供应比率、利率成本分析、
杠杆变化率、投资者净资产等。

Calculates Part1 and Part2 core indicators including market leverage ratio,
money supply ratio, interest cost analysis, leverage change rate, etc.

版本: 1.0.0
日期: 2025-11-08
"""

from typing import Dict, List, Optional, Tuple, Union
import pandas as pd
import numpy as np


class MarginDebtCalculator:
    """
    融资余额指标计算器
    Calculates margin debt related indicators
    """

    def __init__(self) -> None:
        """初始化计算器"""
        pass

    # ==================== Part1 指标计算 (1997-01开始) ====================

    def calculate_market_leverage_ratio(
        self,
        margin_debt: pd.Series,
        sp500_market_cap: pd.Series,
        handle_missing: str = "skip"
    ) -> pd.Series:
        """
        计算市场杠杆率: Margin Debt / S&P 500总市值

        Args:
            margin_debt: 融资余额 Series (万亿美元)
            sp500_market_cap: S&P500总市值 Series (万亿美元)
            handle_missing: 缺失值处理方式 ('skip', 'interpolate', 'ffill')

        Returns:
            市场杠杆率 Series (0-1之间的小数，4位精度)

        Raises:
            ValueError: 负值或零值输入
            DataLengthMismatch: 数据长度不匹配

        Example:
            >>> margin = pd.Series([0.8, 0.85, 0.9])
            >>> market_cap = pd.Series([40, 42, 45])
            >>> ratio = calc.calculate_market_leverage_ratio(margin, market_cap)
            >>> print(ratio.iloc[0])
            0.0200
        """
        raise NotImplementedError

    def calculate_money_supply_ratio(
        self,
        margin_debt: pd.Series,
        m2_money_supply: pd.Series,
        handle_missing: str = "skip"
    ) -> pd.Series:
        """
        计算货币供应比率: Margin Debt / M2货币供应量

        Args:
            margin_debt: 融资余额 Series (万亿美元)
            m2_money_supply: M2货币供应量 Series (万亿美元)

        Returns:
            货币供应比率 Series (0-1之间的小数，4位精度)

        Example:
            >>> margin = pd.Series([0.8, 0.85, 0.9])
            >>> m2 = pd.Series([21.0, 21.5, 22.0])
            >>> ratio = calc.calculate_money_supply_ratio(margin, m2)
            >>> print(ratio.iloc[0])
            0.0381
        """
        raise NotImplementedError

    def calculate_interest_cost_analysis(
        self,
        margin_debt: pd.Series,
        interest_rates: pd.Series,
        window: int = 12
    ) -> pd.DataFrame:
        """
        计算利率成本分析

        分析融资余额与利率的关系，包括相关性、回归分析等

        Args:
            margin_debt: 融资余额 Series (万亿美元)
            interest_rates: 利率 Series (百分比)
            window: 分析窗口 (月数)

        Returns:
            DataFrame，包含以下列:
            - date: 日期
            - correlation: 皮尔逊相关系数
            - regression_slope: 回归斜率
            - r_squared: 决定系数
            - p_value: p值 (统计显著性)
            - sample_size: 样本数量
            - time_period: 时间段描述

        Example:
            >>> margin = pd.Series([0.8, 0.85, 0.9] * 4)  # 12个月
            >>> rates = pd.Series([5.0, 4.8, 4.5] * 4)
            >>> analysis = calc.calculate_interest_cost_analysis(margin, rates)
            >>> print(analysis['correlation'].iloc[-1])
            -0.1234
        """
        raise NotImplementedError

    def calculate_part1_indicators(
        self,
        df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        批量计算Part1所有指标

        Args:
            df: 包含必要列的DataFrame
            必需列: margin_debt, sp500_market_cap, m2_money_supply, federal_funds_rate

        Returns:
            添加了Part1指标列的DataFrame
            新增列: market_leverage_ratio, money_supply_ratio, interest_cost_analysis
        """
        raise NotImplementedError

    # ==================== Part2 指标计算 (2010-02开始) ====================

    def calculate_leverage_change_rate(
        self,
        margin_debt: pd.Series,
        date_index: Optional[pd.DatetimeIndex] = None,
        change_type: str = "yoy"
    ) -> pd.Series:
        """
        计算杠杆变化率

        Args:
            margin_debt: 融资余额 Series
            date_index: 日期索引，用于确定时间间隔
            change_type: 变化类型 ('yoy'年同比, 'mom'月环比, 'qoq'季环比)

        Returns:
            变化率 Series (百分比，2位精度)
            - YoY: 12个月前对比
            - MoM: 1个月前对比
            - QoQ: 3个月前对比

        Example:
            >>> margin = pd.Series([0.8, 0.82, 0.85, 0.95])  # 4个月
            >>> yoy = calc.calculate_leverage_change_rate(margin, change_type='yoy')
            >>> print(yoy.iloc[0])  # NaN (不足12个月)
            >>> print(yoy.iloc[11])  # 第12个月的年同比
            18.75
        """
        raise NotImplementedError

    def calculate_investor_net_worth(
        self,
        margin_debt: pd.Series,
        sp500_market_cap: pd.Series,
        cash_balance: Optional[pd.Series] = None,
        market_cushion_rate: float = 0.1
    ) -> pd.Series:
        """
        计算投资者净资产

        公式: (现金余额 - 借方余额) - 市场缓冲垫
        默认假设: 现金余额 ≈ 0.5 * 融资余额

        Args:
            margin_debt: 融资余额 Series (万亿美元)
            sp500_market_cap: S&P500总市值 Series (万亿美元)
            cash_balance: 现金余额 Series，如果为None则使用估算值
            market_cushion_rate: 市场缓冲垫率 (默认10%)

        Returns:
            投资者净资产 Series (万亿美元，2位精度)
            正常情况下为负值，表示净负债

        Example:
            >>> margin = pd.Series([0.8, 0.85, 0.9])
            >>> market_cap = pd.Series([40, 42, 45])
            >>> net_worth = calc.calculate_investor_net_worth(margin, market_cap)
            >>> print(net_worth.iloc[0])
            -1.2000  # (-0.4) - 4.0 = -4.4, 修正为负值
        """
        raise NotImplementedError

    def calculate_part2_indicators(
        self,
        df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        批量计算Part2所有指标

        Args:
            df: 包含必要列的DataFrame
            必需列: margin_debt, sp500_market_cap

        Returns:
            添加了Part2指标列的DataFrame
            新增列: leverage_yoy_change, investor_net_worth
        """
        raise NotImplementedError

    # ==================== 辅助计算方法 ====================

    def calculate_zscore(
        self,
        series: pd.Series,
        window: int = 252,
        min_periods: Optional[int] = None
    ) -> pd.Series:
        """
        计算滚动Z分数

        Args:
            series: 原始数据 Series
            window: 滚动窗口 (默认252个交易日≈12个月)
            min_periods: 最小观测数，默认window//2

        Returns:
            Z分数 Series (标准化值，可正可负)

        Example:
            >>> data = pd.Series([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
            >>> zscore = calc.calculate_zscore(data, window=3)
            >>> print(zscore.iloc[2])  # 前3个数据的Z分数
            0.0
        """
        raise NotImplementedError

    def calculate_rolling_correlation(
        self,
        series1: pd.Series,
        series2: pd.Series,
        window: int = 12
    ) -> pd.Series:
        """
        计算滚动相关系数

        Args:
            series1: 第一个序列
            series2: 第二个序列
            window: 滚动窗口 (月数)

        Returns:
            相关系数 Series (-1到1之间)
        """
        raise NotImplementedError

    def calculate_percentile_rank(
        self,
        series: pd.Series,
        window: int = 252
    ) -> pd.Series:
        """
        计算历史百分位排名

        Args:
            series: 数据序列
            window: 排名窗口 (数据点数)

        Returns:
            百分位排名 Series (0-100)
        """
        raise NotImplementedError

    # ==================== 数据验证 ====================

    def validate_market_leverage_ratio(self, ratio: float) -> bool:
        """
        验证市场杠杆率合理性

        Args:
            ratio: 杠杆率值

        Returns:
            是否在合理范围内 (0.01 - 0.30)
        """
        return 0.01 <= ratio <= 0.30

    def validate_money_supply_ratio(self, ratio: float) -> bool:
        """
        验证货币供应比率合理性

        Args:
            ratio: 比率值

        Returns:
            是否在合理范围内 (0.01 - 0.10)
        """
        return 0.01 <= ratio <= 0.10

    def validate_leverage_change_rate(self, rate: float) -> bool:
        """
        验证杠杆变化率合理性

        Args:
            rate: 变化率值 (百分比)

        Returns:
            是否在合理范围内 (-50% - 100%)
        """
        return -50.0 <= rate <= 100.0

    def get_calculation_statistics(
        self,
        df: pd.DataFrame
    ) -> Dict[str, any]:
        """
        获取计算统计信息

        Args:
            df: 包含所有指标的DataFrame

        Returns:
            统计信息字典
            {
                'total_records': int,
                'part1_coverage': float,  # Part1指标覆盖率
                'part2_coverage': float,  # Part2指标覆盖率
                'data_gaps': List[str],
                'min_max_values': Dict,
                'calculation_timestamp': str
            }
        """
        raise NotImplementedError

    # ==================== 批量计算接口 ====================

    def calculate_all_indicators(
        self,
        df: pd.DataFrame,
        include_part1: bool = True,
        include_part2: bool = True
    ) -> pd.DataFrame:
        """
        计算所有Part1和Part2指标

        Args:
            df: 原始市场数据DataFrame
            include_part1: 是否计算Part1指标
            include_part2: 是否计算Part2指标

        Returns:
            添加了所有指标列的DataFrame
        """
        raise NotImplementedError

    def export_indicators_summary(
        self,
        df: pd.DataFrame,
        output_path: str
    ) -> bool:
        """
        导出指标摘要到文件

        Args:
            df: 包含所有指标的DataFrame
            output_path: 输出文件路径

        Returns:
            是否成功导出
        """
        raise NotImplementedError

    # ==================== 异常类定义 ====================

class DataLengthMismatch(Exception):
    """数据长度不匹配错误"""
    pass


class InsufficientDataError(Exception):
    """数据不足错误"""
    pass


class CalculationError(Exception):
    """计算错误"""
    pass


class ValidationError(Exception):
    """验证错误"""
    pass


# ==================== 合同版本信息 ====================

CONTRACT_VERSION = "1.0.0"
LAST_UPDATED = "2025-11-08"
API_COMPATIBILITY = "Python 3.11+"
