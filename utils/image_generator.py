import os
import requests
from PIL import Image
from io import BytesIO
import time


class ImageforArenaPulse:
    def __init__(self):
        self.base_url = "https://image.pollinations.ai/prompt"
        
    def generate_image(self, prompt: str, max_retries: int = 3) -> Image.Image:
        """
        Generate image using Pollinations.AI (free, no API key needed)
        """
        if not prompt or not prompt.strip():
            raise ValueError("Image prompt is empty")

        # URL encode the prompt
        encoded_prompt = requests.utils.quote(prompt.strip())
        
        # Build URL with parameters
        url = f"{self.base_url}/{encoded_prompt}"
        params = {
            'width': 720,
            'height': 1280,
            'seed': -1,  # Random seed
            'model': 'flux',  # Use FLUX model
            'nologo': 'true'
        }
        
        last_error = None
        
        for attempt in range(max_retries):
            try:
                print(f"  Generating image via Pollinations.AI (attempt {attempt + 1}/{max_retries})...")
                
                response = requests.get(url, params=params, timeout=60)
                
                if response.status_code == 200:
                    image = Image.open(BytesIO(response.content))
                    print(f"  ✓ Image generated successfully ({image.size})")
                    return image
                else:
                    raise RuntimeError(f"API returned status code {response.status_code}")
                    
            except Exception as e:
                last_error = e
                print(f"  ⚠ Attempt {attempt + 1} failed: {str(e)}")
                
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 2
                    print(f"  Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
        
        raise RuntimeError(f"Image generation failed after {max_retries} attempts: {last_error}")