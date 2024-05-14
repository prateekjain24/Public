import streamlit as st
from openai import OpenAI
#from dotenv import load_dotenv
import llm
import os
from authentication import authenticate_user
from features import create_prd, improve_prd, brainstorm_features, view_history, tracking_plan, summarize_yt
from utils import load_prompts
from models import build_models

#load_dotenv()

# Using Streamlit's session state to store temporary memory
if 'history' not in st.session_state:
    st.session_state['history'] = []

def main():
    prompts = load_prompts()
    fast_llm, quality_llm = build_models()
    system_prompt_prd = prompts['system_prompt_prd']
    system_prompt_director = prompts['system_prompt_director']
    system_prompt_brainstorm = prompts['system_prompt_brainstorm']
    system_prompt_tracking = prompts['system_prompt_tracking']
    user_prompt_tracking = prompts['prompt_tracking_plan']
    system_prompt_directorDA = prompts['system_prompt_directorDA']
    system_prompt_yt_planner = prompts['system_prompt_yt_planner']
    prompt_yt_summary = prompts['prompt_yt_summary']
    #Authenticate the user
    authenticate_user()
    if st.session_state['authenticated']:
        st.title("PM Assisistant")
        st.sidebar.title("Select the Task:")
        option = st.sidebar.selectbox("Choose a feature", ("Create PRD", "Improve PRD","Brainstorm Features", "Tracking Plan","View History"))

        if option == "Create PRD":
            create_prd(system_prompt_prd,system_prompt_director, quality_llm, fast_llm)
        elif option == "Improve PRD":
            improve_prd(system_prompt_prd,system_prompt_director,quality_llm)
        elif option == "Brainstorm Features":
            brainstorm_features(system_prompt_brainstorm,quality_llm)
        elif option == "Tracking Plan":
            tracking_plan(system_prompt_tracking, user_prompt_tracking, system_prompt_directorDA, quality_llm)
        # elif option == "Summarize Youtube":
        #     summarize_yt(system_prompt_yt_planner,prompt_yt_summary, quality_llm)
        elif option == "View History":
            view_history()

if __name__ == "__main__":
    main()
