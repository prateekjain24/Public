import os
import tabulate
import streamlit as st
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_experimental.agents import create_csv_agent



GROQ_API_KEY = os.environ.get("GROQ_API_KEY")


def main():
    st.set_page_config(page_title="ASK YOUR CSV")
    st.header("ASK YOUR CSV")
    csv = st.file_uploader("Upload a CSV file", type="csv")
    if csv is not None:
        agent = create_csv_agent(
            ChatGroq(
                model="llama3-70b-8192",
                temperature=0), 
                csv, 
                verbose=True, 
                handle_parsing_errors=True
                )
        user_question = st.text_input("Ask a question about your CSV: ")


        if user_question is not None and user_question != "":
            with st.spinner(text="In progress..."):
                st.write(agent.run(user_question))


if __name__ == "__main__":
    main()