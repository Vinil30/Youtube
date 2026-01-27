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
Create a terrifying, cinematic horror background image for a ghost story video.

Context (may be short or imperfect):
"{self.context}"

Style requirements:
- Extremely scary and unsettling atmosphere
- No text, no typography, no captions
- No people clearly visible, only vague human-like silhouettes if needed
- Dark abandoned location such as an empty street, old building, forest, tunnel, or ruins
- One unnatural presence suggested subtly, not fully visible
- Deep shadows, fog, mist, or darkness dominating the scene
- Horror-movie cinematic lighting, low-key lighting
- No bright colors, mostly dark tones
- Realistic, high-detail, photo-realistic style
- Composition should create fear and tension, not comfort
- Vertical-friendly framing (can be cropped to 9:16)

Visual tone:
- Dreadful
- Unsettling
- Sinister
- Silent
- Psychological horror
- Feels like something is watching from the darkness

Important:
- Image should feel threatening even without showing the ghost clearly
- Viewer should feel fear, suspense, and discomfort at first glance
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
            width=720,
            height=1280,
            num_inference_steps=4,
            api_name="/infer"
        )

        image_path = result[0]
        image = Image.open(image_path)
        return image
