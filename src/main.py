import os
from datetime import datetime, timezone, timedelta
from processor import generate_content
from editor import create_video
from uploader import upload_to_youtube

def is_within_window():
    if os.getenv("TEST_MODE", "false").lower() == "true":
        return True
    
    # Ustawiamy strefę czasową na Polskę (UTC+1 dla zimy)
    poland_tz = timezone(timedelta(hours=1))
    now_poland = datetime.now(poland_tz)
    
    # Celujemy w 00:00, 10:00 i 20:00 czasu polskiego
    allowed_hours = [0, 10, 20]
    
    print(f"[TIME] Current Poland Time: {now_poland.strftime('%H:%M')}")
    
    if now_poland.hour in allowed_hours and now_poland.minute <= 15:
        return True
    return False

def main():
    if not is_within_window():
        print("[SKIP] Not the scheduled time in Poland.")
        return

    try:
        data = generate_content()
        video_path = create_video(data)
        upload_to_youtube(video_path, data)
    except Exception as e:
        print(f"[CRITICAL ERROR] {e}")

if __name__ == "__main__":
    main()