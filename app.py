from flask import Flask, request, jsonify, send_from_directory, render_template
import os
import subprocess
import re

FFMPEG_PATH = r"C:\Users\VINIL\ffmpeg-8.0.1-essentials_build\bin\ffmpeg.exe"

from utils.script_generator import ScriptGenerator
from utils.image_generator import ImageforArenaPulse
from utils.voice_generator import VoiceGenerator
from utils.youtube_uploader import YouTubeUploader


app = Flask(__name__)

OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)


# -------------------- helpers --------------------
def clean_for_tts(text: str) -> str:
    text = re.sub(r"[*#_>`~:-]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def merge_audio_chunks(chunk_files, output_path):
    # create ffmpeg input list
    list_file = os.path.join(OUTPUT_DIR, "audio_list.txt")
    with open(list_file, "w", encoding="utf-8") as f:
        for file in chunk_files:
            f.write(f"file '{os.path.abspath(file)}'\n")

    subprocess.run(
        [
            FFMPEG_PATH, "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", list_file,
            "-c", "copy",
            output_path
        ],
        check=True
    )

    os.remove(list_file)


# -------------------- UI --------------------
@app.route("/")
def index():
    return render_template("index.html")


# -------------------- STEP 1: Generate Script + Image + Voices --------------------
@app.route("/api/generate", methods=["POST"])
def generate():
    data = request.json
    context = data.get("topic")

    if not context:
        return jsonify({"error": "Topic is required"}), 400

    # -------- Script (TURN BASED) --------
    sg = ScriptGenerator()
    script_result = sg.generate_podcast_script(context)
    dialogue = script_result["dialogue"]

    # -------- Image --------
    img_gen = ImageforArenaPulse(context=context)
    image_prompt = img_gen.generate_image_prompt()
    image = img_gen.generate_image_arena(image_prompt)
    image.save(os.path.join(OUTPUT_DIR, "bg.png"))

    # -------- Voices (TURN BASED) --------
    vg = VoiceGenerator(output_dir=OUTPUT_DIR)
    audio_chunks = []

    for i, turn in enumerate(dialogue):
        clean_text = clean_for_tts(turn["text"])

        if turn["speaker"] == "ai1":
            path = vg.generate_ai1_chunk(clean_text, i)
        else:
            path = vg.generate_ai2_chunk(clean_text, i)

        audio_chunks.append(path)

    return jsonify({
        "status": "generated",
        "turns": len(dialogue),
        "total_words": script_result["total_words"]
    })


# -------------------- STEP 2: Render Video --------------------
@app.route("/api/render-video", methods=["POST"])
def render_video():
    bg = os.path.join(OUTPUT_DIR, "bg.png")
    combined_audio = os.path.join(OUTPUT_DIR, "combined.wav")
    output_video = os.path.join(OUTPUT_DIR, "final_video.mp4")

    # collect all chunks in order
    chunks = sorted([
        os.path.join(OUTPUT_DIR, f)
        for f in os.listdir(OUTPUT_DIR)
        if f.startswith("chunk_") and f.endswith(".wav")
    ])

    if not chunks:
        return jsonify({"error": "No audio chunks found"}), 400

    merge_audio_chunks(chunks, combined_audio)

    subprocess.run(
        [
            FFMPEG_PATH, "-y",
            "-loop", "1",
            "-i", bg,
            "-i", combined_audio,
            "-c:v", "libx264",
            "-tune", "stillimage",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            "-pix_fmt", "yuv420p",
            output_video
        ],
        check=True
    )

    return jsonify({
        "video_url": "/outputs/final_video.mp4"
    })
# -------------------- YouTube Upload --------------------
@app.route("/api/upload-youtube", methods=["POST"])
def upload_youtube():
    data = request.json or {}

    video_path = os.path.join(OUTPUT_DIR, "final_video.mp4")
    if not os.path.exists(video_path):
        return jsonify({"error": "Video not found"}), 400

    uploader = YouTubeUploader()

    response = uploader.upload_video(
        video_path=video_path,
        context=data.get("context"),  # 👈 THIS is key
        title=data.get("title"),
        description=data.get("description"),
        tags=data.get("tags", ["AI podcast"]),
        privacy_status="unlisted"
    )

    return jsonify({
        "status": "uploaded",
        "youtube_url": f"https://www.youtube.com/watch?v={response['id']}"
    })


# -------------------- Serve Output Files --------------------
@app.route("/outputs/<path:filename>")
def download_file(filename):
    return send_from_directory(OUTPUT_DIR, filename, as_attachment=True)


# -------------------- Run --------------------
if __name__ == "__main__":
    app.run(debug=True, port=5000)
