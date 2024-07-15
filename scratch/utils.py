import json
import pandas as pd
import streamlit as st
import yt_dlp
from PIL import Image
import base64
from io import BytesIO

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
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': 'downloaded_audio.%(ext)s',  # Temporary file
        'quiet': True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            path = ydl.get_output_path()
            path
            ydl.download([youtube_url])
            path = ydl.get_output_path()
            print(path)
            return path  # Return the path to the downloaded file
        except Exception as e:
            st.error(f"Failed to download audio: {e}")
            return None
    pass

def encode_image(image, format):
    buffered = BytesIO()
    image.save(buffered, format=format)
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return img_str
    pass
