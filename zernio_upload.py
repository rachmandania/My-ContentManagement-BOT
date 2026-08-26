import os
import sys
import requests
import json

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
    url = "https://api.zernio.com/v1/accounts"
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
        sys.exit(1)
    else:
        print(f"❌ Failed to fetch Zernio accounts. Status: {response.status_code}")
        print(response.text)
        sys.exit(1)

def upload_to_zernio(video_url, caption):
    api_key = os.environ.get('ZERNIO_API_KEY')
    
    if not api_key:
        print("❌ Error: ZERNIO_API_KEY not found in environment variables.")
        sys.exit(1)

    # 1. Use the new radar function to dynamically grab your ID
    account_id = get_tiktok_account_id(api_key)

    # 2. Package the payload exactly how Zernio expects it, routing to Drafts
    print("🚀 Sending video to Zernio for distribution (Draft Mode)...")
    url = "https://api.zernio.com/v1/posts" 
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "content": caption,
        "mediaItems": [
            {
                "type": "video",
                "url": video_url
            }
        ],
        "platforms": [
            {
                "platform": "tiktok",
                "accountId": account_id,
                "tiktokSettings": {
                    "draft": True
                }
            }
        ]
    }
    
    response = requests.post(url, headers=headers, json=payload)
    
    # Accept 207 (Multi-Status) as a success since it signifies Zernio queued it
    if response.status_code in (200, 201, 207):
        print("✅ SUCCESS: Video successfully queued in Zernio!")
    else:
        print(f"❌ Failed to send to Zernio. Status: {response.status_code}")
        print(response.text)
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python zernio_upload.py <video_file_path>")
        sys.exit(1)
        
    video_file = sys.argv[1]
    
    # 1. Read the exact same metadata file used for YouTube
    metadata_file = "video_metadata.json"
    if not os.path.exists(metadata_file):
        print(f"❌ CRITICAL ERROR: Metadata file {metadata_file} not found.")
        sys.exit(1)

    with open(metadata_file, "r", encoding="utf-8") as f:
        meta = json.load(f)

    game_name = meta.get("game_name", "Game Relaxation")
    credits_text = meta.get("credits", "")

    # 2. Keep the exact same tags for maximum reach
    ALL_GAME_TAGS = [
        "GenshinImpact", "Genshin", "HoYoverse",
        "ArknightsEndfield", "Endfield", "Arknights",
        "NevernessToEverness", "NTE", "HottaStudio"
    ]
    
    combined_tags_vert = ALL_GAME_TAGS + ["shorts", "lofi", "relax", "fancontent", "fyp"]

    # 3. Convert the Python list into a string of TikTok hashtags
    hashtag_string = " ".join([f"#{tag}" for tag in combined_tags_vert])

    # 4. Construct the single TikTok caption (Title + Credits + Tags)
    tiktok_caption = (
        f"[Fan Content] {game_name} - Put the phone down and breathe 🌿\n\n"
        f"Credits: {credits_text}\n\n"
        f"{hashtag_string}"
    )
    
    # 5. Execute the upload sequence
    public_link = get_public_video_url(video_file)
    upload_to_zernio(public_link, tiktok_caption)
