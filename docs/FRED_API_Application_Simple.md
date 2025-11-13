# FRED API Key Application - Simple Project Description

## Project: levAnalyzeMM
**Margin Debt Market Analysis System**

### What is this project?
A market risk analysis tool that combines margin debt data with economic indicators to calculate a "Vulnerability Index" for investment research.

### Primary Purpose
Academic research to analyze the relationship between money supply (M2), market leverage, and volatility to identify market stress periods.

### Data Needed from FRED
- **M2SL**: M2 Money Stock (monthly data from 1997 to present)

### How M2 Data Will Be Used
1. Retrieved monthly via FRED API (1-2 calls per month)
2. Merged with margin debt and volatility data
3. Used to analyze correlation between money supply and market risk
4. Provides macroeconomic context for market vulnerability analysis

### Technical Details
- **Language**: Python 3.10+
- **API Library**: fredapi (v0.5.0)
- **Data Volume**: ~300 monthly data points (1997-present)
- **Update Frequency**: Monthly
- **Caching**: Yes, 24-hour cache to minimize API calls

### Expected API Usage
- **Calls per month**: 1-2 (for new data)
- **Calls per year**: <50 total
- **Rate**: Very low, well below FRED limits

### Data Security
- API key stored as environment variable (not in code)
- No personal data collected
- Data used only for stated research purposes
- Compliant with FRED Terms of Use

### Attribution
"Source: FRED, Federal Reserve Bank of St. Louis"

### Project Repository
https://github.com/cattom2000/levAnalyzeMM

---

**Type**: Academic/Research Project
**Use**: Non-commercial research only
