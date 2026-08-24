import os
import requests
import json
import sys

def upload_to_tiktok(video_path, title):
    # 1. Grab the secure token from GitHub Secrets
    access_token = os.environ.get('TIKTOK_ACCESS_TOKEN')
    
    if not access_token:
        print("❌ Error: TIKTOK_ACCESS_TOKEN not found in environment variables.")
        sys.exit(1)

    print(f"🚀 Initializing TikTok upload for: {video_path}")
    
    # 2. Setup the API request
    url = "https://open.tiktokapis.com/v2/post/publish/video/init/"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; charset=UTF-8"
    }
    
    # 3. Configure the video details (SELF_ONLY is required for Sandbox mode)
    file_size = os.path.getsize(video_path)
    init_data = {
        "post_info": {
            "title": title,
            "privacy_level": "SELF_ONLY", 
            "disable_duet": True,
            "disable_comment": False,
            "disable_stitch": True
        },
        "source_info": {
            "source": "FILE_UPLOAD",
            "video_size": file_size,
            "chunk_size": file_size, 
            "total_chunk_count": 1
        }
    }
    
    # 4. Ask TikTok for permission to upload
    response = requests.post(url, headers=headers, data=json.dumps(init_data))
    
    if response.status_code == 200:
        upload_data = response.json()
        print("✅ TikTok granted upload access!")
        
        # 5. Push the actual video file to the URL TikTok provided
        upload_url = upload_data['data']['upload_url']
        print("Uploading video file bytes...")
        
        with open(video_path, 'rb') as f:
            video_data = f.read()
            
        upload_response = requests.put(
            upload_url, 
            headers={"Content-Type": "video/mp4", "Content-Length": str(file_size)}, 
            data=video_data
        )
        
        if upload_response.status_code in (200, 201):
            print("✅ SUCCESS: Video successfully uploaded to your TikTok Drafts!")
        else:
            print(f"❌ Failed to upload video bytes. Status: {upload_response.status_code}")
            print(upload_response.text)
            
    else:
        print(f"❌ Failed to initialize TikTok upload. Status: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    # We will pass the video file name and title directly from main.py or the workflow
    if len(sys.argv) < 3:
        print("Usage: python tiktok_upload.py <video_file_path> <title>")
        sys.exit(1)
        
    video_file = sys.argv[1]
    video_title = sys.argv[2]
    
    upload_to_tiktok(video_file, video_title)
