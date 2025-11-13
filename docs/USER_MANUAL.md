# User Manual - levAnalyzeMM

**Margin Debt Market Analysis System**

**Version**: 1.0.0
**Last Updated**: 2025-11-13

---

## Table of Contents

1. [Introduction](#introduction)
2. [Quick Start](#quick-start)
3. [Installation](#installation)
4. [System Overview](#system-overview)
5. [User Interface Guide](#user-interface-guide)
6. [Understanding the Metrics](#understanding-the-metrics)
7. [Interpreting Results](#interpreting-results)
8. [Data Sources](#data-sources)
9. [FAQ](#faq)
10. [Troubleshooting](#troubleshooting)

---

## Introduction

levAnalyzeMM is a comprehensive market risk analysis tool that combines margin debt data with market volatility indicators to calculate a **Vulnerability Index**. This index helps identify periods of high market risk and potential market stress.

### What is the Vulnerability Index?

The Vulnerability Index is calculated as:
```
Vulnerability Index = Leverage Z-Score - VIX Z-Score
```

**Higher values indicate higher market risk:**
- **> 3.0**: Extremely high risk ⚠️⚠️⚠️
- **> 1.5**: High risk ⚠️⚠️
- **> 0.5**: Medium risk ⚠️
- **-3.0 to 0.5**: Normal/Low risk ✅
- **< -3.0**: Extremely low risk (potential buying opportunity) 💰

### Key Features

✅ **7 Core Indicators** - Comprehensive market analysis
✅ **3 User Stories** - From basic dashboard to advanced insights
✅ **Historical Crisis Detection** - Identify past market stress periods
✅ **Real-time Data** - Up-to-date market information
✅ **Interactive Visualizations** - Explore data with dynamic charts
✅ **Risk Classification** - Automatic risk level assessment

---

## Quick Start

### 1. Start the Application

```bash
# Navigate to project directory
cd /path/to/levAnalyzeMM

# Activate virtual environment
source .venv/bin/activate

# Launch Streamlit app
streamlit run app.py
```

### 2. Open Browser

Navigate to: `http://localhost:8501`

### 3. View Dashboard

The main dashboard automatically loads with:
- Current vulnerability index
- Risk level assessment
- 7 core metric charts
- Latest market data

### 4. Explore Features

- **Tab 1**: Core Dashboard (US1) - View all 7 indicators
- **Tab 2**: Crisis Comparison (US2) - Compare with historical crises
- **Tab 3**: Investment Insights (US3) - Get actionable advice

---

## Installation

### Prerequisites

- Python 3.10 or higher
- pip package manager
- 2GB available disk space

### Step 1: Clone Repository

```bash
git clone https://github.com/cattom2000/levAnalyzeMM.git
cd levAnalyzeMM
```

### Step 2: Create Virtual Environment

```bash
# Using venv
python3 -m venv .venv
source .venv/bin/activate

# Using conda
conda create -n levAnalyzeMM python=3.10
conda activate levAnalyzeMM
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure FRED API Key (Optional)

```bash
# Get your free API key from:
# https://fred.stlouisfed.org/docs/api/api_key.html

# Set environment variable
export FRED_API_KEY=your_api_key_here

# Add to your shell profile (optional)
echo 'export FRED_API_KEY=your_api_key_here' >> ~/.bashrc
source ~/.bashrc
```

### Step 5: Verify Installation

```bash
python -c "from data.fetcher import get_data_fetcher; print('✅ Installation successful')"
```

### Step 6: Launch Application

```bash
streamlit run app.py
```

---

## System Overview

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Streamlit UI                         │
│  ┌─────────────┐ ┌──────────────┐ ┌──────────────┐      │
│  │   Tab 1     │ │    Tab 2     │ │    Tab 3     │      │
│  │ Core Dash   │ │ Crisis Comp  │ │ Inv Insights │      │
│  └─────────────┘ └──────────────┘ └──────────────┘      │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
        ▼                         ▼
┌──────────────┐          ┌──────────────────┐
│ Data Fetcher │          │ Calculation      │
│              │          │ Engine           │
│ - FINRA      │          │                  │
│ - FRED       │          │ - Part 1         │
│ - Yahoo      │          │ - Part 2         │
└──────────────┘          │ - Vulnerability  │
                         └──────────────────┘
```

### Data Flow

```
Data Sources → DataFetcher → Processor → Calculator → Visualization
     ↓             ↓           ↓           ↓            ↓
  FINRA,      Clean &      Calculate   Generate    Charts &
  FRED,       Validate     Metrics     Index       UI
  Yahoo       Data                    (Z-scores)
```

---

## User Interface Guide

### Main Dashboard (Tab 1)

#### Layout

```
┌─────────────────────────────────────────────────────────┐
│ levAnalyzeMM - Margin Debt Market Analysis              │
├─────────────────────────────────────────────────────────┤
│ Sidebar Configuration                                   │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ 📅 Date Range:  [2020-01] ──── [2024-11]          │ │
│ │ 🏦 Data Sources: ☑ FINRA  ☑ FRED  ☑ Yahoo       │ │
│ │ 📊 Refresh Data    [Button]                       │ │
│ └─────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────┤
│ Current Status Panel                                    │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ Vulnerability Index: 1.85                          │ │
│ │ Risk Level: 🔴 High Risk                           │ │
│ │ Last Updated: 2024-11-01                           │ │
│ └─────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────┤
│ Chart Area (7 Core Indicators)                          │
│ ┌─────────────────┐ ┌─────────────────┐               │
│ │  Chart 1        │ │  Chart 2        │               │
│ │ Market Leverage │ │ Money Supply    │               │
│ │     Ratio       │ │     Ratio       │               │
│ └─────────────────┘ └─────────────────┘               │
│ ┌─────────────────┐ ┌─────────────────┐               │
│ │  Chart 3        │ │  Chart 4        │               │
│ │ Interest Cost   │ │ Leverage Change │               │
│ │   Analysis      │ │     Rate        │               │
│ └─────────────────┘ └─────────────────┘               │
│ ┌─────────────────┐ ┌─────────────────┐               │
│ │  Chart 5        │ │  Chart 6        │               │
│ │ Investor Net    │ │ Vulnerability   │               │
│ │     Worth       │ │     Index       │               │
│ └─────────────────┘ └─────────────────┘               │
│ ┌─────────────────────────────────────────────────┐   │
│ │  Chart 7                                        │   │
│ │ VIX vs Leverage (Dual Y-Axis)                   │   │
│ └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

#### Sidebar Controls

**Date Range Slider**
- Adjust the time period for analysis
- Minimum range: 1 year
- Maximum range: Full dataset (1997-2025)
- Chart updates automatically

**Data Source Checkboxes**
- ☑ FINRA: Margin debt statistics
- ☑ FRED: M2 money supply (requires API key)
- ☑ Yahoo Finance: VIX, S&P 500

**Refresh Button**
- Fetch latest data from all sources
- Updates all charts
- Shows last update timestamp

#### Chart Features

**Interactivity**
- **Zoom**: Click and drag to zoom into specific periods
- **Pan**: Hold Shift and drag to pan
- **Hover**: View exact values and dates
- **Legend**: Click to hide/show data series
- **Reset**: Double-click chart to reset zoom

**Chart Types**
- **Line Charts**: Show trends over time
- **Dual Y-Axis**: Compare different scales (VIX vs Leverage)
- **Shaded Regions**: Historical crisis periods highlighted
- **Threshold Lines**: Risk level boundaries marked

---

### Crisis Comparison (Tab 2)

#### Layout

```
┌─────────────────────────────────────────────────────────┐
│ Historical Crisis Comparison Analysis                    │
├─────────────────────────────────────────────────────────┤
│ Crisis Selection                                        │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ Select crisis periods to compare:                   │ │
│ │ ☐ Dotcom Bubble (2000-2002)                        │ │
│ │ ☑ Financial Crisis (2007-2009)                     │ │
│ │ ☐ COVID-19 Pandemic (2020-2022)                    │ │
│ └─────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────┤
│ Comparison Metrics                                      │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ Current vs 2007-2009:                              │ │
│ │                                                     │ │
│ │ Current Vulnerability: 1.85                        │ │
│ │ 2007-2009 Peak: 3.42                               │ │
│ │ Difference: -1.57 (-46%)                           │ │
│ │                                                     │ │
│ │ Interpretation: Current risk is SIGNIFICANTLY      │ │
│ │ lower than during the 2008 financial crisis.       │ │
│ └─────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────┤
│ Charts with Crisis Highlighting                         │
│ ┌─────────────────────────────────────────────────┐   │
│ │ Vulnerability Index with Crisis Periods           │   │
│ │                                                 │   │
│ │ [Chart shows normal data + shaded crisis areas] │   │
│ └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

#### Using Crisis Comparison

**Step 1**: Select Crisis Periods
- Check the boxes for crisis periods you want to analyze
- Each period is pre-configured with relevant date ranges

**Step 2**: View Comparison Metrics
- Automatically calculated differences
- Percentage changes
- Peak values during crises

**Step 3**: Analyze Charts
- Crisis periods highlighted with shaded regions
- Easy visual comparison with current market conditions
- Identify patterns and precursors

#### Available Crisis Periods

| Crisis | Period | Description |
|--------|--------|-------------|
| **Dotcom Bubble** | 2000-03 to 2002-10 | Technology stock crash |
| **Financial Crisis** | 2007-12 to 2009-06 | Subprime mortgage crisis |
| **COVID-19 Pandemic** | 2020-02 to 2022-12 | Global pandemic impact |

---

### Investment Insights (Tab 3)

#### Layout

```
┌─────────────────────────────────────────────────────────┐
│ Investment Insights & Risk Signals                       │
├─────────────────────────────────────────────────────────┤
│ Risk Assessment Panel                                    │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ Current Status (as of 2024-11-01)                   │ │
│ │                                                     │ │
│ │ 📊 Vulnerability Index: 1.85                        │ │
│ │ 🏷️ Risk Level: High Risk                             │ │
│ │ 📈 Trend: Increasing (↗)                            │ │
│ │                                                     │ │
│ │ Market Regime: Late Cycle                           │ │
│ │ Probability of Correction: 68%                      │ │
│ └─────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────┤
│ Investment Signals                                       │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ 🔴 CAUTION ADVISED                                  │ │
│ │                                                     │ │
│ │ Current indicators suggest elevated market risk.    │ │
│ │ Consider the following actions:                     │ │
│ │                                                     │ │
│ │ ✅ Maintain diversified portfolio                   │ │
│ │ ✅ Reduce leverage exposure                         │ │
│ │ ✅ Consider hedging strategies                      │ │
│ │ ✅ Increase cash reserves                           │ │
│ │ ❌ Avoid aggressive expansion                       │ │
│ │ ❌ Do not time the market                           │ │
│ └─────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────�│
│ Historical Precedents                                    │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ Similar market conditions occurred:                 │ │
│ │                                                     │ │
│ │ • 2011 (European Debt Crisis)                       │ │
│ │   - Vulnerability: 1.92                             │ │
│ │   - S&P 500 6-month return: -7%                    │ │
│ │                                                     │ │
│ │ • 2015 (China Market Correction)                    │ │
│ │   - Vulnerability: 1.78                             │ │
│ │   - S&P 500 6-month return: +2%                    │ │
│ └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

#### Understanding Investment Insights

**Risk Assessment**
- Current vulnerability index value
- Risk level classification
- Trend direction (increasing/decreasing/stable)
- Market regime identification

**Investment Signals**
- Color-coded recommendations
- Green (✅): Recommended actions
- Red (❌): Actions to avoid
- Yellow (⚠️): Proceed with caution

**Historical Precedents**
- Past periods with similar conditions
- Historical performance outcomes
- Lessons learned

#### Using Investment Insights

**Interpretation Guide**

| Indicator | Low Risk | Medium Risk | High Risk | Extreme Risk |
|-----------|----------|-------------|-----------|--------------|
| **Vulnerability** | < 0.5 | 0.5-1.5 | 1.5-3.0 | > 3.0 |
| **Recommendation** | 💰 Consider buying | ✅ Normal operations | ⚠️ Reduce risk | 🔴 Defensive position |

**Important Notes**

⚠️ **This tool is for educational purposes only. Not financial advice.**

✅ **Always consult with a financial advisor before making investment decisions.**

🔍 **Use multiple indicators, not just the vulnerability index.**

---

## Understanding the Metrics

### Part 1 Indicators (1997-01 onwards)

#### 1. Market Leverage Ratio
```
D / (CC + CM)
```
- **What**: Measures overall leverage in the market
- **Higher value**: More leverage = higher risk
- **Calculation**: Debit balances divided by total credit balances

#### 2. Money Supply Ratio
```
D / M2
```
- **What**: Ratio of margin debt to money supply
- **Interpretation**: How much of the money supply is used for leverage
- **Note**: Requires FRED API for M2 data

#### 3. Interest Cost Analysis
- **What**: Analyzes the cost of leverage
- **Components**: Interest rate impact on leverage
- **Usage**: Understand financial burden

### Part 2 Indicators (2010-02 onwards)

#### 4. Leverage Change Rate
- **MoM**: Month-over-month percentage change
- **YoY**: Year-over-year percentage change
- **Usage**: Identify accelerating/decelerating trends

#### 5. Investor Net Worth
```
D - (CC + CM)
```
- **What**: Net leverage position
- **Interpretation**: Net exposure to market risk
- **Usage**: Assess investor sentiment

#### 6. Leverage Normalized
- **What**: Z-score of leverage ratios
- **Usage**: Normalized comparison across time
- **Interpretation**: How extreme current leverage is

### Core Index

#### 7. Vulnerability Index
```
Leverage Z-Score - VIX Z-Score
```
- **What**: Main risk indicator
- **Higher**: Higher risk
- **Calculation**: Difference between normalized leverage and normalized volatility

**Risk Levels**:
- **> 3.0**: Extremely high risk ⚠️⚠️⚠️
- **> 1.5**: High risk ⚠️⚠️
- **> 0.5**: Medium risk ⚠️
- **-3.0 to 0.5**: Normal/Low risk ✅
- **< -3.0**: Extremely low risk 💰

---

## Interpreting Results

### Reading the Charts

#### Chart 1: Market Leverage Ratio
- **Upward trend**: Increasing market leverage = higher risk
- **Sharp spikes**: Potential warning signals
- **Historical peaks**: Compare with past crisis periods

#### Chart 2: Money Supply Ratio
- **Rising ratio**: Margin debt growing faster than money supply
- **High values**: Potential bubble indicator
- **Declining ratio**: Leverage becoming more sustainable

#### Chart 3: Interest Cost Analysis
- **Rising costs**: Increased financial burden
- **High interest rates**: Risk of forced deleveraging
- **Cost spikes**: Potential margin call risks

#### Chart 4: Leverage Change Rate
- **Positive MoM**: Accelerating leverage growth
- **Negative YoY**: Deleveraging in progress
- **Volatile changes**: Uncertain market conditions

#### Chart 5: Investor Net Worth
- **Positive values**: Net long exposure
- **Negative values**: Net short exposure
- **Trend changes**: Shifts in investor sentiment

#### Chart 6: Vulnerability Index
- **Primary indicator**: Most important chart
- **Color coding**: Red = high risk, Green = low risk
- **Thresholds**: Horizontal lines show risk boundaries

#### Chart 7: VIX vs Leverage (Dual Axis)
- **Left axis**: VIX (volatility)
- **Right axis**: Leverage ratio
- **Divergence**: When leverage rises but VIX falls = elevated risk
- **Convergence**: Normal market condition

### Market Regimes

#### Early Cycle (Recovery)
- **Vulnerability**: < 0
- **Characteristics**: Low leverage, stable growth
- **Strategy**: Accumulate positions

#### Mid Cycle (Expansion)
- **Vulnerability**: 0 to 1
- **Characteristics**: Moderate leverage, strong growth
- **Strategy**: Maintain diversified portfolio

#### Late Cycle (Slowdown)
- **Vulnerability**: 1 to 2
- **Characteristics**: High leverage, slowing growth
- **Strategy**: Reduce risk, increase quality

#### Recession/Correction
- **Vulnerability**: > 2
- **Characteristics**: Very high leverage, declining growth
- **Strategy**: Defensive positioning

---

## Data Sources

### FINRA (Financial Industry Regulatory Authority)

**What**: Margin debt statistics
**Source**: `datas/margin-statistics.csv`
**Update Frequency**: Monthly
**Components**:
- **D**: Debit balances in margin accounts (in thousands)
- **CC**: Free credit balances in cash accounts
- **CM**: Free credit balances in margin accounts

**Data Range**: 1997-01 to present

### FRED (Federal Reserve Economic Data)

**What**: Macroeconomic data
**Source**: FRED API
**Update Frequency**: Monthly
**Components**:
- **M2SL**: M2 Money Stock (in billions)

**API Key**: Required (free from FRED)
**Registration**: https://fred.stlouisfed.org/docs/api/api_key.html

### Yahoo Finance

**What**: Market index data
**Source**: Yahoo Finance API
**Update Frequency**: Daily
**Components**:
- **^VIX**: CBOE Volatility Index
- **^GSPC**: S&P 500 Index

**Data Range**: Varies by symbol

### Data Synchronization

All data sources are:
1. **Collected** at different frequencies (daily, monthly)
2. **Resampled** to monthly frequency
3. **Aligned** by month-start dates
4. **Merged** into unified dataset
5. **Validated** for quality

---

## FAQ

### General Questions

**Q: How often should I check the vulnerability index?**
A: Weekly or monthly is sufficient. The index is designed for strategic, not tactical, timing.

**Q: Can I use this for day trading?**
A: No. This tool is designed for medium to long-term analysis (months to years), not intraday trading.

**Q: How accurate is the vulnerability index?**
A: It's a useful indicator but should be combined with other analysis. Historical backtesting shows correlation with market stress, but it's not a perfect predictor.

**Q: What timeframe does the index cover?**
A: Part 1 indicators from 1997-01, Part 2 from 2010-02, VIX from 1990, S&P 500 from historical dates.

### Technical Questions

**Q: Why do I need a FRED API key?**
A: For M2 money supply data, which provides important macroeconomic context. Without it, some indicators will be unavailable.

**Q: How do I update the data?**
A: Click the "Refresh Data" button in the sidebar. Data is cached for 1 hour to avoid excessive API calls.

**Q: Can I export the data?**
A: Yes, use the export controls in the sidebar (CSV, Excel, JSON formats).

**Q: What if the data quality score is low?**
A: Check the validation report. Low scores may indicate data source issues or unusual market conditions.

### Data Questions

**Q: Why is my data range limited?**
A: Data availability depends on the source. FINRA data starts 1997-01, FRED data varies by series.

**Q: How are missing values handled?**
A: The system interpolates for short gaps (< 3 months) and marks longer gaps as missing. Validation reports show data quality.

**Q: Can I add custom data sources?**
A: Yes, modify `src/data/fetcher.py` to add new data sources. See API documentation for details.

---

## Troubleshooting

### Common Issues

#### Issue: "FRED_API_KEY not set" Warning

**Solution**:
```bash
# Check if key is set
echo $FRED_API_KEY

# Set the key
export FRED_API_KEY=your_api_key_here

# Make it permanent
echo 'export FRED_API_KEY=your_api_key_here' >> ~/.bashrc
source ~/.bashrc
```

#### Issue: Charts Not Loading

**Solutions**:
1. Check internet connection
2. Refresh the page
3. Click "Refresh Data" button
4. Check browser console for errors (F12)

#### Issue: Low Data Quality Score

**Possible Causes**:
- Data source temporarily unavailable
- Date range too narrow
- Missing API keys

**Solutions**:
1. Expand date range
2. Verify API keys
3. Check data source status
4. Try refreshing data

#### Issue: Application Won't Start

**Solutions**:
```bash
# 1. Check Python version
python --version  # Should be 3.10+

# 2. Verify virtual environment
which python  # Should be .venv/bin/python

# 3. Reinstall dependencies
pip install -r requirements.txt

# 4. Check for errors
streamlit run app.py --logger.level debug
```

#### Issue: Slow Performance

**Solutions**:
1. Reduce date range
2. Clear cache: `fetcher.clear_cache()`
3. Disable real-time updates
4. Check internet speed

#### Issue: Missing Data Columns

**Solutions**:
1. Verify API keys are set
2. Check data source status
3. Try different date range
4. Review validation report

### Performance Optimization

**For Better Speed**:
- Use date ranges wisely (don't fetch unnecessary data)
- Enable caching (default behavior)
- Avoid unnecessary refreshes
- Close unused browser tabs

**For Better Data Quality**:
- Use broader date ranges when possible
- Verify all API keys are set
- Check data source health
- Review validation reports

### Getting Help

**Documentation**:
- API Documentation: `docs/API_DOCUMENTATION.md`
- Technical Reports: `docs/US3_finish_report.md`
- Task Analysis: `docs/fred_task_analyze.md`

**Support Channels**:
- GitHub Issues: https://github.com/cattom2000/levAnalyzeMM/issues
- Email: (if provided)

**Self-Help**:
- Check log files: `logs/levAnalyzeMM.log`
- Review validation reports in UI
- Examine data quality scores
- Test with smaller date ranges

---

## Appendix

### Risk Disclaimer

⚠️ **IMPORTANT DISCLAIMER**

This tool is provided for educational and research purposes only. It is NOT financial advice.

- Past performance does not guarantee future results
- All investments carry risk of loss
- Use multiple analysis methods, not just this tool
- Consult with qualified financial advisors
- The vulnerability index is an indicator, not a prediction
- Market conditions can change rapidly
- The creators are not responsible for investment losses

### Data Attribution

When using or sharing data from this system, please attribute:

- **FINRA Data**: "Source: Financial Industry Regulatory Authority"
- **FRED Data**: "Source: FRED, Federal Reserve Bank of St. Louis"
- **Yahoo Finance**: "Source: Yahoo Finance"

### Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-11-13 | Initial release |
| | | - 7 core indicators |
| | | - 3 user stories |
| | | - Historical crisis detection |
| | | - Real-time data integration |

### License

This project is released under the MIT License. See LICENSE file for details.

---

**Last Updated**: 2025-11-13
**Version**: 1.0.0
**Document Version**: 1.0.0

For the latest information, visit: https://github.com/cattom2000/levAnalyzeMM
