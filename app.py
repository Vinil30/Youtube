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
        context = "Ghost story with real places included"

    # -------- Script (SINGLE STORY) --------
    sg = GhostStoryGenerator()
    story_text = sg.generate_story(context)
    story_text = clean_for_tts(story_text)

    # -------- Image --------
    img_gen = ImageforArenaPulse(context=context)
    image_prompt = img_gen.generate_image_prompt()
    image = img_gen.generate_image_arena(image_prompt)
    image.save(os.path.join(OUTPUT_DIR, "bg.png"))

    # -------- Voice (SINGLE SPEAKER) --------
    vg = VoiceGenerator(output_dir=OUTPUT_DIR)
    audio_path, gender = vg.generate_story_voice(
        text=story_text,
        filename="story.wav"
    )

    return jsonify({
        "status": "generated",
        "voice_gender": gender,
        "story_words": len(story_text.split())
    })



# -------------------- STEP 2: Render Video --------------------
@app.route("/api/render-video", methods=["POST"])
def render_video():
    bg = os.path.join(OUTPUT_DIR, "bg.png")
    audio = os.path.join(OUTPUT_DIR, "story.wav")
    output_video = os.path.join(OUTPUT_DIR, "final_video.mp4")

    if not os.path.exists(audio):
        return jsonify({"error": "Audio not found"}), 400

    subprocess.run(
    [
        FFMPEG_PATH, "-y",
        "-loop", "1",
        "-i", bg,
        "-i", audio,

        # 🔽 ADD THIS
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

# -------------------- YouTube Upload --------------------
@app.route("/api/upload-youtube", methods=["POST"])
def upload_youtube():
    data = request.json or {}

    topic = data.get("topic")
    if not topic:
        topic = "Ghost story with real places included"

    video_path = os.path.join(OUTPUT_DIR, "final_video.mp4")
    if not os.path.exists(video_path):
        return jsonify({"error": "Video not found"}), 400

    uploader = YouTubeUploader()

    response = uploader.upload_video(
        video_path=video_path,
        context=topic,   # ✅ THIS IS ENOUGH
        tags=["Artificial Intelligence"],
        privacy_status="public"
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
