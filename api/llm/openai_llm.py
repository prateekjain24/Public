from openai import OpenAI
import openai
from fastapi import HTTPException
import os

class OpenAIWrapper:
    def __init__(self, api_key=None, model="gpt-4o", system_prompt=None):
        """
        Initialize the OpenAIWrapper class.

        Parameters:
        - api_key (str): Your OpenAI API key. If not provided, it will try to fetch from environment variables.
        - model (str): The default model to use for text generation. Defaults to "gpt-4o.
        - system_prompt (str): An optional system-level prompt to set context.
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.system_prompt = system_prompt
        if not self.api_key:
            raise ValueError("API key must be provided either as a parameter or set in the environment variables.")
        openai.api_key = self.api_key

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
        client = openai.OpenAI()  # Initialize the OpenAI client
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
