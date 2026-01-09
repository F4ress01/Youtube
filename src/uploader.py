import os
import json
import google.oauth2.credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request

def validate_json_content(file_path):
    """Checks if the JSON file is valid to prevent crashes during upload"""
    if not os.path.exists(file_path):
        raise Exception(f"Missing file: {file_path}")
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"[UPLOADER ERROR] {file_path} is corrupted: {e}")
        # Show first characters for debugging
        with open(file_path, 'r') as f:
            content = f.read().strip()
            print(f"[DEBUG] Raw content start: {content[:30]}...")
        raise Exception(f"Invalid JSON format in {file_path}")

def get_service():
    """Authenticates and returns the YouTube API service"""
    # Validate both files before starting
    validate_json_content('client_secrets.json')
    token_data = validate_json_content('token.json')
    
    creds = google.oauth2.credentials.Credentials.from_authorized_user_info(token_data)
    
    # If token is expired, refresh it automatically
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("[UPLOADER] Token expired. Refreshing access...")
            creds.refresh(Request())
            # Save the new token back to token.json for future runs
            with open('token.json', 'w') as token_file:
                token_file.write(creds.to_json())
        else:
            raise Exception("Token is invalid and cannot be refreshed. Please re-run auth.py locally.")

    return build("youtube", "v3", credentials=creds)

def upload_to_youtube(file_path, data):
    """Uploads the final video to YouTube with Shorts optimization"""
    try:
        youtube = get_service()
        
        # Ensure #shorts is present in title and description to trigger Shorts shelf
        title = data['title']
        if "#shorts" not in title.lower():
            title += " #shorts"
            
        description = f"{data['script']}\n\n#shorts #facts #ai #knowledge"

        body = {
            "snippet": {
                "title": title,
                "description": description,
                "tags": ["shorts", "facts", "ai", "amazing"],
                "categoryId": "27" # Education category
            },
            "status": {
                "privacyStatus": "public", # Change to 'private' for initial testing if needed
                "selfDeclaredMadeForKids": False
            }
        }
        
        print(f"[UPLOADER] Preparing to upload: {file_path}")
        
        # Initialize resumable upload
        insert_request = youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=MediaFileUpload(file_path, chunksize=-1, resumable=True)
        )
        
        print(f"[UPLOADER] Sending file to YouTube...")
        response = None
        while response is None:
            status, response = insert_request.next_chunk()
            if status:
                print(f"[UPLOADER] Uploading... {int(status.progress() * 100)}%")
                
        print(f"[SUCCESS] Video uploaded successfully! Video ID: {response['id']}")
        print(f"[URL] https://www.youtube.com/shorts/{response['id']}")
        return response['id']
        
    except Exception as e:
        print(f"[UPLOADER CRITICAL ERROR] {e}")
        raise e