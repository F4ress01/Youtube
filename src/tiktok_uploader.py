import os
from tiktok_uploader.upload import upload_video

def upload_to_tiktok(video_path, data):
    """Przesyła wideo na TikToka używając sessionid i Playwrighta."""
    session_id = os.getenv("TIKTOK_SESSION_ID")
    
    if not session_id:
        print("[TIKTOK] Brak TIKTOK_SESSION_ID w Secrets. Pomijam.")
        return

    print(f"[TIKTOK] Przygotowanie do wysyłki: {video_path}")
    
    try:
        # Budujemy opis z hashtagami
        description = f"{data['title']} #fyp #facts #ai #knowledge"
        
        # Kluczowe ustawienie: browser='chromium' (Playwright)
        # headless=True jest wymagane na serwerze bez monitora
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