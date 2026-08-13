import os
import time
import random
import requests
import sys
from moviepy import ImageClip, AudioFileClip, concatenate_audioclips

# --- 1. SETTINGS & KEYS ---
pixabay_key = os.environ.get("PIXABAY_API_KEY")

if not pixabay_key:
    print("Error: Missing PIXABAY_API_KEY environment variable!")
    sys.exit(1)

# Kept short for testing
HORIZONTAL_DURATION = 30  
VERTICAL_DURATION = 15     

# --- 2. FETCH COZY CAFE IMAGE (PIXABAY) ---
print("--- 1. FETCHING COZY CAFE IMAGE FROM PIXABAY ---")
IMAGE_FILE = "background.jpg"

cafe_queries = ["cozy cafe interior", "coffee shop aesthetic", "lofi room window rain", "warm coffee shop"]
selected_query = random.choice(cafe_queries)
print(f"Searching image for: '{selected_query}'")

pixabay_image_url = f"https://pixabay.com/api/?key={pixabay_key}&q={selected_query}&image_type=photo&orientation=horizontal&per_page=20"
img_response = requests.get(pixabay_image_url).json()
img_hits = img_response.get("hits", [])

if not img_hits:
    pixabay_image_url = f"https://pixabay.com/api/?key={pixabay_key}&q=cafe&image_type=photo&orientation=horizontal&per_page=10"
    img_response = requests.get(pixabay_image_url).json()
    img_hits = img_response.get("hits", [])

chosen_img = random.choice(img_hits)
download_image_url = chosen_img.get("largeImageURL") or chosen_img.get("webformatURL")

print("Downloading cozy background image...")
img_data = requests.get(download_image_url)
with open(IMAGE_FILE, "wb") as f:
    f.write(img_data.content)
print(f"Saved background image: {IMAGE_FILE}")

# --- 3. DOWNLOAD LOFI / JAZZ MUSIC (PIXABAY) ---
print("--- 2. FETCHING RELAXING LOFI / JAZZ AUDIO ---")
AUDIO_FILE = "cafe_music.mp3"
audio_headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
audio_downloaded = False

print("Searching Pixabay Audio API...")
try:
    MUSIC_QUERIES = ["lofi", "jazz cafe", "chillhop", "relaxing jazz", "lofi chill"]
    chosen_music_query = random.choice(MUSIC_QUERIES)
    print(f"Searching for vibe: '{chosen_music_query}'")
    
    pixabay_audio_url = f"https://pixabay.com/api/audio/?key={pixabay_key}&q={chosen_music_query}&per_page=15"
    audio_response = requests.get(pixabay_audio_url).json()
    audio_hits = audio_response.get("hits", [])
    
    if audio_hits:
        chosen_track = random.choice(audio_hits)
        audio_download_url = chosen_track["download"]
        audio_data = requests.get(audio_download_url, headers=audio_headers, timeout=15)
        
        if audio_data.status_code == 200 and len(audio_data.content) > 10000:
            with open(AUDIO_FILE, "wb") as f:
                f.write(audio_data.content)
            print("Pixabay Lofi/Jazz track downloaded successfully!")
            audio_downloaded = True
except Exception as e:
    print(f"Audio Fetch Failed: {e}")

# Backup if Pixabay fails
if not audio_downloaded:
    print("Switching to reliable backup Lofi/Chill stream...")
    backup_url = "https://assets.mixkit.co/active_storage/sfx/1255/1255-preview.mp3"
    audio_data = requests.get(backup_url, headers=audio_headers, allow_redirects=True)
    with open(AUDIO_FILE, "wb") as f:
        f.write(audio_data.content)
    print("Emergency backup audio secured.")

# --- 4. RENDER DUAL FORMAT VIDEOS ---
print("--- 3. RENDERING HORIZONTAL (30 SEC) & CROPPED VERTICAL (15 SEC) ---")
base_img_clip = ImageClip(IMAGE_FILE)
audio_clip = AudioFileClip(AUDIO_FILE)

def build_media(img_clip, a_clip, target_dur):
    v_out = img_clip.with_duration(target_dur)
    
    if a_clip.duration < target_dur:
        a_loops = int(target_dur // a_clip.duration) + 1
        a_out = concatenate_audioclips([a_clip] * a_loops)
    else:
        a_out = a_clip
        
    a_out = a_out.subclipped(0, target_dur)
    return v_out.with_audio(a_out)

print(f"Rendering horizontal_short.mp4 ({HORIZONTAL_DURATION} seconds)...")
horiz_final = build_media(base_img_clip, audio_clip, HORIZONTAL_DURATION)
horiz_final.write_videofile("horizontal_short.mp4", fps=24, codec="libx264", audio_codec="aac")

print(f"Rendering vertical_short.mp4 by cropping horizontal source ({VERTICAL_DURATION} seconds)...")
w, h = base_img_clip.size
target_width = int(h * 9 / 16)
target_height = int(h)

if target_width % 2 != 0:
    target_width -= 1
if target_height % 2 != 0:
    target_height -= 1

cropped_base = base_img_clip.cropped(width=target_width, height=target_height, x_center=w/2, y_center=h/2)
vert_final = build_media(cropped_base, audio_clip, VERTICAL_DURATION)
vert_final.write_videofile("vertical_short.mp4", fps=24, codec="libx264", audio_codec="aac")

print("SUCCESS! Cozy Cafe videos generated successfully!")
