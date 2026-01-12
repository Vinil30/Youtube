# This file is to generate image for the video
import os
from gradio_client import Client
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

class ImageforArenaPulse:
    def __init__(
        self,
        prompt: str = None,
        context: str = None,
        api_key: str = None,
        HF_TOKEN: str = None,
        model: str = "black-forest-labs/FLUX.1-schnell"
    ):
        self.model = model
        self.context = context
        self.prompt = prompt
        self.HF_TOKEN = os.environ.get("HF_TOKEN")
        self.api_key = os.environ.get("API_KEY")
        self.client = Client(self.model)

    def generate_image_prompt(self) -> str:
        """
        Converts short / broken English context into
        a clean, cinematic background image prompt
        suitable for AI podcast videos.
        """

        base_prompt = f"""
Create a calm, cinematic, high-quality background image for an AI podcast video.

Context (may be short or imperfect English):
"{self.context}"

Style requirements:
- Minimalistic and visually soothing
- No text, no typography, no captions
- Two characters facinng each other with a mic and conducting a podcast.
- Soft lighting, cinematic atmosphere
- Abstract or symbolic representation of the topic
- Professional YouTube podcast background
- Clean composition, not distracting
- 16:9 landscape orientation

Visual tone:
- Modern
- Calm
- Thoughtful
- High detail
- Aesthetic but subtle
"""

        self.prompt = base_prompt.strip()
        return self.prompt

    def generate_image_arena(self, prompt: str = None) -> Image.Image:
        """
        Generates the background image using FLUX model
        """

        if prompt is not None:
            self.prompt = prompt

        if not self.prompt:
            raise ValueError("Image prompt is empty. Call generate_image_prompt() first.")

        result = self.client.predict(
            prompt=self.prompt,
            seed=0,
            randomize_seed=True,
            width=1280,
            height=720,
            num_inference_steps=4,
            api_name="/infer"
        )

        image_path = result[0]
        image = Image.open(image_path)
        return image
