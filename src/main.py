import os
from datetime import datetime, timezone, timedelta
from processor import generate_content
from editor import create_video
from uploader import upload_to_youtube

def is_within_window():
    if os.getenv("TEST_MODE", "false").lower() == "true":
        return True
    
    # Polska strefa czasowa (UTC+1 zimą)
    poland_tz = timezone(timedelta(hours=1))
    now = datetime.now(poland_tz)
    
    allowed_hours = [0, 10, 20]
    print(f"[TIME] Local Poland Time: {now.strftime('%H:%M')}")
    
    if now.hour in allowed_hours and now.minute <= 15:
        return True
    return False

def main():
    if not is_within_window():
        print("[SKIP] Waiting for the next 00:00, 10:00 or 20:00 slot.")
        return

    try:
        data = generate_content()
        video_path = create_video(data)
        upload_to_youtube(video_path, data)
    except Exception as e:
        print(f"[ERROR] {e}")

if __name__ == "__main__":
    main()