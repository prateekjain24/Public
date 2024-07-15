import json
import pandas as pd
import streamlit as st

def load_prompts():
    """
    Loads the prompts from a JSON file.

    Returns:
        dict: A dictionary containing the loaded prompts.

    Raises:
        FileNotFoundError: If the 'prompts.json' file is not found.
        json.JSONDecodeError: If the 'prompts.json' file is not in a valid JSON format.
    """
    try:
        with open('prompts.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        st.error("prompts.json file not found. Please ensure it exists in the project root.")
        return {}
    except json.JSONDecodeError:
        st.error("Error decoding prompts.json. Please ensure it's a valid JSON file.")
        return {}

def load_data(file):
    """
    Load data from an uploaded file.

    Args:
        file: A file object (CSV or Excel) uploaded through Streamlit.

    Returns:
        pandas.DataFrame: A DataFrame containing the loaded data.
        None: If the file format is unsupported.
    """
    if file.name.endswith('.csv'):
        return pd.read_csv(file)
    elif file.name.endswith('.xlsx'):
        return pd.read_excel(file)
    else:
        st.error("Unsupported file format. Please upload a CSV or Excel file.")
        return None

def create_data_prd(user, product_name, product_description, output, is_create_new):
    """
    Create a data dictionary for a PRD record.

    Args:
        user (str): The user associated with the data.
        product_name (str): The name of the product.
        product_description (str): The description of the product.
        output (str): The generated PRD content.
        is_create_new (bool): Flag indicating whether this is a new PRD or an improvement.

    Returns:
        dict: A dictionary containing the PRD data.
    """
    return {
        'user': user,
        'product_name': product_name,
        'product_description': product_description,
        'output': output,
        'is_create_new': is_create_new
    }

def create_data_brainstorm(user, message, is_user):
    """
    Create a data dictionary for a brainstorming record.

    Args:
        user (str): The user's name or identifier.
        message (str): The brainstorming message.
        is_user (bool): Indicates whether the message is from the user (True) or the AI (False).

    Returns:
        dict: A dictionary containing the brainstorming data.
    """
    return {
        'user': user,
        'message': message,
        'is_user': is_user
    }

def prepare_feature_data(feature_name, customer_type, other_details, prd_text):
    """
    Prepare data for feature-related tasks (e.g., tracking plan generation).

    Args:
        feature_name (str): The name of the feature.
        customer_type (str): The type of customer the feature is for.
        other_details (str): Any additional details about the feature.
        prd_text (str): The PRD text related to the feature.

    Returns:
        dict: A dictionary containing the prepared feature data.
    """
    return {
        'feature_name': feature_name,
        'customer_type': customer_type,
        'other_details': other_details,
        'prd_text': prd_text
    }

def parse_ab_test_data(data_input):
    """
    Parse input data for A/B test analysis.

    Args:
        data_input (str): A string containing A/B test data in a specific format.

    Returns:
        list of dict: A list of dictionaries, each containing parsed data for a variant.
        None: If the input data is invalid or cannot be parsed.
    """
    try:
        lines = data_input.strip().split('\n')
        variants = []
        for line in lines:
            name, visitors, conversions = line.split(',')
            variants.append({
                'name': name.strip(),
                'visitors': int(visitors.strip()),
                'conversions': int(conversions.strip())
            })
        return variants
    except ValueError:
        st.error("Invalid data format. Please ensure each line is in the format: Variant Name, Visitors, Conversions")
        return None

# Add any additional data loading or preparation functions as needed