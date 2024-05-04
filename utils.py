import json
import pandas as pd
import streamlit as st

def load_prompts():
    """
    Loads the prompts from a JSON file.
    Parameters:
        None
    Returns:
        dict: A dictionary containing the loaded prompts.
    Raises:
        FileNotFoundError: If the 'prompts.json' file is not found.
        json.JSONDecodeError: If the 'prompts.json' file is not in a valid JSON format.
    Usage:
        The function reads the 'prompts.json' file and returns a dictionary containing the loaded prompts.
    """
    with open('prompts.json', 'r') as file:
        return json.load(file)
    pass

def load_data(file):
    """Load data from an uploaded file."""
    if file.name.endswith('.csv'):
        df = pd.read_csv(file)
    elif file.name.endswith('.xlsx'):
        df = pd.read_excel(file)
    else:
        st.error("Unsupported file format. Please upload a CSV or Excel file.")
        return None
    return df
