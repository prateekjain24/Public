import streamlit as st
st.set_page_config(
    page_title="PM Toolkit",
    page_icon="🥊",
    layout="wide",
    )

# import llm
from features.prd import create_prd, improve_prd
from features.view_history import view_history
from features.brainstorm import brainstorm_features
from features.tracking import tracking_plan
from features.gtm import gtm_planner
from features.ab_test import abc_test_significance
from features.test_duration import ab_test_duration_calculator
from utils.models import build_models
from utils.data_loading import load_prompts
from storage.supabase_client import create_client
import os
from supabase import create_client, Client
from utils.authentication import auth_screen 

#from dotenv import load_dotenv
#load_dotenv()

SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
#res = supabase.auth.get_session()
# Using Streamlit's session state to store temporary memory

def main():
    """
    Main function that serves as the entry point of the program.
    
    This function loads prompts, builds models, and presents a menu of options to the user based on their selection.
    The user can choose to create a PRD, improve a PRD, brainstorm features, create a tracking plan, create a GTM plan, or view history.
    Each option calls a specific function to perform the corresponding task.
    """
    prompts = load_prompts()
    fast_llm, quality_llm = build_models()
    system_prompt_prd_experimental = prompts['system_prompt_prd_experimental']
    system_prompt_director = prompts['system_prompt_director']
    system_prompt_brainstorm = prompts['system_prompt_brainstorm']
    system_prompt_tracking = prompts['system_prompt_tracking']
    user_prompt_tracking = prompts['prompt_tracking_plan']
    system_prompt_directorDA = prompts['system_prompt_directorDA']
    system_prompt_GTM = prompts['system_prompt_GTM']
    system_prompt_GTM_critique = prompts['system_prompt_GTM_critique']
    system_prompt_ab_test = prompts['system_prompt_ab_test']
    # Authenticate the user
    # authenticate()
    if 'history' not in st.session_state:
        st.session_state['history'] = []
    auth_screen(supabase)
    # if st.session_state['authenticated']:
    if st.session_state['logged_in']:
        option = st.sidebar.radio(
            "# Select the Task 👉",
            key="task",
            options=[
                "Create PRD", 
                "Improve PRD",
                "Brainstorm Features", 
                "Tracking Plan",
                "Create GTM Plan",
                "A/B Test Significance",
                "A/B Test Duration Calculator",
                "View History"
            ],
        )
        
        if option == "Create PRD":
            create_prd(system_prompt_prd_experimental, system_prompt_director, quality_llm, fast_llm, supabase)
        elif option == "Improve PRD":
            improve_prd(system_prompt_prd_experimental, system_prompt_director, quality_llm, supabase)
        elif option == "Brainstorm Features":
            brainstorm_features(system_prompt_brainstorm, quality_llm, supabase)
        elif option == "Tracking Plan":
            tracking_plan(system_prompt_tracking, user_prompt_tracking, system_prompt_directorDA, quality_llm)
        elif option == "Create GTM Plan":
            gtm_planner(system_prompt_GTM, system_prompt_GTM_critique, fast_llm, quality_llm)
        elif option == "A/B Test Significance":
            abc_test_significance(quality_llm, system_prompt_ab_test)
        elif option == "A/B Test Duration Calculator":
            ab_test_duration_calculator()
        elif option == "View History":
            view_history(supabase)

if __name__ == "__main__":
    main()
