import os
import sys
import time
from datetime import datetime, timezone
from processor import generate_content
from editor import create_video
from uploader import upload_to_youtube

def is_within_window():
    # TEST_MODE check: if 'true', ignore clock
    if os.getenv("TEST_MODE", "false").lower() == "true":
        print("[!] TEST_MODE is ENABLED. Bypassing schedule check.")
        return True
    
    now = datetime.now(timezone.utc)
    allowed_hours = [0, 10, 20]
    
    # Check if current hour is allowed and within the first 3 minutes
    if now.hour in allowed_hours and now.minute <= 3:
        return True
    return False

def main():
    start_time = datetime.now(timezone.utc)
    print(f"--- Automation Cycle Started: {start_time.strftime('%Y-%m-%d %H:%M:%S UTC')} ---")
    
    if not is_within_window():
        print(f"Current time {start_time.strftime('%H:%M')} UTC is outside allowed windows. Exiting.")
        return

    try:
        # 1. Generate unique script and word-level timestamps via edge-tts
        print("[1/3] Generating Script and TTS...")
        script_data = generate_content()
        
        # 2. Render Video with Random Rotation and Zoom
        print("[2/3] Rendering Video with FFmpeg...")
        video_path = create_video(script_data)
        
        # 3. Upload to YouTube
        if video_path and os.path.exists(video_path):
            print("[3/3] Uploading to YouTube...")
            upload_to_youtube(video_path, script_data)
        else:
            print("[ERROR] Video file not found. Skipping upload.")

    except Exception as e:
        print(f"[CRITICAL ERROR] {str(e)}")
    
    end_time = datetime.now(timezone.utc)
    duration = end_time - start_time
    print(f"--- Automation Cycle Ended: {end_time.strftime('%Y-%m-%d %H:%M:%S UTC')} ---")
    print(f"Total Duration: {duration}")

if __name__ == "__main__":
    main()