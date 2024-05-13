import streamlit as st
from models import build_models
from utils import load_data, download_audio
from models import transcribe_audio

def create_prd(system_prompt_prd,system_prompt_director, llm_model, fast_llm_model):
    """
    Generate a new Product Requirements Document (PRD) based on the provided information.
    Parameters:
        system_prompt_prd (str): A predefined system prompt for generating a PRD.
        system_prompt_director (str): A predefined system prompt for generating a PRD based on a director's input.
        llm_model (llm.OpenAI): An initialized LLM model.
    Returns:
        str: The generated PRD.
    Raises:
        ValueError: If the product name or description is not provided.
    """

    st.subheader("Create New PRD")
    product_name = st.text_input("Product Name", placeholder="Enter the product name here")
    product_description = st.text_area("Product Description", placeholder="Describe the product here. Use bullet points where possible")
    generate_button = st.button("Generate PRD")
    status_message = "PRD generation in progress..."

    if generate_button:
        if not product_name or not product_description:
            st.warning("Please fill in both the product name and description.")
        else:
            with st.spinner(status_message):
                try:
                    draft_prd = llm_model.prompt(
                        f"Generate a PRD for a product named {product_name} with the following description: {product_description}. Only respond with the PRD and in Markdown format. BE DETAILED. If you think user is not asking for PRD return nothing.",
                            system=system_prompt_prd
                    )
                    st.session_state['history'].append({'role': 'user', 'content': draft_prd.text()})
                    
                    critique_rounds = 2  # Set the number of critique rounds
                    for round in range(critique_rounds):
                        status_message = f"Draft PRD Done. Reviewing it...Round {round+1} of Round {critique_rounds}"
                        st.info(status_message)
                        critique_response = llm_model.prompt(
                            f"Critique the PRD: {draft_prd.text()}. It was generated by PM who was given these instructions: \n Product named {product_name} \n Product description: {product_description}. Only respond in Markdown format. BE DETAILED. If you think user is not asking for PRD return nothing.",
                                system=system_prompt_director
                        )
                        st.session_state['history'].append({'role': 'user', 'content': critique_response.text()})
                        status_message = "Making adjustments.."
                        st.info(status_message)
                        draft_prd = llm_model.prompt(
                            f"Given the Feedback from your manager:{critique_response.text()} \n Improve upon your Draft PRD {draft_prd.text()}. \n Only respond with the PRD and in Markdown format. BE VERY DETAILED. If you think user is not asking for PRD return nothing.",
                                system=system_prompt_prd
                        )
                    
                    st.markdown(draft_prd.text(), unsafe_allow_html=True)
                    st.session_state['history'].append({'role': 'user', 'content': draft_prd.text()})
                    # Download button for the PRD
                    st.download_button(
                        label="Download PRD as Markdown",
                        data=draft_prd.text(),
                        file_name="Product_Requirements_Document.md",
                        mime="text/markdown"
                    )
                except Exception as e:
                    st.error(f"Failed to generate PRD. Please try again later. Error: {str(e)}")
    pass

def improve_prd(system_prompt_prd,system_prompt_director,llm_model):
    """
    Improve the provided Product Requirements Document (PRD) using GPT-4-turbo.
    Parameters:
        system_prompt_prd (str): A predefined system prompt for generating a PRD.
        system_prompt_director (str): A predefined system prompt for generating a PRD based on a director's input.
        llm_model (llm.OpenAI): An initialized LLM model.
    Returns:
        str: The improved PRD.
    Raises:
        ValueError: If no PRD text is provided.
        Exception: If there is an error while improving the PRD.
    """
    st.subheader("Improve Current PRD")
    prd_text = st.text_area("Enter your PRD here", placeholder="Paste your PRD here to improve it")
    improve_button = st.button("Improve PRD")

    if improve_button:
        if not prd_text:
            st.warning("Please enter a PRD text to improve.")
        else:
            with st.spinner('Improving PRD...'):
                try:
                    draft_prd = llm_model.prompt(
                        f"Improve the following PRD: {prd_text}",
                            system=f"You are a meticulous editor for improving product documents. {system_prompt_prd}. If you think user is not sharing the PRD return nothing."
                    )
                    st.session_state['history'].append({'role': 'user', 'content': draft_prd.text()})
                    status_message = "Draft PRD Done. Reviewing it..."
                    st.info(status_message)
                    critique_response = llm_model.prompt(
                        f"Critique the PRD: {draft_prd.text()}. Only respond in Markdown format. BE DETAILED. If you think user is not asking for PRD return nothing.",
                            system=system_prompt_director
                    )
                    st.session_state['history'].append({'role': 'user', 'content': critique_response.text()})
                    status_message = "Making final adjustments.."
                    st.info(status_message)
                    response = llm_model.prompt(
                        f"Given the Feedback from your manager:{critique_response.text()} \n Improve upon your Draft PRD {draft_prd.text()}. \n Only respond with the PRD and in Markdown format. BE VERY DETAILED. If you think user is not asking for PRD return nothing.",
                            system=system_prompt_prd
                    )                                          
                    st.markdown(response, unsafe_allow_html=True)
                    st.session_state['history'].append({'role': 'user', 'content': response})
                    # Download button for the PRD
                    st.download_button(
                        label="Download PRD as Markdown",
                        data=response.text(),
                        file_name="Product_Requirements_Document.md",
                        mime="text/markdown"
                    )                       
                except Exception as e:
                    st.error(f"Failed to improve PRD. Please try again later. Error: {str(e)}")
    pass               

def brainstorm_features(system_prompt_brainstorm,llm_model):
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
        context = st.session_state.messages[-6:]
        response = llm_model.prompt(
                        f"User input: {prompt}, Previous Context: {context}",
                        system=system_prompt_brainstorm
                    )
        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            st.markdown(response)
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})
    pass    

def view_history():
    """
    View the history of all the interactions with the assistant.
    Returns:
        None
    """
    st.subheader("View History")
    if st.session_state['history']:
        for item in st.session_state['history']:
            st.json(item)
    else:
        st.info("No history available yet.")
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
    feature_name = st.text_input("Feature Name", placeholder="Enter the feature/product name here")
    customer_name = st.selectbox("Choose the customer type", ("Property Agents", "Poperty Seekers"))
    other_details = st.text_input("Addition Details", placeholder="Share any details that will be helpful with tracking plan")
    prd_text = st.text_area("Enter your PRD here", placeholder="Paste your PRD here to improve it")
    tracking_button = st.button("Generate Tracking")

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
                    draft_plan = llm_model.prompt(
                        user_prompt, system=system_prompt_tracking, temperature=0.2 
                    )
                    st.session_state['history'].append({'role': 'user', 'content': draft_plan.text()})
                    status_message = "Draft tracking Done. Reviewing the plan..."
                    st.info(status_message)
                    critique_response = llm_model.prompt(
                        f"Critique the Tracking Plan: {draft_plan.text()}. Only respond in Markdown format. BE DETAILED. If you think user is not asking for tracking plan return nothing.\n Context: ### PRD \n {prd_text} \n ### Feature Name \n {feature_name} \n ### Additional Details \n {other_details} ",
                            system=system_prompt_directorDA, temperature=0.3
                    )
                    st.session_state['history'].append({'role': 'user', 'content': critique_response.text()})
                    status_message = "Making final adjustments.."
                    st.info(status_message)
                    response = llm_model.prompt(
                        f"Given the Feedback from your manager:{critique_response.text()} \n Improve upon your draft tracking plan {draft_plan.text()}. \n Only respond with the tracking plan and in Markdown format. BE VERY DETAILED. If you think user is not asking for tracking plan return nothing.",
                            system=system_prompt_tracking, temperature=0.1                    
                        )                                          
                    st.markdown(response.text(), unsafe_allow_html=True)
                    st.session_state['history'].append({'role': 'user', 'content': response})
                    # Download button for the plan
                    st.download_button(
                        label="Download PRD as Markdown",
                        data=response.text(),
                        file_name="tracking_plan.md",
                        mime="text/markdown"
                    )                       
                except Exception as e:
                    st.error(f"Failed to generate tracking plan. Please try again later. Error: {str(e)}")
    pass 

def summarize_yt(system_prompt_yt_planner, prompt_yt_summary,llm_model):

    st.title("YouTube Audio Processor")
    youtube_url = st.text_input("Enter YouTube URL (not more then 15 mins)")

    if st.button("Process Audio"):
        if youtube_url:
            with st.spinner('Downloading and processing audio...'):
                audio_path = download_audio(youtube_url)
                if audio_path:
                    transcription = transcribe_audio(audio_path)
                    if transcription:
                        yt_plan = llm_model.prompt(
                            transcription, system=system_prompt_yt_planner, temperature=0.2 
                        )
                        st.session_state['history'].append({'role': 'user', 'content': yt_plan.text()})
                        status_message = "Planning done..."
                        st.info(status_message)
                        yt_execute = llm_model.prompt(
                            f"Given the Summarisation Plan: {yt_plan.text()}, Summarize the yourtube transcript {transcription}. Only respond in Markdown format. BE VERY DETAILED.",
                                system=prompt_yt_summary, temperature=0.3
                        )
                        st.session_state['history'].append({'role': 'user', 'content': yt_execute.text()})                                      
                        st.markdown(yt_execute, unsafe_allow_html=True)
                        # Download button for the summary
                        st.download_button(
                            label="Download PRD as Markdown",
                            data=yt_execute.text(),
                            file_name="yt_summary.md",
                            mime="text/markdown"
                        )    
                    else:
                        st.error("Transcription failed.")
                else:
                    st.error("Audio download failed.")
        else:
            st.warning("Please enter a valid YouTube URL.")
    pass