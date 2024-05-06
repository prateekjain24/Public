import streamlit as st
from models import build_models
from utils import load_data

def create_prd(system_prompt_prd,system_prompt_director, llm_model):
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
                    #os.write(1, f"Name:{product_name} \n {product_description}")
                    st.session_state['history'].append({'role': 'user', 'content': draft_prd.text()})
                    status_message = "Draft PRD Done. Reviewing it..."
                    st.info(status_message)
                    critique_response = llm_model.prompt(
                        f"Critique the PRD: {draft_prd.text()}. It was generated by PM who was given these instructions: \n Product named {product_name} \n Product description: {product_description}. Only respond in Markdown format. BE DETAILED. If you think user is not asking for PRD return nothing.",
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
                    st.session_state['history'].append({'role': 'user', 'content': response.text()})
                    # Download button for the PRD
                    st.download_button(
                        label="Download PRD as Markdown",
                        data=response.text(),
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
    st.subheader("View History")
    if st.session_state['history']:
        for item in st.session_state['history']:
            st.json(item)
    else:
        st.info("No history available yet.")
    pass
