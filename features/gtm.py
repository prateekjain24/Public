import streamlit as st
from storage.supabase_client import create_record, read_records
from utils.data_loading import create_data_prd
import os

def gtm_planner(system_prompt_GTM, system_prompt_GTM_critique, fast_llm_model, llm_model):
    """
    Generate GTM (Go-To-Market) Plan.

    Args:
        system_prompt_GTM (str): The system prompt for generating the initial GTM plan.
        system_prompt_GTM_critique (str): The system prompt for critiquing the GTM plan.
        fast_llm_model: The fast language model used for generating text.
        llm_model: The language model used for generating text.

    Returns:
        None
    """
    st.subheader("Generate GTM Plan")
    prd_text = st.text_area("#### Enter your PRD here", placeholder="Paste your PRD here to generate GTM plan", height=400)
    other_details = st.text_area("#### Addition Details", placeholder="Share any details that will be helpful with GTM planning", height=200)
    tracking_button = st.button("Generate GTM Plan", type="primary")

    if tracking_button:
        if not prd_text:
            st.warning("Please enter all the details")
        else:
            with st.spinner('Generating Plan...'):
                try:
                    user_prompt = f"Generate the Go To Market Plan for: \n ## Product Requirements Document \n {prd_text} \n ## Other Details \n {other_details} \n RESPOND in Markdown Only."
                    fast_llm_model.system_prompt = system_prompt_GTM
                    response, input_tokens, output_tokens = fast_llm_model.generate_text(
                        prompt=user_prompt, temperature=0.4
                    )
                    st.markdown(response, unsafe_allow_html=True)
                    st.session_state['history'].append({'role': 'user', 'content': response})
                    # Download button for the plan
                    st.download_button(
                        label="Download GTM Plan as Markdown",
                        data=response,
                        file_name="gtm_plan.md",
                        mime="text/markdown"
                    )
                except Exception as e:
                    st.error(f"Failed to generate GTM plan. Please try again later. Error: {str(e)}")
    pass