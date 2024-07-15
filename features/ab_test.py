import streamlit as st
import numpy as np
import pandas as pd
from scipy import stats
import plotly.graph_objects as go

def calculate_significance(control, variation):
    """
    Calculate statistical significance between control and variation.
    
    Args:
    control (dict): Dictionary containing 'visitors' and 'conversions' for control group
    variation (dict): Dictionary containing 'visitors' and 'conversions' for variation group
    
    Returns:
    float: p-value of the test
    """
    control_rate = control['conversions'] / control['visitors']
    variation_rate = variation['conversions'] / variation['visitors']
    
    pooled_se = np.sqrt(control_rate * (1 - control_rate) / control['visitors'] + 
                        variation_rate * (1 - variation_rate) / variation['visitors'])
    z_score = (variation_rate - control_rate) / pooled_se
    p_value = 2 * (1 - stats.norm.cdf(abs(z_score)))
    
    return p_value

def calculate_relative_uplift(control_rate, variation_rate):
    """Calculate relative uplift between control and variation."""
    return (variation_rate - control_rate) / control_rate * 100

def plot_results(results_df):
    """Create a bar plot of conversion rates."""
    fig = go.Figure(data=[
        go.Bar(name='Conversion Rate', x=results_df['Variant'], y=results_df['Conversion Rate']),
    ])
    fig.update_layout(title='Conversion Rates by Variant', yaxis_title='Conversion Rate')
    return fig

def abc_test_significance(quality_llm, system_prompt_ab_test):
    st.subheader("A/B/C Test Significance Checker")
    
    # Initialize session state for variants if it doesn't exist
    if 'variants' not in st.session_state:
        st.session_state.variants = [
            {'name': 'Control', 'visitors': 1000, 'conversions': 100},
            {'name': 'Variation A', 'visitors': 1000, 'conversions': 120}
        ]
    
    # Function to add a new variant
    def add_variant():
        new_name = f"Variation {chr(ord('A') + len(st.session_state.variants) - 1)}"
        st.session_state.variants.append({'name': new_name, 'visitors': 1000, 'conversions': 100})
    
    # Function to remove a variant
    def remove_variant(index):
        if len(st.session_state.variants) > 2:
            del st.session_state.variants[index]
    
    # Display variants
    for i, variant in enumerate(st.session_state.variants):
        col1, col2, col3, col4 = st.columns([3, 3, 3, 1])
        with col1:
            variant['name'] = st.text_input("Variant Name", value=variant['name'], key=f"name_{i}")
        with col2:
            variant['visitors'] = st.number_input("Visitors", min_value=1, value=variant['visitors'], key=f"visitors_{i}")
        with col3:
            variant['conversions'] = st.number_input("Conversions", min_value=0, max_value=variant['visitors'], value=min(variant['conversions'], variant['visitors']), key=f"conversions_{i}")
        with col4:
            if len(st.session_state.variants) > 2:
                st.button("Remove", key=f"remove_{i}", on_click=remove_variant, args=(i,))
    
    st.button("Add Variant", on_click=add_variant)
    
    significance_level = st.slider("Select Significance Level", min_value=0.01, max_value=0.10, value=0.05, step=0.01)
    
    prd_text = st.text_area("Experiment Details (Optional)", height=200, help="Paste your experiment document here for more context-aware interpretation of the test results.")
    
    if st.button("Calculate Significance"):
        control = st.session_state.variants[0]
        results = []
        p_values = []
        
        for variant in st.session_state.variants[1:]:
            p_value = calculate_significance(control, variant)
            p_values.append(p_value)
            
            control_rate = control['conversions'] / control['visitors']
            variant_rate = variant['conversions'] / variant['visitors']
            relative_uplift = calculate_relative_uplift(control_rate, variant_rate)
            
            results.append({
                'Variant': variant['name'],
                'Visitors': variant['visitors'],
                'Conversions': variant['conversions'],
                'Conversion Rate': variant_rate,
                'Relative Uplift': f"{relative_uplift:.2f}%",
                'P-value': p_value,
                'Significant': 'Yes' if p_value < significance_level else 'No'
            })
        
        # Add control to results
        results.insert(0, {
            'Variant': control['name'],
            'Visitors': control['visitors'],
            'Conversions': control['conversions'],
            'Conversion Rate': control['conversions'] / control['visitors'],
            'Relative Uplift': 'N/A',
            'P-value': 'N/A',
            'Significant': 'N/A'
        })
        
        results_df = pd.DataFrame(results)
        st.dataframe(results_df)
        
        # Plot results
        fig = plot_results(results_df)
        st.plotly_chart(fig)
        
        # Overall test result
        if any(p < significance_level for p in p_values):
            st.success(f"At least one variation is statistically significant at the {significance_level:.0%} level.")
        else:
            st.warning(f"No variations are statistically significant at the {significance_level:.0%} level.")
        
        # Generate interpretation using the LLM
        interpretation_prompt = f"""
        Interpret the following A/B/C test results:
        {results_df.to_string()}
        
        Significance Level: {significance_level:.0%}
        
        Experiment Details:
        {prd_text if prd_text else "No experiment details provided."}
        
        Provide a clear, concise interpretation of these A/B/C test results for a product manager. 
        Include whether any results are statistically significant, what this means practically, 
        and any recommendations or next steps based on these results. If there are multiple variants 
        outperforming the control, discuss which one might be the best choice and why.
        
        If experiment details were provided, incorporate relevant aspects into your interpretation 
        and recommendations. Consider how the test results align with or impact the product goals and features 
        outlined in the experiment details.
        """
        
        quality_llm.system_prompt = system_prompt_ab_test
        st.markdown("### AI Interpretation")
        with st.spinner("Generating AI interpretation... This may take a few moments."):
            interpretation, _, _ = quality_llm.generate_text(interpretation_prompt)
        st.markdown(interpretation)