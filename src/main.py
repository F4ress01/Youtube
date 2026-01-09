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
    allowed_hours = [0, 10, 20]
    print(f"[TIME] Poland Time: {now.strftime('%H:%M')}")
    if now.hour in allowed_hours and now.minute <= 15:
        return True
    return False

def main():
    if not is_within_window():
        print("[SKIP] Waiting for the next slot (00:00, 10:00, 20:00).")
        return
    try:
        data = generate_content()
        video_path = create_video(data)
        upload_to_youtube(video_path, data)
    except Exception as e:
        print(f"[ERROR] {e}")

if __name__ == "__main__":
    main()