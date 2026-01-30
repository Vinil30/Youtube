import os
from gradio_client import Client
from PIL import Image
from dotenv import load_dotenv

load_dotenv()


class ImageforArenaPulse:
    def __init__(
        self,
        model: str = "black-forest-labs/FLUX.1-schnell"
    ):
        self.model = model
        self.client = Client(self.model)

    def generate_image(self, prompt: str) -> Image.Image:
        """
        Generate a vertical background image using FLUX model.
        Expects a fully-formed visual prompt.
        """

        if not prompt or not prompt.strip():
            raise ValueError("Image prompt is empty")

        result = self.client.predict(
            prompt=prompt.strip(),
            seed=0,
            randomize_seed=True,
            width=720,
            height=1280,
            num_inference_steps=4,
            api_name="/infer"
        )

        if not result or not result[0]:
            raise RuntimeError("Image generation failed")

        image_path = result[0]
        return Image.open(image_path)
