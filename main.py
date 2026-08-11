import os
import random
import requests
from moviepy import VideoFileClip, AudioFileClip, concatenate_videoclips, concatenate_audioclips

# --- 1. SETTINGS & KEYS ---
pixabay_key = os.environ.get("PIXABAY_API_KEY")

if not pixabay_key:
    print("Error: Missing PIXABAY_API_KEY environment variable!")
    exit(1)

# Define our two different video durations
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

# --- 3. DOWNLOAD AMBIENT NATURE SOUNDS (INTERNET ARCHIVE) ---
print("--- 2. FETCHING HIGH-QUALITY NATURE SOUNDS ---")

# Reliable public domain nature sounds that do NOT block GitHub servers
NATURE_SOUND_URLS = [
    "https://archive.org/download/NatureSounds_201709/01%20Rain%20%26%20Thunder.mp3",
    "https://archive.org/download/NatureSounds_201709/02%20Stream%20Water.mp3",
    "https://archive.org/download/NatureSounds_201709/03%20Forest%20Birds.mp3"
]

selected_sound_url = random.choice(NATURE_SOUND_URLS)
AUDIO_FILE = "nature_sound.mp3"

print("Downloading nature sound track...")
audio_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}
audio_data = requests.get(selected_sound_url, headers=audio_headers, allow_redirects=True)

# Safety check: ensure we actually downloaded a real audio file (not a blank error page)
if audio_data.status_code == 200 and len(audio_data.content) > 1000:
    with open(AUDIO_FILE, "wb") as f:
        f.write(audio_data.content)
    print("Nature sound downloaded successfully!")
else:
    print(f"CRITICAL ERROR: Failed to download audio. Status {audio_data.status_code}")
    exit(1)

# --- 4. RENDER FINAL VIDEOS (MOVIEPY) ---
print("--- 3. RENDERING DUAL FORMAT VIDEOS ---")
background_clip = VideoFileClip(VIDEO_FILE)
audio_clip = AudioFileClip("nature_sound.mp3")

# Helper function to match clips to exact durations
def prepare_clips(vid_clip, aud_clip, target_duration):
    if vid_clip.duration < target_duration:
        loops = int(target_duration // vid_clip.duration) + 1
        v_clip = concatenate_videoclips([vid_clip] * loops)
    else:
        v_clip = vid_clip
    v_clip = v_clip.subclipped(0, target_duration)
    
    if aud_clip.duration < target_duration:
        a_loops = int(target_duration // aud_clip.duration) + 1
        a_clip = concatenate_audioclips([aud_clip] * a_loops)
    else:
        a_clip = aud_clip
    a_clip = a_clip.subclipped(0, target_duration)
    
    return v_clip.with_audio(a_clip)

# Render 1: Horizontal Version (30 seconds)
print("Rendering Horizontal Version (30s)...")
horizontal_clip = prepare_clips(background_clip, audio_clip, HORIZONTAL_DURATION)
horizontal_clip.write_videofile(
    "horizontal_short.mp4",
    fps=24,
    codec="libx264",
    audio_codec="aac"
)

# Render 2: Vertical Version (15 seconds, cropped)
print("Rendering Vertical Version (15s)...")
w, h = background_clip.size
target_width = int(h * 9 / 16)  # Calculate 9:16 aspect ratio width based on height

# Crop the center of the video for mobile screens
vertical_base = background_clip.cropped(width=target_width, height=h, x_center=w/2, y_center=h/2)
vertical_clip = prepare_clips(vertical_base, audio_clip, VERTICAL_DURATION)
vertical_clip.write_videofile(
    "vertical_short.mp4",
    fps=24,
    codec="libx264",
    audio_codec="aac"
)

print("SUCCESS! Both Horizontal and Vertical videos are ready!")
