from openai import OpenAI
from dotenv import load_dotenv
import os
import re
import json
import time

load_dotenv()


class GhostStoryGenerator:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.environ.get("API_KEY"),
            base_url="https://api.groq.com/openai/v1"
        )

    # --------------------------------------------------
    # Clean ONLY story text for TTS
    # --------------------------------------------------
    def _clean_story_for_tts(self, text: str) -> str:
        text = re.sub(r"[*_#>`~]", "", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    # --------------------------------------------------
    # Extract JSON safely from model output
    # --------------------------------------------------
    def _extract_json(self, raw_text: str) -> dict:
        try:
            return json.loads(raw_text)
        except json.JSONDecodeError:
            # Try to extract JSON block manually
            match = re.search(r"\{.*\}", raw_text, re.DOTALL)
            if match:
                return json.loads(match.group())
            raise RuntimeError("Model did not return valid JSON.")

    # --------------------------------------------------
    # Validate required fields
    # --------------------------------------------------
    def _validate_schema(self, data: dict):
        required = ("story", "title", "description", "thumbnail_prompt")
        for key in required:
            if key not in data or not str(data[key]).strip():
                raise ValueError(f"Missing or empty field: {key}")

    # --------------------------------------------------
    # Main generator
    # --------------------------------------------------
    def generate(self, context: str) -> dict:

        system_prompt = f"""
You are a professional English horror storyteller and YouTube content creator.

Generate ONE complete ghost story meant to be narrated by ONE person,
along with its title, description, and thumbnail image prompt.

All outputs MUST describe the SAME setting, SAME unseen threat, and SAME atmosphere.

STORY:
- Plain spoken English
- Slow-burn psychological horror
- 280–340 words
- Unsettling ending
- No markdown or emojis

TITLE:
- Creepy and curiosity-driven
- Max 100 characters

DESCRIPTION:
- Must mention AI-generated story
- Must mention fictional
- Must mention synthetic voice
- Include #Shorts

THUMBNAIL PROMPT:
- Visual description only
- Extremely scary
- No text
- No real human faces
- Cinematic lighting

OUTPUT STRICTLY IN THIS JSON FORMAT:

{{
  "story": "...",
  "title": "...",
  "description": "...",
  "thumbnail_prompt": "..."
}}

Context:
{context}
"""

        max_attempts = 2

        for attempt in range(max_attempts):
            try:
                response = self.client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": context or "Generate a ghost story"}
                    ],
                    temperature=0.6,
                    max_tokens=1500  # reduced from 2200 (safer)
                )

                raw_output = response.choices[0].message.content

                data = self._extract_json(raw_output)

                # Clean story for TTS
                data["story"] = self._clean_story_for_tts(data["story"])

                # Validate fields
                self._validate_schema(data)

                return data

            except Exception as e:
                print(f"Attempt {attempt+1} failed:", str(e))
                time.sleep(1)

        raise RuntimeError("Story generation failed after retries.")
