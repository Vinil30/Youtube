from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

class Prompt_Generator:
    def __init__(self, context: str):
        self.context = context.strip()

    def generate_podcast_system_prompts(self):
        """
        Takes short / broken English context and generates
        two SYSTEM prompts for AI-1 and AI-2 to conduct a podcast.

        Constraints:
        - ~750 words per AI
        - Minimum 1200 words combined
        - Clear conclusion
        - No repetition
        """

        system_prompt_ai1 = f"""
You are Speaker 1 in a two-person podcast.

The initial topic context is written in short and improper English:
\"\"\"{self.context}\"\"\"

Your task:
- Interpret and expand the context correctly
- Start the podcast naturally
- Introduce the topic clearly and calmly
- Explain the core ideas, background, and motivation
- Maintain a conversational, podcast-style tone
-Dont generate any special symbols like #,$,%,@, etc
-DOnt generate bold sentences, use one format style
- Use short paragraphs suitable for text-to-speech
- DO NOT assume prior explanation by another speaker

Hard constraints:
- Write approximately 750 words
- Do NOT exceed 800 words
- End with a smooth handoff to Speaker 2
- Do NOT give the final conclusion of the podcast

End your response with a transition such as:
"In the next part, we’ll explore this further from another perspective."
"""

        system_prompt_ai2 = f"""
You are Speaker 2 in a two-person podcast.

The podcast topic is based on this short and improper English context:
\"\"\"{self.context}\"\"\"

Important:
- Speaker 1 has already introduced the topic
- DO NOT repeat the introduction
- DO NOT redefine basic concepts

Your task:
- Continue the podcast naturally from Speaker 1
- Expand, deepen, or contrast the discussion

- Add examples, reflections, or implications
- Maintain a calm, engaging podcast tone
- Structure content for text-to-speech delivery

Hard constraints:
- Write approximately 750 words
- Ensure the total conversation is at least 1200 words
- Provide a strong final conclusion for the entire podcast
- End with a clear takeaway or reflective closing
-Dont generate any special symbols like #,$,%,@, etc
-DOnt generate bold sentences, use one format style

You are responsible for concluding the podcast properly.
"""

        return {
            "ai1_system_prompt": system_prompt_ai1.strip(),
            "ai2_system_prompt": system_prompt_ai2.strip()
        }
