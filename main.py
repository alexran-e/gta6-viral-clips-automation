
import json
import re
import subprocess
from pathlib import Path

CHANNEL_FILE = Path("channels.txt")
OUTPUT_FILE = Path("videos.json")

MAX_VIDEOS = 20

GTA_KEYWORDS = [
    "gta 6",
    "gta vi",
    "grand theft auto 6",
    "grand theft auto vi",
    "gta6",
    "gta 6 gameplay",
    "gta 6 trailer",
    "gta 6 funny moments",
    "gta 6 online"
]


def get_channel_videos(channel_url):
    channel_url = channel_url.strip().rstrip("/") + "/videos"

    print(f"\nChecking channel: {channel_url}")

    command = [
        "yt-dlp",
        "--flat-playlist",
        "--dump-json",
        "--playlist-end", str(MAX_VIDEOS),
        channel_url
    ]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=300
        )

        videos = []

        for line in result.stdout.splitlines():
            try:
                video = json.loads(line)

                video_id = video.get("id")
                title = video.get("title", "").strip()

                # Only accept real YouTube video IDs
                if not video_id or not re.fullmatch(r"[A-Za-z0-9_-]{11}", video_id):
                    continue

                # Ignore videos unrelated to GTA 6 by title
                title_lower = title.lower()

                if not any(keyword in title_lower for keyword in GTA_KEYWORDS):
                    continue

                videos.append({
                    "id": video_id,
                    "title": title,
                    "url": f"https://www.youtube.com/watch?v={video_id}",
                    "channel": channel_url.replace("/videos", "")
                })

            except json.JSONDecodeError:
                continue

        if result.returncode != 0:
            print("Warning:", result.stderr[-500:])

        print("GTA 6 videos found:", len(videos))

        return videos

    except subprocess.TimeoutExpired:
        print("Error: Channel scan timed out.")
        return []

    except Exception as error:
        print("Error:", error)
        return []


def main():

    if not CHANNEL_FILE.exists():
        print("ERROR: channels.txt not found!")
        return

    channels = [
        line.strip()
        for line in CHANNEL_FILE.read_text(
            encoding="utf-8"
        ).splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]

    all_videos = []
    seen_ids = set()

    for channel in channels:

        channel_videos = get_channel_videos(channel)

        for video in channel_videos:

            if video["id"] not in seen_ids:
                all_videos.append(video)
                seen_ids.add(video["id"])

    OUTPUT_FILE.write_text(
        json.dumps(
            all_videos,
            indent=2,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )

    print("\n========== SCAN COMPLETED ==========")
    print("Channels checked:", len(channels))
    print("GTA 6 videos found:", len(all_videos))
    print("Database updated:", OUTPUT_FILE)
    print("====================================")


if __name__ == "__main__":
    main()
