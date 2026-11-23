import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone

CHANNEL_FILE = Path("channels.txt")
OUTPUT_FILE = Path("videos.json")
MAX_VIDEOS = 10


def get_channel_videos(channel_url):
    print(f"\nChecking channel: {channel_url}")

    command = [
        "yt-dlp",
        "--flat-playlist",
        "--dump-single-json",
        "--playlist-end", str(MAX_VIDEOS),
        channel_url
    ]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=180
        )

        if result.returncode != 0:
            print("Channel scan failed:", result.stderr[:300])
            return []

        data = json.loads(result.stdout)
        videos = []

        for video in data.get("entries", []):
            if not video:
                continue

            video_id = video.get("id")

            if not video_id:
                continue

            videos.append({
                "id": video_id,
                "title": video.get("title", ""),
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "channel": channel_url
            })

        return videos

    except Exception as error:
        print("Error:", error)
        return []


def main():
    if not CHANNEL_FILE.exists():
        print("channels.txt not found!")
        return

    channels = [
        line.strip()
        for line in CHANNEL_FILE.read_text(
            encoding="utf-8"
        ).splitlines()
        if line.strip() and not line.startswith("#")
    ]

    if not channels:
        print("No YouTube channels added yet.")
        return

    all_videos = []

    for channel in channels:
        all_videos.extend(get_channel_videos(channel))

    old_videos = []

    if OUTPUT_FILE.exists():
        try:
            old_videos = json.loads(
                OUTPUT_FILE.read_text(encoding="utf-8")
            )
        except Exception:
            old_videos = []

    existing_ids = {v["id"] for v in old_videos}
    new_videos = [
        v for v in all_videos
        if v["id"] not in existing_ids
    ]

    combined = old_videos + new_videos

    OUTPUT_FILE.write_text(
        json.dumps(combined, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    print("\nScan completed!")
    print("Channels checked:", len(channels))
    print("New videos found:", len(new_videos))
    print("Total saved videos:", len(combined))


if __name__ == "__main__":
    main()
