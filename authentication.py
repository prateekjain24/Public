import streamlit as st
import os

def check_authentication(password):
    return password == os.getenv('PASSWORD')

def authenticate_user():
    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False
    pwd_input = st.text_input("Password:", type="password")
    if st.button("Login"):
        st.session_state['authenticated'] = check_authentication(pwd_input)
        if not st.session_state['authenticated']:
            st.error("Incorrect password, please try again.")
        else:
            st.session_state['authenticated'] = True
            st.success("Logged in successfully.")
            st.rerun()
