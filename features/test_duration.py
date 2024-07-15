import streamlit as st
import numpy as np
import pandas as pd
from scipy import stats
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def calculate_sample_size(baseline_rate, mde, alpha, power):
    """
    Calculate the required sample size for each variant in an A/B test.
    
    Args:
    baseline_rate (float): The conversion rate of the control group
    mde (float): Minimum Detectable Effect (relative change)
    alpha (float): Significance level (typically 0.05)
    power (float): Statistical power (typically 0.8)
    
    Returns:
    int: Required sample size for each variant
    """
    p1 = baseline_rate
    p2 = baseline_rate * (1 + mde)
    
    z_alpha = stats.norm.ppf(1 - alpha / 2)
    z_beta = stats.norm.ppf(power)
    
    pooled_p = (p1 + p2) / 2
    
    n = ((z_alpha * np.sqrt(2 * pooled_p * (1 - pooled_p)) + 
          z_beta * np.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2) / (p2 - p1) ** 2
    
    return int(np.ceil(n))

def estimate_test_duration(sample_size, daily_visitors, traffic_split=0.5):
    """
    Estimate the test duration based on sample size and daily visitors.
    
    Args:
    sample_size (int): Required sample size for each variant
    daily_visitors (int): Total number of daily visitors
    traffic_split (float): Proportion of traffic allocated to each variant (default 50%)
    
    Returns:
    int: Estimated test duration in days
    """
    visitors_per_variant = daily_visitors * traffic_split
    duration_days = np.ceil(sample_size / visitors_per_variant)
    return int(duration_days)

def generate_time_series(baseline_rate, mde, daily_visitors, duration_days, traffic_split):
    """
    Generate time series data for different scenarios.
    
    Args:
    baseline_rate (float): Baseline conversion rate
    mde (float): Minimum Detectable Effect
    daily_visitors (int): Total daily visitors
    duration_days (int): Estimated test duration
    traffic_split (float): Proportion of traffic allocated to each variant
    
    Returns:
    pd.DataFrame: DataFrame with time series data
    """
    days = np.arange(1, duration_days + 1)
    visitors_per_variant = daily_visitors * traffic_split
    
    control_rate = baseline_rate
    variation_rate = baseline_rate * (1 + mde)
    
    scenarios = {
        'Expected': {'control': control_rate, 'variation': variation_rate},
        'No Effect': {'control': control_rate, 'variation': control_rate},
        'Negative Effect': {'control': control_rate, 'variation': baseline_rate * (1 - mde/2)}
    }
    
    data = []
    for scenario, rates in scenarios.items():
        control_conversions = np.random.binomial(visitors_per_variant, rates['control'], duration_days).cumsum()
        variation_conversions = np.random.binomial(visitors_per_variant, rates['variation'], duration_days).cumsum()
        
        control_rate = control_conversions / (visitors_per_variant * days)
        variation_rate = variation_conversions / (visitors_per_variant * days)
        
        data.extend([
            {'Day': day, 'Scenario': scenario, 'Variant': 'Control', 'Conversion Rate': cr}
            for day, cr in zip(days, control_rate)
        ])
        data.extend([
            {'Day': day, 'Scenario': scenario, 'Variant': 'Variation', 'Conversion Rate': vr}
            for day, vr in zip(days, variation_rate)
        ])
    
    return pd.DataFrame(data)

def plot_time_series(df, baseline_rate, mde):
    """
    Create a plotly figure with time series for different scenarios.
    
    Args:
    df (pd.DataFrame): DataFrame with time series data
    baseline_rate (float): Baseline conversion rate
    mde (float): Minimum Detectable Effect
    
    Returns:
    go.Figure: Plotly figure object
    """
    scenarios = df['Scenario'].unique()
    fig = make_subplots(rows=len(scenarios), cols=1, shared_xaxes=True, vertical_spacing=0.05,
                        subplot_titles=scenarios)
    
    colors = {'Control': '#1f77b4', 'Variation': '#ff7f0e'}
    
    for i, scenario in enumerate(scenarios, start=1):
        scenario_data = df[df['Scenario'] == scenario]
        for variant in ['Control', 'Variation']:
            variant_data = scenario_data[scenario_data['Variant'] == variant]
            fig.add_trace(
                go.Scatter(x=variant_data['Day'], y=variant_data['Conversion Rate'],
                           mode='lines', name=f"{scenario} - {variant}", line=dict(color=colors[variant])),
                row=i, col=1
            )
        
        fig.add_hline(y=baseline_rate, line_dash="dash", line_color="gray", row=i, col=1)
        fig.add_hline(y=baseline_rate*(1+mde), line_dash="dash", line_color="red", row=i, col=1)

    fig.update_layout(height=300*len(scenarios), title_text="A/B Test Scenarios", showlegend=False)
    fig.update_xaxes(title_text="Days")
    fig.update_yaxes(title_text="Conversion Rate", tickformat=".2%")
    
    return fig

def ab_test_duration_calculator():
    st.subheader("A/B Test Duration Calculator")
    
    col1, col2 = st.columns(2)
    
    with col1:
        baseline_rate = st.slider("Baseline Conversion Rate (%)", 0.1, 100.0, 5.0, 0.1) / 100
        mde = st.slider("Minimum Detectable Effect (%)", 1.0, 100.0, 10.0, 0.1) / 100
        daily_visitors = st.number_input("Total Daily Visitors", min_value=10, value=1000, step=10)
    
    with col2:
        alpha = st.selectbox("Significance Level", [0.1, 0.05, 0.01], index=1)
        power = st.selectbox("Statistical Power", [0.7, 0.8, 0.9], index=1)
        traffic_split = st.slider("Traffic Split (% to each variant)", 10, 50, 50) / 100
    
    if st.button("Calculate Test Duration and Generate Scenarios"):
        sample_size = calculate_sample_size(baseline_rate, mde, alpha, power)
        duration = estimate_test_duration(sample_size, daily_visitors, traffic_split)
        
        st.success(f"Estimated test duration: {duration:.0f} days")
        st.info(f"Required sample size per variant: {sample_size:.0f}")
        
        st.markdown("### Test Details:")
        st.markdown(f"- Baseline conversion rate: {baseline_rate:.2%}")
        st.markdown(f"- Minimum detectable effect: {mde:.2%}")
        st.markdown(f"- Significance level (α): {alpha}")
        st.markdown(f"- Statistical power: {power}")
        st.markdown(f"- Traffic allocation: {traffic_split:.0%} to each variant")
        
        # Generate and plot time series data
        df = generate_time_series(baseline_rate, mde, daily_visitors, duration, traffic_split)
        fig = plot_time_series(df, baseline_rate, mde)
        st.plotly_chart(fig, use_container_width=True)
        
        st.warning("Note: These scenarios are simulations and may not reflect actual test results. Always monitor your test closely and consider factors like seasonality and external events.")

        # Add option to download the simulation data
        csv = df.to_csv(index=False)
        st.download_button(
            label="Download Simulation Data",
            data=csv,
            file_name="ab_test_simulation.csv",
            mime="text/csv",
        )