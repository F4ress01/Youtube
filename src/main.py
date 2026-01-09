import os
from datetime import datetime, timezone, timedelta
from processor import generate_content
from editor import create_video
from uploader import upload_to_youtube

def is_within_window():
    if os.getenv("TEST_MODE", "false").lower() == "true":
        return True
    poland_tz = timezone(timedelta(hours=1)) # UTC+1
    now = datetime.now(poland_tz)
    return now.hour in [0, 10, 20] and now.minute <= 10

def main():
    if not is_within_window():
        print("[SKIP] Waiting for 00:00, 10:00 or 20:00 Poland time.")
        return
    try:
        data = generate_content()
        video_path = create_video(data)
        upload_to_youtube(video_path, data)
    except Exception as e:
        print(f"[CRITICAL ERROR] {e}")

if __name__ == "__main__":
    main()