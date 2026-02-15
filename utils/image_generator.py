import requests
from PIL import Image
from io import BytesIO
import os
from dotenv import load_dotenv

load_dotenv()


class ImageforArenaPulse:
    def __init__(self):
        self.api_key = os.getenv("HF_TOKEN")
        self.api_url = "https://router.huggingface.co/hf-inference/models/stabilityai/stable-diffusion-xl-base-1.0"

        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def generate_image(self, prompt: str, max_retries: int = 2):

        if not prompt or not prompt.strip():
            raise ValueError("Image prompt is empty")

        genre_prefix = (
            "psychological horror, dark atmosphere, cinematic lighting, "
            "moody shadows, eerie, unsettling, high contrast, "
            "vertical composition, horror film still, "
        )

        final_prompt = genre_prefix + prompt

        payload = {
            "inputs": final_prompt,
            "parameters": {
                "width": 720,
                "height": 1280
            }
        }

        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=120
            )

            if response.status_code == 200:
                image = Image.open(BytesIO(response.content))
                image.load()
                return image

            else:
                print("HF error:", response.status_code, response.text)

        except Exception as e:
            print("Image generation error:", str(e))

        return None
