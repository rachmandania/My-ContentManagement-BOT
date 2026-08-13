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

# Kept short for testing
HORIZONTAL_DURATION = 30  
VERTICAL_DURATION = 15     

# --- 2. ADVANCED THEME MAPPING ---
# Maps the video topic to BOTH a Pixabay search query AND a perfectly matching Mixkit backup URL
NATURE_MAP = {
    "forest stream": {
        "query": "water stream", 
        "backup": "https://assets.mixkit.co/active_storage/sfx/1255/1255-preview.mp3" # Stream/Water
    },
    "ocean waves": {
        "query": "ocean waves", 
        "backup": "https://assets.mixkit.co/active_storage/sfx/1255/1255-preview.mp3" # Stream/Water
    },
    "waterfall mist": {
        "query": "waterfall", 
        "backup": "https://assets.mixkit.co/active_storage/sfx/1255/1255-preview.mp3" # Stream/Water
    },
    "mountain river": {
        "query": "river", 
        "backup": "https://assets.mixkit.co/active_storage/sfx/1255/1255-preview.mp3" # Stream/Water
    },
    "rain leaves": {
        "query": "rain", 
        "backup": "https://assets.mixkit.co/active_storage/sfx/1245/1245-preview.mp3" # Rain
    },
    "peaceful lake": {
        "query": "forest birds", 
        "backup": "https://assets.mixkit.co/active_storage/sfx/1251/1251-preview.mp3" # Birds
    }
}

selected_video_topic = random.choice(list(NATURE_MAP.keys()))
selected_audio_query = NATURE_MAP[selected_video_topic]["query"]
selected_backup_url = NATURE_MAP[selected_video_topic]["backup"]

# --- 3. FETCH STRICTLY HORIZONTAL VIDEO (PIXABAY) ---
print(f"--- 1. SEARCHING PIXABAY VIDEO FOR THEME: '{selected_video_topic}' ---")

pixabay_video_url = f"https://pixabay.com/api/videos/?key={pixabay_key}&q={selected_video_topic}&per_page=20"
video_response = requests.get(pixabay_video_url).json()
video_hits = video_response.get("hits", [])

# STRICT FILTER: Only keep videos that are true Widescreen (Width > Height)
horizontal_hits = []
for v in video_hits:
    med = v.get("videos", {}).get("medium", {})
    if med.get("width", 0) > med.get("height", 0):
        horizontal_hits.append(v)

if not horizontal_hits:
    print("No horizontal videos found for specific topic. Searching generic nature...")
    pixabay_video_url = f"https://pixabay.com/api/videos/?key={pixabay_key}&q=nature&per_page=20"
    video_response = requests.get(pixabay_video_url).json()
    video_hits = video_response.get("hits", [])
    for v in video_hits:
        med = v.get("videos", {}).get("medium", {})
        if med.get("width", 0) > med.get("height", 0):
            horizontal_hits.append(v)

if not horizontal_hits and video_hits:
    horizontal_hits.append(video_hits[0])

chosen_video = random.choice(horizontal_hits)
video_variants = chosen_video.get("videos", {})
download_video_url = (
    video_variants.get("large", {}).get("url") or 
    video_variants.get("medium", {}).get("url") or 
    video_variants.get("small", {}).get("url")
)

VIDEO_FILE = "background.mp4"
print("Downloading true horizontal nature video from Pixabay...")
video_data = requests.get(download_video_url)
with open(VIDEO_FILE, "wb") as f:
    f.write(video_data.content)
print(f"Saved horizontal video: {VIDEO_FILE}")

# --- 4. DOWNLOAD MATCHING NATURE SOUNDS (MULTI-LAYERED) ---
print(f"--- 2. FETCHING MATCHING AUDIO FOR '{selected_audio_query}' ---")
AUDIO_FILE = "nature_sound.mp3"
audio_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}
audio_downloaded = False

# LAYER 1: PIXABAY AUDIO API (Perfectly Matched Sound)
print("Attempting Layer 1: Pixabay Audio API...")
try:
    pixabay_audio_url = f"https://pixabay.com/api/audio/?key={pixabay_key}&q={selected_audio_query}&per_page=10"
    audio_response = requests.get(pixabay_audio_url).json()
    audio_hits = audio_response.get("hits", [])
    
    if audio_hits:
        chosen_track = random.choice(audio_hits)
        audio_download_url = chosen_track["download"]
        audio_data = requests.get(audio_download_url, headers=audio_headers, timeout=15)
        
        if audio_data.status_code == 200 and len(audio_data.content) > 10000:
            with open(AUDIO_FILE, "wb") as f:
                f.write(audio_data.content)
            print(f"Pixabay matched sound ({selected_audio_query}) downloaded successfully!")
            audio_downloaded = True
except Exception as e:
    print(f"Layer 1 Failed: {e}")

# LAYER 2 & 3: EXACT MIXKIT FAILSAFE (Guaranteed Match)
if not audio_downloaded:
    print("Layer 1 Failed. Switching to guaranteed matching Mixkit backup...")
    for attempt in range(2):
        try:
            audio_data = requests.get(selected_backup_url, headers=audio_headers, allow_redirects=True, timeout=15)
            if audio_data.status_code == 200 and len(audio_data.content) > 10000:
                with open(AUDIO_FILE, "wb") as f:
                    f.write(audio_data.content)
                print("Mixkit backup sound downloaded successfully!")
                audio_downloaded = True
                break
        except Exception as e:
            print(f"Mixkit attempt {attempt + 1} failed. Retrying...")
            time.sleep(2)

# --- 5. RENDER DUAL FORMAT VIDEOS ---
print("--- 3. RENDERING HORIZONTAL (30s) & CROPPED VERTICAL (15s) VIDEOS ---")
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

# ENSURE EVEN DIMENSIONS SO IT DOESN'T CRASH MEDIA PLAYERS
if target_width % 2 != 0:
    target_width -= 1
if target_height % 2 != 0:
    target_height -= 1

cropped_base = base_video_clip.cropped(width=target_width, height=target_height, x_center=w/2, y_center=h/2)
vert_final = build_media(cropped_base, audio_clip, VERTICAL_DURATION)
vert_final.write_videofile("vertical_short.mp4", fps=24, codec="libx264", audio_codec="aac")

print("SUCCESS! Both formats successfully generated from one video source!")
