import openai
import os
from typing import Optional, List

class WhisperWrapper:
    def __init__(self, api_key=None, model="whisper-1"):
        """
        Initialize the WhisperWrapper class.

        Parameters:
        - api_key (str): Your OpenAI API key. If not provided, it will try to fetch from environment variables.
        - model (str): The Whisper model to use for transcription. Currently only "whisper-1" is available.
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        if not self.api_key:
            raise ValueError("API key must be provided either as a parameter or set in the environment variables.")
        openai.api_key = self.api_key

    def transcribe(self, 
                   audio_file: str, 
                   language: Optional[str] = None, 
                   prompt: Optional[str] = None,
                   response_format: str = "json",
                   temperature: float = 0,
                   timestamp_granularities: Optional[List[str]] = None):
        """
        Transcribe the given audio file using the Whisper model.

        Parameters:
        - audio_file (str): Path to the audio file to transcribe.
        - language (str, optional): The language of the input audio in ISO-639-1 format.
        - prompt (str, optional): An optional text to guide the model's style or continue a previous audio segment.
        - response_format (str, optional): The format of the transcript output. Default is "json".
        - temperature (float, optional): The sampling temperature, between 0 and 1. Default is 0.
        - timestamp_granularities (List[str], optional): The timestamp granularities to populate for this transcription.

        Returns:
        - Transcribed text or JSON object, depending on the response_format.
        """
        client = openai.OpenAI()
        
        with open(audio_file, "rb") as audio:
            params = {
                "model": self.model,
                "file": audio,
                "response_format": response_format,
                "temperature": temperature
            }
            
            if language:
                params["language"] = language
            if prompt:
                params["prompt"] = prompt
            if timestamp_granularities:
                params["timestamp_granularities"] = timestamp_granularities

            response = client.audio.transcriptions.create(**params)
        
        if response_format == "json" or response_format == "verbose_json":
            return response.json()
        else:
            return response.text