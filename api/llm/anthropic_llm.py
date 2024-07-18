import os
from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT
import base64

class AnthropicWrapper:
    def __init__(self, api_key=None, model="claude-3-5-sonnet-20240620", system_prompt=None):
        """
        Initialize the AnthropicWrapper class.

        Parameters:
        - api_key (str): Your Anthropic API key. If not provided, it will try to fetch from environment variables.
        - model (str): The default model to use for text generation. Defaults to "claude-3-sonnet-20240229".
        - system_prompt (str): An optional system-level prompt to set context.
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.model = model
        self.system_prompt = system_prompt
        if not self.api_key:
            raise ValueError("API key must be provided either as a parameter or set in the environment variables.")
        self.client = Anthropic(api_key=self.api_key)

    @property
    def system_prompt(self):
        """Gets the system prompt."""
        return self._system_prompt

    @system_prompt.setter
    def system_prompt(self, value):
        """Sets the system prompt."""
        self._system_prompt = value
    
    def generate_text(self, prompt, max_tokens=4000, temperature=0.5, **kwargs):
        """
        Generate text using the specified model.

        Parameters:
        - prompt (str): The prompt text to generate responses for.
        - max_tokens (int): The maximum number of tokens to generate.
        - temperature (float): The temperature for text generation.
        - kwargs: Additional keyword arguments for the Anthropic API call.

        Returns:
        - Generated text from the model, input tokens count, and output tokens count.
        """
        messages = [{"role": "user", "content": prompt}]
        
        response = self.client.messages.create(
            model=self.model,
            messages=messages,
            system=self.system_prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            **kwargs
        )

        return (
            response.content[0].text,
            response.usage.input_tokens,
            response.usage.output_tokens
        )
    

    def image_to_text(self, 
                      image_path: str, 
                      prompt: str = "Describe this image in detail.",
                      max_tokens: int = 1000) -> str:
        """
        Convert an image to text description using Claude.

        Parameters:
        - image_path (str): Path to the image file.
        - prompt (str): The prompt to guide Claude's description. Default is "Describe this image in detail."
        - max_tokens (int): The maximum number of tokens to generate. Default is 1000.

        Returns:
        - str: The generated text description of the image.
        """
        with open(image_path, "rb") as image_file:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/jpeg",
                                    "data": image_file.read().decode("utf-8")
                                }
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ]
                    }
                ]
            )
        
        return response.content[0].text