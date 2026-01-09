import os
from datetime import datetime, timezone
from processor import generate_content
from editor import create_video
from uploader import upload_to_youtube

def is_within_window():
    # Bypass timing if TEST_MODE is enabled in GitHub Secrets/Env
    if os.getenv("TEST_MODE", "false").lower() == "true":
        print("[INFO] TEST_MODE enabled. Bypassing schedule.")
        return True
    
    now = datetime.now(timezone.utc)
    # Allowed UTC hours for upload
    allowed_hours = [0, 10, 20]
    
    if now.hour in allowed_hours and now.minute <= 5:
        return True
    return False

def main():
    start_ts = datetime.now(timezone.utc)
    print(f"--- Cycle Start: {start_ts.strftime('%Y-%m-%d %H:%M:%S UTC')} ---")
    
    if not is_within_window():
        print(f"[SKIP] Current time {start_ts.strftime('%H:%M')} is not in schedule.")
        return

    try:
        # Step 1: Generate Script and TTS
        data = generate_content()
        
        # Step 2: Render Video
        video_path = create_video(data)
        
        # Step 3: Upload
        if video_path:
            upload_to_youtube(video_path, data)
            
    except Exception as e:
        print(f"[CRITICAL ERROR] {e}")

    end_ts = datetime.now(timezone.utc)
    print(f"--- Cycle End. Duration: {end_ts - start_ts} ---")

if __name__ == "__main__":
    main()