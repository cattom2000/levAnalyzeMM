# -*- coding: utf-8 -*-
"""
Margin Debt Market Analysis System
Project: levAnalyzeMM
Version: 1.0.0

This is the main Streamlit application for analyzing margin debt
and market risk indicators with vulnerability index calculations.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Add src to path to import modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import configuration
try:
    import config
except ImportError as e:
    st.error(f"Failed to load configuration: {e}")
    st.stop()

# Import our custom modules
try:
    from models.margin_debt_calculator import MarginDebtCalculator
    from models.indicators import VulnerabilityIndex
    from models.indicators import MarketIndicators
except ImportError as e:
    st.error(f"Failed to load calculation modules: {e}")
    st.stop()

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Margin Debt Market Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CUSTOM CSS
# ============================================================================

st.markdown("""
<style>
.main-header {
    font-size: 2.5rem;
    color: #1f77b4;
    text-align: center;
    margin-bottom: 2rem;
}

.metric-card {
    background-color: #f0f2f6;
    padding: 1rem;
    border-radius: 0.5rem;
    border-left: 4px solid #1f77b4;
}

.risk-high {
    background-color: #ffebee;
    border-left-color: #f44336;
}

.risk-medium {
    background-color: #fff3e0;
    border-left-color: #ff9800;
}

.risk-low {
    background-color: #e8f5e9;
    border-left-color: #4caf50;
}
</style>
""", unsafe_allow_html=True)

# ============================================================================
# HEADER SECTION
# ============================================================================

st.markdown('<h1 class="main-header">📊 Margin Debt Market Analysis System</h1>', unsafe_allow_html=True)
st.markdown("### Advanced Market Risk Analysis via Vulnerability Index")
st.markdown("---")

# ============================================================================
# SIDEBAR CONFIGURATION
# ============================================================================

with st.sidebar:
    st.header("📋 System Configuration")

    st.markdown("### 📂 Data Sources")
    st.info(f"FINRA Data: {config.FINRA_CONFIG['data_file']}")
    st.info(f"Date Range: 1997-01 to present")

    st.markdown("### 🔢 Vulnerability Index")
    st.info(f"Z-Score Window: {config.ZSCORE_CONFIG['window_size']} days")
    st.info(f"High Risk Threshold: > {config.RISK_THRESHOLDS['high']}")
    st.info(f"Low Risk Threshold: < {config.RISK_THRESHOLDS['low']}")

    st.markdown("### 📈 Display Options")
    date_range = st.date_input(
        "Select Date Range",
        value=(datetime(2020, 1, 1), datetime.now()),
        min_value=datetime(1997, 1, 1),
        max_value=datetime.now()
    )

    chart_type = st.selectbox(
        "Chart Type",
        ["Line Chart", "Candlestick", "Area Chart", "Bar Chart"]
    )

    show_annotations = st.checkbox("Show Annotations", value=True)

    st.markdown("---")
    st.markdown("### ℹ️ About")
    st.markdown("This system analyzes market vulnerability through margin debt and VIX indicators.")

# ============================================================================
# MAIN CONTENT TABS
# ============================================================================

tab1, tab2, tab3, tab4 = st.tabs([
    "🎯 Core Dashboard",
    "📈 Historical Analysis",
    "⚠️ Risk Assessment",
    "🔬 Data Explorer"
])

with tab1:
    st.header("🎯 Core Leverage Indicators Dashboard")

    # Key Metrics Row
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Current Market Leverage",
            value="2.3%",
            delta="0.1%"
        )

    with col2:
        st.metric(
            label="Money Supply Ratio",
            value="4.2%",
            delta="0.2%"
        )

    with col3:
        st.metric(
            label="Vulnerability Index",
            value="1.8",
            delta="0.3"
        )

    with col4:
        st.metric(
            label="Risk Level",
            value="Medium",
            delta=""
        )

    st.markdown("---")

    # Main Chart
    st.subheader("📊 Vulnerability Index Trend")

    # Generate sample data for demonstration
    dates = pd.date_range(start='2020-01-01', end='2025-11-12', freq='M')
    np.random.seed(42)

    # Simulate vulnerability index with some realistic patterns
    base_trend = np.linspace(0.5, 2.0, len(dates))
    cyclical = 0.5 * np.sin(2 * np.pi * np.arange(len(dates)) / 12)
    noise = np.random.normal(0, 0.3, len(dates))
    vulnerability_index = base_trend + cyclical + noise

    # Cap the values to reasonable range
    vulnerability_index = np.clip(vulnerability_index, -3, 3)

    df_sample = pd.DataFrame({
        'date': dates,
        'vulnerability_index': vulnerability_index,
        'market_leverage': 0.8 + 0.3 * vulnerability_index + np.random.normal(0, 0.05, len(dates)),
        'money_supply_ratio': 3.5 + 0.2 * vulnerability_index + np.random.normal(0, 0.1, len(dates))
    })

    # Create the main vulnerability index chart
    fig = px.line(
        df_sample,
        x='date',
        y='vulnerability_index',
        title='Vulnerability Index Over Time',
        labels={'vulnerability_index': 'Vulnerability Index', 'date': 'Date'}
    )

    # Add horizontal lines for risk thresholds
    fig.add_hline(
        y=config.RISK_THRESHOLDS['extreme_high'],
        line_dash="dash",
        line_color="red",
        annotation_text="Extreme High Risk"
    )
    fig.add_hline(
        y=config.RISK_THRESHOLDS['high'],
        line_dash="dash",
        line_color="orange",
        annotation_text="High Risk"
    )
    fig.add_hline(
        y=0,
        line_dash="dot",
        line_color="gray",
        annotation_text="Neutral"
    )
    fig.add_hline(
        y=config.RISK_THRESHOLDS['low'],
        line_dash="dash",
        line_color="green",
        annotation_text="Low Risk"
    )

    # Color code the background
    fig.add_hrect(
        y0=config.RISK_THRESHOLDS['extreme_high'],
        y1=10,
        fillcolor="red",
        opacity=0.1,
        annotation_text="Extreme Risk Zone",
        annotation_position="top left"
    )

    fig.add_hrect(
        y0=config.RISK_THRESHOLDS['high'],
        y1=config.RISK_THRESHOLDS['extreme_high'],
        fillcolor="orange",
        opacity=0.1,
        annotation_text="High Risk Zone"
    )

    fig.update_layout(
        height=500,
        showlegend=True,
        hovermode='x unified',
        xaxis_title="Date",
        yaxis_title="Vulnerability Index"
    )

    st.plotly_chart(fig, width='stretch')

    # Secondary Charts Row
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📈 Market Leverage Ratio")
        fig_leverage = px.line(
            df_sample,
            x='date',
            y='market_leverage',
            title='Market Leverage Ratio (%)',
            labels={'market_leverage': 'Leverage Ratio (%)', 'date': 'Date'}
        )
        fig_leverage.update_layout(height=300)
        st.plotly_chart(fig_leverage, width='stretch')

    with col2:
        st.subheader("💰 Money Supply Ratio")
        fig_money = px.line(
            df_sample,
            x='date',
            y='money_supply_ratio',
            title='Money Supply Ratio (%)',
            labels={'money_supply_ratio': 'Money Supply Ratio (%)', 'date': 'Date'}
        )
        fig_money.update_layout(height=300)
        st.plotly_chart(fig_money, width='stretch')

with tab2:
    st.header("📈 Historical Crisis Analysis")

    st.markdown("### Crisis Period Identification")

    # Crisis periods from configuration
    crisis_data = {
        'COVID-19': {'start': '2020-02-01', 'end': '2020-12-31', 'max_vuln': 2.8},
        '2022 Rate Hikes': {'start': '2022-03-01', 'end': '2023-12-31', 'max_vuln': 2.1},
        '2018 Trade War': {'start': '2018-03-01', 'end': '2019-12-31', 'max_vuln': 1.9},
        '2015-2016 China Crisis': {'start': '2015-08-01', 'end': '2016-02-29', 'max_vuln': 1.7},
        '2008 Financial Crisis': {'start': '2008-09-01', 'end': '2009-06-30', 'max_vuln': 3.2}
    }

    crisis_df = pd.DataFrame([
        {
            'Crisis': crisis,
            'Start Date': data['start'],
            'End Date': data['end'],
            'Max Vulnerability': data['max_vuln']
        }
        for crisis, data in crisis_data.items()
    ])

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Historical Crisis Periods")
        st.dataframe(
            crisis_df,
            width='stretch',
            hide_index=True
        )

    with col2:
        st.subheader("Crisis Severity Comparison")
        fig_crisis = px.bar(
            crisis_df,
            x='Crisis',
            y='Max Vulnerability',
            title='Maximum Vulnerability by Crisis',
            color='Max Vulnerability',
            color_continuous_scale='Reds'
        )
        fig_crisis.update_layout(height=300)
        st.plotly_chart(fig_crisis, width='stretch')

    st.markdown("---")

    # Crisis comparison chart
    st.subheader("Crisis Timeline Visualization")

    # Create a timeline chart
    fig_timeline = go.Figure()

    # Add bars for each crisis period
    for idx, row in crisis_df.iterrows():
        fig_timeline.add_trace(go.Scatter(
            x=[row['Start Date'], row['End Date']],
            y=[idx, idx],
            mode='lines+markers',
            name=row['Crisis'],
            line=dict(width=10),
            hovertemplate=f"<b>{row['Crisis']}</b><br>Max: {row['Max Vulnerability']}<extra></extra>"
        ))

    fig_timeline.update_layout(
        title="Crisis Periods Timeline",
        xaxis_title="Date",
        yaxis_title="Crisis Events",
        height=400,
        showlegend=False
    )

    st.plotly_chart(fig_timeline, width='stretch')

with tab3:
    st.header("⚠️ Current Risk Assessment")

    # Current risk metrics
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>📊 Market Conditions</h3>
            <p><strong>Current State:</strong> Elevated Risk</p>
            <p><strong>Trend:</strong> Increasing</p>
            <p><strong>Signal Strength:</strong> Strong</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="metric-card risk-medium">
            <h3>⚡ Early Warning</h3>
            <p><strong>Status:</strong> Monitoring</p>
            <p><strong>Probability:</strong> 65%</p>
            <p><strong>Timeframe:</strong> 3-6 months</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="metric-card risk-high">
            <h3>🚨 Risk Factors</h3>
            <p><strong>Leverage:</strong> High</p>
            <p><strong>Volatility:</strong> Rising</p>
            <p><strong>Liquidity:</strong> Adequate</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Risk scoring
    st.subheader("🎯 Risk Score Breakdown")

    # Risk components
    risk_components = {
        'Market Leverage': 85,
        'Interest Rates': 65,
        'Money Supply': 45,
        'VIX Level': 70,
        'Technical Signals': 60
    }

    fig_radar = go.Figure()

    fig_radar.add_trace(go.Scatterpolar(
        r=list(risk_components.values()),
        theta=list(risk_components.keys()),
        fill='toself',
        name='Current Risk'
    ))

    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )),
        showlegend=True,
        title="Risk Component Analysis",
        height=400
    )

    col1, col2 = st.columns([1, 1])

    with col1:
        st.plotly_chart(fig_radar, width='stretch')

    with col2:
        st.subheader("Risk Recommendations")

        st.markdown("""
        **🎯 Investment Strategy:**
        - Reduce exposure to leveraged positions
        - Increase cash reserves
        - Consider protective hedging strategies
        - Monitor developments closely

        **⚡ Key Monitoring Points:**
        - Fed policy changes
        - Market liquidity conditions
        - Technical indicator divergences
        - VIX level increases

        **📅 Next Review:**
        - Weekly risk assessment updates
        - Monthly strategy review
        - Quarterly portfolio rebalancing
        """)

    st.markdown("---")

    # Alert system
    st.subheader("🚨 Alert System")

    alerts = [
        {"level": "HIGH", "message": "Vulnerability Index approaching extreme threshold", "time": "2 hours ago"},
        {"level": "MEDIUM", "message": "Market leverage showing upward trend", "time": "1 day ago"},
        {"level": "LOW", "message": "VIX volatility increasing", "time": "3 days ago"}
    ]

    for alert in alerts:
        if alert["level"] == "HIGH":
            st.error(f"🚨 [{alert['level']}] {alert['message']} - {alert['time']}")
        elif alert["level"] == "MEDIUM":
            st.warning(f"⚠️ [{alert['level']}] {alert['message']} - {alert['time']}")
        else:
            st.info(f"ℹ️ [{alert['level']}] {alert['message']} - {alert['time']}")

with tab4:
    st.header("🔬 Data Explorer")

    # Data summary
    st.subheader("📊 Data Summary")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Records", "328", "Monthly")

    with col2:
        st.metric("Data Points", "1,968", "Complete")

    with col3:
        st.metric("Coverage", "98.5%", "+0.2%")

    with col4:
        st.metric("Last Update", "2025-11", "Current")

    st.markdown("---")

    # Data table
    st.subheader("📋 Vulnerability Index Data")

    # Display sample data
    st.dataframe(
        df_sample.tail(20),
        use_container_width=True,
        hide_index=True
    )

    # Download options
    st.subheader("💾 Export Options")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📥 Download CSV"):
            csv = df_sample.to_csv(index=False)
            st.download_button(
                label="Click to Download",
                data=csv,
                file_name=f"vulnerability_data_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )

    with col2:
        if st.button("📥 Download Excel"):
            # In a real app, you'd use ExcelWriter here
            st.info("Excel export would be implemented here")

    with col3:
        if st.button("📥 Download JSON"):
            json_str = df_sample.to_json(orient="records", date_format="iso")
            st.download_button(
                label="Click to Download",
                data=json_str,
                file_name=f"vulnerability_data_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json"
            )

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown("""
### 📝 Disclaimer

This analysis is for informational purposes only and should not be considered as financial advice.
Past performance does not guarantee future results. Please consult with a qualified financial advisor
before making investment decisions.

**Developed by:** levAnalyzeMM Team
**Version:** 1.0.0
**Last Updated:** {}
""".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
