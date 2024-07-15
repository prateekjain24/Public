from api.llm.openai_llm import OpenAIWrapper
from api.llm.groq_llm import GroqWrapper
from api.llm.anthropic_llm import AnthropicWrapper
import os
import openai
import streamlit as st

def build_models():
    """
    Builds and initializes the GPT-3.5-turbo and GPT-4-turbo models.
    Returns:
        tuple: A tuple containing the initialized GPT-3.5-turbo and GPT-4-turbo models.
    Raises:
        ValueError: If the OPENAI_API_KEY environment variable is not set.
    """
    gpt4_model = OpenAIWrapper(model ="gpt-4o")
    groq_model = GroqWrapper(model = "llama3-70b-8192")
    claude_model = AnthropicWrapper(model="claude-3-5-sonnet-20240620")


    return claude_model, gpt4_model

def transcribe_audio(audio_path):
    """Transcribe the downloaded audio file using OpenAI's Whisper model."""
    try:
        # Open the audio file
        with open(audio_path, "rb") as audio_file:
            # Make the API call to transcribe the audio file
            transcription = openai.Audio.transcription.create(
                model="whisper-1",
                file=audio_file
            )
        os.remove(audio_path)  # Clean up the audio file after processing
        return transcription['text']
    except Exception as e:
          # Ensure the audio file is cleaned up even on failure
        st.error(f"Failed to transcribe audio: {e}")
        return None