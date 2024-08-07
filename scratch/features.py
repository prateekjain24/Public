import streamlit as st
import os
from storage import create_data_prd, create_record, read_records, delete_record, create_data_brainstorm
import scipy.stats as stats
import numpy as np
import pandas as pd

prd_table = os.environ.get('SUPABASE_TABLE')
brainstorm_table = os.environ.get('SUPABASE_BRAINTORM_TABLE')

def create_prd(system_prompt_prd, system_prompt_director, llm_model, fast_llm_model, supabase):
    """
    Create a new PRD (Product Requirements Document).

    Args:
        system_prompt_prd (str): The system prompt for generating the PRD.
        system_prompt_director (str): The system prompt for critiquing the PRD.
        llm_model: The language model used for generating the PRD.
        fast_llm_model: The fast language model used for generating the PRD.
        supabase: The Supabase client for saving the PRD to the database.

    Returns:
        None
    """
    st.subheader("Create New PRD")
    product_name = st.text_input("#### Product Name", placeholder="Enter the product name here")
    product_description = st.text_area("#### Product Description", placeholder="Describe the product here. Use bullet points where possible", height=400)
    generate_button = st.button("Generate PRD", type="primary")
    status_message = "PRD generation in progress..."

    if generate_button:
        if not product_name or not product_description:
            st.warning("Please fill in both the product name and description.")
        else:
            with st.spinner(status_message):
                try:
                    llm_model.system_prompt = system_prompt_prd
                    draft_prd, input_tokens, output_tokens = llm_model.generate_text(
                        prompt=f"Generate a PRD for a product named {product_name} with the following description: {product_description}. Only respond with the PRD and in Markdown format. BE DETAILED. If you think user is not asking for PRD return nothing."
                    )
                    critique_rounds = 2  # Set the number of critique rounds
                    for round in range(critique_rounds):
                        st.session_state['history'].append({'role': 'user', 'content': draft_prd})
                        status_message = f"Draft PRD Done. Reviewing it...Round {round+1} of {critique_rounds}"
                        st.info(status_message)
                        llm_model.system_prompt = system_prompt_director
                        critique_response, input_tokens, output_tokens = llm_model.generate_text(
                            prompt=f"Critique the PRD: {draft_prd}. It was generated by PM who was given these instructions: \n Product named {product_name} \n Product description: {product_description}. Only respond in Markdown format. BE DETAILED. If you think user is not asking for PRD return nothing."
                        )
                        st.session_state['history'].append({'role': 'user', 'content': critique_response})
                        status_message = "Making adjustments.."
                        st.info(status_message)
                        if round != 0:
                            llm_model.system_prompt = system_prompt_prd
                            draft_prd, input_tokens, output_tokens = llm_model.generate_text(
                                prompt=f"Given the Feedback from your manager:{critique_response} \n Improve upon your Draft PRD {draft_prd}. \n Only respond with the PRD and in Markdown format. BE VERY DETAILED. If you think user is not asking for PRD return nothing."
                            )
                        else:
                            fast_llm_model.system_prompt = system_prompt_prd
                            draft_prd, input_tokens, output_tokens = fast_llm_model.generate_text(
                                prompt=f"Given the Feedback from your manager:{critique_response} \n Improve upon your Draft PRD {draft_prd}. \n Only respond with the PRD and in Markdown format. BE VERY DETAILED. If you think user is not asking for PRD return nothing."
                            )
                    st.markdown(draft_prd, unsafe_allow_html=True)
                    st.session_state['history'].append({'role': 'user', 'content': draft_prd})
                    data = create_data_prd(st.session_state['user']['email'], product_name, product_description, draft_prd, True)
                    try:
                        create_record(prd_table, data, supabase)
                    except Exception as e:
                        st.error(f"Failed to save PRD to database. Error: {str(e)}")
                    # Download button for the PRD
                    st.download_button(
                        label="Download PRD as Markdown",
                        data=draft_prd,
                        file_name="Product_Requirements_Document.md",
                        mime="text/markdown"
                    )
                except Exception as e:
                    st.error(f"Failed to generate PRD. Please try again later. Error: {str(e)}")
    pass

def improve_prd(system_prompt_prd, system_prompt_director, llm_model, supabase):
    """
    Improves the current Product Requirements Document (PRD) by generating a draft PRD, receiving critique, and making final adjustments.

    Args:
        system_prompt_prd (str): The system prompt for generating the draft PRD.
        system_prompt_director (str): The system prompt for critiquing the PRD.
        llm_model: The language model used for text generation.
        supabase: The Supabase client used for database operations.

    Returns:
        None
    """
    st.subheader("Improve Current PRD")
    prd_text = st.text_area("#### Enter your PRD here", placeholder="Paste your PRD here to improve it", height=400)
    improve_button = st.button("Improve PRD", type="primary")

    if improve_button:
        if not prd_text:
            st.warning("Please enter a PRD text to improve.")
        else:
            with st.spinner('Improving PRD...'):
                try:
                    llm_model.system_prompt = f"You are a meticulous editor for improving product documents. {system_prompt_prd}. If you think user is not sharing the PRD return nothing."
                    draft_prd, input_tokens, output_tokens = llm_model.generate_text(
                        prompt=f"Improve the following PRD: {prd_text}"
                    )
                    st.session_state['history'].append({'role': 'user', 'content': draft_prd})
                    status_message = "Draft PRD Done. Reviewing it..."
                    st.info(status_message)
                    llm_model.system_prompt = system_prompt_director
                    critique_response, input_tokens, output_tokens = llm_model.generate_text(
                        prompt=f"Critique the PRD: {draft_prd}. Only respond in Markdown format. BE DETAILED. If you think user is not asking for PRD return nothing."
                    )
                    st.session_state['history'].append({'role': 'user', 'content': critique_response})
                    status_message = "Making final adjustments.."
                    st.info(status_message)
                    llm_model.system_prompt = system_prompt_prd
                    response, input_tokens, output_tokens = llm_model.generate_text(
                        prompt=f"Given the Feedback from your manager:{critique_response} \n Improve upon your Draft PRD {draft_prd}. \n Only respond with the PRD and in Markdown format. BE VERY DETAILED. If you think user is not asking for PRD return nothing."
                    )
                    st.markdown(response, unsafe_allow_html=True)
                    st.session_state['history'].append({'role': 'user', 'content': response})
                    data = create_data_prd(st.session_state['user']['email'], "Improve PRD", prd_text, response, False)
                    try:
                        create_record(prd_table, data, supabase)
                    except Exception as e:
                        st.error(f"Failed to save PRD to database. Error: {str(e)}")
                    # Download button for the PRD
                    st.download_button(
                        label="Download PRD as Markdown",
                        data=response,
                        file_name="Product_Requirements_Document.md",
                        mime="text/markdown"
                    )
                except Exception as e:
                    st.error(f"Failed to improve PRD. Please try again later. Error: {str(e)}")
    pass

def brainstorm_features(system_prompt_brainstorm,llm_model,supabase):
    """
    This function allows the user to interact with an AI model to brainstorm ideas on a given topic.
    Parameters:
    system_prompt_brainstorm (str): A predefined system prompt for generating a response.
    llm_model (llm.OpenAI): An initialized LLM model.
    Returns:
    None
    Usage:
    ```python
    brainstorm_features(system_prompt_brainstorm, llm_model)
    ```
    The function initializes a chat history if it doesn't already exist. It then displays chat messages from the history on app rerun. The function reacts to user input by displaying the user message in a chat message container, adding the user message to the chat history, and generating an assistant response using the provided LLM model. The assistant response is then displayed in a chat message container and added to the chat history.
    """
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # React to user input
    if prompt := st.chat_input("What  would you like to brainstorm on today?"):
        # Display user message in chat message container
        st.chat_message("user").markdown(prompt)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        data = create_data_brainstorm(st.session_state['user']['email'], prompt, True)
        try:
            create_record(brainstorm_table, data, supabase)
        except Exception as e:
            st.error(f"Failed to save brainstorm message from user to database. Error: {str(e)}")
        context = st.session_state.messages[-6:]
        llm_model.system_prompt = system_prompt_brainstorm
        response, input_tokens, output_tokens = llm_model.generate_text(
            prompt = f"User input: {prompt}, Previous Context: {context}"
        )
        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            st.markdown(response)
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})
        data = create_data_brainstorm(st.session_state['user']['email'], response, False)
        try:
            create_record(brainstorm_table, data, supabase)
        except Exception as e:
            st.error(f"Failed to save brainstorm message to database. Error: {str(e)}")
    pass    


def tracking_plan(system_prompt_tracking, user_prompt_tracking, system_prompt_directorDA, llm_model):
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
                        prompt = f"Given the Feedback from your manager:{critique_response} \n Improve upon your draft tracking plan {draft_plan}. \n Only respond with the tracking plan and in Markdown format. BE VERY DETAILED. If you think user is not asking for tracking plan return nothing.",
                        temperature=0.1                    
                    )                                          
                    st.markdown(response, unsafe_allow_html=True)
                    st.session_state['history'].append({'role': 'user', 'content': response})
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

def view_history(supabase):
    """
    View the history of generated PRDs and GTM plans.

    Returns:
        None
    """
    prd_table = os.environ.get('SUPABASE_TABLE')
    st.subheader("View PRD Generation History")
    records = read_records(prd_table, st.session_state['user']['email'], supabase)
    for record in records:
        with st.expander(f"{record['product_name']} - Generated on: {record['created_at']}"):
            st.markdown(record['product_name'])
            st.markdown(record['output'])
            st.download_button(
                label="Download PRD as Markdown",
                data=record['output'],
                file_name=f"prd_{record['product_name']}.md",
                mime="text/markdown",
                key=f"prd_{record['id']}"
            )
    pass

def abc_test_significance(quality_llm, system_prompt_ab_test):
    st.subheader("A/B/C Test Significance Checker")
    
    # Initialize session state for variants if it doesn't exist
    if 'variants' not in st.session_state:
        st.session_state.variants = [
            {'name': 'Control', 'visitors': 1000, 'conversions': 100},
            {'name': 'Treatment 1', 'visitors': 1000, 'conversions': 120}
        ]
    
    # Function to add a new variant
    def add_variant():
        new_name = chr(ord('A') + len(st.session_state.variants))
        st.session_state.variants.append({'name': new_name, 'visitors': 1000, 'conversions': 100})
    
    # Function to remove a variant
    def remove_variant(index):
        if len(st.session_state.variants) > 2:
            del st.session_state.variants[index]
    
    # Function to update variant data
    def update_variant(index, field):
        st.session_state.variants[index][field] = st.session_state[f"{field}_{index}"]
    
    # Display variants
    for i, variant in enumerate(st.session_state.variants):
        col1, col2, col3, col4 = st.columns([3, 3, 3, 1])
        with col1:
            st.text_input("Variant Name", value=variant['name'], key=f"name_{i}", 
                          on_change=update_variant, args=(i, 'name'))
        with col2:
            st.number_input("Visitors", min_value=1, step=1, value=variant['visitors'], key=f"visitors_{i}", 
                            on_change=update_variant, args=(i, 'visitors'))
        with col3:
            st.number_input("Conversions", min_value=0, step=1, value=variant['conversions'], key=f"conversions_{i}", 
                            on_change=update_variant, args=(i, 'conversions'))
        with col4:
            if len(st.session_state.variants) > 2:
                st.button("Remove", key=f"remove_{i}", on_click=remove_variant, args=(i,))
    
    st.button("Add Variant", on_click=add_variant)
    
    st.markdown("### Significance Level")
    st.markdown("The significance level (alpha) is the probability of rejecting the null hypothesis when it is true. "
                "A lower value (e.g., 0.01) means stronger evidence is required to reject the null hypothesis and "
                "declare a significant result, while a higher value (e.g., 0.10) requires less evidence but increases "
                "the risk of a Type I error (false positive).")
    
    significance_level = st.slider("Select Significance Level", min_value=0.01, max_value=0.10, value=0.05, step=0.01)
    
    st.markdown("### Experiment Document (Optional)")
    st.markdown("Provide paste your experiment details/document here for more context-aware interpretation of the test results.")
    prd_text = st.text_area("Experiment Details", height=200, help="Paste your experiment document here (optional).")
    
    if st.button("Calculate Significance"):
        # Prepare data for chi-square test
        observed = np.array([[v['conversions'], v['visitors'] - v['conversions']] for v in st.session_state.variants])
        
        # Perform chi-square test
        chi2, p_value = stats.chi2_contingency(observed)[:2]
        
        # Calculate conversion rates and relative uplifts
        rates = [v['conversions'] / v['visitors'] for v in st.session_state.variants]
        control_rate = rates[0]
        relative_uplifts = [(rate - control_rate) / control_rate * 100 for rate in rates[1:]]
        
        # Display results
        st.markdown("### Results")
        results_df = pd.DataFrame({
            'Variant': [v['name'] for v in st.session_state.variants],
            'Visitors': [v['visitors'] for v in st.session_state.variants],
            'Conversions': [v['conversions'] for v in st.session_state.variants],
            'Conversion Rate': rates
        })
        results_df['Relative Uplift'] = ['N/A'] + [f"{uplift:.2f}%" for uplift in relative_uplifts]
        st.dataframe(results_df)
        
        st.markdown(f"**P-value:** {p_value:.4f}")
        
        if p_value < significance_level:
            st.success(f"The result is statistically significant at the {significance_level:.0%} level.")
        else:
            st.warning(f"The result is not statistically significant at the {significance_level:.0%} level.")
        
        # Generate interpretation using the LLM
        interpretation_prompt = f"""
        Interpret the following A/B/C test results:
        {results_df.to_string()}
        
        P-value: {p_value:.4f}
        Significance Level: {significance_level:.0%}
        
        Product Requirements Document:
        {prd_text if prd_text else "No PRD provided."}
        
        Provide a clear, concise interpretation of these A/B/C test results for a product manager. 
        Include whether the result is statistically significant, what this means practically, 
        and any recommendations or next steps based on these results. If there are multiple variants 
        outperforming the control, discuss which one might be the best choice and why.
        
        If a PRD was provided, incorporate relevant aspects of the product requirements into your interpretation 
        and recommendations. Consider how the test results align with or impact the product goals and features 
        outlined in the PRD.
        """
        
        quality_llm.system_prompt = system_prompt_ab_test
        st.markdown("### AI Interpretation")
        with st.spinner("Generating AI interpretation... This may take a few moments."):
            interpretation, _, _ = quality_llm.generate_text(interpretation_prompt)
        st.markdown(interpretation)