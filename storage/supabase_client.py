import os
from supabase import create_client, Client
import streamlit as st

# Initialize Supabase client
def init_supabase():
    """
    Initialize and return a Supabase client.

    Returns:
        Client: An initialized Supabase client.

    Raises:
        ValueError: If the Supabase URL or key is not set in environment variables.
    """
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    if not url or not key:
        raise ValueError("Supabase URL and key must be set as environment variables.")
    return create_client(url, key)

supabase: Client = init_supabase()

def create_record(table_name: str, data: dict) -> dict:
    """
    Create a new record in the specified table.

    Args:
        table_name (str): The name of the table to insert the record into.
        data (dict): The data to be inserted as a new record.

    Returns:
        dict: The created record data returned by Supabase.

    Raises:
        Exception: If there's an error in creating the record.
    """
    try:
        response = supabase.table(table_name).insert(data).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        st.error(f"Error creating record: {str(e)}")
        raise

def read_records(table_name: str, user_email: str) -> list:
    """
    Read records from the specified table based on the user's email ID.

    Args:
        table_name (str): The name of the table to read records from.
        user_email (str): The email ID of the user to filter records.

    Returns:
        list: A list of records matching the user's email.

    Raises:
        Exception: If there's an error in reading the records.
    """
    try:
        response = supabase.table(table_name).select("*").eq('user', user_email).order('created_at', desc=True).execute()
        return response.data
    except Exception as e:
        st.error(f"Error reading records: {str(e)}")
        raise

def update_record(table_name: str, record_id: str, data: dict) -> dict:
    """
    Update an existing record in the specified table.

    Args:
        table_name (str): The name of the table containing the record.
        record_id (str): The ID of the record to be updated.
        data (dict): The updated data for the record.

    Returns:
        dict: The updated record data returned by Supabase.

    Raises:
        Exception: If there's an error in updating the record.
    """
    try:
        response = supabase.table(table_name).update(data).eq('id', record_id).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        st.error(f"Error updating record: {str(e)}")
        raise

def delete_record(table_name: str, record_id: str) -> bool:
    """
    Delete a record from the specified table based on the record ID.

    Args:
        table_name (str): The name of the table to delete the record from.
        record_id (str): The ID of the record to be deleted.

    Returns:
        bool: True if the record was successfully deleted, False otherwise.

    Raises:
        Exception: If there's an error in deleting the record.
    """
    try:
        response = supabase.table(table_name).delete().eq('id', record_id).execute()
        return len(response.data) > 0
    except Exception as e:
        st.error(f"Error deleting record: {str(e)}")
        raise

def get_user_data(user_id: str) -> dict:
    """
    Retrieve user data from the 'users' table.

    Args:
        user_id (str): The ID of the user to retrieve data for.

    Returns:
        dict: The user data if found, None otherwise.

    Raises:
        Exception: If there's an error in retrieving the user data.
    """
    try:
        response = supabase.table('users').select("*").eq('id', user_id).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        st.error(f"Error retrieving user data: {str(e)}")
        raise

# Add any additional Supabase-related functions as needed