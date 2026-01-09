import os
from datetime import datetime, timezone
from processor import generate_content
from editor import create_video
from uploader import upload_to_youtube

def is_within_window():
    if os.getenv("TEST_MODE", "false").lower() == "true":
        return True
    now = datetime.now(timezone.utc)
    return now.hour in [0, 10, 20] and now.minute <= 5

def main():
    start = datetime.now(timezone.utc)
    print(f"--- Cycle Start: {start.strftime('%Y-%m-%d %H:%M:%S UTC')} ---")
    
    if not is_within_window():
        print("[SKIP] Outside schedule.")
        return

    try:
        data = generate_content()
        video_path = create_video(data)
        upload_to_youtube(video_path, data)
    except Exception as e:
        print(f"[CRITICAL ERROR] {e}")

    print(f"--- Cycle End. Duration: {datetime.now(timezone.utc) - start} ---")

if __name__ == "__main__":
    main()