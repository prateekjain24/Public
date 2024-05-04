import llm
import os

def build_models():
    """
    Builds and initializes the GPT-3.5-turbo and GPT-4-turbo models.
    Returns:
        tuple: A tuple containing the initialized GPT-3.5-turbo and GPT-4-turbo models.
    Raises:
        ValueError: If the OPENAI_API_KEY environment variable is not set.
    """
    gpt3_model = llm.get_model("gpt-3.5-turbo")
    gpt3_model.key = os.getenv("OPENAI_API_KEY")

    gpt4_model = llm.get_model("gpt-4-turbo")
    gpt4_model.key = os.getenv("OPENAI_API_KEY")

    return gpt3_model, gpt4_model