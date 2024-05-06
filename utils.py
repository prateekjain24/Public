import json
import pandas as pd
import streamlit as st
import yt_dlp

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
    pass

def load_data(file):
    """Load data from an uploaded file."""
    if file.name.endswith('.csv'):
        df = pd.read_csv(file)
    elif file.name.endswith('.xlsx'):
        df = pd.read_excel(file)
    else:
        st.error("Unsupported file format. Please upload a CSV or Excel file.")
        return None
    return df

def download_audio(youtube_url):
    """Download the medium audio stream of a YouTube video."""
    ydl_opts = {
        'format': 'bestaudio',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '128',
        }],
        'outtmpl': 'temp_downloaded_audio.%(ext)s',  # Temporary file
        'quiet': True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info_dict = ydl.extract_info(youtube_url, download=False)
            audio_file = ydl.prepare_filename(info_dict).replace("temp_downloaded_audio", "downloaded_audio")
            ydl.download([youtube_url])
            return audio_file  # Return the path to the downloaded file
        except Exception as e:
            st.error(f"Failed to download audio: {e}")
            return None
    pass
