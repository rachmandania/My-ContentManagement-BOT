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

# 3. Trigger the uploads with your specific Social Media Detox titles
print("--- STARTING YOUTUBE UPLOADS ---")

# Horizontal Upload (10 Minutes)
upload_video(
    file_path="horizontal_short.mp4",
    title="Take a moment to breathe 🌿 Lofi for a social media break",
    description="It's okay to rest. Put the phone down, listen to the calming lofi beats, and take a moment to breathe. No glowing screens, just a peaceful forest window and a warm cup of coffee.\n\nVisuals and audio compiled using AI tools.\n#lofi #socialmediadetox #relax #mentalhealth",
    tags=["lofi", "social media detox", "take a break", "relaxing music", "chillhop", "mental health break", "study music", "peaceful"]
)

# Vertical Short Upload (15 Seconds)
upload_video(
    file_path="vertical_short.mp4",
    title="Put the phone down and breathe 🌿 #shorts",
    description="A quick reminder to take a break from scrolling. Rest up and enjoy the lofi vibes. #shorts #lofi #detox #relax",
    tags=["shorts", "lofi", "social media detox", "take a break", "relax"]
)

print("--- YOUTUBE UPLOADS COMPLETE ---")
