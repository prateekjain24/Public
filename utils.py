import json

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

