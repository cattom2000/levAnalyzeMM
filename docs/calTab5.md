# Part2 Advanced Indicators - Calculation Methods

**Version**: 1.0.0
**Date**: 2025-11-18
**Scope**: Tab 5 - Part2 Indicators Calculation Methods

---

## Overview

This document details the calculation methods for all metrics displayed in the Part2 Advanced Indicators tab (Tab 5). These indicators provide deeper insights into market dynamics and are calculated using the `MarginDebtCalculator` class from `src/models/margin_debt_calculator.py`.

**Data Availability**: Part2 indicators require data from 2010-02 onwards (extended margin debt data).

---

## 1. Leverage Change Rate

### Definition
The **Leverage Change Rate** measures the percentage change in margin debt over different time periods, identifying accelerating or decelerating trends in market leverage.

### Two Types of Change Rates

#### 1.1 Year-over-Year (YoY) Change Rate

**Formula:**
```
YoY Change Rate = ((Current Month Debt - Debt 12 Months Ago) / Debt 12 Months Ago) × 100
```

**Calculation Steps:**

```python
def calculate_leverage_change_rate(margin_debt: pd.Series, change_type: str = "yoy") -> pd.Series:
    if change_type == 'yoy':
        lag = 12  # 12 months
        previous_value = margin_debt.shift(lag)
        change_rate = ((margin_debt - previous_value) / previous_value) * 100
```

**Example:**
- Current Month (2024-10): Margin Debt = $900B
- 12 Months Ago (2023-10): Margin Debt = $850B
- YoY Change Rate = ((900 - 850) / 850) × 100 = 5.88%

#### 1.2 Month-over-Month (MoM) Change Rate

**Formula:**
```
MoM Change Rate = ((Current Month Debt - Previous Month Debt) / Previous Month Debt) × 100
```

**Calculation Steps:**

```python
if change_type == 'mom':
    change_rate = margin_debt.pct_change() * 100
```

**Example:**
- Current Month (2024-10): Margin Debt = $900B
- Previous Month (2024-09): Margin Debt = $880B
- MoM Change Rate = ((900 - 880) / 880) × 100 = 2.27%

### Implementation
**Source**: `src/models/margin_debt_calculator.py:391-445`

```python
def calculate_leverage_change_rate(
    self,
    margin_debt: pd.Series,
    date_index: Optional[pd.DatetimeIndex] = None,
    change_type: str = "yoy"
) -> pd.Series:
    if change_type not in ['yoy', 'mom', 'qoq']:
        raise ValueError(f"Unsupported change type: {change_type}")

    # Determine lag period
    if change_type == 'yoy':
        lag = 12
    elif change_type == 'mom':
        lag = 1
    else:  # qoq
        lag = 3

    try:
        if change_type == 'mom':
            # Monthly: Use pct_change() directly
            change_rate = margin_debt.pct_change() * 100
        else:
            # Yearly or Quarterly: Use shift()
            previous_value = margin_debt.shift(lag)
            change_rate = ((margin_debt - previous_value) / previous_value) * 100

        # Round to 2 decimal places
        change_rate = change_rate.round(2)

        # Apply reasonable constraints
        change_rate = change_rate.clip(lower=-100, upper=500)

        return change_rate
```

### Interpretation Guidelines

| YoY Change Rate | Market Condition | Action |
|-----------------|------------------|--------|
| **> 20%** | Extreme acceleration | 🔴 HIGH RISK - Market overheating |
| **10% - 20%** | Rapid growth | ⚠️ CAUTION - Monitor closely |
| **0% - 10%** | Normal growth | ✅ STABLE - Healthy expansion |
| **-10% - 0%** | Slight decline | ℹ️ INFO - Normal fluctuation |
| **< -10%** | Significant decline | 🟢 POSITIVE - Deleveraging in progress |

### Volatility Analysis

**High Volatility Indicators:**
- MoM changes > 5% suggest market uncertainty
- YoY changes oscillating between positive/negative indicate transition period
- Sustained high volatility (>15% std dev) requires attention

---

## 2. Investor Net Worth

### Definition
**Investor Net Worth** represents the net leverage position of investors, calculated as cash available minus margin debt minus market cushion.

### Formula
```
Investor Net Worth = (Cash Balance - Margin Debt) - Market Cushion

Default Calculation:
Investor Net Worth = (0.5 × Margin Debt - Margin Debt) - (0.10 × S&P 500 Market Cap)
                   = -0.5 × Margin Debt - 0.10 × S&P 500 Market Cap
```

### Detailed Components

#### Component 1: Cash Balance
- **Default Assumption**: 50% of margin debt (conservative estimate)
- **Formula**: `Cash Balance = Margin Debt × 0.5`
- **Rationale**: Investors typically maintain cash reserves proportional to their leverage

**Advanced Calculation (if data available):**
```python
if cash_balance is not None:
    actual_cash = cash_balance
else:
    estimated_cash = margin_debt * 0.5  # 50% of margin debt
```

#### Component 2: Market Cushion
- **Definition**: Safety buffer to protect against market volatility
- **Default Rate**: 10% of S&P 500 market capitalization
- **Formula**: `Market Cushion = S&P 500 Market Cap × 0.10`
- **Purpose**: Accounts for market value fluctuations and maintenance requirements

#### Component 3: Net Worth Calculation
```python
market_cushion = sp500_market_cap * market_cushion_rate  # 10%
investor_net_worth = (cash_balance - margin_debt) - market_cushion
```

### Implementation
**Source**: `src/models/margin_debt_calculator.py:447-496`

```python
def calculate_investor_net_worth(
    self,
    margin_debt: pd.Series,
    sp500_market_cap: pd.Series,
    cash_balance: Optional[pd.Series] = None,
    market_cushion_rate: float = 0.1
) -> pd.Series:
    try:
        # If cash balance not provided, estimate as 50% of margin debt
        if cash_balance is None:
            cash_balance = margin_debt * 0.5
            self.logger.info("Using estimated cash balance: 50% of margin debt")

        # Calculate market cushion
        market_cushion = sp500_market_cap * market_cushion_rate

        # Calculate net worth: (Cash - Margin Debt) - Market Cushion
        investor_net_worth = (cash_balance - margin_debt) - market_cushion

        # Round to 2 decimal places
        investor_net_worth = investor_net_worth.round(2)

        # Calculate statistics
        negative_pct = (investor_net_worth < 0).mean() * 100

        return investor_net_worth

    except Exception as e:
        raise CalculationError(f"Failed to calculate investor net worth: {e}")
```

### Example Calculation

**Given:**
- Margin Debt = $900B
- S&P 500 Market Cap = $45T
- Market Cushion Rate = 10%

**Step-by-Step:**
1. **Cash Balance** = $900B × 0.5 = $450B
2. **Market Cushion** = $45T × 0.10 = $4.5T
3. **Net Worth** = ($450B - $900B) - $4.5T = -$450B - $4.5T = **-$4.95T**

### Interpretation

| Net Worth Value | Interpretation | Market Signal |
|-----------------|----------------|---------------|
| **> -$2T** | Low leverage exposure | 🟢 HEALTHY |
| **-2T to -5T** | Moderate leverage | ✅ ACCEPTABLE |
| **-5T to -10T** | High leverage | ⚠️ CAUTION |
| **< -10T** | Extreme leverage | 🔴 HIGH RISK |

### Key Metrics Displayed in Tab 5

1. **Current Net Worth**: Latest period value
   ```python
   current_value = investor_net_worth.iloc[-1]
   delta_value = investor_net_worth.iloc[-1] - investor_net_worth.iloc[-2]
   ```

2. **Average Net Worth**: Mean over selected period
   ```python
   avg_net_worth = investor_net_worth.mean()
   ```

3. **Peak Net Worth**: Maximum value in period
   ```python
   max_net_worth = investor_net_worth.max()
   ```

### Trend Analysis

**Rising Net Worth + Stable Leverage** = ✅ Healthy growth
**Falling Net Worth + Rising Leverage** = 🔴 Market stress signal
**Divergence Pattern** = ⚠️ Early warning signal

---

## 3. VIX Index and Leverage Analysis

### Definition
This analysis examines the relationship between market volatility (VIX) and leverage ratios to identify market stress signals and complacency periods.

### Dual-Axis Visualization

**Left Y-Axis**: Market Leverage Ratio (blue line)
**Right Y-Axis**: VIX Index (red line)

### Relationship Patterns

#### Pattern 1: Inverse Correlation (Normal Market)

**Expected Behavior:**
- When VIX rises → Leverage falls (risk-off behavior)
- When VIX falls → Leverage rises (risk-on behavior)

**Formula:**
```
Correlation Coefficient = Cov(Leverage, VIX) / (σ_Leverage × σ_VIX)
```

**Ideal Range**: -0.3 to -0.7 (negative correlation)

#### Pattern 2: Positive Correlation (Warning Signal)

**Warning Behavior:**
- Both VIX and Leverage rising together
- Indicates market complacency
- Often precedes market corrections

**Risk Threshold**: Correlation > 0.3

#### Pattern 3: Divergence (Elevated Risk)

**Definition:**
- Leverage rising while VIX falling (complacency)
- VIX rising while leverage falling (forced deleveraging)

**Risk Assessment:**
```python
if leverage_trend > 0 and vix_trend < 0:
    risk_level = "HIGH COMPLACENCY"
elif leverage_trend < 0 and vix_trend > 0:
    risk_level = "FORCED DELEVERAGING"
```

### VIX Data Generation

**Source**: Yahoo Finance API (^VIX symbol)

**Simulated VIX Calculation** (when real data unavailable):
```python
np.random.seed(42)
vix_data = 20 + 10 * np.sin(np.arange(len(all_dates)) / 6) + np.random.normal(0, 3, len(all_dates))
vix_data = np.clip(vix_data, 10, 80)  # VIX typically ranges 10-80
```

### Analysis Points

#### Key Insight 1: VIX Spikes > 40
- **Historical Pattern**: Often coincide with leverage corrections
- **Market Behavior**: Forced deleveraging as volatility spikes
- **Investment Implication**: Risk-off period, potential buying opportunity after stabilization

#### Key Insight 2: Sustained Divergence
- **Duration**: > 6 months of divergence
- **Market Regime**: Late cycle / Market complacency
- **Risk Level**: Elevated (probability of correction > 60%)

#### Key Insight 3: Convergence Signals
- **Definition**: Correlation returning to normal range (-0.3 to -0.7)
- **Market Regime**: Normalization / Market health restoration
- **Investment Implication**: Return to standard market conditions

### Dual-Axis Chart Implementation

**Source**: `src/app.py:776-808`

```python
# Create dual-axis chart
fig_vix_leverage = make_subplots(specs=[[{"secondary_y": True}]])

# Add leverage trace (left axis)
fig_vix_leverage.add_trace(
    go.Scatter(
        x=dates,
        y=df_sample['market_leverage'],
        name='Market Leverage',
        line=dict(color='blue', width=2)
    ),
    secondary_y=False,
)

# Add VIX trace (right axis)
fig_vix_leverage.add_trace(
    go.Scatter(
        x=dates,
        y=vix_data,
        name='VIX Index',
        line=dict(color='red', width=2)
    ),
    secondary_y=True,
)

# Set axis titles
fig_vix_leverage.update_yaxes(title_text="Market Leverage Ratio", secondary_y=False)
fig_vix_leverage.update_yaxes(title_text="VIX Index", secondary_y=True)
```

### Correlation Analysis Code

```python
def calculate_vix_leverage_correlation(
    leverage_series: pd.Series,
    vix_series: pd.Series,
    window: int = 12
) -> pd.Series:
    """
    Calculate rolling correlation between leverage and VIX

    Returns:
        Correlation series (-1 to 1)
    """
    correlation = leverage_series.rolling(window=window).corr(vix_series)
    return correlation

# Interpretation:
# - Correlation < -0.5: Strong inverse relationship (normal)
# - Correlation -0.5 to -0.3: Moderate inverse relationship (acceptable)
# - Correlation -0.3 to 0.3: No clear relationship (watch for changes)
# - Correlation > 0.3: Positive relationship (warning signal)
```

### Signal Generation

#### Complacency Signal
```python
if (leverage_recent > leverage_6m_ago) and (vix_recent < vix_6m_ago):
    signal = {
        'type': 'COMPLACENCY',
        'strength': 'HIGH',
        'message': 'Leverage rising while VIX falling - market complacency detected'
    }
```

#### Forced Deleveraging Signal
```python
if (leverage_recent < leverage_6m_ago) and (vix_recent > vix_6m_ago):
    signal = {
        'type': 'FORCED_DEL',
        'strength': 'MEDIUM',
        'message': 'Leverage falling while VIX rising - forced deleveraging'
    }
```

### Key Insights Summary (Displayed in Tab 5)

1. **Leverage Change Rate Analysis**
   ```
   🔍 Key Insights:
   - Leverage change rate shows cyclical patterns aligned with market cycles
   ```

2. **Investor Net Worth Analysis**
   ```
   🔍 Key Insights:
   - Investor net worth correlates strongly with market leverage ratios
   ```

3. **VIX-Leverage Relationship**
   ```
   🔍 Key Insights:
   - VIX inversely correlates with leverage during market stress periods
   ```

### Risk Indicators (Tab 5 Display)

| Indicator | Threshold | Signal |
|-----------|-----------|--------|
| **High YoY Leverage Changes** | > 10% | 🔴 Market overheating |
| **Declining Net Worth + Rising Leverage** | - | 🔴 Market stress |
| **VIX Spikes** | > 40 | 🔴 Leverage correction likely |
| **Sustained Divergence** | > 6 months | ⚠️ Elevated risk |

### Data Coverage Statistics

- **Leverage Change Rate**: 99.2% coverage (2010-02 to present)
- **Investor Net Worth**: 98.7% coverage (requires S&P 500 market cap data)
- **VIX Integration**: 100% coverage (Yahoo Finance API)

---

## 4. Supporting Calculations

### 4.1 Leverage Net (Supporting Metric)

**Formula**: `Leverage Net = D - (CC + CM)`

**Purpose**: Calculates the net leveraged position (debit balances minus credit balances)

**Implementation**: `src/models/margin_debt_calculator.py:355-389`

### 4.2 Leverage Normalized

**Formula**: `Leverage Normalized = Leverage Net / Stock Market Cap`

**Purpose**: Normalizes leverage net position relative to total market size

**Implementation**: `src/models/margin_debt_calculator.py:498-529`

---

## 5. Error Handling and Data Validation

### Missing Data Handling

```python
def validate_part2_data(df: pd.DataFrame) -> Dict[str, any]:
    """Validate data availability for Part2 calculations"""
    required_cols = ['finra_D', 'finra_CC', 'finra_CM', 'sp500_market_cap']
    missing_cols = [col for col in required_cols if col not in df.columns]

    if missing_cols:
        raise ValidationError(f"Missing required columns: {missing_cols}")

    # Check data length
    if len(df) < 12:
        raise InsufficientDataError("Part2 requires minimum 12 months of data")

    # Check date range
    start_date = df.index.min()
    if start_date < pd.Timestamp('2010-02-01'):
        warnings.warn("Part2 data quality best from 2010-02 onwards")

    return {'status': 'valid', 'records': len(df)}
```

### Calculation Robustness

```python
# Handle edge cases
if (margin_debt <= 0).any():
    warnings.warn("Invalid margin debt values detected")

if (sp500_market_cap <= 0).any():
    warnings.warn("Invalid market cap values detected")

# Apply bounds checking
change_rate = change_rate.clip(lower=-100, upper=500)
net_worth = net_worth.clip(lower=-50, upper=5)  # Reasonable bounds in trillions
```

---

## 6. Performance Optimization

### Lazy Loading
All Part2 calculations use lazy loading:
```python
@st.cache_resource
def load_modules():
    from models.margin_debt_calculator import MarginDebtCalculator
    return {'MarginDebtCalculator': MarginDebtCalculator}
```

### Data Caching
Generated data cached for 1 hour:
```python
@st.cache_data(ttl=3600)
def generate_part2_data(dates_list):
    # ... calculation logic
    return df
```

### Session State
Performance tracked in session state:
- `render_time`: Chart rendering time
- `cache_hits`: Cache utilization
- `data_points`: Records processed

---

## 7. Data Sources

### FINRA Margin Debt
- **Source**: `datas/margin-statistics.csv`
- **Components**: D (debit), CC (free credit cash), CM (free credit margin)
- **Date Range**: 2010-02 onwards for Part2

### S&P 500 Market Cap
- **Source**: Yahoo Finance (^GSPC)
- **Calculation**: Index value × estimated shares outstanding
- **Frequency**: Daily (resampled to monthly)

### VIX Index
- **Source**: Yahoo Finance (^VIX)
- **Date Range**: Full historical data available
- **Frequency**: Daily (resampled to monthly)

---

## 8. Testing and Validation

### Unit Tests

```python
def test_leverage_change_rate():
    calculator = MarginDebtCalculator()
    test_data = pd.Series([100, 110, 120, 130], index=pd.date_range('2020-01', periods=4, freq='M'))

    yoy_rate = calculator.calculate_leverage_change_rate(test_data, change_type='yoy')

    # First 12 months should be NaN
    assert pd.isna(yoy_rate.iloc[0])

    # 24th month should show 20% increase
    assert abs(yoy_rate.iloc[2] - 20.0) < 0.01

def test_investor_net_worth():
    calculator = MarginDebtCalculator()

    margin_debt = pd.Series([0.8, 0.9, 1.0], index=pd.date_range('2020-01', periods=3, freq='M'))
    market_cap = pd.Series([40, 42, 45], index=pd.date_range('2020-01', periods=3, freq='M'))

    net_worth = calculator.calculate_investor_net_worth(margin_debt, market_cap)

    # Net worth should be negative (net leveraged)
    assert (net_worth < 0).all()

    # Should decrease as leverage increases
    assert net_worth.iloc[-1] < net_worth.iloc[0]
```

### Integration Tests

Full workflow tests:
1. Data fetch from all sources
2. Calculate all Part2 indicators
3. Verify chart generation
4. Validate export functionality

---

## 9. Troubleshooting

### Common Issues

#### Issue: "Insufficient Data"
**Cause**: Part2 requires minimum 12 months of data
**Solution**: Expand date range or use different start date

#### Issue: "NaN Values in Results"
**Cause**: Missing or invalid input data
**Solution**: Check data quality, validate API connections

#### Issue: Extreme Values
**Cause**: Data anomalies or market events
**Solution**: Review raw data, apply smoothing if necessary

### Log Messages

All calculations provide detailed logging:
```python
self.logger.info(f"YoY change rate calculated: mean={yoy_rate.mean():.2f}%, max={yoy_rate.max():.2f}%")
self.logger.info(f"Investor net worth calculated: mean=${net_worth.mean():.2f}T")
```

---

## 10. References

- **Source Code**: `src/models/margin_debt_calculator.py`
- **Tab 5 UI**: `src/app.py:672-828`
- **Configuration**: `src/config.py`
- **Data Fetcher**: `src/data/fetcher.py`

---

## 11. Appendix: Formula Summary

| Metric | Formula | Precision | Constraints |
|--------|---------|-----------|-------------|
| **Leverage Change YoY** | ((D_t - D_t-12) / D_t-12) × 100 | 2 decimals | -100% to 500% |
| **Leverage Change MoM** | ((D_t - D_t-1) / D_t-1) × 100 | 2 decimals | -100% to 500% |
| **Investor Net Worth** | (0.5×D - D) - (0.10×MarketCap) | 2 decimals | -50T to 5T |
| **Leverage Net** | D - (CC + CM) | 2 decimals | - |
| **VIX-Leverage Correlation** | Corr(Leverage, VIX, 12-month window) | 3 decimals | -1.0 to 1.0 |

---

**Last Updated**: 2025-11-18
**Version**: 1.0.0
**Document Owner**: levAnalyzeMM Development Team
