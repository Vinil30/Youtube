import edge_tts
import asyncio
import random
import os


class VoiceGenerator:
    def __init__(self, output_dir="outputs"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        # English voices (correct)
        self.voices = {
    "male": "en-US-GuyNeural",
    "female": "en-US-JennyNeural"
}


    async def _generate(self, text: str, output_path: str, voice: str):
        tts = edge_tts.Communicate(
            text=text,
            voice=voice,
            rate="-10%",   # slower = creepier
            pitch="-3Hz"   # deeper tone
        )
        await tts.save(output_path)

    def generate_story_voice(self, text: str, filename="story.wav"):
        gender = random.choice(["male", "female"])
        voice = self.voices[gender]

        output_path = os.path.join(self.output_dir, filename)

        # 🔥 IMPORTANT: Flask-safe event loop handling
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            loop.run_until_complete(
                self._generate(text, output_path, voice)
            )
        finally:
            loop.close()

        return output_path, gender
