# 数据模型: 融资余额市场分析系统

**版本**: 1.0.1 (根据用户提供的文档更新)
**日期**: 2025-11-11
**分支**: 001-margin-debt-analysis

## 概述

本文档定义 `datas/complete_market_analysis_monthly.csv` 的完整数据模型，包含所有原始市场数据、计算指标和元数据信息。数据模型支持Part1指标（1997-01开始）和Part2指标（2010-02开始）的差异化覆盖要求。

**数据源文件**:
- `datas/margin-statistics.csv` - FINRA融资余额数据 (用户提供，1997-01至2025-09)
- `docs/dataSourceExplain.md` - 数据源详细说明
- `docs/sig_Bubbles.md` - 脆弱性指数算法
- `docs/calMethod.md` - 核心计算指标方法
- `docs/tableElements.md` - 图表展示规范

## 主数据文件

### 文件信息
- **文件名**: `datas/complete_market_analysis_monthly.csv`
- **编码**: UTF-8
- **分隔符**: 逗号 (,)
- **时间范围**: 1997-01 至 2025-09 (345个月度记录)
- **主键**: 日期 (YYYY-MM-DD)

## 核心数据架构

### 1. 基础市场数据 (Base Market Data)

| 字段名 | 类型 | 格式 | 描述 | 数据源 | 可用性 |
|--------|------|------|------|--------|--------|
| `date` | DATE | YYYY-MM-DD | 月度日期标识 | - | 全时段 |
| `sp500_index` | FLOAT | 十进制数 | S&P 500指数收盘价 | Yahoo Finance | 1997-01起 |
| `sp500_market_cap` | FLOAT | 十进制数 | Wilshire 5000总市值 (万亿美元) | FRED | 1997-01起 |
| `vix_index` | FLOAT | 十进制数 | VIX波动率指数 (月度均值) | CBOE | 1997-01起 |
| `m2_money_supply` | FLOAT | 十进制数 | M2货币供应量 (万亿美元) | FRED | 1997-01起 |
| `federal_funds_rate` | FLOAT | 百分比 | 联邦基金利率 (%) | FRED | 1997-01起 |
| `treasury_10y_rate` | FLOAT | 百分比 | 10年期国债收益率 (%) | FRED | 1997-01起 |
| `finra_D` | FLOAT | 十进制数 | 客户保证金账户借方余额 (万亿美元) | FINRA (margin-statistics.csv) | 1997-01起 |
| `finra_CC` | FLOAT | 十进制数 | 客户现金账户贷方余额 (万亿美元) | FINRA (margin-statistics.csv) | 1997-01起 |
| `finra_CM` | FLOAT | 十进制数 | 客户保证金账户贷方余额 (万亿美元) | FINRA (margin-statistics.csv) | 1997-01起 |
| `margin_debt` | FLOAT | 十进制数 | 融资余额 (万亿美元) (alias for finra_D) | FINRA | 1997-01起 |

**数据质量要求**:
- 所有数值字段不允许为NULL
- 百分比字段范围: -10% 到 50%
- 指数和市值字段必须 > 0
- 日期字段格式严格校验
- FINRA三字段 (D, CC, CM) 必须 ≥ 0
- 杠杆净值 (Leverage_Net) 可正可负，但应有合理范围
- VIX指数月度均值应基于日度数据计算 (参考 `docs/dataSourceExplain.md`)

### 2. Part1 计算指标 (1997-01开始，≥95%覆盖率)

| 字段名 | 类型 | 公式 | 描述 | 精度 |
|--------|------|------|------|------|
| `market_leverage_ratio` | FLOAT | margin_debt / sp500_market_cap | 市场杠杆率 | 4位小数 |
| `money_supply_ratio` | FLOAT | margin_debt / m2_money_supply | 货币供应比率 | 4位小数 |
| `interest_cost_analysis` | JSON | {correlation: float, regression_slope: float} | 利率成本分析 | 见下 |

**interest_cost_analysis JSON结构**:
```json
{
    "correlation": -0.1234,  // Margin Debt与联邦基金利率的相关系数
    "regression_slope": -0.0456,  // 回归分析斜率
    "r_squared": 0.2345,  // 决定系数
    "p_value": 0.0123,  // 统计显著性p值
    "sample_size": 24,  // 样本数量（月度）
    "time_period": "2023-01 to 2024-12"
}
```

### 3. Part2 计算指标 (2010-02开始，≥95%覆盖率)

| 字段名 | 类型 | 公式 | 描述 | 精度 |
|--------|------|------|------|------|
| `leverage_net` | FLOAT | D - (CC + CM) | 杠杆净值 | 2位小数 |
| `leverage_change_mom` | FLOAT | 月度变化率 | 杠杆净值月度环比变化率 | 2位小数 |
| `leverage_change_yoy` | FLOAT | 年度变化率 | 杠杆净值年度同比变化率 | 2位小数 |
| `investor_net_worth` | FLOAT | Leverage_Net | 投资者净资产 (等于杠杆净值) | 2位小数 |
| `leverage_normalized` | FLOAT | Leverage_Net / Stock_Market_Cap | 杠杆净值与S&P500总市值比 | 6位小数 |
| `market_return_mom` | FLOAT | 月度变化率 | S&P500市场回报月度变化率 | 2位小数 |
| `market_return_yoy` | FLOAT | 年度变化率 | S&P500市场回报年度变化率 | 2位小数 |
| `vulnerability_index` | FLOAT | Leverage_Z - VIX_Z | **脆弱性指数** (最核心) | 3位小数 |

**Part2指标计算逻辑** (参考 `docs/calMethod.md`):
- **杠杆净值**: `Leverage_Net = D - (CC + CM)` (投资者净杠杆)
- **杠杆变化率**:
  - 月度: `(Leverage_Net_t / Leverage_Net_{t-1}) - 1`
  - 年度: `(Leverage_Net_t / Leverage_Net_{t-12}) - 1`
- **投资者净资产**: 直接等于杠杆净值
- **杠杆标准化**: `Leverage_Normalized = Leverage_Net / Stock_Market_Cap` (用于Z-Score)
- **市场回报率**:
  - 月度: `(S&P500_t / S&P500_{t-1}) - 1`
  - 年度: `(S&P500_t / S&P500_{t-12}) - 1`
- **脆弱性指数**: `Vulnerability = Leverage_Z - VIX_Z` (核心算法)

**vulnerability_index计算 (参考 `docs/sig_Bubbles.md`)**:
- **核心公式**: `Vulnerability_t = Leverage_Z_t - VIX_Z_t`
- **杠杆标准化**: `Leverage_Normalized_t = Leverage_Net_t / Stock_Market_Cap_t`
- **Z-Score计算**:
  ```python
  Leverage_Z_t = (Leverage_Normalized_t - μ_lev) / σ_lev
  VIX_Z_t = (VIX_t - μ_vix) / σ_vix
  ```
- **窗口**: 252个交易日 (约12个月)
- **风险阈值**:
  - Vulnerability > 3: 高风险 (泡沫/自满)
  - Vulnerability < -3: 低风险 (恐慌/去杠杆)
  - -1 ~ +1: 中性 (正常市场)
- **更新频率**: 月度

### 4. Z-Score标准化字段 (参考 `docs/sig_Bubbles.md`)

| 字段名 | 类型 | 描述 | 计算方法 | 窗口 |
|--------|------|------|----------|------|
| `leverage_zscore` | FLOAT | 杠杆Z分数 | (Leverage_Normalized - rolling_mean) / rolling_std | 252日 |
| `vix_zscore` | FLOAT | VIX Z分数 | (vix_index - rolling_mean) / rolling_std | 252日 |

**Z-Score计算方法**:
```python
def calculate_zscore(series, window=252):
    """
    Z-Score标准化
    Z > 0: 高于历史平均
    Z < 0: 低于历史平均
    Z = ±2: 偏离2个标准差
    Z = ±3: 偏离3个标准差 (极端值)
    """
    rolling_mean = series.rolling(window=window, min_periods=1).mean()
    rolling_std = series.rolling(window=window, min_periods=1).std()
    return (series - rolling_mean) / rolling_std
```

**关键应用**:
- **杠杆Z分数**: 基于 `Leverage_Normalized` 的252天滚动标准化
- **VIX Z分数**: 基于 `vix_index` 的252天滚动标准化
- **脆弱性指数**: `Vulnerability = Leverage_Z - VIX_Z`

### 5. 风险分析字段

| 字段名 | 类型 | 描述 | 值域 |
|--------|------|------|------|
| `risk_level` | ENUM | 风险等级 | 低/中/高/极高 |
| `risk_score` | FLOAT | 风险评分 (0-100) | 0.0-100.0 |
| `confidence_level` | FLOAT | 置信度 | 0.0-1.0 |

**风险等级映射** (参考 `docs/sig_Bubbles.md`):
```python
def map_risk_level(vulnerability_index):
    """
    风险等级分类
    基于脆弱性指数的阈值判断
    """
    if vulnerability_index > 3:
        return '极高'  # 泡沫/自满状态，高风险
    elif vulnerability_index > 1:
        return '高'    # 杠杆高、波动率低
    elif vulnerability_index < -3:
        return '低'    # 恐慌/去杠杆状态，可能见底
    elif vulnerability_index < -1:
        return '中'    # 杠杆低、波动率高
    else:
        return '中'    # -1 ~ +1: 市场风险中性
```

### 6. 元数据字段

| 字段名 | 类型 | 描述 | 示例 |
|--------|------|------|------|
| `data_source` | JSON | 数据源信息 | 见下 |
| `calculation_date` | DATETIME | 指标计算时间戳 | 2025-11-08 12:00:00 |
| `data_quality_flag` | ENUM | 数据质量标记 | 见下 |
| `notes` | TEXT | 备注信息 | 可选 |

**data_source JSON结构** (参考 `docs/dataSourceExplain.md`):
```json
{
    "finra_margin": {
        "source": "finra_local",
        "file": "margin-statistics.csv",
        "fields": {
            "D": "Debit Balances in Customers' Securities Margin Accounts",
            "CC": "Free Credit Balances in Customers' Cash Accounts",
            "CM": "Free Credit Balances in Customers' Securities Margin Accounts"
        },
        "date_range": "1997-01 to 2025-09",
        "last_updated": "2025-10-31"
    },
    "vix": {
        "source": "cboe",
        "url": "https://www.cboe.com/tradable_products/vix/vix_historical_data/",
        "method": "daily_to_monthly_mean",
        "date_range": "1997-01 to 2025-09",
        "last_updated": "2025-11-07"
    },
    "sp500": {
        "source": "yahoo_finance",
        "api_version": "v8",
        "date_range": "1997-01 to 2025-09",
        "last_updated": "2025-11-07"
    },
    "wilshire5000": {
        "source": "fred",
        "series_id": "WILL5000INDFC",
        "date_range": "1997-01 to 2025-09",
        "last_updated": "2025-11-07"
    },
    "m2": {
        "source": "fred",
        "series_id": "M2SL",
        "date_range": "1997-01 to 2025-09",
        "last_updated": "2025-11-07"
    }
}
```

**data_quality_flag选项**:
- `VALIDATED`: 数据验证通过
- `MISSING_VALUES`: 存在缺失值
- `OUTLIER_DETECTED`: 检测到异常值
- `CROSS_VALIDATED`: 跨源验证通过
- `ESTIMATED`: 使用估算值
- `STALE`: 数据可能过时

## 数据完整性约束

### 主键约束
```sql
-- 日期字段唯一
UNIQUE (date)
```

### 检查约束
```sql
-- 数值范围检查
CHECK (sp500_index > 0)
CHECK (vix_index >= 0)
CHECK (federal_funds_rate >= -5 AND federal_funds_rate <= 50)
CHECK (vulnerability_index >= -10 AND vulnerability_index <= 10)
```

### 非空约束
```sql
-- 基础数据不能为空
NOT NULL (date, sp500_index, sp500_market_cap, vix_index, m2_money_supply, margin_debt)

-- Part1指标从1997-01开始不能为空
NOT NULL (market_leverage_ratio, money_supply_ratio) FROM 1997-01

-- Part2指标从2010-02开始不能为空
NOT NULL (leverage_yoy_change, investor_net_worth, vulnerability_index) FROM 2010-02
```

## 数据验证规则

### 1. 逻辑一致性

**规则1: 杠杆率合理性**
- `market_leverage_ratio` 应在 0.01 - 0.30 范围内
- 超过0.15标记为高风险状态

**规则2: VIX范围**
- `vix_index` 应在 8 - 80 范围内
- 异常值 (>2σ) 需要人工验证

**规则3: 利率关系**
- 联邦基金利率与10年期国债收益率应正相关
- 相关系数 < 0.3 时标记警告

### 2. 时间连续性

**规则4: 月度间隔**
- 日期字段必须按月递增，间隔30-31天
- 跳月数据需要标记并说明原因

**规则5: 数据新鲜度**
- 数据更新不应超过60天
- 超过90天标记为STALE

### 3. 跨字段验证

**规则6: 脆弱性指数计算**
- `vulnerability_index = leverage_zscore - vix_zscore`
- 允许误差: ±0.001

**规则7: 投资者净资产**
- 正常市场条件下应为负值（融资余额>现金余额）
- 长期正值需要验证

## 索引策略

### 主要索引
```sql
-- 主键索引 (日期)
CREATE INDEX idx_date ON complete_market_analysis_monthly (date);

-- Part1指标索引
CREATE INDEX idx_market_leverage ON complete_market_analysis_monthly (date)
WHERE market_leverage_ratio IS NOT NULL;

-- Part2指标索引
CREATE INDEX idx_vulnerability ON complete_market_analysis_monthly (date)
WHERE vulnerability_index IS NOT NULL;

-- 风险等级索引
CREATE INDEX idx_risk_level ON complete_market_analysis_monthly (risk_level);
```

## 数据质量监控

### 自动化检查

**每日检查**:
- [ ] 数据刷新状态
- [ ] 缺失值统计
- [ ] 异常值检测
- [ ] 逻辑一致性验证

**每周检查**:
- [ ] 数据源可靠性
- [ ] 计算准确性验证
- [ ] 性能基准测试
- [ ] 备份完整性

**每月检查**:
- [ ] 历史数据回溯验证
- [ ] 模型精度评估
- [ ] 数据源协议合规性
- [ ] 存储空间优化

### 质量报告

**质量评分算法**:
```python
def calculate_data_quality_score(df):
    """
    数据质量评分 (0-100)
    """
    score = 100

    # 缺失值扣分
    missing_rate = df.isnull().sum() / len(df)
    score -= missing_rate * 20

    # 异常值扣分
    outlier_rate = detect_outliers(df) / len(df)
    score -= outlier_rate * 15

    # 逻辑错误扣分
    logic_errors = validate_logic_constraints(df)
    score -= logic_errors * 10

    return max(0, min(100, score))
```

## 数据版本管理

### 版本策略
- **主版本**: 数据结构重大变更
- **次版本**: 指标计算方法优化
- **修订版本**: 数据修正或补全

### 变更日志
```python
CHANGELOG = {
    "1.0.0": {
        "date": "2025-11-08",
        "changes": ["初始数据结构", "Part1 & Part2指标", "风险分析字段"],
        "backward_compatible": True
    }
}
```

## 数据字典 (完整字段列表)

### 完整CSV字段定义 (48字段)

| # | 字段名 | 类型 | 必填 | 默认值 | 描述 |
|---|--------|------|------|--------|------|
| 1 | date | DATE | 是 | - | 日期 (YYYY-MM-DD) |
| 2 | sp500_index | FLOAT | 是 | - | S&P 500指数 |
| 3 | sp500_market_cap | FLOAT | 是 | - | S&P 500市值 (万亿美元) |
| 4 | vix_index | FLOAT | 是 | - | VIX波动率 |
| 5 | m2_money_supply | FLOAT | 是 | - | M2货币供应 (万亿美元) |
| 6 | federal_funds_rate | FLOAT | 是 | - | 联邦基金利率 (%) |
| 7 | treasury_10y_rate | FLOAT | 是 | - | 10年期国债收益率 (%) |
| 8 | margin_debt | FLOAT | 是 | - | 融资余额 (万亿美元) |
| 9 | market_leverage_ratio | FLOAT | 部分 | NULL | 市场杠杆率 (1997-01起) |
| 10 | money_supply_ratio | FLOAT | 部分 | NULL | 货币供应比率 (1997-01起) |
| 11 | interest_cost_analysis | JSON | 部分 | NULL | 利率成本分析 |
| 12 | leverage_yoy_change | FLOAT | 部分 | NULL | 杠杆变化率YoY% (2010-02起) |
| 13 | investor_net_worth | FLOAT | 部分 | NULL | 投资者净资产 (2010-02起) |
| 14 | vulnerability_index | FLOAT | 部分 | NULL | 脆弱性指数 (2010-02起) ⭐ |
| 15 | leverage_zscore | FLOAT | 部分 | NULL | 杠杆Z分数 |
| 16 | vix_zscore | FLOAT | 部分 | NULL | VIX Z分数 |
| 17 | risk_level | ENUM | 部分 | NULL | 风险等级 (低/中/高/极高) |
| 18 | risk_score | FLOAT | 部分 | NULL | 风险评分 (0-100) |
| 19 | confidence_level | FLOAT | 部分 | NULL | 置信度 (0-1) |
| 20 | data_source | JSON | 是 | - | 数据源信息 |
| 21 | calculation_date | DATETIME | 是 | - | 计算时间戳 |
| 22 | data_quality_flag | ENUM | 是 | - | 数据质量标记 |
| 23 | notes | TEXT | 否 | - | 备注 |

*注: 实际CSV包含原始数据的月度值 + 计算指标的月度值，共约45个字段*

## 数据流转图

```mermaid
graph TD
    A[datas/margin-statistics.csv] -->|Load FINRA Data| B[原始数据合并]
    B --> B1[finra_D (借方余额)]
    B --> B2[finra_CC (现金贷方)]
    B --> B3[finra_CM (保证金贷方)]

    C[FRED API] -->|Wilshire 5000| D[市场总市值]
    C -->|M2SL| E[M2货币供应]
    C -->|DFF| F[联邦基金利率]
    C -->|DGS10| G[10年期国债]

    H[CBOE VIX] -->|日度转月度| I[VIX月度均值]
    J[Yahoo Finance] -->|S&P500| K[市场指数]

    B1 & B2 & B3 --> L[数据清洗与合并]
    D & E & F & G & I & K --> L

    L --> M[Part1计算 (1997-01起)]
    L --> N[Part2计算 (2010-02起)]

    M --> O[市场杠杆率、货币供应比率、利率分析]
    N --> P[杠杆净值、变化率、脆弱性指数]

    O --> Q[完整数据集 complete_market_analysis_monthly.csv]
    P --> Q

    Q --> R[风险等级分类]
    Q --> S[数据验证]
    S --> T[质量报告]

    style Q fill:#e1f5fe
    style vulnerability_index fill:#ffeb3b
    style leverage_net fill:#f9f9f9
```

---

**数据模型版本**: 1.0.1
**最后更新**: 2025-11-11
**变更记录**:
- v1.0.0: 初始数据结构
- v1.0.1: 整合用户提供的文档，添加FINRA三字段详情，更新脆弱性指数算法说明
**状态**: ✅ 已通过技术审查
**下一步**: 创建API合同 (contracts/)

**参考文档**:
- `docs/dataSourceExplain.md` - 数据源详细说明
- `docs/calMethod.md` - 核心计算指标方法
- `docs/sig_Bubbles.md` - 脆弱性指数算法
- `docs/tableElements.md` - 图表展示规范
