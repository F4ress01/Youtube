import os
from tiktok_uploader.upload import upload_video

def upload_to_tiktok(video_path, data):
    """Przesyła wideo na TikToka używając ciasteczka sessionid."""
    session_id = os.getenv("TIKTOK_SESSION_ID")
    
    if not session_id:
        print("[TIKTOK] Brak TIKTOK_SESSION_ID w Secrets. Pomijam TikTok.")
        return

    print(f"[TIKTOK] Przygotowanie do wysyłki: {video_path}")
    
    try:
        # Tytuł filmu + hashtagi
        description = f"{data['title']} #fyp #facts #ai #knowledge"
        
        # Przesyłamy film używając wygenerowanego pliku cookies
        # browser='chromium' jest kluczowy dla Playwright
        upload_video(
            video_path,
            description=description,
            cookies='tiktok_cookies.json',
            browser='chromium',
            headless=True
        )
        print("[SUCCESS] Film pomyślnie wrzucony na TikToka!")
        
    except Exception as e:
        print(f"[TIKTOK ERROR] Wystąpił błąd: {e}")