import os
import time
import random
import requests
import sys
from moviepy import VideoFileClip, AudioFileClip, concatenate_videoclips, concatenate_audioclips

# --- 1. SETTINGS & KEYS ---
pixabay_key = os.environ.get("PIXABAY_API_KEY")

if not pixabay_key:
    print("Error: Missing PIXABAY_API_KEY environment variable!")
    sys.exit(1)

HORIZONTAL_DURATION = 30  # 30 seconds
VERTICAL_DURATION = 15     # 15 seconds

# --- 2. FETCH RANDOM NATURE VIDEO (PIXABAY API) ---
NATURE_TOPICS = [
    "forest stream", "ocean waves", "waterfall mist", 
    "mountain river", "rain leaves", "peaceful lake"
]

selected_topic = random.choice(NATURE_TOPICS)
print(f"--- 1. SEARCHING PIXABAY VIDEO FOR THEME: '{selected_topic}' ---")

pixabay_video_url = f"https://pixabay.com/api/videos/?key={pixabay_key}&q={selected_topic}&per_page=15"
video_response = requests.get(pixabay_video_url).json()
video_hits = video_response.get("hits", [])

if not video_hits:
    pixabay_video_url = f"https://pixabay.com/api/videos/?key={pixabay_key}&q=nature&per_page=10"
    video_response = requests.get(pixabay_video_url).json()
    video_hits = video_response.get("hits", [])

chosen_video = random.choice(video_hits)
video_variants = chosen_video.get("videos", {})
download_video_url = (
    video_variants.get("large", {}).get("url") or 
    video_variants.get("medium", {}).get("url") or 
    video_variants.get("small", {}).get("url")
)

VIDEO_FILE = "background.mp4"
print("Downloading nature video from Pixabay...")
video_data = requests.get(download_video_url)
with open(VIDEO_FILE, "wb") as f:
    f.write(video_data.content)
print(f"Saved nature video: {VIDEO_FILE}")

# --- 3. DOWNLOAD AMBIENT NATURE SOUNDS (MULTI-LAYERED) ---
print("--- 2. FETCHING HIGH-QUALITY NATURE SOUNDS ---")
AUDIO_FILE = "nature_sound.mp3"
audio_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
audio_downloaded = False

# LAYER 1: PIXABAY AUDIO API (Main)
print("Attempting Layer 1: Pixabay Audio API...")
try:
    AUDIO_QUERIES = ["water stream", "rain", "forest birds", "ocean waves"]
    chosen_audio_query = random.choice(AUDIO_QUERIES)
    pixabay_audio_url = f"https://pixabay.com/api/audio/?key={pixabay_key}&q={chosen_audio_query}&per_page=10"
    
    audio_response = requests.get(pixabay_audio_url).json()
    audio_hits = audio_response.get("hits", [])
    
    if audio_hits:
        chosen_track = random.choice(audio_hits)
        audio_download_url = chosen_track["download"]
        audio_data = requests.get(audio_download_url, headers=audio_headers, timeout=15)
        
        if audio_data.status_code == 200 and len(audio_data.content) > 10000:
            with open(AUDIO_FILE, "wb") as f:
                f.write(audio_data.content)
            print("Pixabay nature sound downloaded successfully!")
            audio_downloaded = True
except Exception as e:
    print(f"Layer 1 Failed: {e}")

# LAYER 2: MIXKIT DIRECT LINKS (Backup)
if not audio_downloaded:
    print("Attempting Layer 2: Mixkit Direct Links...")
    MIXKIT_URLS = [
        "https://assets.mixkit.co/active_storage/sfx/1255/1255-preview.mp3",
        "https://assets.mixkit.co/active_storage/sfx/1251/1251-preview.mp3",
        "https://assets.mixkit.co/active_storage/sfx/1245/1245-preview.mp3"
    ]
    for attempt in range(2):
        try:
            mixkit_url = random.choice(MIXKIT_URLS)
            audio_data = requests.get(mixkit_url, headers=audio_headers, allow_redirects=True, timeout=15)
            if audio_data.status_code == 200 and len(audio_data.content) > 10000:
                with open(AUDIO_FILE, "wb") as f:
                    f.write(audio_data.content)
                print("Mixkit backup sound downloaded successfully!")
                audio_downloaded = True
                break
        except Exception as e:
            print(f"Mixkit attempt {attempt + 1} failed. Retrying...")
            time.sleep(2)

# LAYER 3: EMERGENCY FAILSAFE (Guaranteed Stream)
if not audio_downloaded:
    print("Attempting Layer 3: Emergency Failsafe Stream...")
    backup_url = "https://assets.mixkit.co/active_storage/sfx/1255/1255-preview.mp3"
    audio_data = requests.get(backup_url, headers=audio_headers, allow_redirects=True)
    with open(AUDIO_FILE, "wb") as f:
        f.write(audio_data.content)
    print("Emergency backup audio secured.")

# --- 4. RENDER DUAL FORMAT VIDEOS FROM ONE SOURCE ---
print("--- 3. RENDERING HORIZONTAL (10 MIN) & CROPPED VERTICAL (15 SEC) VIDEOS ---")
base_video_clip = VideoFileClip(VIDEO_FILE)
audio_clip = AudioFileClip(AUDIO_FILE)

def build_media(v_clip, a_clip, target_dur):
    if v_clip.duration < target_dur:
        loops = int(target_dur // v_clip.duration) + 1
        v_out = concatenate_videoclips([v_clip] * loops)
    else:
        v_out = v_clip
    v_out = v_out.subclipped(0, target_dur)
    
    if a_clip.duration < target_dur:
        a_loops = int(target_dur // a_clip.duration) + 1
        a_out = concatenate_audioclips([a_clip] * a_loops)
    else:
        a_out = a_clip
    a_out = a_out.subclipped(0, target_dur)
    
    return v_out.with_audio(a_out)

print("Rendering horizontal_short.mp4...")
horiz_final = build_media(base_video_clip, audio_clip, HORIZONTAL_DURATION)
horiz_final.write_videofile("horizontal_short.mp4", fps=24, codec="libx264", audio_codec="aac")

print("Rendering vertical_short.mp4 by cropping horizontal source...")
w, h = base_video_clip.size
target_width = int(h * 9 / 16)
target_height = int(h)

cropped_base = base_video_clip.cropped(width=target_width, height=target_height, x_center=w/2, y_center=h/2)
vert_final = build_media(cropped_base, audio_clip, VERTICAL_DURATION)
vert_final.write_videofile("vertical_short.mp4", fps=24, codec="libx264", audio_codec="aac")

print("SUCCESS! Both formats successfully generated from one video source!")
