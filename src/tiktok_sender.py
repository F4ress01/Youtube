import os
from tiktok_uploader.upload import upload_video

def upload_to_tiktok(video_path, data):
    """Przesyła wideo na TikToka używając sessionid."""
    session_id = os.getenv("TIKTOK_SESSION_ID")
    
    if not session_id:
        print("[TIKTOK] Missing TIKTOK_SESSION_ID. Skipping.")
        return

    print(f"[TIKTOK] Starting upload to TikTok: {video_path}")
    
    try:
        # Hashtagi dla TikToka
        description = f"{data['title']} #fyp #facts #ai #knowledge"
        
        # Używamy chromium (Playwright)
        upload_video(
            video_path,
            description=description,
            cookies='tiktok_cookies.json',
            browser='chromium',
            headless=True
        )
        print("[SUCCESS] Video uploaded to TikTok!")
        
    except Exception as e:
        print(f"[TIKTOK ERROR] {e}")