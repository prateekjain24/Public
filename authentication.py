import streamlit as st
import os

def check_authentication(password):
    return password == os.getenv('PASSWORD')

def authenticate_user():
    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False

    # Create a placeholder for the login form
    login_placeholder = st.empty()

    if not st.session_state['authenticated']:
        with login_placeholder.container():
            pwd_input = st.text_input("Password:", type="password", key="pwd")
            if st.button("Login", key="login_button"):
                st.session_state['authenticated'] = check_authentication(pwd_input)
                if st.session_state['authenticated']:
                    # Clear the login placeholder if authenticated
                    login_placeholder.empty()
                else:
                    st.error("Incorrect password, please try again.")
