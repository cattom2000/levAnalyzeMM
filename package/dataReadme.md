# Market Data Readme

## 数据概览

**文件名**: market_data.csv
**数据期间**: 2010年2月 - 2025年9月
**数据频率**: 月度
**数据点数量**: 188条记录
**更新时间**: 2025-11-19

---

## 字段说明

### 1. finra_D (Debit Balances in Customers' Securities Margin Accounts)
- **中文名称**: 客户证券保证金账户中的借方余额
- **单位**: 千美元 ($1,000)
- **数据来源**: FINRA (Financial Industry Regulatory Authority)
- **描述**: 投资者通过保证金账户借款购买证券的总金额，反映市场杠杆使用情况
- **重要性**: 这是计算市场杠杆率的核心数据，数值越高表示市场杠杆越大

### 2. finra_CC (Free Credit Balances in Customers' Cash Accounts)
- **中文名称**: 客户现金账户中的自由信贷余额
- **单位**: 千美元 ($1,000)
- **数据来源**: FINRA
- **描述**: 投资者现金账户中的可用资金，不受保证金限制
- **用途**: 用于计算投资者净价值和流动性指标

### 3. finra_CM (Free Credit Balances in Customers' Securities Margin Accounts)
- **中文名称**: 客户证券保证金账户中的自由信贷余额
- **单位**: 千美元 ($1,000)
- **数据来源**: FINRA
- **描述**: 投资者在保证金账户中持有的可用资金
- **用途**: 分析投资者在保证金账户中的资金配置

### 4. vix_index (CBOE Volatility Index)
- **中文名称**: 芝加哥期权交易所波动率指数
- **单位**: 指数值
- **数据来源**: Yahoo Finance (^VIX)
- **描述**: 衡量S&P 500指数期权隐含波动率的市场恐慌指数
- **用途**:
  - 计算Vulnerability Index的关键组件
  - 市场风险情绪指标
  - 投资组合风险评估
- **解释**:
  - VIX < 15: 低波动率，市场相对平静
  - VIX 15-30: 正常波动率水平
  - VIX > 30: 高波动率，市场恐慌

### 5. sp500_index (S&P 500 Index)
- **中文名称**: 标普500指数
- **单位**: 指数点
- **数据来源**: Yahoo Finance (^GSPC)
- **描述**: 代表美国500家大型上市公司的市值加权指数
- **用途**:
  - 计算市场总市值 (market_cap)
  - 市场表现基准
  - 杠杆率计算的分母

### 6. m2_money_supply (M2 Money Supply)
- **中文名称**: 广义货币供应量M2
- **单位**: 百万美元 ($1,000,000)
- **数据来源**: FRED (Federal Reserve Economic Data) - M2SL
- **描述**: 包括现金、支票存款、储蓄存款等广义货币供应量
- **用途**:
  - 计算Money Supply Ratio (Margin Debt / M2)
  - 衡量市场流动性环境
  - 货币政策影响分析

### 7. federal_funds_rate (Federal Funds Rate)
- **中文名称**: 联邦基金利率
- **单位**: 年利率百分比 (%)
- **数据来源**: FRED (DFF series)
- **描述**: 美国央行美联储设定的银行间隔夜拆借利率基准
- **用途**:
  - 利率环境分析
  - 杠杆成本评估
  - 货币政策影响研究

### 8. market_cap (Market Capitalization)
- **中文名称**: 市场总市值
- **单位**: 指数点 (基于S&P 500)
- **计算方法**: S&P 500指数 × 400 (近似系数)
- **描述**: 标普500成分股的总市值估算
- **用途**:
  - 计算Market Leverage Ratio (Margin Debt / Market Cap)
  - 市场规模衡量
  - 杠杆率分析的关键指标

---

## 数据质量信息

### 完整性
- 所有字段在2010-02至2025-09期间数据完整
- 无缺失值
- 数据及时性：延迟约1个月 (FINRA数据发布滞后)

### 可靠性
- 数据来源权威：FINRA、FRED、Yahoo Finance
- 数据经过验证和清洗
- 异常值检测和处理已完成

### 使用建议

1. **时间序列分析**: 所有指标都可以进行时间序列分析，观察趋势变化
2. **相关性分析**: 建议分析各指标之间的相关性
3. **风险指标计算**: 基于这些原始数据可以计算出多个风险评估指标
4. **预警系统**: 可以设置阈值监控市场风险水平

---

## 计算衍生指标

基于原始数据可以计算以下衍生指标：

1. **Market Leverage Ratio** = finra_D / market_cap
2. **Money Supply Ratio** = finra_D / m2_money_supply
3. **Vulnerability Index** = Leverage Z-Score - VIX Z-Score
4. **Leverage Change Rate** = (本期finra_D - 上期finra_D) / 上期finra_D × 100%
5. **Investor Net Worth** = market_cap - finra_D
6. **Interest Cost Analysis** = finra_D × federal_funds_rate / 100
7. **VIX vs Leverage Correlation** = correlation(vix_index, market_leverage_ratio)

---

## 更新频率

- **FINRA数据**: 每月发布，滞后约3-4周
- **VIX数据**: 每日更新
- **S&P 500数据**: 每日更新
- **M2货币供应**: 每月更新
- **联邦基金利率**: 每日更新

---

## 免责声明

本数据集仅供研究和教育目的使用。投资者在做出任何投资决策前应咨询专业财务顾问。过去的表现不代表未来的结果。

---

## 联系信息

如有问题或建议，请联系：
- 项目: levAnalyzeMM
- 版本: 1.0.0
- 更新日期: 2025-11-19
