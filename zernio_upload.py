import os
import sys
import requests

def get_public_video_url(file_path):
    print(f"🌍 Uploading {file_path} to temporary public host...")
    url = "https://tmpfiles.org/api/v1/upload"
    
    with open(file_path, "rb") as f:
        files = {"file": f}
        response = requests.post(url, files=files)
        
    if response.status_code == 200:
        # Inject '/dl' to make it a direct download link
        viewer_url = response.json()['data']['url']
        public_url = viewer_url.replace("tmpfiles.org/", "tmpfiles.org/dl/")
        print(f"✅ Public URL generated: {public_url}")
        return public_url
    else:
        print(f"❌ Failed to get public URL. Status: {response.status_code}")
        sys.exit(1)

def get_tiktok_account_id(api_key):
    print("🔍 Fetching your connected TikTok account ID from Zernio...")
    url = "https://zernio.com/api/v1/accounts"
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        
        # Handle the API list structure securely
        accounts = data.get('accounts', data.get('data', data)) if isinstance(data, dict) else data
        
        for acc in accounts:
            if acc.get('platform') == 'tiktok':
                # Grab the ID regardless of how Zernio formats it
                acc_id = acc.get('_id', acc.get('id', acc.get('accountId')))
                print(f"✅ Found TikTok Account ID: {acc_id}")
                return acc_id
                
        print("❌ Error: No connected TikTok account found in your Zernio dashboard!")
        print("👉 Please log into zernio.com and ensure your TikTok account is connected.")
        sys.exit(1)
    else:
        print(f"❌ Failed to fetch Zernio accounts. Status: {response.status_code}")
        print(response.text)
        sys.exit(1)

def upload_to_zernio(video_url, title):
    api_key = os.environ.get('ZERNIO_API_KEY')
    
    if not api_key:
        print("❌ Error: ZERNIO_API_KEY not found in environment variables.")
        sys.exit(1)

    # 1. Use the new radar function to dynamically grab your ID
    account_id = get_tiktok_account_id(api_key)

    # 2. Package the payload exactly how Zernio expects it
    print("🚀 Sending video to Zernio for distribution...")
    url = "https://zernio.com/api/v1/posts" 
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
        "platforms": [
            {
                "platform": "tiktok",
                "accountId": account_id
            }
        ],
        "publishNow": True
    }
    
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code in (200, 201):
        print("✅ SUCCESS: Video successfully queued in Zernio!")
    else:
        print(f"❌ Failed to send to Zernio. Status: {response.status_code}")
        print(response.text)
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python zernio_upload.py <video_file_path> <title>")
        sys.exit(1)
        
    video_file = sys.argv[1]
    video_title = sys.argv[2]
    
    public_link = get_public_video_url(video_file)
    upload_to_zernio(public_link, video_title)
