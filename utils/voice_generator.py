import os
from TTS.api import TTS


class VoiceGenerator:
    def __init__(self, output_dir="outputs"):
        os.makedirs(output_dir, exist_ok=True)
        self.output_dir = output_dir

        # AI 1 - Male (VCTK multi-speaker)
        self.tts_ai1 = TTS(
            model_name="tts_models/en/vctk/vits",
            progress_bar=False,
            gpu=False
        )

        # AI 2 - Male (VCTK multi-speaker)
        self.tts_ai2 = TTS(
            model_name="tts_models/en/vctk/vits",
            progress_bar=False,
            gpu=False
        )

        # Hard-locked male speakers
        self.ai1_speaker = "p226"
        self.ai2_speaker = "p231"

    # -----------------------------
    # Generate ONE turn (AI 1)
    # -----------------------------
    def generate_ai1_chunk(self, text: str, index: int) -> str:
        output_path = os.path.join(self.output_dir, f"chunk_{index:03d}_ai1.wav")

        self.tts_ai1.tts_to_file(
            text=text,
            file_path=output_path,
            speaker=self.ai1_speaker
        )

        return output_path

    # -----------------------------
    # Generate ONE turn (AI 2)
    # -----------------------------
    def generate_ai2_chunk(self, text: str, index: int) -> str:
        output_path = os.path.join(self.output_dir, f"chunk_{index:03d}_ai2.wav")

        self.tts_ai2.tts_to_file(
            text=text,
            file_path=output_path,
            speaker=self.ai2_speaker
        )

        return output_path
