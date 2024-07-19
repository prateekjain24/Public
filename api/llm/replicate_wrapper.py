import os
import replicate
import time
from typing import Optional, Dict, Any

class ReplicateWrapper:
    def __init__(self, api_key=None):
        """
        Initialize the ReplicateWrapper class.

        Parameters:
        - api_key (str): Your Replicate API key. If not provided, it will try to fetch from environment variables.
        """
        self.api_key = api_key or os.getenv("REPLICATE_API_KEY")
        if not self.api_key:
            raise ValueError("API key must be provided either as a parameter or set in the environment variables.")
        os.environ["REPLICATE_API_TOKEN"] = self.api_key

    def text_to_image(self, 
                      prompt: str, 
                      aspect_ratio: str = "3:2",
                      model: str = "stability-ai/stable-diffusion-3",
                      **kwargs) -> str:
        """
        Generate an image from text using Replicate's Stable Diffusion model.

        Parameters:
        - prompt (str): The text description of the image to generate.
        - aspect_ratio (str): The aspect ratio of the generated image. Default is "3:2".
        - model (str): The model to use for image generation. Default is "stability-ai/stable-diffusion-3".
        - kwargs: Additional keyword arguments to pass to the model.

        Returns:
        - str: The URL of the generated image.
        """
        input_data = {
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            **kwargs
        }
        
        prediction = replicate.predictions.create(
            version=model,
            input=input_data
        )
        
        while prediction.status != "succeeded":
            time.sleep(1)
            prediction.reload()
            if prediction.status == "failed":
                raise Exception("Image generation failed")

        return prediction.output[0]  # Return the URL of the generated image

    def get_prediction_status(self, prediction_id: str) -> Dict[str, Any]:
        """
        Get the status of a prediction.

        Parameters:
        - prediction_id (str): The ID of the prediction to check.

        Returns:
        - Dict[str, Any]: A dictionary containing the prediction status and details.
        """
        prediction = replicate.predictions.get(prediction_id)
        return {
            "id": prediction.id,
            "status": prediction.status,
            "output": prediction.output,
            "error": prediction.error,
            "logs": prediction.logs
        }