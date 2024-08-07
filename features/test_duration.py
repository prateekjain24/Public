import streamlit as st
import numpy as np
import pandas as pd
from scipy import stats
import plotly.graph_objects as go

def calculate_sample_size(baseline_rate, mde, alpha, power):
    p1 = baseline_rate
    p2 = baseline_rate * (1 + mde)
    
    z_alpha = stats.norm.ppf(1 - alpha / 2)
    z_beta = stats.norm.ppf(power)
    
    pooled_p = (p1 + p2) / 2
    
    n = ((z_alpha * np.sqrt(2 * pooled_p * (1 - pooled_p)) + 
          z_beta * np.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2) / (p2 - p1) ** 2
    
    return int(np.ceil(n))

def estimate_test_duration(sample_size, daily_visitors, traffic_split):
    visitors_per_variant = daily_visitors * traffic_split
    duration_days = np.ceil(sample_size / visitors_per_variant)
    return int(duration_days)

@st.cache_data
def generate_duration_mde_data(baseline_rate, daily_visitors, alpha, power, traffic_splits):
    mde_range = np.linspace(0.05, 0.2, 31)  # 5% to 20% MDE
    data = []
    
    for traffic_split in traffic_splits:
        for mde in mde_range:
            sample_size = calculate_sample_size(baseline_rate, mde, alpha, power)
            duration = estimate_test_duration(sample_size, daily_visitors, traffic_split)
            data.append({
                'MDE': mde * 100,  # Convert to percentage
                'Duration (days)': duration,
                'Traffic Split': f"{traffic_split:.0%}"
            })
    
    return pd.DataFrame(data)

def plot_duration_vs_mde(df):
    fig = go.Figure()
    
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c']  # Blue, Orange, Green
    
    for i, split in enumerate(df['Traffic Split'].unique()):
        split_data = df[df['Traffic Split'] == split]
        fig.add_trace(go.Scatter(
            x=split_data['MDE'],
            y=np.minimum(split_data['Duration (days)'], 90),  # Cap at 90 days
            mode='lines+markers',
            name=f"{split} Traffic",
            line=dict(color=colors[i], width=2),
            marker=dict(size=6, symbol='circle')
        ))
    
    fig.update_layout(
        title='Test Duration vs. Minimum Detectable Effect (MDE)',
        xaxis_title='Minimum Detectable Effect (%)',
        yaxis_title='Test Duration (Days)',
        legend_title='Traffic Split',
        hovermode="x unified",
        plot_bgcolor='white',
        xaxis=dict(
            tickmode='array',
            tickvals=[5, 10, 15, 20],
            ticktext=['5%', '10%', '15%', '20%'],
            gridcolor='lightgray',
            minor_gridcolor='lightgray',
            minor_ticks='inside'
        ),
        yaxis=dict(
            range=[0, 90],
            tickmode='linear',
            dtick=10,
            gridcolor='lightgray',
            minor_gridcolor='lightgray',
            minor_ticks='inside'
        )
    )
    
    fig.update_traces(hovertemplate='MDE: %{x:.1f}%<br>Duration: %{y:.0f} days')
    
    # Add annotations for key points
    mde_points = [5, 10, 15]
    for mde in mde_points:
        for i, split in enumerate(df['Traffic Split'].unique()):
            split_data = df[df['Traffic Split'] == split]
            duration = split_data[split_data['MDE'].round(1) == mde]['Duration (days)'].values[0]
            if duration <= 90:
                fig.add_annotation(
                    x=mde,
                    y=duration,
                    text=f"{duration:.0f}d",
                    showarrow=False,
                    yshift=10,
                    font=dict(size=8, color=colors[i])
                )
    
    return fig

def ab_test_duration_calculator():
    st.subheader("A/B Test Duration Calculator")
    
    st.markdown("""
    ### Key Terms:
    - **Baseline Conversion Rate**: The current conversion rate of your product or feature.
    - **Minimum Detectable Effect (MDE)**: The smallest improvement you want to be able to detect in your A/B test. E.g. If your baseline conversion is 5% & MDE is 10%, then you're aiming to detect a minimum absolute improvement of 0.5 percentage points (to 5.5%) or greater.
    - **Significance Level**: The probability of detecting an effect that is not actually present (Type I error or false positive).
    - **Statistical Power**: The probability of detecting an effect that is actually present (1 - Type II error rate).
    - **Traffic Split**: The proportion of traffic allocated to each variant in the test.
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        baseline_rate = st.slider("Baseline Conversion Rate (%)", 0.1, 50.0, 5.0, 0.1) / 100
        st.info("This is your current conversion rate. For example, if 5% of visitors convert, enter 5.0.")
        
        daily_visitors = st.number_input("Total Daily Visitors", min_value=10, value=1000, step=10)
        st.info("The average number of visitors your product or feature receives per day.")
    
    with col2:
        alpha = st.slider("Significance Level", 0.01, 0.1, 0.05, 0.01, format="%.2f")
        st.info("""
        Common values are 0.05 (5%) or 0.01 (1%). A lower value means stricter criteria for statistical significance,
        reducing false positives but potentially increasing false negatives.
        """)
        
        power = st.selectbox("Statistical Power", [0.7, 0.8, 0.9], index=1)
        st.info("""
        Common values are 0.8 (80%) or 0.9 (90%). Higher power increases the chance of detecting a true effect,
        but also increases the required sample size.
        """)
    
    traffic_splits = [0.1, 0.2, 0.5]
    
    df = generate_duration_mde_data(baseline_rate, daily_visitors, alpha, power, traffic_splits)
    
    fig = plot_duration_vs_mde(df)
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("### How to use this chart:")
    st.markdown("""
    1. The x-axis shows the Minimum Detectable Effect (MDE) from 5% to 20%.
    2. The y-axis shows the required test duration in days, capped at 90 days.
    3. Different lines represent different traffic allocation splits between control and variant.
    4. Hover over the lines to see exact values for MDE and duration.
    5. Annotations show test duration for key MDE points (5%, 10%, 15%).
    6. Adjust the significance level slider to see how it affects the test duration in real-time.
    """)
    
    st.markdown("### Key Insights:")
    st.markdown("""
    - Smaller MDEs require longer test durations to achieve statistical significance.
    - Allocating more traffic to the test (higher percentages) reduces the required duration.
    - There's a clear trade-off between test sensitivity (lower MDE) and test duration.
    - Changing the significance level affects the required test duration. A stricter (lower) significance level 
      increases the test duration but reduces the chance of false positives.
    - The impact of traffic allocation is more pronounced for smaller MDEs.
    """)
    
    st.markdown("### Next Steps:")
    st.markdown("""
    1. Decide on your desired MDE based on what improvement would be meaningful for your product.
       Consider both statistical and practical significance.
    2. Choose a traffic allocation that balances test duration with your ability to handle potential negative impacts.
       Higher allocations lead to faster tests but expose more users to potential negative effects.
    3. If the test duration is too long, consider ways to increase your daily traffic, accept a larger MDE,
       or adjust your significance level and power.
    4. Adjust the significance level based on your tolerance for false positives vs. false negatives.
       A lower significance level (e.g., 0.01) reduces false positives but may increase false negatives and test duration.
    5. Consider the trade-offs between statistical rigor (high power, low significance level) and practical constraints 
       (test duration, traffic allocation) when designing your A/B test.
    """)

    # Add option to download the data
    csv = df.to_csv(index=False)
    st.download_button(
        label="Download Data",
        data=csv,
        file_name="ab_test_duration_mde_data.csv",
        mime="text/csv",
    )