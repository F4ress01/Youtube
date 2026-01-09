import os
import google.oauth2.credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request

def get_service():
    creds = None
    if os.path.exists('token.json'):
        creds = google.oauth2.credentials.Credentials.from_authorized_user_file('token.json')
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        else:
            raise Exception("No valid token.json found.")
    return build("youtube", "v3", credentials=creds)

def upload_to_youtube(file_path, data):
    youtube = get_service()
    body = {
        "snippet": {"title": data['title'], "description": data['script'], "categoryId": "27"},
        "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False}
    }
    
    insert_request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=MediaFileUpload(file_path, chunksize=-1, resumable=True)
    )
    
    print("Uploading to YouTube...")
    response = None
    while response is None:
        status, response = insert_request.next_chunk()
    print(f"Done! Video ID: {response['id']}")