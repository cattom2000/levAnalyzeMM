# 实施计划: 融资余额市场分析系统

**分支**: `001-margin-debt-analysis` | **日期**: 2025-11-08 | **规格**: [Link to spec.md](spec.md)
**输入**: Feature specification from `/specs/001-margin-debt-analysis/spec.md`

**说明**: 此模板由 `/speckit.plan` 命令填充。参见 `.specify/templates/commands/plan.md` 了解执行工作流。

## 摘要

本项目构建一个基于Streamlit的融资余额市场分析系统，通过多数据源集成和高级可视化，识别市场风险信号和投资机会。系统核心为**脆弱性指数**（杠杆Z分数 - VIX Z分数），配合Part1和Part2共7个核心指标图表，实现从1997年至2025年的市场数据分析和历史危机时期对比。

**新增内容**:
- 用户提供数据源：`datas/margin-statistics.csv` (FINRA融资余额数据，1997-01至2025-09)
- 脆弱性指数算法详细文档：`docs/sig_Bubbles.md`
- 计算方法说明：`docs/calMethod.md` 和图表展示说明：`docs/tableElements.md`
- 数据源说明：`docs/dataSourceExplain.md`

**技术方法**:
- Python + Streamlit构建Web应用
- Pandas进行数据处理和分析
- Plotly实现交互式多图表可视化
- 多数据源集成（FRED、Yahoo Finance、CBOE + 本地FINRA数据）
- 特殊时间范围覆盖：Part1 (1997-01至2025-09, ≥95%覆盖率)，Part2 (2010-02至2025-09, ≥95%覆盖率)

## 技术上下文

**语言/版本**: Python 3.11+
**主要依赖**: Streamlit, Pandas, Plotly, yfinance, fredapi
**存储**:
- `datas/margin-statistics.csv` - FINRA融资余额数据（用户提供，1997-01至2025-09）
- `datas/complete_market_analysis_monthly.csv` - 完整市场分析数据（计算生成）
**测试**: pytest (单元测试), Streamlit测试框架
**目标平台**: Linux服务器，Web浏览器访问
**项目类型**: 单体Web应用
**性能目标**: 页面加载 < 30秒, 图表交互响应 < 2秒, 单次分析 < 10秒
**约束条件**: 数据覆盖率 Part1 ≥95%, Part2 ≥95%, 核心算法测试覆盖率 > 80%
**规模/范围**: 处理25+年历史数据，月度频率，7个核心指标图表，3个历史危机时期（1999-2003互联网泡沫、2006-2010金融危机、2019-2023疫情冲击）

## 章程检查

*GATE: 必须在Phase 0研究之前通过。Phase 1设计后重新检查。*

### 核心原则合规性检查

✅ **数据驱动分析** - 多数据源交叉验证 (FINRA, FRED, Yahoo Finance, CBOE)
✅ **风险检测与预警机制** - 四级风险等级 (低/中/高/极高)
✅ **跨指标关联分析** - 皮尔逊相关系数 + Granger因果关系检验
✅ **基于证据的投资洞察** - 置信度 > 80%, 历史回测验证
✅ **持续监控与迭代优化** - 定期数据更新和模型验证

### 额外约束合规性

✅ **技术约束** - CSV/JSON/Excel导出, 批处理模式, >80%测试覆盖
✅ **合规要求** - 数据源许可协议, 免责声明, 90天访问日志
✅ **可视化标准** - 数据来源标注, 标准化风险颜色系统, 置信区间

### 验证阶段合规性

✅ **回测验证** - ≥10年历史数据验证
✅ **压力测试** - 极端市场条件模拟
✅ **同行评审** - 关键算法独立评审
✅ **用户验收** - 3轮用户测试

**检查结果**: ✅ 所有章程要求已满足，可以继续Phase 0研究

## 项目结构

### 文档结构 (此功能)

```text
specs/001-margin-debt-analysis/
├── plan.md              # 此文件 (/speckit.plan 命令输出)
├── research.md          # Phase 0 输出 (/speckit.plan 命令)
├── data-model.md        # Phase 1 输出 (/speckit.plan 命令)
├── quickstart.md        # Phase 1 输出 (/speckit.plan 命令)
├── contracts/           # Phase 1 输出 (/speckit.plan 命令)
│   ├── data_fetcher.py
│   ├── margin_debt_calculator.py
│   ├── vulnerability_index.py
│   ├── risk_analyzer.py
│   └── visualization.py
└── tasks.md             # Phase 2 输出 (/speckit.tasks 命令 - 非 /speckit.plan 创建)
```

### 源代码结构 (仓库根目录)

```text
# 单体项目结构
src/
├── data/
│   ├── __init__.py
│   ├── fetcher.py          # 数据获取模块 (FRED, Yahoo Finance, FINRA)
│   ├── processor.py        # 数据处理和清洗
│   └── margin_statistics.csv  # FINRA特殊数据文件
├── models/
│   ├── __init__.py
│   ├── market_data.py      # 市场数据模型
│   └── indicators.py       # 指标计算 (Part1 & Part2)
├── services/
│   ├── __init__.py
│   ├── vulnerability_index.py  # 脆弱性指数核心算法
│   ├── risk_analysis.py    # 风险信号识别
│   └── historical_crises.py # 历史危机时期数据
├── utils/
│   ├── __init__.py
│   ├── calculations.py     # Z分数和统计计算
│   └── formatters.py       # 数据格式化
├── tests/
│   ├── __init__.py
│   ├── test_data_fetcher.py
│   ├── test_indicators.py
│   ├── test_vulnerability_index.py
│   └── test_integration.py
├── app.py                 # Streamlit主应用
├── config.py              # 配置管理
└── requirements.txt       # 依赖管理

# 数据文件
datas/
├── complete_market_analysis_monthly.csv  # 完整数据集
└── margin-statistics.csv                 # FINRA数据 (用户提供)

# 文档
docs/
├── sig_Bubbles.md          # 脆弱性指数Z-score计算方法 (算法参考)
├── calMethod.md            # 核心计算指标计算方法
├── tableElements.md        # 图表展示说明 (7个核心指标)
└── dataSourceExplain.md    # 数据源说明 (VIX获取、FINRA数据字段)

```

**结构决策**: 单体Web应用结构，数据处理逻辑与Streamlit UI分离，模块化设计便于测试和维护。选择了"Option 1: Single project"结构，因为这是一个纯前端分析工具，不需要分离的后端API或移动端。

**文档参考**:
- 核心算法: `docs/sig_Bubbles.md` (脆弱性指数计算方法)
- 计算逻辑: `docs/calMethod.md` (Part1 & Part2指标计算公式)
- 可视化设计: `docs/tableElements.md` (7个核心图表展示方式)
- 数据源处理: `docs/dataSourceExplain.md` (FINRA数据字段说明 & VIX数据获取)

## 复杂度跟踪

> **仅在章程检查有违规需要证明时填写**

| 违规 | 为什么需要 | 被拒绝的更简单替代方案 |
|------|-----------|----------------------|
| 无违规 | N/A | N/A |

---

## Phase 0: 大纲与研究

### 未知项提取

**技术依赖研究**:
- 需要研究: Streamlit最佳实践和性能优化
- 需要研究: Plotly交互式图表在Streamlit中的最佳集成
- 需要研究: yfinance和fredapi数据获取的稳定性和速率限制
- 需要研究: 大数据量(1997-2025)处理的性能优化策略

**数据模型研究**:
- ✅ 已提供: `datas/margin-statistics.csv`文件格式 (Year-Month, D, CC, CM三字段)
- ✅ 已提供: Z-score计算的统计方法 (参考 `docs/sig_Bubbles.md`)
- ✅ 已提供: 计算方法说明 (`docs/calMethod.md`) 和图表展示 (`docs/tableElements.md`)
- ✅ 已提供: 数据源说明 (`docs/dataSourceExplain.md`)
- 需要研究: 多数据源同步和对齐的挑战

**集成模式研究**:
- 需要研究: Plotly动态图表与Streamlit的响应式集成
- 需要研究: 时间序列可视化中历史危机时期的标记方法
- 需要研究: 交互式时间范围选择器的实现模式

### 研究任务分配

**Streamlit + Plotly性能研究**
- 任务: "研究Streamlit与Plotly集成的性能优化和最佳实践"
- 重点: 大数据集渲染、交互响应时间、内存优化
- 输出: 技术选型建议和实现方案

**多数据源集成研究**
- 任务: "研究FRED、Yahoo Finance、CBOE数据获取的稳定方案"
- 重点: API限制、数据同步、错误处理、缓存策略
- 输出: 数据获取架构和容错机制

**脆弱性指数算法研究**
- 任务: "研究Z-score计算和脆弱性指数实现方法"
- 重点: 统计计算准确性、历史回测验证、性能优化
- 输出: 核心算法详细设计和测试策略

**可视化最佳实践研究**
- 任务: "研究金融时间序列可视化的交互式设计模式"
- 重点: 多图表同步、危机时期标记、响应式设计
- 输出: UI/UX设计方案和组件库

## Phase 1: 设计与合同

### 数据模型设计 (data-model.md)

**主数据实体** (参考 `docs/dataSourceExplain.md`):
- **FINRA融资余额数据** (1997-01至2025-09)
  - Year-Month: 年月
  - D (Debit Balances): 客户保证金账户借方余额（融资余额）
  - CC (Cash Credit): 客户现金账户贷方余额
  - CM (Margin Credit): 客户保证金账户贷方余额

- **外部数据源**
  - VIX指数: CBOE (月度平均从日度数据转换)
  - S&P500指数和总市值: Yahoo Finance/FRED
  - M2货币供应量: FRED
  - 联邦基金利率: FRED
  - Wilshire 5000: FRED (用于杠杆标准化)

- **计算指标 (Part1 - 1997-01开始)**
  - 市场杠杆率: Margin Debt / S&P500总市值
  - 货币供应比率: Margin Debt / M2
  - 利率成本分析: Margin Debt vs 利率关系

- **计算指标 (Part2 - 2010-02开始)**
  - 杠杆净值: `Leverage_Net = D - (CC + CM)`
  - 杠杆变化率: 月度环比和年度同比变化率
  - 投资者净资产: Leverage_Net
  - 脆弱性指数: 杠杆Z分数 - VIX Z分数 (⭐核心指标)
  - 杠杆标准化: `Leverage_Normalized = Leverage_Net / Stock_Market_Cap`

- **Z-Score标准化**
  - Leverage_Z: 252天滚动窗口标准化
  - VIX_Z: 252天滚动窗口标准化
  - 脆弱性指数: `Vulnerability = Leverage_Z - VIX_Z`

- **元数据**
  - 数据源标注
  - 计算时间戳
  - 数据质量标记
  - 风险等级分类 (低/中/高/极高)

### API合同 (contracts/)

**data_fetcher.py** (参考 `docs/dataSourceExplain.md`)
- `load_finra_data() -> pd.DataFrame`: 加载 `datas/margin-statistics.csv` (D, CC, CM字段)
- `fetch_vix_data(start_date: str, end_date: str) -> pd.Series`: 从CBOE获取VIX数据
- `fetch_market_cap_data(start_date: str, end_date: str) -> pd.Series`: 获取S&P500/Wilshire 5000数据
- `fetch_fred_data(series_id: str, start_date: str, end_date: str) -> pd.Series`: 获取M2、利率数据
- `sync_data_sources(finra_df: pd.DataFrame) -> pd.DataFrame`: 同步多数据源

**margin_debt_calculator.py** (参考 `docs/calMethod.md`)
- `calculate_leverage_net(df: pd.DataFrame) -> pd.Series`: 计算 `Leverage_Net = D - (CC + CM)`
- `calculate_leverage_change_rate(df: pd.DataFrame) -> Tuple[pd.Series, pd.Series]`: 月度和年度变化率
- `calculate_market_leverage(df: pd.DataFrame) -> pd.Series`: 市场杠杆率 (Margin Debt / S&P500总市值)
- `calculate_money_supply_ratio(df: pd.DataFrame) -> pd.Series`: 货币供应比率 (Margin Debt / M2)
- `calculate_investor_net_worth(df: pd.DataFrame) -> pd.Series`: 投资者净资产
- `calculate_mkt_return(df: pd.DataFrame) -> Tuple[pd.Series, pd.Series]`: 月度和年度市场回报率

**vulnerability_index.py** (⭐核心模块，参考 `docs/sig_Bubbles.md`)
- `calculate_zscore(series: pd.Series, window: int = 252) -> pd.Series`: Z-Score标准化
- `calculate_leverage_zscore(df: pd.DataFrame) -> pd.Series`: 杠杆Z分数
- `calculate_vix_zscore(vix_series: pd.Series, window: int = 252) -> pd.Series`: VIX Z分数
- `calculate_vulnerability_index(leverage_zscore: pd.Series, vix_zscore: pd.Series) -> pd.Series`: 核心公式
- `classify_risk_level(vulnerability_index: pd.Series) -> pd.Series`: 风险等级 (>3高风险, <-3低风险)
- `validate_vulnerability_calculation(df: pd.DataFrame) -> bool`: 算法验证

**risk_analyzer.py**
- `detect_bubble_signals(vulnerability_index: pd.Series) -> pd.Series`: 泡沫信号检测 (Vulnerability > 3)
- `classify_market_regime(df: pd.DataFrame) -> pd.Series`: 市场状态分类
- `generate_investment_insights(df: pd.DataFrame, confidence_threshold: float = 0.8) -> dict`
- `analyze_historical_crises(df: pd.DataFrame) -> dict`: 分析3个历史危机时期

**visualization.py** (参考 `docs/tableElements.md` - 7个核心图表)
- `create_market_leverage_chart(df: pd.DataFrame) -> plotly.graph_objects.Figure`: 双Y轴图表 (市场杠杆率 & S&P500)
- `create_money_supply_chart(df: pd.DataFrame) -> plotly.graph_objects.Figure`: Margin Debt / M2 比率
- `create_interest_cost_chart(df: pd.DataFrame) -> plotly.graph_objects.Figure`: 利率成本分析
- `create_leverage_change_chart(df: pd.DataFrame) -> plotly.graph_objects.Figure`: 杠杆变化率对比
- `create_investor_net_worth_chart(df: pd.DataFrame) -> plotly.graph_objects.Figure`: 投资者净资产
- `create_vulnerability_index_chart(df: pd.DataFrame) -> plotly.graph_objects.Figure`: 脆弱性指数图表
- `create_vix_leverage_chart(df: pd.DataFrame) -> plotly.graph_objects.Figure`: VIX与杠杆对比图表 (第一Y轴VIX_t，第二Y轴Leverage_Normalized_t)
- `highlight_historical_crises(fig: plotly.graph_objects.Figure) -> plotly.graph_objects.Figure`: 标记3个历史危机时期

### 快速开始指南 (quickstart.md)

**环境设置**
```bash
# 克隆仓库
git clone <repo-url>
cd levAnalyzeMM

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

**数据准备**
```bash
# 验证数据文件 (已提供)
ls -la datas/margin-statistics.csv
head -5 datas/margin-statistics.csv

# 验证数据源文档
cat docs/dataSourceExplain.md
cat docs/calMethod.md
cat docs/tableElements.md

# 验证脆弱性指数算法
cat docs/sig_Bubbles.md
```

**运行应用**
```bash
# 启动Streamlit应用
streamlit run app.py

# 访问 http://localhost:8501
```

**使用指南**
- 选择时间范围查看核心指标
- 对比历史危机时期
- 分析脆弱性指数趋势
- 查看风险信号和投资洞察

## 关键决策记录

### 技术栈选择
- **Streamlit**: 选择原因 - 快速开发金融数据可视化，优秀的Plotly集成
- **Pandas**: 选择原因 - 强大的时间序列数据处理能力
- **Plotly**: 选择原因 - 金融图表的行业标准，交互性强

### 数据模型决策
- **CSV文件存储**: 选择原因 - 简单、跨平台、便于版本控制
- **月度频率**: 匹配融资余额数据发布周期
- **覆盖范围**: Part1 (1997-01) + Part2 (2010-02) 满足历史回测需求

### 核心算法决策
- **Z-score窗口**: 252个交易日 (1年) 平衡稳定性与响应性
- **脆弱性指数公式**: `Vulnerability = Leverage_Z - VIX_Z` (参考 `docs/sig_Bubbles.md`)
- **风险等级**:
  - Vulnerability > 3: 高风险 (泡沫/自满)
  - Vulnerability < -3: 低风险 (恐慌/去杠杆)
  - -1 ~ +1: 中性 (正常市场)
- **杠杆净值计算**: `Leverage_Net = D - (CC + CM)` (参考 `docs/calMethod.md`)
- **杠杆标准化**: `Leverage_Normalized = Leverage_Net / Stock_Market_Cap`

---

**计划完成时间**: 2025-11-08
**状态**: ✅ Phase 0 & Phase 1 已完成
**已生成文件**:
- ✅ plan.md - 实施计划
- ✅ research.md - Phase 0 研究成果
- ✅ data-model.md - Phase 1 数据模型
- ✅ contracts/ - 5个API合同模块
- ✅ quickstart.md - Phase 1 快速开始指南

**下一步**: 运行 `/speckit.tasks` 进行任务分解
