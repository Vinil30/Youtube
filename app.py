from flask import Flask, request, jsonify, send_from_directory, render_template
import os
import subprocess
import re

FFMPEG_PATH = r"C:\Users\VINIL\ffmpeg-8.0.1-essentials_build\bin\ffmpeg.exe"

from utils.script_generator import GhostStoryGenerator
from utils.image_generator import ImageforArenaPulse
from utils.voice_generator import VoiceGenerator
from utils.youtube_uploader import YouTubeUploader


app = Flask(__name__)

OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --------------------------------------------------
# Helpers
# --------------------------------------------------
def clean_for_tts(text: str) -> str:
    text = re.sub(r"[*#_>`~:-]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# --------------------------------------------------
# UI
# --------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html")


# --------------------------------------------------
# STEP 1: Generate Story + Image + Voice
# --------------------------------------------------
@app.route("/api/generate", methods=["POST"])
def generate():
    data = request.json or {}
    context = data.get("topic") or "Ghost story with real places included"

    # -------- Unified Script Generation --------
    sg = GhostStoryGenerator()
    creative = sg.generate(context)

    story_text = clean_for_tts(creative["story"])
    title = creative["title"]
    description = creative["description"]
    image_prompt = creative["thumbnail_prompt"]

    # -------- Image --------
    img_gen = ImageforArenaPulse()
    image = img_gen.generate_image(image_prompt)
    image.save(os.path.join(OUTPUT_DIR, "bg.png"))

    # -------- Voice (STORY ONLY) --------
    vg = VoiceGenerator(output_dir=OUTPUT_DIR)
    audio_path, gender = vg.generate_story_voice(
        text=story_text,
        filename="story.wav"
    )

    # Store metadata for later upload step
    with open(os.path.join(OUTPUT_DIR, "meta.txt"), "w", encoding="utf-8") as f:
        f.write(title + "\n")
        f.write(description)

    return jsonify({
        "status": "generated",
        "voice_gender": gender,
        "story_words": len(story_text.split())
    })


# --------------------------------------------------
# STEP 2: Render Video
# --------------------------------------------------
@app.route("/api/render-video", methods=["POST"])
def render_video():
    bg = os.path.join(OUTPUT_DIR, "bg.png")
    audio = os.path.join(OUTPUT_DIR, "story.wav")
    output_video = os.path.join(OUTPUT_DIR, "final_video.mp4")

    if not os.path.exists(bg) or not os.path.exists(audio):
        return jsonify({"error": "Image or audio missing"}), 400

    subprocess.run(
        [
            FFMPEG_PATH, "-y",
            "-loop", "1",
            "-i", bg,
            "-i", audio,
            "-vf", "scale=1080:1920,setsar=1",
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


# --------------------------------------------------
# STEP 3: Upload to YouTube
# --------------------------------------------------
@app.route("/api/upload-youtube", methods=["POST"])
def upload_youtube():
    video_path = os.path.join(OUTPUT_DIR, "final_video.mp4")
    meta_path = os.path.join(OUTPUT_DIR, "meta.txt")

    if not os.path.exists(video_path):
        return jsonify({"error": "Video not found"}), 400

    if not os.path.exists(meta_path):
        return jsonify({"error": "Metadata not found"}), 400

    with open(meta_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        title = lines[0].strip()
        description = "".join(lines[1:]).strip()

    uploader = YouTubeUploader()
    response = uploader.upload_video(
        video_path=video_path,
        title=title,
        description=description,
        tags=["AI Horror", "Ghost Story"],
        privacy_status="public"
    )

    return jsonify({
        "status": "uploaded",
        "youtube_url": f"https://www.youtube.com/watch?v={response['id']}"
    })


# --------------------------------------------------
# Serve Output Files
# --------------------------------------------------
@app.route("/outputs/<path:filename>")
def download_file(filename):
    return send_from_directory(OUTPUT_DIR, filename, as_attachment=True)


# --------------------------------------------------
# Run
# --------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True, port=5000)
