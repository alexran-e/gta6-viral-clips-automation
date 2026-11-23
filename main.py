
import json
import re
import subprocess
from pathlib import Path

VIDEO_FILE = Path("videos.json")
DOWNLOAD_DIR = Path("downloads")
CLIPS_DIR = Path("clips")

CLIP_DURATION = 45

DOWNLOAD_DIR.mkdir(exist_ok=True)
CLIPS_DIR.mkdir(exist_ok=True)


def run_command(command):
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=900
        )

        if result.returncode != 0:
            print("\nCOMMAND FAILED:")
            print(result.stderr[-2000:])
            raise RuntimeError("Video processing failed!")

        return True

    except subprocess.TimeoutExpired:
        raise RuntimeError("Operation timed out!")


def download_video(video):
    video_id = video["id"]
    output_file = DOWNLOAD_DIR / f"{video_id}.mp4"

    if output_file.exists():
        print("Already downloaded:", video_id)
        return output_file

    print("\nDownloading:", video.get("title", ""))

    command = [
        "yt-dlp",
        "--no-playlist",
        "--js-runtimes", "deno",
        "-f", "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/b",
        "--merge-output-format", "mp4",
        "-o", str(output_file),
        video["url"]
    ]

    run_command(command)

    if not output_file.exists():
        raise FileNotFoundError("Downloaded video file not found!")

    return output_file


def create_clip(video, input_file):
    video_id = video["id"]
    output_file = CLIPS_DIR / f"{video_id}_clip.mp4"

    if output_file.exists():
        print("Clip already exists:", output_file)
        return

    print("\nCreating vertical clip:", video.get("title", ""))

    command = [
        "ffmpeg",
        "-y",
        "-ss", "0",
        "-i", str(input_file),
        "-t", str(CLIP_DURATION),
        "-vf",
        "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "23",
        "-c:a", "aac",
        "-b:a", "128k",
        "-movflags", "+faststart",
        str(output_file)
    ]

    run_command(command)

    if not output_file.exists():
        raise FileNotFoundError("Clip was not created!")

    print("SUCCESS! Clip created:", output_file)


def main():
    if not VIDEO_FILE.exists():
        raise FileNotFoundError("videos.json not found!")

    videos = json.loads(
        VIDEO_FILE.read_text(encoding="utf-8")
    )

    if not isinstance(videos, list):
        raise ValueError("videos.json must contain a list!")

    if not videos:
        raise ValueError("No videos found in videos.json!")

    for video in videos:
        video_id = video.get("id", "")

        if not re.fullmatch(r"[A-Za-z0-9_-]{11}", video_id):
            print("Skipping invalid video ID:", video_id)
            continue

        input_file = download_video(video)
        create_clip(video, input_file)

    print("\nALL VIDEO PROCESSING COMPLETED!")


if __name__ == "__main__":
    main()
