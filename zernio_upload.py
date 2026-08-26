import os
import sys
import requests

def get_public_video_url(file_path):
    print(f"🌍 Uploading {file_path} to temporary public host...")
    url = "https://catbox.moe/user/api.php"
    data = {"reqtype": "fileupload"}
    
    with open(file_path, "rb") as f:
        files = {"fileToUpload": f}
        response = requests.post(url, data=data, files=files)
        
    if response.status_code == 200:
        public_url = response.text.strip()
        print(f"✅ Public URL generated: {public_url}")
        return public_url
    else:
        print(f"❌ Failed to get public URL. Status: {response.status_code}")
        sys.exit(1)

def upload_to_zernio(video_url, title):
    # Grab your secure key from GitHub Secrets
    api_key = os.environ.get('ZERNIO_API_KEY')
    
    if not api_key:
        print("❌ Error: ZERNIO_API_KEY not found in environment variables.")
        sys.exit(1)

    print("🚀 Sending video to Zernio for distribution...")
    
    # Standard Zernio API endpoint for posting
    url = "https://api.zernio.com/v1/posts" 
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "content": title,
        "mediaItems": [
            {
                "type": "video",
                "url": video_url
            }
        ],
        "platforms": ["tiktok"] 
    }
    
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code in (200, 201):
        print("✅ SUCCESS: Video successfully queued in Zernio!")
    else:
        print(f"❌ Failed to send to Zernio. Status: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python zernio_upload.py <video_file_path> <title>")
        sys.exit(1)
        
    video_file = sys.argv[1]
    video_title = sys.argv[2]
    
    # 1. Get the public link
    public_link = get_public_video_url(video_file)
    
    # 2. Send to Zernio
    upload_to_zernio(public_link, video_title)
