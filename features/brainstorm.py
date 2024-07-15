import streamlit as st
from storage.supabase_client import create_record
from utils.data_loading import create_data_brainstorm
import os

brainstorm_table = os.environ.get('SUPABASE_BRAINTORM_TABLE')

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
