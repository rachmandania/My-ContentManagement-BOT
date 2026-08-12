import os
import sys
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# This script expects a saved token.json file containing your YouTube access credentials
TOKEN_ENV = os.environ.get("YOUTUBE_TOKEN_JSON")

if not TOKEN_ENV:
    print("Error: YOUTUBE_TOKEN_JSON secret is missing! Cannot authenticate to YouTube.")
    sys.exit(1)

# Load the credentials to authorize the upload
creds_data = json.loads(TOKEN_ENV)
credentials = Credentials.from_authorized_user_info(creds_data)
youtube = build("youtube", "v3", credentials=credentials)

def upload_video(file_path, title, description, tags, category_id="15"): # Category 15 = Pets & Animals/Nature
    if not os.path.exists(file_path):
        print(f"File {file_path} not found. Skipping upload.")
        return

    print(f"Uploading {file_path} to YouTube...")
    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": category_id
        },
        "status": {
            "privacyStatus": "public" # Change to "private" if you want to review them first
        }
    }

    media = MediaFileUpload(file_path, chunksize=-1, resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    
    response = request.execute()
    print(f"Upload Successful! Video ID: {response['id']}")

# 1. Upload the 10-Minute Horizontal Video
upload_video(
    file_path="horizontal_short.mp4",
    title="Rest up, enjoy the Nature",
    description="Take a deep breath and relax. 10 minutes of pure, uninterrupted nature and ambient sounds. #relax #nature #meditation",
    tags=["nature", "relax", "meditation", "ambient sounds"]
)

# 2. Upload the 15-Second Vertical Short
upload_video(
    file_path="vertical_short.mp4",
    title="Rest up, enjoy the Nature #shorts",
    description="A quick 15-second nature escape. #relax #nature #shorts",
    tags=["nature", "relax", "shorts", "peaceful"]
)
