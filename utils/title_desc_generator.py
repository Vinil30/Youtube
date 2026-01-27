import os
import json
import re
from dotenv import load_dotenv
from groq import Groq
from PIL import Image
from gradio_client import Client

load_dotenv()


class TitleAndDescGenerator:
    def __init__(
        self,
        context: str,
        api_key: str | None = None,
        model: str = "openai/gpt-oss-20b"
    ):
        self.context = context
        self.api_key = api_key or os.environ.get("GROQ_API_KEY_1")
        self.model = model

        if not self.api_key:
            raise ValueError("GROQ_API_KEY_1 not found in environment variables")

        # Text LLM client (Groq)
        self.text_client = Groq(api_key=self.api_key)

        # Image generation client (FLUX via HuggingFace Space)
        self.image_client = Client("black-forest-labs/FLUX.1-schnell")

        self.image_prompt = None

    # --------------------------------------------------
    # Internal: Safe JSON extraction
    # --------------------------------------------------
    def _extract_json_object(self, text: str) -> str:
        match = re.search(r"\{[\s\S]*\}", text)
        if not match:
            raise ValueError("No valid JSON object found in model output")
        return match.group(0)

    # --------------------------------------------------
    # Generate Title, Description & Thumbnail Prompt
    # --------------------------------------------------
    def generate(self) -> dict:
        system_prompt = f"""
You are an expert YouTube content strategist and growth-focused creator.

You are generating the YouTube title, description, and thumbnail prompt for the following topic:
Ghost stories that are randoly produced by ai, so give a random title and in description just mention they are entertainment purpose only and the story is not true its just an ai made fictional story

Your task is to generate EXACTLY THREE things:
1) A YouTube TITLE
2) A YouTube DESCRIPTION
3) A THUMBNAIL GENERATION PROMPT

CONTEXT:
- AI-generated Hindi ghost horror story
- Dark, eerie, suspenseful tone
- Storytelling format (single narrator)
- Voices are synthetic
- For entertainment purposes only
- Inspired by folklore and imagination
- No real incidents claimed as factual


RULES:

TITLE:
- Creepy and curiosity-driven
- No emojis
- No clickbait words like shocking, real footage, proof
- Should feel like a horror story title
- Do not subtly hint AI-generated
- Max 100 characters
- Suitable for YouTube Shorts
-Use Hinglish language


DESCRIPTION:
- MUST mention AI-generated story
- MUST say fictional / for entertainment
- MUST mention synthetic voice
- Written in simple hinglish
- 2 short paragraphs max
- Natural storytelling tone, not legal-heavy
- Include #Shorts


THUMBNAIL PROMPT:
- Visual description only
- Extremely scary and unsettling
- Horror atmosphere (dark street, abandoned place, fog, shadows)
- No readable text
- No real human faces
- Shadowy or blurred human-like silhouettes allowed
- High contrast, cinematic horror lighting
- YouTube Shorts friendly
- No misleading real-world claims


OUTPUT FORMAT (STRICT JSON ONLY):

{{
  "title": "...",
  "description": "...",
  "thumbnail_prompt": "..."
}}
"""

        response = self.text_client.chat.completions.create(
            model=self.model,
            messages=[{"role": "system", "content": system_prompt}],
            temperature=0
        )

        raw_output = response.choices[0].message.content.strip()
        clean_json = self._extract_json_object(raw_output)
        data = json.loads(clean_json)

        # Schema validation
        for key in ("title", "description", "thumbnail_prompt"):
            if key not in data:
                raise ValueError(f"Missing key '{key}' in model output")

        return data

    # --------------------------------------------------
    # Generate Thumbnail Image using FLUX
    # --------------------------------------------------
    def generate_image_arena(self, image_prompt: str) -> Image.Image:
        if not image_prompt or not image_prompt.strip():
            raise ValueError("Image prompt is empty")

        self.image_prompt = image_prompt

        result = self.image_client.predict(
            prompt=self.image_prompt,
            seed=0,
            randomize_seed=True,
            width=1280,
            height=720,
            num_inference_steps=4,
            api_name="/infer"
        )

        image_path = result[0]
        return Image.open(image_path)
    
    def generate_all(self) -> dict:
        """
        Generates title, description, thumbnail prompt,
        and also creates the thumbnail image.
        """
        data = self.generate()

        image = self.generate_image_arena(
            data["thumbnail_prompt"]
        )

        return {
            "title": data["title"],
            "description": data["description"],
            "thumbnail_prompt": data["thumbnail_prompt"],
            "thumbnail_image": image
        }
