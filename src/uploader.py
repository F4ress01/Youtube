import os
import json
import google.oauth2.credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request

def get_service():
    with open('token.json', 'r') as f:
        token_data = json.load(f)
    creds = google.oauth2.credentials.Credentials.from_authorized_user_info(token_data)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open('token.json', 'w') as f: f.write(creds.to_json())
    return build("youtube", "v3", credentials=creds)

def upload_to_youtube(file_path, data):
    youtube = get_service()
    title = data['title'] if "#shorts" in data['title'].lower() else data['title'] + " #shorts"
    
    body = {
        "snippet": {
            "title": title, 
            "description": f"{data['script']}\n\n#shorts #facts #ai", 
            "categoryId": "27"
        },
        "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False}
    }
    
    print(f"[UPLOADER] Starting upload...")
    insert_request = youtube.videos().insert(
        part="snippet,status", body=body,
        media_body=MediaFileUpload(file_path, chunksize=-1, resumable=True)
    )
    
    res = None
    while res is None:
        status, res = insert_request.next_chunk()
        if status:
            print(f"[UPLOADER] Uploading... {int(status.progress() * 100)}%")
            
    video_id = res['id']
    print("-" * 30)
    print(f"[SUCCESS] Video Uploaded!")
    print(f"[URL] https://www.youtube.com/shorts/{video_id}")
    print("-" * 30)
    return video_id