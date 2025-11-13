# Part1 Coverage Issue - Root Cause Analysis

**Date**: 2025-11-13
**Version**: 1.0.0
**Status**: 🔍 Root Cause Identified

---

## Executive Summary

The Part1 Coverage showing 0% is caused by a **data schema mismatch** between the DataFetcher and the Calculator. The Calculator expects specific column names that don't match what the DataFetcher provides.

---

## Investigation Results

### ✅ What Works
1. **FRED API**: Successfully configured and working
2. **M2 Data**: Fetched successfully with 100% coverage (345 records, 1997-01 to 2025-09)
3. **FINRA Data**: Loaded successfully (345 records, all non-null)
4. **Data Alignment**: Index alignment working correctly

### ❌ The Problem

#### Column Name Mismatch

**What DataFetcher Provides:**
```python
{
    'finra_D': 345/345 non-null (100.00%),           # Debit Balances (margin debt)
    'finra_CC': 345/345 non-null (100.00%),          # Cash Credit
    'finra_CM': 188/345 non-null (54.49%),           # Margin Credit
    'vix_index': 344/345 non-null (99.71%),          # VIX data
    'sp500_index': 344/345 non-null (99.71%),        # S&P 500 index
    'm2_money_supply': 345/345 non-null (100.00%),   # M2 money supply
    'market_cap': 344/345 non-null (99.71%)          # Market cap (calculated)
}
```

**What Calculator Expects:**
```python
{
    'margin_debt':          # ❌ NOT PRESENT (should be 'finra_D')
    'sp500_market_cap':     # ❌ NOT PRESENT (should be 'market_cap')
    'federal_funds_rate':   # ❌ NOT PRESENT (not fetched at all)
    'm2_money_supply':      # ✅ PRESENT
}
```

---

## Detailed Root Cause Analysis

### Issue 1: Column Name Mismatch for Margin Debt

**Location**: `src/models/margin_debt_calculator.py:313-324`

```python
# Calculator checks for:
if 'margin_debt' in df.columns and 'sp500_market_cap' in df.columns:
    result_df['market_leverage_ratio'] = ...

if 'margin_debt' in df.columns and 'm2_money_supply' in df.columns:
    result_df['money_supply_ratio'] = ...
```

**DataFetcher provides**: `'finra_D'`
**Calculator expects**: `'margin_debt'`

### Issue 2: Column Name Mismatch for Market Cap

**Location**: `src/models/margin_debt_calculator.py:303`

```python
# Calculator expects:
'margin_debt', 'sp500_market_cap', 'm2_money_supply', 'federal_funds_rate'
```

**DataFetcher provides**: `'market_cap'`
**Calculator expects**: `'sp500_market_cap'`

### Issue 3: Missing Federal Funds Rate

**Location**: `src/models/margin_debt_calculator.py:327-334`

```python
if 'margin_debt' in df.columns and 'federal_funds_rate' in df.columns:
    interest_analysis = self.calculate_interest_cost_analysis(...)
```

**DataFetcher provides**: ❌ Nothing (DFF series not fetched)
**Calculator expects**: `'federal_funds_rate'`

---

## Impact Analysis

### Affected Part1 Indicators

| Indicator | Required Columns | Status | Impact |
|-----------|------------------|--------|---------|
| **Market Leverage Ratio** | `margin_debt` + `sp500_market_cap` | ❌ Failed | 0% coverage |
| **Money Supply Ratio** | `margin_debt` + `m2_money_supply` | ❌ Failed | 0% coverage |
| **Interest Cost Analysis** | `margin_debt` + `federal_funds_rate` | ❌ Skipped | Missing data |

### Coverage Calculation

```python
# In margin_debt_calculator.py:336-339
part1_coverage = self._calculate_coverage(
    result_df,
    ['market_leverage_ratio', 'money_supply_ratio', 'interest_correlation']
)
```

Since none of the columns are created, coverage = 0 / (345 × 2) = **0%**

---

## Why Part2 Works

Part2 indicators work because they use the correct column names:

```python
# Part2 uses 'finra_D' directly in calculation
result_df['leverage_net'] = self.calculate_leverage_net(
    df['finra_D'], df['finra_CC'], df['finra_CM']
)
```

This is why Part2 shows normal coverage while Part1 shows 0%.

---

## Data Flow Analysis

```
FINRA CSV → load_finra_data() → 'finra_D', 'finra_CC', 'finra_CM'
                  ↓
FRED API → fetch_m2_money_supply() → 'm2_money_supply'
                  ↓
Yahoo → fetch_sp500_data() → 'sp500_index' → calculate 'market_cap'
                  ↓
[All data combined into DataFrame with above column names]
                  ↓
calculate_part1_indicators() → Looks for 'margin_debt', 'sp500_market_cap', 'federal_funds_rate'
                  ↓
[Columns not found, no calculations performed]
                  ↓
Coverage = 0%
```

---

## FRED Series Availability Check

The FRED API provides multiple series (configured in `src/config.py:30-35`):

```python
FRED_CONFIG['series_ids'] = {
    'M2SL': 'M2 Money Stock',           # ✅ Fetched and working
    'DFF': 'Federal Funds Rate',        # ❌ Not fetched (needed for Part1)
    'DGS10': '10-Year Treasury',        # ❌ Not fetched
    'WILL5000INDFC': 'Wilshire 5000'    # ❌ Not fetched
}
```

**M2SL (M2 Money Stock)**:
- ✅ Successfully fetched
- ✅ Covers 1959-2025 (includes entire Part1 range: 1997-2025)
- ✅ 100% data availability

**DFF (Federal Funds Rate)**:
- ❌ Not fetched
- ❌ Required for Interest Cost Analysis

---

## M2 Data Verification

```bash
FRED API Key Status: Set
M2 Data Fetch: SUCCESS
M2 Date Range: 1959-01-01 to 2025-09-01
M2 Data Points: 801
```

**M2 data IS available and IS being fetched correctly.**

The issue is purely the column name mismatch, not data availability.

---

## Date Range Verification

| Component | Start Date | End Date | Coverage |
|-----------|------------|----------|----------|
| **FINRA Data** | 1997-01 | 2025-09 | ✅ Full coverage |
| **M2 Data** | 1959-01 | 2025-09 | ✅ Full coverage (includes FINRA range) |
| **VIX Data** | 1997-01 | 2025-09 | ✅ Full coverage |
| **S&P500 Data** | 1997-01 | 2025-09 | ✅ Full coverage |

**Conclusion**: All data sources have sufficient date range coverage for Part1 calculations.

---

## Fix Options

### Option 1: Rename Columns in DataFetcher (Recommended)

Modify `src/data/fetcher.py` to rename columns to what Calculator expects:

```python
# Line 371: Add column renaming
combined_data['margin_debt'] = combined_data['finra_D']
combined_data['sp500_market_cap'] = combined_data['market_cap']
```

**Pros:**
- Minimal code change
- No API changes needed
- Fixes the immediate issue

**Cons:**
- Doesn't fetch DFF (Federal Funds Rate)
- Still missing interest cost analysis

### Option 2: Update Calculator to Use DataFetcher Column Names

Modify `src/models/margin_debt_calculator.py` to use `'finra_D'` instead of `'margin_debt'`:

```python
# Line 313: Change condition
if 'finra_D' in df.columns and 'market_cap' in df.columns:
    result_df['market_leverage_ratio'] = self.calculate_market_leverage_ratio(
        df['finra_D'], df['market_cap']
    )
```

**Pros:**
- Aligns Calculator with actual data schema
- Consistent with Part2 approach

**Cons:**
- Multiple changes required
- Need to update documentation

### Option 3: Fetch Federal Funds Rate (DFF)

Add DFF series fetching to `src/data/fetcher.py`:

```python
def fetch_federal_funds_rate(self, start_date: str, end_date: str) -> pd.Series:
    dff_data = self.fred_client.get_series('DFF', start=start_date, end=end_date)
    combined_data['federal_funds_rate'] = dff_aligned
```

**Pros:**
- Enables Interest Cost Analysis
- Improves data completeness

**Cons:**
- Additional API calls
- More code changes

---

## Recommended Solution

**Phase 1 (Immediate)**: Fix column name mismatch
- Update Calculator to use DataFetcher column names
- This will restore Part1 coverage to ~67% (2 out of 3 indicators)

**Phase 2 (Follow-up)**: Add Federal Funds Rate
- Implement DFF series fetching
- This will complete all Part1 indicators
- Coverage will reach 100%

---

## Code References

### Files Involved

1. **`src/config.py`**
   - Lines 26-36: FRED series configuration
   - Series defined but not all fetched

2. **`src/data/fetcher.py`**
   - Line 194: `fetch_m2_money_supply()` - ✅ Working
   - Line 341: M2 data fetching - ✅ Working
   - Line 371: Column assignment - Uses `'m2_money_supply'` ✅
   - Missing: DFF (Federal Funds Rate) fetching

3. **`src/models/margin_debt_calculator.py`**
   - Line 313: Checks for `'margin_debt'` ❌
   - Line 320: Checks for `'margin_debt'` ❌
   - Line 327: Checks for `'federal_funds_rate'` ❌
   - Should check for `'finra_D'`, `'market_cap'`, and fetch DFF

---

## Verification Commands

To verify the fix:

```bash
# Test M2 data fetching
python3 -c "from src.data.fetcher import DataFetcher; fetcher = DataFetcher(); m2 = fetcher.fetch_m2_money_supply('1997-01-01', '2025-09-30'); print(f'M2 data: {len(m2)} records')"

# Test complete dataset
python3 -c "from src.data.fetcher import DataFetcher; fetcher = DataFetcher(); data = fetcher.fetch_complete_market_dataset('1997-01-01', '2025-09-30'); print(f'Columns: {list(data.columns)}')"

# Test Part1 calculation
python3 -c "from src.data.fetcher import DataFetcher; from src.models.margin_debt_calculator import MarginDebtCalculator; fetcher = DataFetcher(); data = fetcher.fetch_complete_market_dataset('1997-01-01', '2025-09-30'); calc = MarginDebtCalculator(); result = calc.calculate_part1_indicators(data); stats = calc.get_calculation_statistics(result); print(f'Part1 Coverage: {stats[\"part1_coverage\"]:.2%}')"
```

---

## Conclusion

**The Part1 Coverage issue is NOT caused by:**
- ❌ Missing M2 data
- ❌ FRED API configuration issues
- ❌ Date range problems
- ❌ Data alignment issues

**The Part1 Coverage issue IS caused by:**
- ✅ **Data schema mismatch** between DataFetcher and Calculator
- ✅ **Column name differences**: `'finra_D'` vs `'margin_debt'`
- ✅ **Missing Federal Funds Rate** (DFF series not fetched)

**Impact**: Low (as stated in acceptance report) because:
- Part2 indicators work correctly
- Core vulnerability index calculation doesn't depend on Part1
- System remains functional with Part2 data

**Fix Complexity**: Low-Medium
**Estimated Fix Time**: 2-4 hours
**Testing Required**: Data fetching and calculation validation
