
import json
import re
from pathlib import Path

VIDEO_FILE = Path("videos.json")


def main():
    if not VIDEO_FILE.exists():
        raise FileNotFoundError("videos.json not found!")

    videos = json.loads(
        VIDEO_FILE.read_text(encoding="utf-8")
    )

    if not isinstance(videos, list):
        raise ValueError("videos.json must contain a list.")

    valid_videos = []

    for video in videos:
        video_id = video.get("id", "")

        if not re.fullmatch(r"[A-Za-z0-9_-]{11}", video_id):
            continue

        valid_videos.append(video)

    print("Total valid YouTube videos:", len(valid_videos))

    for video in valid_videos:
        print("\nTitle:", video.get("title", ""))
        print("URL:", video.get("url", ""))

    print("\nVideo scanning completed.")
    print("No video clips were created.")
    print(
        "A YouTube URL alone does not provide "
        "the video file needed for editing."
    )


if __name__ == "__main__":
    main()
