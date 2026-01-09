import os
from datetime import datetime, timezone, timedelta
from processor import generate_content
from editor import create_video
from uploader import upload_to_youtube
from tiktok_uploader import upload_to_tiktok

def is_within_window():
    if os.getenv("TEST_MODE", "false").lower() == "true":
        return True
    # Czas Polski (UTC+1)
    poland_tz = timezone(timedelta(hours=1))
    now = datetime.now(poland_tz)
    # 00:00, 10:00, 20:00
    return now.hour in [0, 10, 20] and now.minute <= 15

def main():
    if not is_within_window():
        print("[SKIP] Czekam na okno czasowe (00, 10, 20).")
        return

    try:
        print("[SYSTEM] Rozpoczynam generowanie treści...")
        data = generate_content()
        
        print("[SYSTEM] Rozpoczynam montaż wideo...")
        video_path = create_video(data)
        
        print("[SYSTEM] Wysyłka na YouTube...")
        upload_to_youtube(video_path, data)
        
        print("[SYSTEM] Wysyłka na TikTok...")
        upload_to_tiktok(video_path, data)
        
    except Exception as e:
        print(f"[CRITICAL ERROR] {e}")

if __name__ == "__main__":
    main()