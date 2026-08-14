import os
import sys
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# 1. Load the secret token
token_env = os.environ.get("YOUTUBE_TOKEN_JSON")
if not token_env:
    print("CRITICAL ERROR: YOUTUBE_TOKEN_JSON is missing from GitHub Secrets.")
    sys.exit(1)

try:
    token_info = json.loads(token_env)
    creds = Credentials.from_authorized_user_info(token_info)
    youtube = build("youtube", "v3", credentials=creds)
except Exception as e:
    print(f"CRITICAL ERROR: Failed to authorize YouTube. {e}")
    sys.exit(1)

# 2. Define the upload function
def upload_video(file_path, title, description, tags, category_id="10"):
    # Note: category_id="10" maps to "Music" on YouTube
    if not os.path.exists(file_path):
        print(f"Error: Could not find {file_path} to upload.")
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
            "privacyStatus": "public",
            # This is the official API flag that tells YouTube the video is AI-generated!
            "containsSyntheticMedia": True 
        }
    }
    
    media = MediaFileUpload(file_path, chunksize=-1, resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    
    try:
        response = request.execute()
        print(f"SUCCESS! Video uploaded. YouTube ID: {response.get('id')}")
    except Exception as e:
        print(f"Upload failed for {file_path}. Error: {e}")

# 3. Trigger the uploads with your specific Cozy Cafe Lofi title
print("--- STARTING YOUTUBE UPLOADS ---")

# Horizontal Upload (10 Minutes)
upload_video(
    file_path="horizontal_short.mp4",
    title="Cozy Cafe Lofi ☕ Relax, Study, & Chill",
    description="Take a moment to relax in this cozy cafe. Perfect background lofi and jazz for studying, working, or just chilling out.\n\nVisuals and audio compiled using AI tools.\n#lofi #cozycafe #study #relax #chillhop",
    tags=["lofi", "cozy cafe", "study music", "relaxing jazz", "chillhop", "background music"]
)

# Vertical Short Upload (15 Seconds)
upload_video(
    file_path="vertical_short.mp4",
    title="Cozy Cafe Lofi ☕ Chill Vibes #shorts",
    description="Quick relaxation and cozy cafe vibes for your day. #shorts #lofi #cozycafe #study",
    tags=["shorts", "lofi", "cozy cafe", "relax"]
)

print("--- YOUTUBE UPLOADS COMPLETE ---")import os
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
