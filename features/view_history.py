import streamlit as st
from storage.supabase_client import create_record, read_records
from utils.data_loading import create_data_prd
import os

prd_table = os.environ.get('SUPABASE_TABLE')

def view_history(supabase):
    """
    View the history of generated PRDs.

    Args:
        supabase: The Supabase client used for database operations.

    Returns:
        None
    """
    st.subheader("View PRD Generation History")
    records = read_records(prd_table, st.session_state['user']['email'], supabase)
    for record in records:
        with st.expander(f"{record['product_name']} - Generated on: {record['created_at']}"):
            st.markdown(record['product_name'])
            st.markdown(record['output'])
            st.download_button(
                label="Download PRD as Markdown",
                data=record['output'],
                file_name=f"prd_{record['product_name']}.md",
                mime="text/markdown",
                key=f"prd_{record['id']}"
            )