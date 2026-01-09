import os
import json
import google.oauth2.credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request

def get_service():
    """Authenticates using token.json and returns YouTube API service."""
    with open('token.json', 'r') as f:
        token_data = json.load(f)
    
    creds = google.oauth2.credentials.Credentials.from_authorized_user_info(token_data)
    
    # Auto-refresh token if expired
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("[UPLOADER] Token expired. Refreshing...")
            creds.refresh(Request())
            with open('token.json', 'w') as f:
                f.write(creds.to_json())
    
    return build("youtube", "v3", credentials=creds)

def upload_to_youtube(file_path, data):
    """Uploads the video file to YouTube and prints the final URL."""
    youtube = get_service()
    
    # Ensure #shorts tag is present for the algorithm
    title = data['title'] if "#shorts" in data['title'].lower() else data['title'] + " #shorts"
    
    body = {
        "snippet": {
            "title": title,
            "description": f"{data['script']}\n\n#shorts #facts #ai #knowledge",
            "categoryId": "27" # Education
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False
        }
    }
    
    print(f"[UPLOADER] Starting upload of: {file_path}")
    
    insert_request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=MediaFileUpload(file_path, chunksize=-1, resumable=True)
    )
    
    res = None
    while res is None:
        status, res = insert_request.next_chunk()
        if status:
            print(f"[UPLOADER] Uploading... {int(status.progress() * 100)}%")
            
    # Pobieranie ID i tworzenie linków
    video_id = res['id']
    short_url = f"https://www.youtube.com/shorts/{video_id}"
    full_url = f"https://www.youtube.com/watch?v={video_id}"
    
    print("-" * 30)
    print(f"[SUCCESS] Video uploaded successfully!")
    print(f"[VIDEO ID] {video_id}")
    print(f"[SHORTS URL] {short_url}")
    print(f"[WATCH URL] {full_url}")
    print("-" * 30)
    
    return video_id