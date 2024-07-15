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

def generate_scenarios(baseline_rate, mde, daily_visitors, traffic_split, alpha, power):
    """
    Generate scenarios for different parameter combinations.
    
    Args:
    baseline_rate (float): Baseline conversion rate
    mde (float): Minimum Detectable Effect
    daily_visitors (int): Total daily visitors
    traffic_split (float): Proportion of traffic allocated to each variant
    alpha (float): Significance level
    power (float): Statistical power
    
    Returns:
    pd.DataFrame: DataFrame with scenario data
    """
    scenarios = []
    
    # Baseline scenario
    sample_size = calculate_sample_size(baseline_rate, mde, alpha, power)
    duration = estimate_test_duration(sample_size, daily_visitors, traffic_split)
    scenarios.append({
        'Scenario': 'Baseline',
        'Baseline Rate': baseline_rate,
        'MDE': mde,
        'Alpha': alpha,
        'Power': power,
        'Sample Size': sample_size,
        'Duration (days)': duration
    })
    
    # Varying MDE
    for mde_factor in [0.5, 1.5, 2.0]:
        new_mde = mde * mde_factor
        sample_size = calculate_sample_size(baseline_rate, new_mde, alpha, power)
        duration = estimate_test_duration(sample_size, daily_visitors, traffic_split)
        scenarios.append({
            'Scenario': f'MDE {mde_factor}x',
            'Baseline Rate': baseline_rate,
            'MDE': new_mde,
            'Alpha': alpha,
            'Power': power,
            'Sample Size': sample_size,
            'Duration (days)': duration
        })
    
    # Varying significance level
    for new_alpha in [0.1, 0.01]:
        sample_size = calculate_sample_size(baseline_rate, mde, new_alpha, power)
        duration = estimate_test_duration(sample_size, daily_visitors, traffic_split)
        scenarios.append({
            'Scenario': f'Alpha {new_alpha}',
            'Baseline Rate': baseline_rate,
            'MDE': mde,
            'Alpha': new_alpha,
            'Power': power,
            'Sample Size': sample_size,
            'Duration (days)': duration
        })
    
    # Varying power
    for new_power in [0.7, 0.9]:
        sample_size = calculate_sample_size(baseline_rate, mde, alpha, new_power)
        duration = estimate_test_duration(sample_size, daily_visitors, traffic_split)
        scenarios.append({
            'Scenario': f'Power {new_power}',
            'Baseline Rate': baseline_rate,
            'MDE': mde,
            'Alpha': alpha,
            'Power': new_power,
            'Sample Size': sample_size,
            'Duration (days)': duration
        })
    
    return pd.DataFrame(scenarios)

def plot_scenarios(df):
    """
    Create a plotly figure with bar charts for sample size and duration.
    
    Args:
    df (pd.DataFrame): DataFrame with scenario data
    
    Returns:
    go.Figure: Plotly figure object
    """
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1,
                        subplot_titles=('Sample Size per Variant', 'Test Duration (Days)'))
    
    scenarios = df['Scenario']
    
    fig.add_trace(
        go.Bar(x=scenarios, y=df['Sample Size'], name='Sample Size'),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Bar(x=scenarios, y=df['Duration (days)'], name='Duration'),
        row=2, col=1
    )

    fig.update_layout(height=600, title_text="A/B Test Scenarios", showlegend=False)
    fig.update_xaxes(title_text="Scenarios", row=2, col=1)
    fig.update_yaxes(title_text="Sample Size", row=1, col=1)
    fig.update_yaxes(title_text="Days", row=2, col=1)
    
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
        scenarios_df = generate_scenarios(baseline_rate, mde, daily_visitors, traffic_split, alpha, power)
        
        st.success(f"Baseline scenario:")
        st.info(f"Required sample size per variant: {scenarios_df.iloc[0]['Sample Size']:.0f}")
        st.info(f"Estimated test duration: {scenarios_df.iloc[0]['Duration (days)']:.0f} days")
        
        st.markdown("### Test Details:")
        st.markdown(f"- Baseline conversion rate: {baseline_rate:.2%}")
        st.markdown(f"- Minimum detectable effect: {mde:.2%}")
        st.markdown(f"- Significance level (α): {alpha}")
        st.markdown(f"- Statistical power: {power}")
        st.markdown(f"- Traffic allocation: {traffic_split:.0%} to each variant")
        
        # Plot scenarios
        fig = plot_scenarios(scenarios_df)
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("### Scenario Explanations:")
        st.markdown("""
        - **Baseline**: The scenario with the parameters you specified.
        - **MDE 0.5x, 1.5x, 2x**: How sample size and duration change if the Minimum Detectable Effect is half, 1.5 times, or double the specified value.
        - **Alpha 0.1, 0.01**: The effect of changing the significance level to 10% or 1%.
        - **Power 0.7, 0.9**: The impact of changing the statistical power to 70% or 90%.
        """)
        
        st.warning("Note: These scenarios illustrate how different parameters affect the required sample size and test duration. Consider these trade-offs when planning your A/B test.")

        # Add option to download the scenario data
        csv = scenarios_df.to_csv(index=False)
        st.download_button(
            label="Download Scenario Data",
            data=csv,
            file_name="ab_test_scenarios.csv",
            mime="text/csv",
        )