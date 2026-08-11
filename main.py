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

# --- 3. FETCH NATURE AUDIO (PIXABAY API) ---
print("--- 2. SEARCHING PIXABAY FOR NATURE SOUNDS ---")
AUDIO_QUERIES = ["water stream", "rain", "forest birds", "ocean waves"]
chosen_audio_query = random.choice(AUDIO_QUERIES)

pixabay_audio_url = f"https://pixabay.com/api/audio/?key={pixabay_key}&q={chosen_audio_query}&per_page=10"
audio_response = requests.get(pixabay_audio_url).json()
audio_hits = audio_response.get("hits", [])

if not audio_hits:
    # Fallback search if specific query fails
    pixabay_audio_url = f"https://pixabay.com/api/audio/?key={pixabay_key}&q=nature&per_page=5"
    audio_response = requests.get(pixabay_audio_url).json()
    audio_hits = audio_response.get("hits", [])

chosen_track = random.choice(audio_hits)
audio_download_url = chosen_track["download"]

AUDIO_FILE = "nature_sound.mp3"
print(f"Downloading audio track: {chosen_track.get('title', 'Nature Sound')}...")
audio_data = requests.get(audio_download_url)
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
