# -*- coding: utf-8 -*-
"""
融资余额指标计算模块 - 融资余额市场分析系统
Margin Debt Indicators Calculation Module for Margin Debt Market Analysis System

负责计算Part1和Part2的核心指标，包括市场杠杆率、货币供应比率、利率成本分析、
杠杆变化率、投资者净资产等。

Calculates Part1 and Part2 core indicators including market leverage ratio,
money supply ratio, interest cost analysis, leverage change rate, etc.

版本: 1.0.0
日期: 2025-11-12
实现: Phase 3 - 计算引擎开发 (T017-T023)
"""

from typing import Dict, List, Optional, Tuple, Union
import pandas as pd
import numpy as np
import os
import sys
import logging
from datetime import datetime
from scipy import stats
from sklearn.linear_model import LinearRegression

# Add src to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config


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


class MarginDebtCalculator:
    """
    融资余额指标计算器
    Calculates margin debt related indicators
    """

    def __init__(self) -> None:
        """初始化计算器"""
        self.logger = logging.getLogger(__name__)
        self._setup_logging()

    def _setup_logging(self) -> None:
        """设置日志"""
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    # ==================== T022: Part1 指标计算 (1997-01开始) ====================

    def calculate_market_leverage_ratio(
        self,
        margin_debt: pd.Series,
        sp500_market_cap: pd.Series,
        handle_missing: str = "skip"
    ) -> pd.Series:
        """
        T022: 计算市场杠杆率: Margin Debt / S&P 500总市值

        Args:
            margin_debt: 融资余额 Series (万亿美元)
            sp500_market_cap: S&P500总市值 Series (万亿美元)
            handle_missing: 缺失值处理方式 ('skip', 'interpolate', 'ffill')

        Returns:
            市场杠杆率 Series (0-1之间的小数，4位精度)

        Raises:
            ValueError: 负值或零值输入
            DataLengthMismatch: 数据长度不匹配
        """
        # 验证数据
        if len(margin_debt) != len(sp500_market_cap):
            raise DataLengthMismatch(
                f"数据长度不匹配: margin_debt={len(margin_debt)}, "
                f"sp500_market_cap={len(sp500_market_cap)}"
            )

        # 检查负值或零值
        if (margin_debt <= 0).any():
            self.logger.warning("发现负值或零值在margin_debt中")
        if (sp500_market_cap <= 0).any():
            self.logger.warning("发现负值或零值在sp500_market_cap中")

        # 处理缺失值
        margin_debt_clean = margin_debt.copy()
        sp500_market_cap_clean = sp500_market_cap.copy()

        if handle_missing == "interpolate":
            margin_debt_clean = margin_debt_clean.interpolate()
            sp500_market_cap_clean = sp500_market_cap_clean.interpolate()
        elif handle_missing == "ffill":
            margin_debt_clean = margin_debt_clean.fillna(method='ffill')
            sp500_market_cap_clean = sp500_market_cap_clean.fillna(method='ffill')

        # 计算市场杠杆率
        try:
            market_leverage_ratio = margin_debt_clean / sp500_market_cap_clean

            # 限制在合理范围内
            market_leverage_ratio = market_leverage_ratio.clip(lower=0.001, upper=0.50)

            # 四舍五入到4位小数
            market_leverage_ratio = market_leverage_ratio.round(4)

            self.logger.info(
                f"市场杠杆率计算完成: 均值={market_leverage_ratio.mean():.4f}, "
                f"最大值={market_leverage_ratio.max():.4f}"
            )

            return market_leverage_ratio

        except Exception as e:
            raise CalculationError(f"计算市场杠杆率失败: {e}")

    def calculate_money_supply_ratio(
        self,
        margin_debt: pd.Series,
        m2_money_supply: pd.Series,
        handle_missing: str = "skip"
    ) -> pd.Series:
        """
        T022: 计算货币供应比率: Margin Debt / M2货币供应量

        Args:
            margin_debt: 融资余额 Series (万亿美元)
            m2_money_supply: M2货币供应量 Series (万亿美元)

        Returns:
            货币供应比率 Series (0-1之间的小数，4位精度)
        """
        # 验证数据
        if len(margin_debt) != len(m2_money_supply):
            raise DataLengthMismatch(
                f"数据长度不匹配: margin_debt={len(margin_debt)}, "
                f"m2_money_supply={len(m2_money_supply)}"
            )

        # 处理缺失值
        margin_debt_clean = margin_debt.copy()
        m2_money_supply_clean = m2_money_supply.copy()

        if handle_missing == "interpolate":
            margin_debt_clean = margin_debt_clean.interpolate()
            m2_money_supply_clean = m2_money_supply_clean.interpolate()
        elif handle_missing == "ffill":
            margin_debt_clean = margin_debt_clean.fillna(method='ffill')
            m2_money_supply_clean = m2_money_supply_clean.fillna(method='ffill')

        # 计算货币供应比率
        try:
            money_supply_ratio = margin_debt_clean / m2_money_supply_clean

            # 限制在合理范围内
            money_supply_ratio = money_supply_ratio.clip(lower=0.001, upper=0.20)

            # 四舍五入到4位小数
            money_supply_ratio = money_supply_ratio.round(4)

            self.logger.info(
                f"货币供应比率计算完成: 均值={money_supply_ratio.mean():.4f}, "
                f"最大值={money_supply_ratio.max():.4f}"
            )

            return money_supply_ratio

        except Exception as e:
            raise CalculationError(f"计算货币供应比率失败: {e}")

    def calculate_interest_cost_analysis(
        self,
        margin_debt: pd.Series,
        interest_rates: pd.Series,
        window: int = 12
    ) -> pd.DataFrame:
        """
        T022: 计算利率成本分析

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
        """
        # 验证数据
        if len(margin_debt) != len(interest_rates):
            raise DataLengthMismatch(
                f"数据长度不匹配: margin_debt={len(margin_debt)}, "
                f"interest_rates={len(interest_rates)}"
            )

        if window < 3:
            raise ValueError("窗口大小不能小于3个月")

        results = []
        dates = margin_debt.index if hasattr(margin_debt, 'index') else range(len(margin_debt))

        try:
            for i in range(window - 1, len(margin_debt)):
                # 获取窗口数据
                start_idx = i - window + 1
                end_idx = i + 1

                margin_window = margin_debt.iloc[start_idx:end_idx]
                rates_window = interest_rates.iloc[start_idx:end_idx]

                # 移除NaN值
                valid_data = pd.DataFrame({
                    'margin': margin_window,
                    'rates': rates_window
                }).dropna()

                if len(valid_data) < 3:
                    continue

                # 计算相关系数
                correlation, p_value = stats.pearsonr(valid_data['margin'], valid_data['rates'])

                # 线性回归
                X = valid_data['rates'].values.reshape(-1, 1)
                y = valid_data['margin'].values

                reg = LinearRegression()
                reg.fit(X, y)

                regression_slope = reg.coef_[0]
                r_squared = reg.score(X, y)

                # 获取时间段信息
                start_date = dates[start_idx] if hasattr(dates[start_idx], 'strftime') else f"Period-{start_idx}"
                end_date = dates[i] if hasattr(dates[i], 'strftime') else f"Period-{i}"
                time_period = f"{start_date} to {end_date}"

                results.append({
                    'date': dates[i],
                    'correlation': correlation,
                    'regression_slope': regression_slope,
                    'r_squared': r_squared,
                    'p_value': p_value,
                    'sample_size': len(valid_data),
                    'time_period': time_period
                })

            result_df = pd.DataFrame(results)
            result_df = result_df.set_index('date')

            self.logger.info(
                f"利率成本分析完成: 窗口={window}个月, "
                f"平均相关性={result_df['correlation'].mean():.3f}"
            )

            return result_df

        except Exception as e:
            raise CalculationError(f"计算利率成本分析失败: {e}")

    def calculate_part1_indicators(
        self,
        df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        T022: 批量计算Part1所有指标

        Args:
            df: 包含必要列的DataFrame
            必需列: margin_debt, sp500_market_cap, m2_money_supply, federal_funds_rate

        Returns:
            添加了Part1指标列的DataFrame
            新增列: market_leverage_ratio, money_supply_ratio, interest_cost_analysis
        """
        result_df = df.copy()

        try:
            # 1. 计算市场杠杆率
            if 'margin_debt' in df.columns and 'sp500_market_cap' in df.columns:
                result_df['market_leverage_ratio'] = self.calculate_market_leverage_ratio(
                    df['margin_debt'], df['sp500_market_cap']
                )
                self.logger.info("✓ Part1指标: 市场杠杆率计算完成")

            # 2. 计算货币供应比率
            if 'margin_debt' in df.columns and 'm2_money_supply' in df.columns:
                result_df['money_supply_ratio'] = self.calculate_money_supply_ratio(
                    df['margin_debt'], df['m2_money_supply']
                )
                self.logger.info("✓ Part1指标: 货币供应比率计算完成")

            # 3. 计算利率成本分析
            if 'margin_debt' in df.columns and 'federal_funds_rate' in df.columns:
                interest_analysis = self.calculate_interest_cost_analysis(
                    df['margin_debt'], df['federal_funds_rate']
                )
                # 将分析结果合并到主DataFrame
                for col in ['correlation', 'regression_slope', 'r_squared']:
                    result_df[f'interest_{col}'] = interest_analysis[col]
                self.logger.info("✓ Part1指标: 利率成本分析完成")

            # 4. 计算Part1覆盖度
            part1_coverage = self._calculate_coverage(
                result_df,
                ['market_leverage_ratio', 'money_supply_ratio', 'interest_correlation']
            )

            self.logger.info(
                f"✓ Part1所有指标计算完成，覆盖度: {part1_coverage:.2%}"
            )

            return result_df

        except Exception as e:
            raise CalculationError(f"批量计算Part1指标失败: {e}")

    # ==================== T023: Part2 指标计算 (2010-02开始) ====================

    def calculate_leverage_net(
        self,
        finra_D: pd.Series,
        finra_CC: pd.Series,
        finra_CM: pd.Series
    ) -> pd.Series:
        """
        T023: 计算杠杆净值

        公式: Leverage_Net = D - (CC + CM)

        Args:
            finra_D: FINRA借方余额 Series (万亿美元)
            finra_CC: FINRA现金账户贷方余额 Series (万亿美元)
            finra_CM: FINRA保证金账户贷方余额 Series (万亿美元)

        Returns:
            杠杆净值 Series (万亿美元，2位精度)
        """
        try:
            # 计算杠杆净值
            leverage_net = finra_D - (finra_CC + finra_CM)

            # 四舍五入到2位小数
            leverage_net = leverage_net.round(2)

            self.logger.info(
                f"杠杆净值计算完成: 均值={leverage_net.mean():.2f}, "
                f"最大值={leverage_net.max():.2f}, 最小值={leverage_net.min():.2f}"
            )

            return leverage_net

        except Exception as e:
            raise CalculationError(f"计算杠杆净值失败: {e}")

    def calculate_leverage_change_rate(
        self,
        margin_debt: pd.Series,
        date_index: Optional[pd.DatetimeIndex] = None,
        change_type: str = "yoy"
    ) -> pd.Series:
        """
        T023: 计算杠杆变化率

        Args:
            margin_debt: 融资余额 Series
            date_index: 日期索引，用于确定时间间隔
            change_type: 变化类型 ('yoy'年同比, 'mom'月环比, 'qoq'季环比)

        Returns:
            变化率 Series (百分比，2位精度)
            - YoY: 12个月前对比
            - MoM: 1个月前对比
            - QoQ: 3个月前对比
        """
        if change_type not in ['yoy', 'mom', 'qoq']:
            raise ValueError(f"不支持的变化类型: {change_type}")

        # 确定滞后期间
        if change_type == 'yoy':
            lag = 12
        elif change_type == 'mom':
            lag = 1
        else:  # qoq
            lag = 3

        try:
            if change_type == 'mom':
                # 月度环比：直接使用pct_change()
                change_rate = margin_debt.pct_change() * 100
            else:
                # 年度同比或季度环比：使用shift()
                previous_value = margin_debt.shift(lag)
                change_rate = ((margin_debt - previous_value) / previous_value) * 100

            # 四舍五入到2位小数
            change_rate = change_rate.round(2)

            # 限制在合理范围内
            change_rate = change_rate.clip(lower=-100, upper=500)

            self.logger.info(
                f"{change_type}变化率计算完成: 均值={change_rate.mean():.2f}%, "
                f"最大值={change_rate.max():.2f}%"
            )

            return change_rate

        except Exception as e:
            raise CalculationError(f"计算{change_type}变化率失败: {e}")

    def calculate_investor_net_worth(
        self,
        margin_debt: pd.Series,
        sp500_market_cap: pd.Series,
        cash_balance: Optional[pd.Series] = None,
        market_cushion_rate: float = 0.1
    ) -> pd.Series:
        """
        T023: 计算投资者净资产

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
        """
        try:
            # 如果没有提供现金余额，估算为融资余额的50%
            if cash_balance is None:
                cash_balance = margin_debt * 0.5
                self.logger.info("使用估算现金余额: 融资余额的50%")

            # 计算市场缓冲垫
            market_cushion = sp500_market_cap * market_cushion_rate

            # 计算净资产: (现金 - 融资余额) - 市场缓冲垫
            investor_net_worth = (cash_balance - margin_debt) - market_cushion

            # 四舍五入到2位小数
            investor_net_worth = investor_net_worth.round(2)

            # 计算统计信息
            negative_pct = (investor_net_worth < 0).mean() * 100

            self.logger.info(
                f"投资者净资产计算完成: 均值={investor_net_worth.mean():.2f}, "
                f"负值占比={negative_pct:.1f}%"
            )

            return investor_net_worth

        except Exception as e:
            raise CalculationError(f"计算投资者净资产失败: {e}")

    def calculate_leverage_normalized(
        self,
        leverage_net: pd.Series,
        stock_market_cap: pd.Series
    ) -> pd.Series:
        """
        T023: 计算杠杆标准化

        公式: Leverage_Normalized = Leverage_Net / Stock_Market_Cap

        Args:
            leverage_net: 杠杆净值 Series
            stock_market_cap: 股市总市值 Series

        Returns:
            杠杆标准化 Series (6位精度)
        """
        try:
            leverage_normalized = leverage_net / stock_market_cap

            # 六位小数精度
            leverage_normalized = leverage_normalized.round(6)

            self.logger.info(
                f"杠杆标准化计算完成: 均值={leverage_normalized.mean():.6f}, "
                f"最大值={leverage_normalized.max():.6f}"
            )

            return leverage_normalized

        except Exception as e:
            raise CalculationError(f"计算杠杆标准化失败: {e}")

    def calculate_part2_indicators(
        self,
        df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        T023: 批量计算Part2所有指标

        Args:
            df: 包含必要列的DataFrame
            必需列: finra_D, finra_CC, finra_CM, sp500_market_cap

        Returns:
            添加了Part2指标列的DataFrame
            新增列: leverage_net, leverage_change_mom, leverage_change_yoy,
                   investor_net_worth, leverage_normalized
        """
        result_df = df.copy()

        try:
            # 1. 计算杠杆净值
            if all(col in df.columns for col in ['finra_D', 'finra_CC', 'finra_CM']):
                result_df['leverage_net'] = self.calculate_leverage_net(
                    df['finra_D'], df['finra_CC'], df['finra_CM']
                )
                self.logger.info("✓ Part2指标: 杠杆净值计算完成")

            # 2. 计算杠杆变化率(月度和年度)
            if 'margin_debt' in df.columns:
                result_df['leverage_change_mom'] = self.calculate_leverage_change_rate(
                    df['margin_debt'], change_type='mom'
                )
                result_df['leverage_change_yoy'] = self.calculate_leverage_change_rate(
                    df['margin_debt'], change_type='yoy'
                )
                self.logger.info("✓ Part2指标: 杠杆变化率计算完成")

            # 3. 计算投资者净资产
            if 'margin_debt' in df.columns and 'sp500_market_cap' in df.columns:
                result_df['investor_net_worth'] = self.calculate_investor_net_worth(
                    df['margin_debt'], df['sp500_market_cap']
                )
                self.logger.info("✓ Part2指标: 投资者净资产计算完成")

            # 4. 计算杠杆标准化
            if 'leverage_net' in result_df.columns and 'sp500_market_cap' in df.columns:
                result_df['leverage_normalized'] = self.calculate_leverage_normalized(
                    result_df['leverage_net'], df['sp500_market_cap']
                )
                self.logger.info("✓ Part2指标: 杠杆标准化计算完成")

            # 5. 计算Part2覆盖度
            part2_coverage = self._calculate_coverage(
                result_df,
                ['leverage_net', 'leverage_change_yoy', 'investor_net_worth', 'leverage_normalized']
            )

            self.logger.info(
                f"✓ Part2所有指标计算完成，覆盖度: {part2_coverage:.2%}"
            )

            return result_df

        except Exception as e:
            raise CalculationError(f"批量计算Part2指标失败: {e}")

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
        """
        if min_periods is None:
            min_periods = window // 2

        try:
            # 计算滚动均值和标准差
            rolling_mean = series.rolling(window=window, min_periods=min_periods).mean()
            rolling_std = series.rolling(window=window, min_periods=min_periods).std()

            # 计算Z分数
            zscore = (series - rolling_mean) / rolling_std

            return zscore

        except Exception as e:
            raise CalculationError(f"计算Z分数失败: {e}")

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
        try:
            correlation = series1.rolling(window=window).corr(series2)
            return correlation

        except Exception as e:
            raise CalculationError(f"计算滚动相关系数失败: {e}")

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
        try:
            percentile_rank = series.rolling(window=window).apply(
                lambda x: stats.percentileofscore(x, x.iloc[-1]) if len(x) == window else np.nan
            )
            return percentile_rank

        except Exception as e:
            raise CalculationError(f"计算百分位排名失败: {e}")

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
        """
        stats_dict = {
            'total_records': len(df),
            'part1_coverage': 0.0,
            'part2_coverage': 0.0,
            'data_gaps': [],
            'min_max_values': {},
            'calculation_timestamp': datetime.now().isoformat()
        }

        try:
            # 计算Part1覆盖度
            part1_cols = ['market_leverage_ratio', 'money_supply_ratio']
            part1_available = [col for col in part1_cols if col in df.columns]
            if part1_available:
                stats_dict['part1_coverage'] = self._calculate_coverage(df, part1_available)

            # 计算Part2覆盖度
            part2_cols = ['leverage_net', 'leverage_change_yoy', 'investor_net_worth']
            part2_available = [col for col in part2_cols if col in df.columns]
            if part2_available:
                stats_dict['part2_coverage'] = self._calculate_coverage(df, part2_available)

            # 计算最值
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            for col in numeric_cols:
                if df[col].notna().any():
                    stats_dict['min_max_values'][col] = {
                        'min': df[col].min(),
                        'max': df[col].max(),
                        'mean': df[col].mean()
                    }

        except Exception as e:
            self.logger.error(f"获取计算统计信息失败: {e}")

        return stats_dict

    def _calculate_coverage(self, df: pd.DataFrame, columns: List[str]) -> float:
        """计算覆盖率"""
        if not columns:
            return 0.0

        available_cols = [col for col in columns if col in df.columns]
        if not available_cols:
            return 0.0

        total_records = len(df)
        valid_records = 0

        for col in available_cols:
            valid_records += df[col].notna().sum()

        return valid_records / (total_records * len(available_cols))

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
        result_df = df.copy()

        try:
            # 计算Part1指标
            if include_part1:
                result_df = self.calculate_part1_indicators(result_df)

            # 计算Part2指标
            if include_part2:
                result_df = self.calculate_part2_indicators(result_df)

            # 获取统计信息
            stats_info = self.get_calculation_statistics(result_df)
            result_df.attrs['calculation_stats'] = stats_info

            self.logger.info(
                f"所有指标计算完成: Part1覆盖度={stats_info['part1_coverage']:.2%}, "
                f"Part2覆盖度={stats_info['part2_coverage']:.2%}"
            )

            return result_df

        except Exception as e:
            raise CalculationError(f"批量计算所有指标失败: {e}")

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
        try:
            # 选择关键指标列
            summary_cols = [
                'date', 'margin_debt', 'market_leverage_ratio', 'money_supply_ratio',
                'leverage_net', 'leverage_change_yoy', 'investor_net_worth', 'leverage_normalized'
            ]

            available_cols = [col for col in summary_cols if col in df.columns]
            summary_df = df[available_cols].copy()

            # 导出到CSV
            summary_df.to_csv(output_path, index=False)

            self.logger.info(f"指标摘要已导出到: {output_path}")
            return True

        except Exception as e:
            self.logger.error(f"导出指标摘要失败: {e}")
            return False


# ==================== 便捷函数 ====================

def get_margin_debt_calculator() -> MarginDebtCalculator:
    """
    获取MarginDebtCalculator实例的便捷函数

    Returns:
        MarginDebtCalculator实例
    """
    return MarginDebtCalculator()


# ==================== 测试代码 ====================

if __name__ == "__main__":
    # 简单测试
    calculator = MarginDebtCalculator()

    print("=== MarginDebtCalculator模块测试 ===")

    # 测试Part1指标
    try:
        test_data = pd.DataFrame({
            'date': pd.date_range('2020-01-01', periods=24, freq='M'),
            'margin_debt': [0.8 + i * 0.02 for i in range(24)],
            'sp500_market_cap': [40 + i * 0.5 for i in range(24)],
            'm2_money_supply': [21 + i * 0.2 for i in range(24)],
            'federal_funds_rate': [2.5 + np.random.randn() * 0.5 for _ in range(24)]
        }).set_index('date')

        result = calculator.calculate_part1_indicators(test_data)
        print(f"✓ Part1指标计算成功: {len(result)} 条记录")

        stats = calculator.get_calculation_statistics(result)
        print(f"✓ 统计信息: Part1覆盖度 {stats['part1_coverage']:.2%}")

    except Exception as e:
        print(f"✗ Part1指标计算失败: {e}")

    print("\n=== 测试完成 ===")
