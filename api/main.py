from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Query
from pydantic import BaseModel, Field
from typing import Optional, List
import uvicorn
from llm.openai_llm import OpenAIWrapper
from llm.groq_llm import GroqWrapper
from llm.whisper_wrapper import WhisperWrapper
from llm.groq_stt_wrapper import GroqSTTWrapper
from llm.anthropic_llm import AnthropicWrapper
#from dotenv import load_dotenv
import os
import tempfile

#load_dotenv()
app = FastAPI()

class GenerateTextRequest(BaseModel):
    provider: str = Field(..., description="The text generation service provider, e.g., 'groq' or 'openai'.")
    model: str = Field(..., description="The model identifier, specifying which language model to use for text generation. gpt4, llama3-8b-8192, llama3-70b-8192")
    prompt: str = Field(..., description="The input prompt to the language model based on which the text is generated.")
    temperature: float = Field(0.5, description="Controls the randomness of the output. Lower values make it more deterministic.")
    return_prompt: bool = Field(False, description="A boolean flag to specify whether to return the original prompt with the generated text.")
    max_tokens: Optional[int] = Field(4000, description="The maximum number of tokens to generate. Default is 4000.")
    system_instructions: str = Field("You are working for PropertyGuru", description="Instructions that define the context or constraints under which the model operates. Typically used to create agents or give personality.")


class GenerateTextResponse(BaseModel):
    generated_text: str = Field(..., description="The text generated by the AI model based on the input prompt.")
    input_token: int = Field(0, description="The number of tokens in the input prompt. Defaults to 0 if not provided.")
    output_token: int = Field(0, description="The number of tokens generated by the AI model as output.")
    prompt_returned: Optional[str] = Field(None, description="The original prompt returned along with the output text, if requested.")

class TranscribeAudioResponse(BaseModel):
    transcription: str = Field(..., description="The transcribed text or JSON object from the audio file.")

class ImageToTextResponse(BaseModel):
    description: str = Field(..., description="The text description generated from the image.")



@app.post("/generate-text", response_model=GenerateTextResponse)
async def generate_text(request: GenerateTextRequest):
    try:
        if request.provider == "openai":
            client = OpenAIWrapper(model=request.model, system_prompt=request.system_instructions)
            generated_text, input_tokens, output_tokens = client.generate_text(
                prompt=request.prompt,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
            )
        else:
            client = GroqWrapper(model=request.model,system_prompt=request.system_instructions)
            generated_text, input_tokens, output_tokens = client.generate_text(
                prompt=request.prompt,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
            )
        result = GenerateTextResponse(
            generated_text=generated_text,
            input_token=input_tokens,
            output_token=output_tokens
        )
        if request.return_prompt:
            result.prompt_returned = request.prompt

        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
    
@app.post("/transcribe-audio", response_model=TranscribeAudioResponse)
async def transcribe_audio(
    audio_file: UploadFile = File(...),
    provider: str = Form(..., description="The provider to use for transcription. Either 'openai' or 'groq'."),
    language: Optional[str] = Form(None, description="The language of the input audio."),
    prompt: Optional[str] = Form(None, description="An optional text to guide the model's style or continue a previous audio segment."),
    response_format: str = Form("json", description="The format of the transcript output."),
    temperature: float = Form(0.0, description="The sampling temperature, between 0 and 1."),
    timestamp_granularities: Optional[List[str]] = Query(None, description="The timestamp granularities to populate for this transcription (OpenAI only).")
):
    try:
        # Check if the provider is valid
        if provider not in ["openai", "groq"]:
            raise HTTPException(status_code=400, detail="Invalid provider. Choose either 'openai' or 'groq'.")

        # Check if the file is in a supported format
        supported_formats = ["flac", "mp3", "mp4", "mpeg", "mpga", "m4a", "ogg", "wav", "webm"]
        file_extension = os.path.splitext(audio_file.filename)[1][1:].lower()
        if file_extension not in supported_formats:
            raise HTTPException(status_code=400, detail=f"Unsupported file format. Supported formats are: {', '.join(supported_formats)}")

        # Save the uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_extension}") as temp_audio:
            temp_audio.write(audio_file.file.read())
            temp_audio_path = temp_audio.name

        # Prepare common parameters
        common_params = {
            "language": language,
            "prompt": prompt,
            "response_format": response_format,
            "temperature": temperature
        }

        # Initialize the appropriate wrapper and transcribe based on the provider
        if provider == "openai":
            transcription_client = WhisperWrapper()
            if timestamp_granularities:
                common_params["timestamp_granularities"] = timestamp_granularities
        else:  # provider == "groq"
            transcription_client = GroqSTTWrapper()

        # Transcribe the audio
        transcription = transcription_client.transcribe(temp_audio_path, **common_params)

        # Delete the temporary file
        os.unlink(temp_audio_path)

        return TranscribeAudioResponse(transcription=transcription)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription error: {str(e)}")

@app.post("/image-to-text", response_model=ImageToTextResponse)
async def image_to_text(
    image_file: UploadFile = File(...),
    provider: str = Form(..., description="The provider to use for image-to-text conversion. Either 'openai' or 'anthropic'."),
    prompt: str = Form("Describe this image in detail.", description="The prompt to guide the model's description."),
    max_tokens: int = Form(1000, description="The maximum number of tokens to generate.")
):
    try:
        # Check if the provider is valid
        if provider not in ["openai", "anthropic"]:
            raise HTTPException(status_code=400, detail="Invalid provider. Choose either 'openai' or 'anthropic'.")

        # Check if the file is an image
        if not image_file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Uploaded file is not an image.")

        # Save the uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_image:
            temp_image.write(image_file.file.read())
            temp_image_path = temp_image.name

        # Initialize the appropriate wrapper based on the provider
        if provider == "openai":
            client = OpenAIWrapper()
        else:  # provider == "anthropic"
            client = AnthropicWrapper()

        # Convert image to text
        description = client.image_to_text(
            image_path=temp_image_path,
            prompt=prompt,
            max_tokens=max_tokens
        )

        # Delete the temporary file
        os.unlink(temp_image_path)

        return ImageToTextResponse(description=description)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image-to-text conversion error: {str(e)}")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8024)
    #uvicorn main:app --host 0.0.0.0 --port $PORT
    
