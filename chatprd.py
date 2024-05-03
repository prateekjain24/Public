import streamlit as st
from openai import OpenAI
#from dotenv import load_dotenv
import llm
import os
#load_dotenv()
# Set up the OpenAI API client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Setting a hardcoded password for auth
PASSWORD = os.getenv('PASSWORD')

# Using Streamlit's session state to store the authentication status
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

def authenticate_user(password):
    if password == PASSWORD:
        st.session_state['authenticated'] = True
    else:
        st.error("Incorrect password, please try again.")

# Using Streamlit's session state to store temporary memory
if 'history' not in st.session_state:
    st.session_state['history'] = []

def build_models():
    """
    Builds and initializes the GPT-3.5-turbo and GPT-4-turbo models.

    Returns:
    tuple: A tuple containing the initialized GPT-3.5-turbo and GPT-4-turbo models.

    Raises:
    ValueError: If the OPENAI_API_KEY environment variable is not set.
    """
    gpt3_model = llm.get_model("gpt-3.5-turbo")
    gpt3_model.key = os.getenv("OPENAI_API_KEY")

    gpt4_model = llm.get_model("gpt-4-turbo")
    gpt4_model.key = os.getenv("OPENAI_API_KEY")

    return gpt3_model, gpt4_model

def create_prd():
    """
    Generate a new Product Requirements Document (PRD) based on the provided information.

    Parameters:
    product_name (str): The name of the product.
    product_description (str): A description of the product.

    Returns:
    str: The generated PRD.

    Raises:
    ValueError: If the product name or description is not provided.
    """
    system_prompt = """
    You are a Senior Product Manager working for PropertyGuru. Your language is engaging but uses Simple english & No Buzz words.  Given the objective, create a detailed PRD. The PRD should outline the problem, propose a solution, and include specific sections such as goals, user stories, user experience flow, success metrics, technical considerations, and milestones. Follow the structure provided below:

    ### PRD Outline for KYC Feature with OTP Verified Login

    #### tl;dr

    Provide a brief overview of the feature, emphasizing the introduction of a secure, OTP verified mobile login to enhance KYC compliance and ensure a frictionless yet secure user authentication process.

    #### Goals

    Divide the goals into Business Goals and User Goals, detailing how the feature will increase security, comply with regulations, and improve user satisfaction.

    #### Non-Goals

    List what the feature will not aim to achieve at this stage, such as replacing other forms of authentication or implementing additional security measures like biometric verification.

    #### User Stories

    Outline the key user stories that this feature will address, focusing on the needs of both the users and the administrators of the platform.

    #### User Experience - Step by Step Flow

    Describe the step-by-step user interaction flow from registration or login to successful account access, emphasizing the OTP verification process.

    #### Narrative

    Explain the importance and impact of integrating an OTP verified mobile login, addressing how it will improve security and user trust while complying with KYC regulations.

    #### Success Metrics

    Identify the metrics that will measure the success of this feature, such as reductions in unauthorized access attempts and user feedback on the login process.

    #### Technical Considerations

    Discuss the technical requirements and considerations, including third-party integrations, compliance issues, and scalability challenges.

    #### Milestones & Sequencing

    Detail the timeline and key milestones for the development and implementation of the feature, from initial research to deployment and monitoring post-launch.
    """

    st.subheader("Create New PRD")
    product_name = st.text_input("Product Name", placeholder="Enter the product name here")
    product_description = st.text_area("Product Description", placeholder="Describe the product here")
    generate_button = st.button("Generate PRD")

    if generate_button:
        if not product_name or not product_description:
            st.warning("Please fill in both the product name and description.")
        else:
            with st.spinner('Generating PRD...'):
                try:
                    completion = client.chat.completions.create(
                        model="gpt-4-turbo",
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": f"Generate a PRD for a product named {product_name} with the following description: {product_description}. Only respond with the PRD and in Markdown format"}
                        ]
                    )
                    response = completion.choices[0].message.content
                    st.markdown(response, unsafe_allow_html=True)
                    #st.text_area("Generated PRD", response, height=300)
                    st.session_state['history'].append({'role': 'user', 'content': response})
                except Exception as e:
                    st.error(f"Failed to generate PRD. Please try again later. Error: {str(e)}")

def improve_prd():
    """
    Improve the provided Product Requirements Document (PRD) using GPT-3.5-turbo.

    Parameters:
    prd_text (str): The text of the PRD to be improved.

    Returns:
    str: The improved PRD.

    Raises:
    ValueError: If no PRD text is provided.
    Exception: If there is an error while improving the PRD.
    """
    system_prompt = """
    You are a Senior Product Manager working for PropertyGuru. Your language is engaging but uses Simple english & No Buzz words.  Given the objective, create a detailed PRD. The PRD should outline the problem, propose a solution, and include specific sections such as goals, user stories, user experience flow, success metrics, technical considerations, and milestones. Follow the structure provided below:

    ### PRD Outline for KYC Feature with OTP Verified Login

    #### tl;dr

    Provide a brief overview of the feature, emphasizing the introduction of a secure, OTP verified mobile login to enhance KYC compliance and ensure a frictionless yet secure user authentication process.

    #### Goals

    Divide the goals into Business Goals and User Goals, detailing how the feature will increase security, comply with regulations, and improve user satisfaction.

    #### Non-Goals

    List what the feature will not aim to achieve at this stage, such as replacing other forms of authentication or implementing additional security measures like biometric verification.

    #### User Stories

    Outline the key user stories that this feature will address, focusing on the needs of both the users and the administrators of the platform.

    #### User Experience - Step by Step Flow

    Describe the step-by-step user interaction flow from registration or login to successful account access, emphasizing the OTP verification process.

    #### Narrative

    Explain the importance and impact of integrating an OTP verified mobile login, addressing how it will improve security and user trust while complying with KYC regulations.

    #### Success Metrics

    Identify the metrics that will measure the success of this feature, such as reductions in unauthorized access attempts and user feedback on the login process.

    #### Technical Considerations

    Discuss the technical requirements and considerations, including third-party integrations, compliance issues, and scalability challenges.

    #### Milestones & Sequencing

    Detail the timeline and key milestones for the development and implementation of the feature, from initial research to deployment and monitoring post-launch.
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
                    completion = client.chat.completions.create(
                        model="gpt-4-turbo",
                        messages=[
                            {"role": "system", "content": f"You are a meticulous editor for improving product documents. {system_prompt}"},
                            {"role": "user", "content": f"Improve the following PRD: {prd_text}"}
                        ]
                    )
                    response = completion.choices[0].message.content
                    st.markdown(response, unsafe_allow_html=True)
                    #st.text_area("Improved PRD", response, height=300)
                    st.session_state['history'].append({'role': 'user', 'content': response})
                except Exception as e:
                    st.error(f"Failed to improve PRD. Please try again later. Error: {str(e)}")

def brainstorm_features():
    """
    Brainstorm innovative features for a product based on a given topic.
    Parameters:
    None

    Returns:
    None

    Raises:
    ValueError: If no topic is provided.
    Exception: If there is an error while brainstorming features.

    Usage:
    The function takes a topic as input and generates a list of innovative features for a product based on that topic. It uses the GPT-3.5-turbo model to generate the list of features. The generated list of features is displayed in a text area in the Streamlit interface.
    """
    st.subheader("Brainstorm Features")
    topic = st.text_input("Enter a topic for brainstorming", placeholder="Enter the topic to brainstorm about")
    brainstorm_button = st.button("Brainstorm")

    if brainstorm_button:
        if not topic:
            st.warning("Please enter a topic to brainstorm.")
        else:
            with st.spinner('Brainstorming features...'):
                try:
                    # Get the last three messages for context
                    context = st.session_state['history'][-3:] if len(st.session_state['history']) >= 3 else st.session_state['history']
                    context.append({"role": "system", "content": "You are a creative genius for brainstorming product features."})
                    context.append({"role": "user", "content": f"List innovative features for a product based on the following topic: {topic}"})
                    
                    completion = client.chat.completions.create(
                        model="gpt-4-turbo",
                        messages=context
                    )
                    response = completion.choices[0].message.content
                    st.text_area("Brainstormed Ideas", response, height=300)
                    st.session_state['history'].append({'role': 'user', 'content': response})
                except Exception as e:
                    st.error(f"Failed to brainstorm features. Please try again later. Error: {str(e)}")

def view_history():
    st.subheader("View History")
    if st.session_state['history']:
        for item in st.session_state['history']:
            st.json(item)
    else:
        st.info("No history available yet.")

def main():
    st.title("Product Management Assistant")
    if not st.session_state['authenticated']:
        pwd_placeholder = st.empty()
        pwd_input = pwd_placeholder.text_input("Enter your password:", type="password")
        if st.button("Login"):
            authenticate_user(pwd_input)
            pwd_placeholder.empty()  # Clears the password input after button press
    if st.session_state['authenticated']:
        st.sidebar.title("Navigation")
        option = st.sidebar.selectbox("Choose a feature", ("Create PRD", "Improve PRD"))

        if option == "Create PRD":
            create_prd()
        elif option == "Improve PRD":
            improve_prd()
        #elif option == "Brainstorm Features":
            #brainstorm_features()
        elif option == "View History":
            view_history()

if __name__ == "__main__":
    main()
