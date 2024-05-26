from openai import OpenAI
import os

def retrieve_assistant(assistant_id = "asst_58YMdnJhEyfR8YvfldglhRZy"):
    client = OpenAI()
    my_assistant = client.beta.assistants.retrieve(assistant_id)
    return my_assistant

