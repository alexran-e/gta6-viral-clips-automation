
import json
import subprocess
import re
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
            print(result.stderr[-1500:])
            return False

        return True

    except Exception as error:
        print("Error:", error)
        return False


def download_video(video):
    video_id = video["id"]
    url = video["url"]

    output_file = DOWNLOAD_DIR / f"{video_id}.mp4"

    if output_file.exists():
        print("Video already downloaded:", video_id)
        return output_file

    print("\nDownloading:", video["title"])

    command = [
        "yt-dlp",
        "--no-playlist",
        "-f", "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/b",
        "--merge-output-format", "mp4",
        "-o", str(output_file),
        url
    ]

    if run_command(command) and output_file.exists():
        return output_file

    return None


def create_clip(video, input_file):
    video_id = video["id"]

    output_file = CLIPS_DIR / f"{video_id}_clip.mp4"

    if output_file.exists():
        print("Clip already exists:", output_file)
        return

    print("\nCreating vertical clip:", video["title"])

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

    if run_command(command):
        print("Clip created:", output_file)


def main():
    if not VIDEO_FILE.exists():
        print("videos.json not found!")
        return

    videos = json.loads(
        VIDEO_FILE.read_text(encoding="utf-8")
    )

    for video in videos:
        if not re.fullmatch(r"[A-Za-z0-9_-]{11}", video.get("id", "")):
            continue

        input_file = download_video(video)

        if input_file:
            create_clip(video, input_file)

    print("\nVideo processing completed!")


if __name__ == "__main__":
    main()
