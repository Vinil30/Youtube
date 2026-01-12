from groq import Groq
import os
import json
from dotenv import load_dotenv

load_dotenv()


class ScriptGenerator:
    def __init__(self, model="llama-3.1-8b-instant"):
        self.client = Groq(api_key=os.environ.get("GROQ_API_KEY_1"))
        self.model = model

    def _extract_first_json_array(self, text: str) -> str:
        """
        Extract ONLY the first complete JSON array using bracket depth tracking.
        Handles:
        - Extra text before/after
        - Multiple arrays
        - Model commentary
        """
        start = text.find("[")
        if start == -1:
            raise ValueError("No JSON array start found")

        depth = 0
        for i in range(start, len(text)):
            if text[i] == "[":
                depth += 1
            elif text[i] == "]":
                depth -= 1
                if depth == 0:
                    return text[start:i + 1]

        raise ValueError("No complete JSON array found")

    def generate_podcast_script(self, context: str):
        system_prompt = f"""
You are generating a TWO PERSON PODCAST conversation.

Topic written in short broken English
\"\"\"{context}\"\"\"

Rules STRICT
Two speakers ai1 and ai2
Strict alternation ai1 ai2 ai1 ai2
Each turn two to three short sentences only
Tone natural calm thoughtful podcast discussion
No markdown
No special symbols
No headings
Plain spoken English only
Total length between 1200 and 1500 words
ai2 must give final conclusion

Output format
Return ONLY valid JSON array like

[
  {{ "speaker": "ai1", "text": "..." }},
  {{ "speaker": "ai2", "text": "..." }}
]
"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "system", "content": system_prompt}],
            temperature=0.7,
            max_tokens=3500
        )

        raw_output = response.choices[0].message.content.strip()

        # Attempt 1
        try:
            clean_json = self._extract_first_json_array(raw_output)
            dialogue = json.loads(clean_json)

        # Attempt 2 (self-healing)
        except Exception:
            repair_prompt = f"""
Convert the following into ONE valid JSON array ONLY.
Do not add or remove content.
No explanations.

Text:
{raw_output}
"""

            repair_response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": repair_prompt}],
                temperature=0,
                max_tokens=3500
            )

            repaired_output = repair_response.choices[0].message.content.strip()
            clean_json = self._extract_first_json_array(repaired_output)
            dialogue = json.loads(clean_json)

        return {
            "dialogue": dialogue,
            "total_turns": len(dialogue),
            "total_words": sum(len(turn["text"].split()) for turn in dialogue)
        }
