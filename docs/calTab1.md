# Core Leverage Indicators Dashboard - Calculation Methods

**Version**: 1.0.0
**Date**: 2025-11-18
**Scope**: Tab 1 - Core Dashboard Calculation Methods

---

## Overview

This document details the calculation methods for all metrics displayed in the Core Leverage Indicators Dashboard (Tab 1). All calculations are performed by the `MarginDebtCalculator` and `VulnerabilityIndex` classes in `src/models/`.

---

## 1. Vulnerability Index

### Definition
The **Vulnerability Index** is the primary risk indicator that measures market vulnerability based on the relationship between market leverage and volatility.

### Formula
```
Vulnerability Index = Leverage Z-Score - VIX Z-Score
```

### Calculation Steps

#### Step 1: Calculate Leverage Z-Score
```python
leverage_zscore = (current_leverage - rolling_mean_leverage) / rolling_std_leverage
```
- **Rolling Window**: 252 trading days (approximately 12 months)
- **Min Periods**: 63 (6 months minimum for calculation)

#### Step 2: Calculate VIX Z-Score
```python
vix_zscore = (current_vix - rolling_mean_vix) / rolling_std_vix
```
- Uses the same rolling window as leverage Z-score
- If VIX data unavailable, uses constant value of 0

#### Step 3: Calculate Final Index
```python
vulnerability_index = leverage_zscore - vix_zscore
```

### Risk Thresholds
| Level | Threshold | Color Code |
|-------|-----------|------------|
| **Extreme High Risk** | > 3.0 | 🔴 Red |
| **High Risk** | > 1.5 | 🟠 Orange |
| **Medium Risk** | 0.5 to 1.5 | 🟡 Yellow |
| **Normal/Low Risk** | -3.0 to 0.5 | 🟢 Green |
| **Extremely Low Risk** | < -3.0 | 🔵 Blue |

### Implementation
**Source**: `src/models/indicators.py:53-80`

```python
def calculate_vulnerability_index(self, data: pd.DataFrame, leverage_ratio: pd.Series) -> pd.Series:
    leverage_zscore = self.calculate_zscore(leverage_ratio)

    if 'vix_index' in data.columns:
        vix_zscore = self.calculate_zscore(data['vix_index'])
    else:
        vix_zscore = pd.Series(0, index=leverage_ratio.index)

    vulnerability_index = leverage_zscore - vix_zscore
    return vulnerability_index
```

---

## 2. Market Leverage Ratio

### Definition
The **Market Leverage Ratio** measures the ratio of margin debt to total S&P 500 market capitalization, indicating overall leverage in the market.

### Formula
```
Market Leverage Ratio = Margin Debt / S&P 500 Market Capitalization
```

### Input Data
- **Margin Debt (D)**: FINRA debit balances in thousands of dollars
- **S&P 500 Market Capitalization**: Total market value of S&P 500 companies

### Calculation Steps

#### Step 1: Data Validation
```python
if len(margin_debt) != len(market_cap):
    raise DataLengthMismatch("Data length mismatch")

if (margin_debt <= 0).any() or (market_cap <= 0).any():
    raise ValueError("Invalid values detected")
```

#### Step 2: Handle Missing Values
```python
if handle_missing == "interpolate":
    margin_debt = margin_debt.interpolate()
    market_cap = market_cap.interpolate()
elif handle_missing == "ffill":
    margin_debt = margin_debt.fillna(method='ffill')
    market_cap = market_cap.fillna(method='ffill')
```

#### Step 3: Calculate Ratio
```python
market_leverage_ratio = margin_debt / market_cap
```

#### Step 4: Apply Constraints and Precision
```python
# Limit to reasonable range
market_leverage_ratio = market_leverage_ratio.clip(lower=0.001, upper=0.50)

# Round to 4 decimal places
market_leverage_ratio = market_leverage_ratio.round(4)
```

### Expected Range
- **Typical Range**: 0.01 to 0.30 (1% to 30%)
- **Maximum**: 0.50 (50%)
- **Minimum**: 0.001 (0.1%)

### Implementation
**Source**: `src/models/margin_debt_calculator.py:77-140`

```python
def calculate_market_leverage_ratio(self, margin_debt: pd.Series, sp500_market_cap: pd.Series) -> pd.Series:
    # Validate data length
    if len(margin_debt) != len(sp500_market_cap):
        raise DataLengthMismatch(...)

    # Check for negative or zero values
    if (margin_debt <= 0).any() or (sp500_market_cap <= 0).any():
        self.logger.warning("Invalid values detected")

    # Handle missing values
    margin_debt_clean = margin_debt.copy()
    sp500_market_cap_clean = sp500_market_cap.copy()

    # Calculate ratio
    market_leverage_ratio = margin_debt_clean / sp500_market_cap_clean

    # Apply constraints
    market_leverage_ratio = market_leverage_ratio.clip(lower=0.001, upper=0.50)
    market_leverage_ratio = market_leverage_ratio.round(4)

    return market_leverage_ratio
```

---

## 3. Money Supply Ratio

### Definition
The **Money Supply Ratio** measures the ratio of margin debt to M2 money supply, indicating how much of the money supply is used for leverage.

### Formula
```
Money Supply Ratio = Margin Debt / M2 Money Supply
```

### Input Data
- **Margin Debt (D)**: FINRA debit balances in thousands of dollars
- **M2 Money Supply**: M2 money stock from FRED (in billions)

### Calculation Steps

#### Step 1: Data Validation
```python
if len(margin_debt) != len(m2_money_supply):
    raise DataLengthMismatch("Data length mismatch")
```

#### Step 2: Handle Missing Values
```python
if handle_missing == "interpolate":
    margin_debt = margin_debt.interpolate()
    m2_money_supply = m2_money_supply.interpolate()
elif handle_missing == "ffill":
    margin_debt = margin_debt.fillna(method='ffill')
    m2_money_supply = m2_money_supply.fillna(method='ffill')
```

#### Step 3: Calculate Ratio
```python
money_supply_ratio = margin_debt / m2_money_supply
```

#### Step 4: Apply Constraints and Precision
```python
# Limit to reasonable range
money_supply_ratio = money_supply_ratio.clip(lower=0.001, upper=0.20)

# Round to 4 decimal places
money_supply_ratio = money_supply_ratio.round(4)
```

### Expected Range
- **Typical Range**: 0.01 to 0.10 (1% to 10%)
- **Maximum**: 0.20 (20%)
- **Minimum**: 0.001 (0.1%)

### Implementation
**Source**: `src/models/margin_debt_calculator.py:142-194`

```python
def calculate_money_supply_ratio(self, margin_debt: pd.Series, m2_money_supply: pd.Series) -> pd.Series:
    # Validate data length
    if len(margin_debt) != len(m2_money_supply):
        raise DataLengthMismatch(...)

    # Handle missing values
    margin_debt_clean = margin_debt.copy()
    m2_money_supply_clean = m2_money_supply.copy()

    # Calculate ratio
    money_supply_ratio = margin_debt_clean / m2_money_supply_clean

    # Apply constraints
    money_supply_ratio = money_supply_ratio.clip(lower=0.001, upper=0.20)
    money_supply_ratio = money_supply_ratio.round(4)

    return money_supply_ratio
```

---

## 4. Current Metrics Display

### Market Leverage (Top Row)
- **Display**: Current value as percentage (e.g., "2.3%")
- **Delta**: Month-over-month change
- **Calculation**: Uses last value from `market_leverage_ratio` series

### Money Supply Ratio (Top Row)
- **Display**: Current value as percentage (e.g., "4.2%")
- **Delta**: Month-over-month change
- **Calculation**: Uses last value from `money_supply_ratio` series

### Vulnerability Index (Top Row)
- **Display**: Current index value (e.g., "1.8")
- **Delta**: Change from previous period
- **Calculation**: Uses last value from `vulnerability_index` series

### Risk Level (Top Row)
- **Display**: Text classification (Low, Medium, High, Extreme)
- **Calculation**: Based on current vulnerability index value and thresholds

```python
if vulnerability >= 3.0:
    risk_level = "Extreme High"
elif vulnerability >= 1.5:
    risk_level = "High"
elif vulnerability >= 0.5:
    risk_level = "Medium"
elif vulnerability >= -3.0:
    risk_level = "Low"
else:
    risk_level = "Extremely Low"
```

---

## 5. Data Quality and Validation

### Missing Value Handling
The calculator supports three strategies:
1. **skip**: Leave missing values as NaN
2. **interpolate**: Linear interpolation for short gaps
3. **ffill**: Forward fill from previous valid value

### Value Validation
- **Market Leverage**: Must be between 0.001 and 0.50
- **Money Supply Ratio**: Must be between 0.001 and 0.20
- **Negative values**: Trigger warnings but don't halt calculation
- **Zero values**: Clipped to minimum threshold

### Coverage Calculation
```python
coverage = (valid_records / total_records) * 100
```
- **Valid Records**: Non-NaN values
- **Total Records**: All records in date range

---

## 6. Performance Optimization

### Lazy Loading
Modules are loaded on-demand using `@st.cache_resource`:
```python
@st.cache_resource
def load_modules():
    from models.margin_debt_calculator import MarginDebtCalculator
    from models.indicators import VulnerabilityIndex
    # ... other imports
    return {...}
```

### Data Caching
Calculated data is cached for 1 hour:
```python
@st.cache_data(ttl=3600)
def generate_sample_data(dates_list):
    # ... calculation logic
    return df
```

### Session State
Performance statistics tracked in session state:
- `render_time`: Page load time
- `error_count`: Error occurrence count
- `cache_hits`: Cache utilization
- `data_points`: Number of records processed

---

## 7. Error Handling

### Retry Logic
Data fetching includes retry mechanism (3 attempts):
```python
@handle_api_error
def safe_fetch_data(start_date, end_date):
    max_retries = 3
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(1)
            else:
                st.error(f"Failed after {max_retries} attempts")
```

### Graceful Degradation
- If real data unavailable, falls back to simulated data
- API failures don't crash application
- Users notified of data quality issues

---

## 8. Data Sources

### FINRA (Margin Debt)
- **Source**: `datas/margin-statistics.csv`
- **Update**: Monthly
- **Components**: D (debit), CC (free credit cash), CM (free credit margin)

### FRED (Economic Data)
- **Source**: FRED API
- **Series**: M2SL (M2 Money Stock)
- **Frequency**: Monthly
- **API Key**: Required

### Yahoo Finance (Market Index)
- **Source**: Yahoo Finance API
- **Symbols**: ^VIX (volatility), ^GSPC (S&P 500)
- **Frequency**: Daily

---

## 9. Testing and Validation

### Unit Tests
Each calculation method includes validation:
```python
def test_calculate_market_leverage_ratio():
    calculator = MarginDebtCalculator()

    # Test with valid data
    result = calculator.calculate_market_leverage_ratio(
        margin_debt, market_cap
    )
    assert 0.001 <= result.mean() <= 0.50

    # Test with invalid data
    try:
        calculator.calculate_market_leverage_ratio(
            pd.Series([-1]), market_cap
        )
        assert False, "Should raise ValueError"
    except ValueError:
        pass  # Expected
```

### Integration Tests
Full workflow tested with real data:
- Data fetch from all sources
- Calculation of all indicators
- Visualization rendering
- Export functionality

---

## 10. Troubleshooting

### Common Issues

#### Low Coverage
- **Cause**: Missing data in date range
- **Solution**: Expand date range or check API keys

#### Extreme Values
- **Cause**: Data quality issues or market anomalies
- **Solution**: Check data sources, apply smoothing

#### Calculation Errors
- **Cause**: Invalid input data
- **Solution**: Validate data before calculation, check for NaN values

### Log Messages
All calculations log detailed information:
```python
self.logger.info(f"Market leverage ratio: mean={result.mean():.4f}, max={result.max():.4f}")
```

---

## 11. References

- **Source Code**: `src/models/margin_debt_calculator.py`
- **Vulnerability Index**: `src/models/indicators.py`
- **Configuration**: `src/config.py`
- **Data Fetcher**: `src/data/fetcher.py`

---

## 12. Appendix: Formula Summary

| Metric | Formula | Input Data | Precision |
|--------|---------|------------|-----------|
| **Vulnerability Index** | Leverage_ZScore - VIX_ZScore | Leverage ratio, VIX | 4 decimals |
| **Market Leverage Ratio** | Margin Debt / S&P 500 Market Cap | FINRA D, Market Cap | 4 decimals |
| **Money Supply Ratio** | Margin Debt / M2 Money Supply | FINRA D, M2 | 4 decimals |

---

**Last Updated**: 2025-11-18
**Version**: 1.0.0
**Document Owner**: levAnalyzeMM Development Team
