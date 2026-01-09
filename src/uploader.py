import os
import google.oauth2.credentials
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
import pickle

# YouTube API scopes - Must match what you authorized in token.json
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def get_authenticated_service():
    creds = None
    # token.json stores the user's access and refresh tokens
    if os.path.exists('token.json'):
        creds = google.oauth2.credentials.Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If there are no (valid) credentials available, refresh them
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing Access Token...")
            creds.refresh(Request())
            # Save the refreshed credentials back to token.json for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        else:
            raise Exception("No valid token.json found. You must generate it locally first.")

    return build("youtube", "v3", credentials=creds)

def upload_to_youtube(video_file, data):
    youtube = get_authenticated_service()

    # Metadata for the video
    body = {
        "snippet": {
            "title": data['title'],
            "description": data['script'] + "\n\n#shorts #facts #mindblowing",
            "tags": ["shorts", "facts", "educational"],
            "categoryId": "27" # Education category
        },
        "status": {
            "privacyStatus": "public", # Use "private" or "unlisted" for testing
            "selfDeclaredMadeForKids": False,
        }
    }

    # Upload process
    insert_request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=MediaFileUpload(video_file, chunksize=-1, resumable=True)
    )

    print(f"Uploading file: {video_file}...")
    response = None
    while response is None:
        status, response = insert_request.next_chunk()
        if status:
            print(f"Uploaded {int(status.progress() * 100)}%")

    print(f"Upload Complete! Video ID: {response['id']}")
    return response['id']