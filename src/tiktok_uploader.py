import os
import json
from tiktok_uploader.upload import upload_video

def upload_to_tiktok(video_path, data):
    """Przesyła wideo na TikToka używając sessionid."""
    session_id = os.getenv("TIKTOK_SESSION_ID")
    
    if not session_id:
        print("[TIKTOK] Brak TIKTOK_SESSION_ID w Secrets. Pomijam.")
        return

    print(f"[TIKTOK] Przygotowanie do wysyłki: {video_path}")
    
    try:
        # Budujemy opis z hashtagami
        description = f"{data['title']} #fyp #facts #ai #knowledge"
        
        # Przesyłamy film
        # Używamy ścieżki do plików cookies stworzonej w workflow
        upload_video(
            video_path,
            description=description,
            cookies='tiktok_cookies.json',
            browser='chromium',
            headless=True
        )
        print("[SUCCESS] Film pomyślnie wrzucony na TikToka!")
        
    except Exception as e:
        print(f"[TIKTOK ERROR] Wystąpił błąd podczas wysyłki: {e}")