import os
import random
import requests
from moviepy import VideoFileClip, AudioFileClip, concatenate_videoclips, concatenate_audioclips

# --- 1. SETTINGS & KEYS ---
pixabay_key = os.environ.get("PIXABAY_API_KEY")

if not pixabay_key:
    print("Error: Missing PIXABAY_API_KEY environment variable!")
    exit(1)

TARGET_DURATION = 30  # Duration of the relaxation Short in seconds

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
    # Fallback search if specific topic yields no results
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

# --- 3. DOWNLOAD AMBIENT NATURE SOUNDS (GOOGLE LIBRARY) ---
print("--- 2. FETCHING HIGH-QUALITY NATURE SOUNDS ---")
NATURE_SOUND_URLS = [
    "https://actions.google.com/sounds/v1/ambiences/outdoor_river_stream.ogg",
    "https://actions.google.com/sounds/v1/weather/rain_heavy_loud.ogg",
    "https://actions.google.com/sounds/v1/water/ocean_waves.ogg",
    "https://actions.google.com/sounds/v1/ambiences/forest_birds.ogg"
]

selected_sound_url = random.choice(NATURE_SOUND_URLS)
AUDIO_FILE = "nature_sound.ogg"

print("Downloading nature sound track...")
audio_data = requests.get(selected_sound_url)

with open(AUDIO_FILE, "wb") as f:
    f.write(audio_data.content)
print("Nature sound downloaded successfully!")

# --- 4. RENDER FINAL VIDEO (MOVIEPY) ---
print("--- 3. RENDERING FINAL RELAXATION SHORT ---")
background_clip = VideoFileClip(VIDEO_FILE)
audio_clip = AudioFileClip(AUDIO_FILE)

# Loop or trim video clip to match TARGET_DURATION
if background_clip.duration < TARGET_DURATION:
    loops_needed = int(TARGET_DURATION // background_clip.duration) + 1
    video_clip = concatenate_videoclips([background_clip] * loops_needed)
else:
    video_clip = background_clip

video_clip = video_clip.subclipped(0, TARGET_DURATION)

# Loop or trim audio to match TARGET_DURATION
if audio_clip.duration < TARGET_DURATION:
    audio_loops = int(TARGET_DURATION // audio_clip.duration) + 1
    audio_clip = concatenate_audioclips([audio_clip] * audio_loops)

audio_clip = audio_clip.subclipped(0, TARGET_DURATION)

# Attach ambient nature audio to video
final_clip = video_clip.with_audio(audio_clip)

# Render output MP4
FINAL_OUTPUT = "final_short.mp4"
final_clip.write_videofile(
    FINAL_OUTPUT,
    fps=24,
    codec="libx264",
    audio_codec="aac"
)

print(f"SUCCESS! Relaxing nature video ready: {FINAL_OUTPUT}")
