import os
import random
import requests
from moviepy import VideoFileClip, AudioFileClip, concatenate_videoclips, concatenate_audioclips

# --- 1. SETTINGS & KEYS ---
pixabay_key = os.environ.get("PIXABAY_API_KEY")

if not pixabay_key:
    print("Error: Missing PIXABAY_API_KEY environment variable!")
    exit(1)

HORIZONTAL_DURATION = 30
VERTICAL_DURATION = 15

# --- 2. FETCH RANDOM NATURE VIDEO (PIXABAY API) ---
NATURE_TOPICS = [
    "forest stream",
    "ocean waves",
    "waterfall mist",
    "mountain river",
    "rain leaves",
    "peaceful lake"
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

# --- 3. DOWNLOAD AMBIENT NATURE SOUNDS (ARCHIVE.ORG) ---
print("--- 2. FETCHING HIGH-QUALITY NATURE SOUNDS ---")
NATURE_SOUND_URLS = [
    "https://archive.org/download/NatureSounds_201709/01%20Rain%20%26%20Thunder.mp3",
    "https://archive.org/download/NatureSounds_201709/02%20Stream%20Water.mp3",
    "https://archive.org/download/NatureSounds_201709/03%20Forest%20Birds.mp3"
]

selected_sound_url = random.choice(NATURE_SOUND_URLS)
AUDIO_FILE = "nature_sound.mp3"

print("Downloading nature sound track...")
audio_headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
audio_data = requests.get(selected_sound_url, headers=audio_headers, allow_redirects=True)

if audio_data.status_code == 200 and len(audio_data.content) > 1000:
    with open(AUDIO_FILE, "wb") as f:
        f.write(audio_data.content)
    print("Nature sound downloaded successfully!")
else:
    print(f"CRITICAL ERROR: Failed to download audio. Status {audio_data.status_code}")
    exit(1)

# --- 4. RENDER DUAL FORMAT VIDEOS FROM ONE SOURCE ---
print("--- 3. RENDERING HORIZONTAL & CROPPED VERTICAL VIDEOS ---")
base_video_clip = VideoFileClip(VIDEO_FILE)
audio_clip = AudioFileClip(AUDIO_FILE)

# Helper function to prepare clips for target durations
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

# 1. Render Full Horizontal Video (30s)
print("Rendering horizontal_short.mp4...")
horiz_final = build_media(base_video_clip, audio_clip, HORIZONTAL_DURATION)
horiz_final.write_videofile("horizontal_short.mp4", fps=24, codec="libx264", audio_codec="aac")

# 2. Crop Horizontal Video into Vertical Short (15s)
print("Rendering vertical_short.mp4 by cropping horizontal source...")
w, h = base_video_clip.size
target_width = int(h * 9 / 16) # Calculate 9:16 width based on height

cropped_base = base_video_clip.cropped(width=target_width, height=h, x_center=w/2, y_center=h/2)
vert_final = build_media(cropped_base, audio_clip, VERTICAL_DURATION)
vert_final.write_videofile("vertical_short.mp4", fps=24, codec="libx264", audio_codec="aac")

print("SUCCESS! Both formats successfully generated from one video source!")
