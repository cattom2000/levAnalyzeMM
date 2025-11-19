# Market Analysis Algorithms

## 概述

本文档详细描述了市场杠杆分析系统中7个核心指标的计算算法。这些算法基于真实的金融市场数据，用于评估市场风险、杠杆水平和投资者行为。

---

## 1. Market Leverage Ratio (市场杠杆比率)

### 算法描述
**Overall market leverage measurement**

### 计算公式
```
Market Leverage Ratio = Margin Debt / Market Capitalization
                     = finra_D / market_cap
```

### 详细步骤

1. **数据预处理**
   - 获取Margin Debt数据 (finra_D，单位：千美元)
   - 获取Market Capitalization数据 (market_cap，指数点)
   - 数据单位标准化

2. **数值处理**
   - 应用边界限制：[0.001, 0.50]
   - 公式：`market_leverage_ratio = np.clip(margin_debt / market_cap, 0.001, 0.50)`
   - 四舍五入到4位小数

3. **统计指标**
   - 计算均值、最大值、最小值
   - 监控异常值和边界情况

### 参数说明
- **Margin Debt**: 客户证券保证金账户中的借方余额
- **Market Capitalization**: 基于S&P 500指数的市场总市值
- **单位**: 比率 (0-1之间，通常转换为百分比显示)

### 风险阈值
- **正常范围**: 0.2% - 0.8%
- **警告级别**: 0.8% - 1.5%
- **高风险**: > 1.5%

---

## 2. Money Supply Ratio (货币供应比率)

### 算法描述
**Margin debt to money supply ratio**

### 计算公式
```
Money Supply Ratio = Margin Debt / M2 Money Supply
                   = finra_D / m2_money_supply
```

### 详细步骤

1. **数据获取**
   - Margin Debt: finra_D (千美元)
   - M2 Money Supply: m2_money_supply (百万美元)
   - 单位统一：将M2转换为千美元单位

2. **计算过程**
   ```
   money_supply_ratio = finra_D / (m2_money_supply * 1000)
   ```

3. **边界处理**
   - 应用边界限制：[0.001, 0.20]
   - 四舍五入到4位小数

4. **解释指标**
   - 衡量保证金债务相对于整体货币供应量的比例
   - 反映杠杆占用的社会资源比例

### 应用场景
- 货币政策制定参考
- 市场流动性分析
- 金融系统性风险评估

---

## 3. Interest Cost Analysis (利息成本分析)

### 算法描述
**Financial burden assessment**

### 计算公式
```
Annual Interest Cost = Margin Debt × Federal Funds Rate / 100
                    = finra_D × federal_funds_rate / 100
```

### 详细步骤

1. **基础计算**
   ```
   annual_interest = margin_debt * (federal_funds_rate / 100)
   ```

2. **月均利息成本**
   ```
   monthly_interest = annual_interest / 12
   ```

3. **利息负担率**
   ```
   interest_burden_ratio = monthly_interest / market_cap × 100
   ```

4. **成本趋势分析**
   - 计算同比变化率
   - 分析利率敏感性
   - 压力测试模型

### 输出指标
- **年度利息成本** (千美元)
- **月均利息成本** (千美元)
- **利息负担率** (%)
- **杠杆成本弹性** (%)

---

## 4. Leverage Change Rate (杠杆变化率)

### 算法描述
**Month-over-month and year-over-year changes**

### 计算公式

#### 月度环比变化率 (MoM)
```
MoM Change Rate = (本期Margin Debt - 上期Margin Debt) / 上期Margin Debt × 100%
```

#### 年度同比变化率 (YoY)
```
YoY Change Rate = (本期Margin Debt - 12个月前Margin Debt) / 12个月前Margin Debt × 100%
```

### 详细步骤

1. **数据准备**
   - 按时间序列排列Margin Debt数据
   - 确认数据连续性和完整性

2. **MoM计算**
   ```python
   def calculate_mom_change(margin_debt_series):
       mom_change = margin_debt_series.pct_change() * 100
       return mom_change.round(2)
   ```

3. **YoY计算**
   ```python
   def calculate_yoy_change(margin_debt_series):
       yoy_change = ((margin_debt_series / margin_debt_series.shift(12)) - 1) * 100
       return yoy_change.round(2)
   ```

4. **统计特征**
   - 均值和标准差
   - 极值分析
   - 波动性度量

### 解释意义
- **高正值** (>10%): 市场杠杆快速扩张，风险积累
- **高负值** (<-10%): 市场去杠杆，可能伴随市场调整
- **零附近**: 市场杠杆保持稳定

---

## 5. Investor Net Worth (投资者净资产)

### 算法描述
**Net leverage position analysis**

### 计算公式
```
Investor Net Worth = Market Capitalization - Margin Debt
                   = market_cap - finra_D
```

### 详细步骤

1. **基础计算**
   ```
   net_worth = market_cap - finra_D
   ```

2. **净杠杆率**
   ```
   Net Leverage Ratio = finra_D / net_worth
                     = finra_D / (market_cap - finra_D)
   ```

3. **杠杆效率指标**
   ```
   Leverage Efficiency = (net_worth / market_cap) × 100%
   ```

4. **风险调整指标**
   - 最大回撤分析
   - 波动率调整收益
   - 风险调整后净资产

### 衍生指标
- **净杠杆倍数**: 杠杆使用的净效应
- **净资产回报率**: (净资产变化 / 初始净资产) × 100%
- **风险调整净值**: 考虑波动率的净值

---

## 6. Vulnerability Index (脆弱性指数)

### 算法描述
**Primary risk indicator**

### 计算公式
```
Vulnerability Index = Leverage Z-Score - VIX Z-Score
                   = Z(margin_debt) - Z(vix_index)
```

### 详细步骤

1. **Z-Score计算**
   ```python
   def calculate_zscore(series, window=252, min_periods=63):
       rolling_mean = series.rolling(window=window, min_periods=min_periods).mean()
       rolling_std = series.rolling(window=window, min_periods=min_periods).std()
       zscore = (series - rolling_mean) / rolling_std
       return zscore
   ```

2. **脆弱性指数计算**
   ```python
   def calculate_vulnerability_index(data):
       leverage_zscore = calculate_zscore(data['margin_debt'])
       vix_zscore = calculate_zscore(data['vix_index'])
       vulnerability_index = leverage_zscore - vix_zscore
       return vulnerability_index
   ```

3. **风险等级分类**
   - **极端高风险**: VI > 3.0
   - **高风险**: VI > 1.5
   - **中等风险**: VI > 0.5
   - **低风险**: VI < -3.0

### 算法原理
- **正Z-Score**: 杠杆高于历史平均水平
- **负Z-Score**: VIX低于历史平均水平 (市场过于平静)
- **指数高值**: 高杠杆 + 低波动 = 风险累积

---

## 7. VIX vs Leverage (VIX与杠杆比较分析)

### 算法描述
**Comparative volatility analysis**

### 分析方法

#### 相关性分析
```python
correlation = np.corrcoef(vix_index, market_leverage_ratio)[0, 1]
```

#### 回归分析
```python
from sklearn.linear_model import LinearRegression
X = vix_index.values.reshape(-1, 1)
y = market_leverage_ratio.values
model = LinearRegression().fit(X, y)
r_squared = model.score(X, y)
```

#### 领先滞后分析
- **VIX领先杠杆**: 分析VIX变化对后续杠杆变化的影响
- **杠杆领先VIX**: 分析杠杆变化对后续VIX的影响

### 关键洞察

#### 负相关情况 (< -0.3)
- 高杠杆期间，市场波动率较低
- 投资者过度自信，"风险平价"幻觉
- 市场处于自满状态

#### 正相关情况 (> 0.3)
- 杠杆与波动率同步变化
- 市场恐慌时去杠杆
- 健康的风险反馈机制

#### 零相关 (±0.3内)
- 杠杆与波动率关系复杂
- 需要多维度分析
- 考虑其他市场因素

---

## 算法实现要点

### 1. 数据质量控制
- 异常值检测和处理
- 缺失值插值方法
- 数据平滑技术

### 2. 参数优化
- 滚动窗口大小选择
- 最小样本数量要求
- 自适应阈值调整

### 3. 计算效率
- 向量化计算
- 缓存机制
- 并行处理

### 4. 结果验证
- 交叉验证
- 回测验证
- 压力测试

---

## 使用注意事项

1. **数据延迟**: FINRA数据有3-4周延迟
2. **样本偏差**: 数据覆盖主要市场，散户杠杆可能不完整
3. **模型局限**: 基于历史数据，不保证未来表现
4. **风险警告**: 高杠杆时期需要特别关注流动性风险

---

## 更新日志

- **v1.0.0** (2025-11-19): 初始算法文档
  - 7个核心指标算法定义
  - 计算公式和实现细节
  - 风险阈值和解释框架

---

## 联系方式

- 项目: levAnalyzeMM
- 算法版本: 1.0.0
- 文档更新: 2025-11-19
