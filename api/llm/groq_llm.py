from groq import Groq
import openai
from fastapi import HTTPException
import os
import groq


class GroqWrapper:
    def __init__(self, api_key=None, model="llama3-70b-8192", system_prompt=None):
        """
        Initialize the OpenAIWrapper class.

        Parameters:
        - api_key (str): Your Groq API key. If not provided, it will try to fetch from environment variables.
        - model (str): The default model to use for text generation. Defaults to "llama3-70b-8192".
        - system_prompt (str): An optional system-level prompt to set context.
        """
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.model = model
        self.system_prompt = system_prompt
        if not self.api_key:
            raise ValueError("API key must be provided either as a parameter or set in the environment variables.")
        groq.api_key = self.api_key

    @property
    def system_prompt(self):
        """Gets the system prompt."""
        return self._system_prompt

    @system_prompt.setter
    def system_prompt(self, value):
        """Sets the system prompt."""
        self._system_prompt = value
    
    def generate_text(self, prompt, max_tokens=100, temperature=0.7, **kwargs):
        """
        Generate text using the specified model.

        Parameters:
        - prompt (str): The prompt text to generate responses for.
        - max_tokens (int): The maximum number of tokens to generate.
        - temperature (float): The temperature for text generation.
        - kwargs: Additional keyword arguments for the OpenAI API call.

        Returns:
        - Generated text from the model.
        """
        client = groq.Groq()  # Initialize the OpenAI client
        messages = []
        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})
        messages.append({"role": "user", "content": prompt})
        response = client.chat.completions.create(
            model = self.model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            **kwargs
        )
        return response.choices[0].message.content, int(response.usage.prompt_tokens), int(response.usage.completion_tokens)


# def call_openai_api(prompt, model, max_tokens, temperature, system_instructions):
#     client = OpenAI()
#     if 'gpt4' in model or 'GPT4' in model or 'gpt-4' in model or 'GPT-4' in model:
#         model = "gpt-4o"
#     else:
#         model = "gpt-3.5-turbo"

#     try:
#         messages=[
#         {"role": "system", "content": f"{system_instructions}. You are working for PropertyGuru."},
#         {"role": "user", "content": f"{prompt}"}
#           ]
#         response = client.chat.completions.create(
#             model=model,
#             messages=messages,
#             max_tokens=max_tokens,
#             temperature=temperature,
#             # user="your-user-id"  # Replace 'your-user-id' with appropriate user identification if necessary
#         )
#         return response.choices[0].message.content, int(response.usage.prompt_tokens), int(response.usage.completion_tokens)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"OpenAI API call failed: {str(e)}")