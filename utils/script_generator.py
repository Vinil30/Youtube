from openai import OpenAI
from dotenv import load_dotenv
import os
import re

load_dotenv()


class GhostStoryGenerator:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.environ.get("API_KEY"),
            base_url="https://api.groq.com/openai/v1"
        )

    def _clean_text(self, text: str) -> str:
        """
        Remove markdown, symbols, emojis, etc.
        Keep only spoken-language safe text.
        """
        text = re.sub(r"[*_#>`~\[\]{}()]", "", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def generate_story(self, context: str) -> str:
        system_prompt = f"""
You are a professional hindi horror storyteller.

Generate ONE complete ghost story meant to be narrated by ONE person.
Generate Hindi Horror Story of your choice, but just make sure to add real famous place names such that people could connect.
Rules STRICT:
- Plain spoken Hindi only
- No markdown
- No special symbols
- No emojis
- No headings
- No formatting
- Natural pauses using commas and full stops only
- Creepy, slow-burn horror
- Ending must be unsettling

Duration constraint:
- Story must fit within  1.5 to 2 minutes of narration
- Approx 280 to 340 words

Context:
{context}
"""

        response = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": context or "Generate a story"}
    ],
            temperature=0.8,
            max_tokens=900
        )

        raw_story = response.choices[0].message.content
        return self._clean_text(raw_story)
