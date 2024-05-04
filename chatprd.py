import streamlit as st
from openai import OpenAI
#from dotenv import load_dotenv
import llm
import os
from authentication import authenticate_user
from features import create_prd, improve_prd, brainstorm_features, view_history
from utils import load_prompts
from models import build_models

# Using Streamlit's session state to store temporary memory
if 'history' not in st.session_state:
    st.session_state['history'] = []

def main():
    prompts = load_prompts()
    fast_llm, quality_llm = build_models()
    system_prompt_prd = prompts['system_prompt_prd']
    system_prompt_director = prompts['system_prompt_director']
    system_prompt_brainstorm = prompts['system_prompt_brainstorm']
    #Authenticate the user
    authenticate_user()
    if st.session_state['authenticated']:
        st.title("PM Assisistant")
        st.sidebar.title("Select the Task:")
        option = st.sidebar.selectbox("Choose a feature", ("Create PRD", "Improve PRD","Brainstorm Features", "View History"))

        if option == "Create PRD":
            create_prd(system_prompt_prd,system_prompt_director, quality_llm)
        elif option == "Improve PRD":
            improve_prd(system_prompt_prd,system_prompt_director,quality_llm)
        elif option == "Brainstorm Features":
            brainstorm_features(system_prompt_brainstorm,quality_llm)
        elif option == "View History":
            view_history()

if __name__ == "__main__":
    main()
