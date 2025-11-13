# Project Description for FRED API Key Application

## Project Overview

**Project Name**: levAnalyzeMM - Margin Debt Market Analysis System

**Purpose**: A comprehensive market risk analysis tool designed to analyze margin debt data and calculate market vulnerability indicators for investment research and risk assessment.

**Development Status**: In active development (Phase 8-10 of implementation)

## Research Objectives

This project aims to:
- Analyze the relationship between margin debt and market volatility
- Calculate a composite "Vulnerability Index" combining leverage metrics and volatility indicators
- Provide historical analysis of market stress periods (1997-2025)
- Support evidence-based investment decision-making through quantitative analysis

## Data Requirements

### FRED Data Series Needed:
- **M2SL**: M2 Money Stock (Primary data series)
  - Purpose: Economic liquidity indicator
  - Frequency: Monthly
  - Time Range: 1997-01 to present
  - Usage: Provide macroeconomic context for market vulnerability analysis

### How M2SL Data is Used:
The M2 Money Stock data from FRED will be integrated with:
1. **FINRA Margin Debt Statistics** (monthly margin debt balances)
2. **CBOE VIX Index** (market volatility indicator)
3. **S&P 500 Index** (market capitalization reference)

Combined analysis enables:
- Correlation between money supply growth and market leverage
- Identification of liquidity-driven market stress
- Understanding macro-level factors affecting market vulnerability

## Project Architecture

### Data Sources:
- **FRED API**: M2 Money Stock (M2SL series)
- **Yahoo Finance**: Market indices (VIX, S&P 500)
- **FINRA**: Margin debt statistics (local CSV data)

### Technical Stack:
- **Backend**: Python 3.10+
- **Data Processing**: pandas, numpy
- **API Integration**: fredapi library (v0.5.0+)
- **Web Interface**: Streamlit
- **Analysis Engine**: Custom vulnerability index calculation

### Data Processing:
```python
# Example data integration workflow
1. Fetch M2SL data via FRED API (monthly frequency)
2. Resample to align with other monthly data sources
3. Merge with margin debt and volatility indicators
4. Calculate composite vulnerability metrics
5. Generate visualization and analysis reports
```

## Use Case Example

**Analyst Workflow**:
1. Load historical margin debt and M2 money supply data
2. Calculate 12-month rolling Z-scores for both series
3. Analyze correlation during stress periods (e.g., 2008 Financial Crisis, 2020 COVID-19)
4. Generate market vulnerability assessment
5. Export analysis results for investment committee review

## Data Usage Policy

### Frequency:
- **API Calls**: Approximately 1-2 calls per month (batch data retrieval)
- **Caching**: All data cached locally with 24-hour TTL to minimize redundant calls
- **Update Frequency**: Monthly (aligns with data publication schedule)

### Volume:
- **M2SL Series**: Approximately 300 data points (monthly from 1997)
- **Expected Monthly Calls**: 1-2 calls for new data retrieval
- **Annual Estimate**: <50 API calls per year

### Data Handling:
- All data stored locally in encrypted format
- No redistribution of FRED data
- Compliant with FRED API Terms of Use
- Academic/research use only (not commercial)

## Privacy & Security

- **API Key**: Stored securely as environment variable (not in code)
- **Local Storage**: Data cached locally with access controls
- **No User Data**: The system does not collect or store personal information
- **Public Project**: Code and analysis results may be published for academic purposes

## Project Benefits

1. **Academic Research**: Contributes to understanding of market-liquidity relationships
2. **Risk Management**: Provides quantitative tools for institutional risk assessment
3. **Educational**: Demonstrates practical application of economic data analysis
4. **Open Source**: Project code may be released as educational resource

## Development Timeline

- **Phase 1-4**: ✅ Completed (Core system implementation)
- **Phase 8-10**: 🔄 In Progress (System integration and testing)
- **Expected Completion**: December 2024
- **Project Duration**: Active development through Q1 2025

## Contact Information

**Primary Developer**: levAnalyzeMM Development Team
**Project Repository**: https://github.com/cattom2000/levAnalyzeMM
**Contact Method**: GitHub Issues/Discussions

## Data Attribution

When using FRED data, proper attribution will be provided:
- "Source: FRED, Federal Reserve Bank of St. Louis"
- "M2 Money Stock (M2SL), retrieved from FRED"

## Compliance

This project will:
- ✅ Comply with all FRED API Terms of Use
- ✅ Respect API rate limits
- ✅ Provide proper data attribution
- ✅ Not redistribute FRED data
- ✅ Use data for stated research purposes only

---

**Note**: This application is for academic and research purposes only. No commercial use of the data is intended.

**Project License**: Open source (educational use)
**Last Updated**: November 2025
