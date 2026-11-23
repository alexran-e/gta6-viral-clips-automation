
import json
import subprocess
from pathlib import Path

CHANNEL_FILE = Path("channels.txt")
OUTPUT_FILE = Path("videos.json")
MAX_VIDEOS = 20


def get_channel_videos(channel_url):
    channel_url = channel_url.strip().rstrip("/") + "/videos"

    print(f"\nChecking: {channel_url}")

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

                if not video_id or video.get("_type") == "playlist":
                    continue

                videos.append({
                    "id": video_id,
                    "title": video.get("title", ""),
                    "url": f"https://www.youtube.com/watch?v={video_id}",
                    "channel": channel_url.replace("/videos", "")
                })

            except json.JSONDecodeError:
                continue

        if result.returncode != 0:
            print("Warning:", result.stderr[-500:])

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
        for line in CHANNEL_FILE.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]

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
            pass

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
    print("Videos found:", len(all_videos))
    print("New videos:", len(new_videos))


if __name__ == "__main__":
    main()
