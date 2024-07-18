import os
from groq import Groq
from typing import Optional

class GroqSTTWrapper:
    def __init__(self, api_key=None, model="whisper-large-v3"):
        """
        Initialize the GroqSTTWrapper class.

        Parameters:
        - api_key (str): Your Groq API key. If not provided, it will try to fetch from environment variables.
        - model (str): The model to use for transcription. Defaults to "whisper-large-v3".
        """
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.model = model
        if not self.api_key:
            raise ValueError("API key must be provided either as a parameter or set in the environment variables.")
        self.client = Groq(api_key=self.api_key)

    def transcribe(self, 
                   audio_file: str, 
                   language: Optional[str] = None, 
                   prompt: Optional[str] = None,
                   response_format: str = "json",
                   temperature: float = 0.0):
        """
        Transcribe the given audio file using the Groq speech-to-text API.

        Parameters:
        - audio_file (str): Path to the audio file to transcribe.
        - language (str, optional): The language of the input audio.
        - prompt (str, optional): An optional text to guide the model's style or continue a previous audio segment.
        - response_format (str, optional): The format of the transcript output. Default is "json".
        - temperature (float, optional): The sampling temperature. Default is 0.0.

        Returns:
        - Transcribed text or JSON object, depending on the response_format.
        """
        with open(audio_file, "rb") as file:
            params = {
                "file": (os.path.basename(audio_file), file.read()),
                "model": self.model,
                "response_format": response_format,
                "temperature": temperature
            }
            
            if language:
                params["language"] = language
            if prompt:
                params["prompt"] = prompt

            response = self.client.audio.transcriptions.create(**params)
        
        if response_format == "json":
            return response.json()
        else:
            return response.text