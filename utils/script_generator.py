from openai import OpenAI
from dotenv import load_dotenv
import os
import re
import json

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
    # Main generator
    # --------------------------------------------------
    def generate(self, context: str) -> dict:
        system_prompt = f"""
You are a professional English horror storyteller and YouTube content creator.

Generate ONE complete ghost story meant to be narrated by ONE person,
along with its title, description, and thumbnail image prompt.

All outputs MUST describe the SAME setting, SAME unseen threat, and SAME atmosphere.

--------------------
STORY RULES:
- Plain spoken English only
- No markdown, emojis, or headings
- Creepy, slow-burn psychological horror
- Ending must be unsettling
- Natural pauses using commas and full stops only

Duration:
- 1.5 to 2 minutes narration
- Approximately 280 to 340 words

--------------------
TITLE RULES:
- Creepy and curiosity-driven
- No emojis or clickbait words
- Max 100 characters

--------------------
DESCRIPTION RULES:
- MUST mention AI-generated story
- MUST say fictional / for entertainment
- MUST mention synthetic voice
- Simple English
- Max 2 short paragraphs
- Include #Shorts

--------------------
THUMBNAIL PROMPT RULES:
- Visual description only
- Extremely scary and unsettling
- Dark horror atmosphere
- No text
- No real human faces
- Cinematic lighting
- Vertical friendly

--------------------
OUTPUT FORMAT (STRICT JSON ONLY):

{{
  "story": "...",
  "title": "...",
  "description": "...",
  "thumbnail_prompt": "..."
}}

Context:
{context}
"""

        response = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": context or "Generate a ghost story"}
            ],
            temperature=0.6,
            max_tokens=1800,
            response_format={"type": "json_object"}
        )

        # API already guarantees valid JSON
        data = json.loads(response.choices[0].message.content)

        # Clean story ONLY for TTS
        data["story"] = self._clean_story_for_tts(data["story"])

        # Validate schema
        for key in ("story", "title", "description", "thumbnail_prompt"):
            if key not in data or not data[key].strip():
                raise ValueError(f"Missing or empty field: {key}")

        return data
