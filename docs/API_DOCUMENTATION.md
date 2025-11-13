# API Documentation - levAnalyzeMM

**Version**: 1.0.0
**Last Updated**: 2025-11-13
**Project**: Margin Debt Market Analysis System

---

## Overview

This document provides comprehensive API documentation for the levAnalyzeMM system, including data fetching, processing, and analysis capabilities.

---

## Table of Contents

1. [DataFetcher API](#datafetcher-api)
2. [MarginDebtCalculator API](#margindeebtcalculator-api)
3. [VulnerabilityIndex API](#vulnerabilityindex-api)
4. [Usage Examples](#usage-examples)
5. [Error Handling](#error-handling)
6. [Performance Notes](#performance-notes)

---

## DataFetcher API

### Class: `DataFetcher`

Multi-source market data fetcher supporting FINRA, FRED, and Yahoo Finance.

#### Constructor

```python
from data.fetcher import DataFetcher

fetcher = DataFetcher(cache_enabled=True)
```

**Parameters**:
- `cache_enabled` (bool): Enable caching mechanism (default: True)

#### Methods

##### `load_finra_data() -> pd.DataFrame`

Load FINRA margin debt data from CSV file.

**Returns**: DataFrame with columns:
- `finra_D`: Debit Balances (in thousands)
- `finra_CC`: Cash Credit (in thousands)
- `finra_CM`: Margin Credit (in thousands)

**Example**:
```python
finra_data = fetcher.load_finra_data()
print(f"Loaded {len(finra_data)} months of FINRA data")
```

**Raises**:
- `FileNotFoundError`: If CSV file not found
- `DataSourceError`: If data format is invalid

---

##### `fetch_vix_data(start_date: str, end_date: str) -> pd.Series`

Fetch VIX (Volatility Index) data from Yahoo Finance.

**Parameters**:
- `start_date`: Start date in 'YYYY-MM-DD' format
- `end_date`: End date in 'YYYY-MM-DD' format

**Returns**: Series with VIX index values

**Example**:
```python
vix_data = fetcher.fetch_vix_data('2020-01-01', '2024-11-01')
print(f"VIX range: {vix_data.min():.2f} - {vix_data.max():.2f}")
```

---

##### `fetch_sp500_data(start_date: str, end_date: str) -> pd.Series`

Fetch S&P 500 index data from Yahoo Finance.

**Parameters**:
- `start_date`: Start date in 'YYYY-MM-DD' format
- `end_date`: End date in 'YYYY-MM-DD' format

**Returns**: Series with S&P 500 index values

**Example**:
```python
sp500_data = fetcher.fetch_sp500_data('2020-01-01', '2024-11-01')
print(f"S&P 500 latest: {sp500_data.iloc[-1]:.2f}")
```

---

##### `fetch_m2_money_supply(start_date: str, end_date: str) -> pd.Series`

Fetch M2 Money Supply data from FRED API.

**Parameters**:
- `start_date`: Start date in 'YYYY-MM-DD' format
- `end_date`: End date in 'YYYY-MM-DD' format

**Returns**: Series with M2 money supply values (in billions)

**Example**:
```python
m2_data = fetcher.fetch_m2_money_supply('2020-01-01', '2024-11-01')
print(f"M2 latest: ${m2_data.iloc[-1]:,.2f} billion")
```

**Note**: Requires FRED_API_KEY environment variable

---

##### `fetch_complete_market_dataset(start_date: str, end_date: str) -> pd.DataFrame`

Fetch and combine data from all sources.

**Parameters**:
- `start_date`: Start date in 'YYYY-MM-DD' format
- `end_date`: End date in 'YYYY-MM-DD' format

**Returns**: DataFrame with all market data columns:
- `finra_D`, `finra_CC`, `finra_CM`: FINRA margin debt data
- `vix_index`: VIX volatility index
- `sp500_index`: S&P 500 index values
- `m2_money_supply`: M2 money supply (billions)
- `market_cap`: Approximate market capitalization

**Example**:
```python
complete_data = fetcher.fetch_complete_market_dataset('2020-01-01', '2024-11-01')
print(f"Complete dataset: {len(complete_data)} months")
print(f"Columns: {list(complete_data.columns)}")
```

---

##### `sync_data_sources(data: pd.DataFrame) -> pd.DataFrame`

Synchronize and calculate derived metrics.

**Parameters**:
- `data`: DataFrame with market data

**Returns**: DataFrame with added columns:
- `leverage_ratio`: Market leverage ratio
- `vix_zscore`: VIX Z-score (252-day rolling)

**Example**:
```python
synced_data = fetcher.sync_data_sources(complete_data)
print(f"Leverage ratio latest: {synced_data['leverage_ratio'].iloc[-1]:.4f}")
```

---

##### `validate_market_data(data: pd.DataFrame) -> Dict`

Validate market data quality.

**Parameters**:
- `data`: DataFrame to validate

**Returns**: Dictionary with validation metrics:
- `total_rows`: Total number of records
- `missing_data_pct`: Percentage of missing data
- `outliers_count`: Number of outliers detected
- `quality_score`: Overall quality score (0-100)
- `validation_date`: Timestamp of validation

**Example**:
```python
validation = fetcher.validate_market_data(complete_data)
print(f"Quality score: {validation['quality_score']:.1f}/100")
```

---

##### `detect_data_anomalies(data: pd.DataFrame) -> pd.DataFrame`

Detect anomalies in market data using 3-sigma rule.

**Parameters**:
- `data`: DataFrame to analyze

**Returns**: DataFrame with anomaly flags for each column

**Example**:
```python
anomalies = fetcher.detect_data_anomalies(complete_data)
print(f"Total anomalies detected: {anomalies['anomaly_flag'].sum()}")
```

---

##### `clear_cache() -> int`

Clear cached data.

**Returns**: Number of items cleared from cache

---

## MarginDebtCalculator API

### Class: `MarginDebtCalculator`

Calculates all Part1 and Part2 market indicators.

#### Methods

##### `calculate_all_indicators(data: pd.DataFrame) -> Dict`

Calculate all margin debt indicators.

**Parameters**:
- `data`: DataFrame with market data

**Returns**: Dictionary containing all calculated indicators

**Example**:
```python
from models.margin_debt_calculator import MarginDebtCalculator

calculator = MarginDebtCalculator()
indicators = calculator.calculate_all_indicators(complete_data)
print(f"Calculated {len(indicators)} indicators")
```

---

##### `calculate_part1_indicators(data: pd.DataFrame) -> Dict`

Calculate Part1 indicators (1997-01 onwards).

**Returns**:
- `market_leverage_ratio`: D / (CC + CM)
- `money_supply_ratio`: D / M2
- `interest_cost_analysis`: Derived interest metrics

---

##### `calculate_part2_indicators(data: pd.DataFrame) -> Dict`

Calculate Part2 indicators (2010-02 onwards).

**Returns**:
- `leverage_change_mom`: Month-over-month change
- `leverage_change_yoy`: Year-over-year change
- `investor_net_worth`: D - (CC + CM)
- `leverage_normalized`: Normalized leverage metrics

---

##### `calculate_market_leverage_ratio(data: pd.DataFrame) -> pd.Series`

Calculate market leverage ratio = D / (CC + CM)

---

##### `calculate_money_supply_ratio(data: pd.DataFrame) -> pd.Series`

Calculate money supply ratio = D / M2

---

##### `calculate_leverage_net(data: pd.DataFrame) -> pd.Series`

Calculate net leverage = D - (CC + CM)

---

##### `calculate_leverage_change_rate(data: pd.DataFrame) -> Dict`

Calculate leverage change rates:
- Month-over-month (MoM)
- Year-over-year (YoY)

---

##### `calculate_investor_net_worth(data: pd.DataFrame) -> pd.Series`

Calculate investor net worth = D - (CC + CM)

---

##### `calculate_leverage_normalized(data: pd.DataFrame) -> pd.Series`

Calculate normalized leverage using Z-score

---

##### `calculate_interest_cost_analysis(data: pd.DataFrame) -> Dict`

Analyze interest cost implications

---

## VulnerabilityIndex API

### Class: `VulnerabilityIndex`

Calculates and analyzes the market vulnerability index.

#### Methods

##### `calculate_vulnerability_index(data: pd.DataFrame, leverage_ratio: pd.Series) -> pd.Series`

Calculate vulnerability index = Leverage_ZScore - VIX_ZScore

**Parameters**:
- `data`: DataFrame with market data
- `leverage_ratio`: Series with leverage ratio values

**Returns**: Series with vulnerability index values

**Example**:
```python
from models.indicators import VulnerabilityIndex

vuln_calc = VulnerabilityIndex()
vulnerability = vuln_calc.calculate_vulnerability_index(complete_data, indicators['market_leverage_ratio'])
print(f"Current vulnerability: {vulnerability.iloc[-1]:.3f}")
```

**Interpretation**:
- `> 3.0`: Extremely high risk
- `> 1.5`: High risk
- `> 0.5`: Medium risk
- `-3.0 to 0.5`: Normal/Low risk
- `< -3.0`: Extremely low risk

---

##### `calculate_zscore(series: pd.Series, window: int = 252) -> pd.Series`

Calculate rolling Z-score.

**Parameters**:
- `series`: Input time series
- `window`: Rolling window size (default: 252 trading days)

**Returns**: Z-score series

---

##### `classify_risk_level(vulnerability_index: pd.Series) -> pd.Series`

Classify risk levels based on vulnerability index.

**Parameters**:
- `vulnerability_index`: Series with vulnerability values

**Returns**: Series with risk level labels:
- `'极低风险'`: Extremely low risk
- `'低风险'`: Low risk
- `'正常'`: Normal
- `'中风险'`: Medium risk
- `'高风险'`: High risk
- `'极高风险'`: Extremely high risk

---

##### `detect_crisis_periods(vulnerability_index: pd.Series) -> pd.DataFrame`

Detect historical crisis periods.

**Parameters**:
- `vulnerability_index`: Series with vulnerability values

**Returns**: DataFrame with detected crisis periods

---

##### `get_risk_summary(vulnerability_index: pd.Series, risk_levels: pd.Series) -> Dict`

Get risk summary statistics.

**Parameters**:
- `vulnerability_index`: Series with vulnerability values
- `risk_levels`: Series with risk level classifications

**Returns**: Dictionary with summary statistics

---

## Usage Examples

### Example 1: Complete Market Analysis

```python
from data.fetcher import get_data_fetcher
from models.margin_debt_calculator import MarginDebtCalculator
from models.indicators import VulnerabilityIndex

# Initialize components
fetcher = get_data_fetcher()
calculator = MarginDebtCalculator()
vuln_calc = VulnerabilityIndex()

# Fetch data
data = fetcher.fetch_complete_market_dataset('2020-01-01', '2024-11-01')

# Calculate indicators
indicators = calculator.calculate_all_indicators(data)
vulnerability = vuln_calc.calculate_vulnerability_index(
    data,
    indicators['market_leverage_ratio']
)

# Get risk level
risk_levels = vuln_calc.classify_risk_level(vulnerability)

# Print results
print(f"Current vulnerability index: {vulnerability.iloc[-1]:.3f}")
print(f"Current risk level: {risk_levels.iloc[-1]}")
```

---

### Example 2: Data Validation

```python
# Fetch and validate data
data = fetcher.fetch_complete_market_dataset('2020-01-01', '2024-11-01')

# Validate quality
validation = fetcher.validate_market_data(data)
print(f"Quality score: {validation['quality_score']:.1f}/100")

# Detect anomalies
anomalies = fetcher.detect_data_anomalies(data)
if anomalies['anomaly_flag'].any():
    print("⚠️ Anomalies detected in data")
```

---

### Example 3: Historical Crisis Detection

```python
# Calculate vulnerability index
vulnerability = vuln_calc.calculate_vulnerability_index(data, indicators['market_leverage_ratio'])

# Detect crisis periods
crisis_periods = vuln_calc.detect_crisis_periods(vulnerability)
print(f"Detected {len(crisis_periods)} crisis periods")

# Show crisis details
for idx, crisis in crisis_periods.iterrows():
    print(f"Crisis: {crisis['start_date'].date()} - {crisis['end_date'].date()}")
    print(f"  Duration: {crisis['duration_days']} days")
    print(f"  Peak vulnerability: {crisis['peak_vulnerability']:.3f}")
```

---

### Example 4: Caching Configuration

```python
# Enable caching for better performance
fetcher = get_data_fetcher(cache_enabled=True)

# First call - fetches from API
data1 = fetcher.fetch_complete_market_dataset('2020-01-01', '2024-11-01')

# Second call - uses cached data (much faster)
data2 = fetcher.fetch_complete_market_dataset('2020-01-01', '2024-11-01')

# Clear cache when needed
cleared = fetcher.clear_cache()
print(f"Cleared {cleared} cached items")
```

---

## Error Handling

### DataSourceError

Raised when data source is unavailable or returns invalid data.

```python
from data.fetcher import DataSourceError

try:
    data = fetcher.fetch_m2_money_supply('2020-01-01', '2024-11-01')
except DataSourceError as e:
    print(f"Data source error: {e}")
    # Handle error (e.g., use cached data, skip FRED data)
```

### DataFormatError

Raised when data format is invalid or columns are missing.

```python
from data.fetcher import DataFormatError

try:
    finra_data = fetcher.load_finra_data()
except DataFormatError as e:
    print(f"Data format error: {e}")
    # Handle error (e.g., check CSV file format)
```

### Best Practices

1. **Always validate data after fetching**:
```python
data = fetcher.fetch_complete_market_dataset(start_date, end_date)
validation = fetcher.validate_market_data(data)

if validation['quality_score'] < 50:
    print("⚠️ Low quality data detected")
    # Consider re-fetching or using fallback data
```

2. **Handle missing FRED API Key**:
```python
import os

if not os.getenv('FRED_API_KEY'):
    print("Warning: FRED_API_KEY not set. M2 data will not be available.")
    # System will continue without FRED data
```

3. **Use try-except for API calls**:
```python
try:
    data = fetcher.fetch_complete_market_dataset(start_date, end_date)
    # Process data
except DataSourceError as e:
    print(f"Failed to fetch data: {e}")
    # Use fallback or cached data
```

---

## Performance Notes

### Caching

- **Cache duration**: 1 hour (3600 seconds)
- **Cache size**: 100 items maximum
- **Recommendation**: Enable caching for production use

### Data Update Frequency

| Data Source | Update Frequency | API Calls/Month |
|------------|------------------|-----------------|
| FINRA | Monthly | 0 (local file) |
| FRED (M2) | Monthly | 1-2 |
| Yahoo Finance | Daily | 20-22 |

### Optimization Tips

1. **Use date ranges wisely**: Fetch only needed date ranges
2. **Enable caching**: Always use `cache_enabled=True`
3. **Batch operations**: Use `fetch_complete_market_dataset()` instead of individual calls
4. **Validate once**: Don't validate the same dataset multiple times

### Memory Usage

- **Typical dataset**: 59 months × 7 columns = ~3.5KB
- **Large dataset**: 10 years × 7 columns = ~350KB
- **Recommendation**: Current memory usage is minimal

---

## Data Source Configuration

### Required Environment Variables

```bash
export FRED_API_KEY=your_fred_api_key_here
```

### Optional Configuration

Edit `src/config.py` to customize:

```python
# FRED configuration
FRED_CONFIG = {
    'series_ids': {
        'M2SL': 'M2 Money Stock',
        # Add more series as needed
    }
}

# Risk thresholds
RISK_THRESHOLDS = {
    'extreme_high': 3.0,
    'high': 1.5,
    'medium': 0.5,
    'low': -3.0,
    'watch': 1.0
}
```

---

## Support

For questions or issues:
- Check existing documentation in `docs/`
- Review test files in `src/tests/`
- Open an issue on GitHub: https://github.com/cattom2000/levAnalyzeMM

---

**Last Updated**: 2025-11-13
**API Version**: 1.0.0
