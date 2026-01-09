import os
import json
import google.oauth2.credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request

def validate_json_file(file_path):
    """Checks if a file is a valid JSON to prevent crash"""
    if not os.path.exists(file_path):
        raise Exception(f"File {file_path} is missing!")
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"[ERROR] {file_path} is not a valid JSON: {e}")
        # Print a snippet of the problematic file for debugging (hiding sensitive data)
        with open(file_path, 'r') as f:
            content = f.read().strip()
            snippet = content[:20] + "..." if len(content) > 20 else content
            print(f"[DEBUG] Start of {file_path} looks like: {snippet}")
        raise Exception(f"Corrupted JSON in {file_path}")

def get_service():
    # Validate files before use
    validate_json_file('client_secrets.json')
    token_data = validate_json_file('token.json')
    
    creds = google.oauth2.credentials.Credentials.from_authorized_user_info(token_data)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("[UPLOADER] Token expired, refreshing...")
            creds.refresh(Request())
            # Save refreshed token
            with open('token.json', 'w') as token_file:
                token_file.write(creds.to_json())
        else:
            raise Exception("Token is invalid and cannot be refreshed. Re-generate token.json locally.")

    return build("youtube", "v3", credentials=creds)

def upload_to_youtube(file_path, data):
    try:
        youtube = get_service()
        
        body = {
            "snippet": {
                "title": data['title'],
                "description": data['script'] + "\n\n#shorts #facts #amazing",
                "categoryId": "27" # Education
            },
            "status": {
                "privacyStatus": "public",
                "selfDeclaredMadeForKids": False
            }
        }
        
        print(f"[UPLOADER] Starting upload: {file_path}")
        
        insert_request = youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=MediaFileUpload(file_path, chunksize=-1, resumable=True)
        )
        
        response = None
        while response is None:
            status, response = insert_request.next_chunk()
            if status:
                print(f"[UPLOADER] Uploading... {int(status.progress() * 100)}%")
                
        print(f"[SUCCESS] Video uploaded! ID: {response['id']}")
        return response['id']
        
    except Exception as e:
        print(f"[UPLOADER ERROR] {e}")
        raise e