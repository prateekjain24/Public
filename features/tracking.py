import streamlit as st
from storage.supabase_client import create_record, read_records
from utils.data_loading import create_tracking_plan
import os

tracking_table = os.environ.get('SUPABASE_TRACKING_TABLE')
def tracking_plan(system_prompt_tracking, user_prompt_tracking, system_prompt_directorDA, llm_model, supabase):
    """
    Generate a tracking plan for a given feature, customer type, additional details, and PRD text.

    Parameters:
    system_prompt_tracking (str): A predefined system prompt for generating a tracking plan.
    user_prompt_tracking (str): A predefined user prompt for generating a tracking plan.
    system_prompt_directorDA (str): A predefined system prompt for generating a tracking plan based on a director's input.
    llm_model (llm.OpenAI): An initialized LLM model.

    Returns:
    str: The generated tracking plan in Markdown format.

    Raises:
    ValueError: If no PRD text is provided.
    Exception: If there is an error while generating the tracking plan.

    Usage:
    ```python
    tracking_plan(system_prompt_tracking, user_prompt_tracking, system_prompt_directorDA, llm_model)
    ```
    """
    st.subheader("Generate Tracking Plan")
    feature_name = st.text_input("#### Feature Name", placeholder="Enter the feature/product name here")
    customer_name = st.selectbox("#### Choose the customer type", ("Property Agents", "Poperty Seekers"))
    other_details = st.text_input("#### Addition Details", placeholder="Share any details that will be helpful with tracking plan")
    prd_text = st.text_area("#### Enter your PRD here", placeholder="Paste your PRD here to improve it", height = 400)
    tracking_button = st.button("Generate Tracking", type="primary")

    if tracking_button:
        if not prd_text:
            st.warning("Please enter a all the details")
        else:
            with st.spinner('Generating Plan...'):
                try:
                    user_prompt = user_prompt_tracking.replace("{feature}", feature_name)
                    user_prompt = user_prompt.replace("{customer}", customer_name)
                    user_prompt = user_prompt.replace("{details}", other_details)
                    user_prompt = user_prompt.replace("{prd}", prd_text)
                    llm_model.system_prompt = system_prompt_tracking
                    draft_plan, input_tokens, output_tokens = llm_model.generate_text(
                        prompt = user_prompt, temperature=0.2 
                    )
                    st.session_state['history'].append({'role': 'user', 'content': draft_plan})
                    status_message = "Draft tracking Done. Reviewing the plan..."
                    st.info(status_message)
                    llm_model.system_prompt = system_prompt_directorDA
                    critique_response, input_tokens, output_tokens = llm_model.generate_text(
                        prompt = f"Critique the Tracking Plan: {draft_plan}. Only respond in Markdown format. BE DETAILED. If you think user is not asking for tracking plan return nothing.\n Context: ### PRD \n {prd_text} \n ### Feature Name \n {feature_name} \n ### Additional Details \n {other_details} ",
                        temperature=0.3
                    )
                    st.session_state['history'].append({'role': 'user', 'content': critique_response})
                    status_message = "Making final adjustments.."
                    st.info(status_message)
                    llm_model.system_prompt = system_prompt_tracking
                    response, input_tokens, output_tokens = llm_model.generate_text(
                        prompt = f"Given the Feedback from your manager:{critique_response} \n Improve upon your draft tracking plan {draft_plan}. \n Only respond with the tracking plan and in Markdown. BE VERY DETAILED. If you think user is not asking for tracking plan return nothing.",
                        temperature=0.1                    
                    )                                          
                    st.markdown(response, unsafe_allow_html=True)
                    st.session_state['history'].append({'role': 'user', 'content': response})
                    # save the data
                    data = create_tracking_plan(st.session_state['user']['email'], feature_name, customer_name, other_details, prd_text,response)
                    try:
                        create_record(tracking_table, data, supabase)
                    except Exception as e:
                        st.error(f"Failed to save PRD to database. Error: {str(e)}")
                    # Download button for the plan
                    st.download_button(
                        label="Download Tracking Plan as Markdown",
                        data=response,
                        file_name="tracking_plan.md",
                        mime="text/markdown"
                    )                       
                except Exception as e:
                    st.error(f"Failed to generate tracking plan. Please try again later. Error: {str(e)}")
    pass 