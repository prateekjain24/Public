import llm
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
    gpt3_model = llm.get_model("gpt-3.5-turbo")
    gpt3_model.key = os.getenv("OPENAI_API_KEY")

    gpt4_model = llm.get_model("gpt-4-turbo")
    gpt4_model.key = os.getenv("OPENAI_API_KEY")

    return gpt3_model, gpt4_model

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
        os.remove(audio_path)  # Ensure the audio file is cleaned up even on failure
        st.error(f"Failed to transcribe audio: {e}")
        return None