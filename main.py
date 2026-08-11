import os
import random
import requests
from moviepy import VideoFileClip, AudioFileClip, concatenate_videoclips, concatenate_audioclips

# --- 1. SETTINGS & KEYS ---
pexels_key = os.environ.get("PEXELS_API_KEY")

if not pexels_key:
    print("Error: Missing PEXELS_API_KEY!")
    exit(1)

# Desired duration of the relaxation Short in seconds
TARGET_DURATION = 30 

# --- 2. RANDOM NATURE SEARCH (NO PEOPLE / LANDSCAPES ONLY) ---
NATURE_TOPICS = [
    "calm forest stream landscape",
    "ocean waves shore landscape",
    "waterfall mist landscape",
    "mountain river nature",
    "rain on green leaves vertical",
    "peaceful lake water landscape",
    "bamboo forest wind vertical",
    "coastal beach waves landscape"
]

selected_topic = random.choice(NATURE_TOPICS)
print(f"--- 1. SELECTED THEME: '{selected_topic}' ---")

# --- 3. FETCH RANDOM NATURE VIDEO (PEXELS API) ---
headers = {"Authorization": pexels_key}

# Pick a random page (1–5) to guarantee a different video every run
random_page = random.randint(1, 5)
pexel_url = f"https://api.pexels.com/videos/search?query={selected_topic}&orientation=portrait&per_page=15&page={random_page}"

search_response = requests.get(pexel_url, headers=headers).json()
videos = search_response.get("videos", [])

# Fallback search if page/query yields empty results
if not videos:
    pexel_url = "https://api.pexels.com/videos/search?query=nature+landscape&orientation=portrait&per_page=10"
    search_response = requests.get(pexel_url, headers=headers).json()
    videos = search_response.get("videos", [])

# Pick a random video from the list
chosen_video = random.choice(videos)
video_files = chosen_video["video_files"]

# Get optimal vertical HD link or fallback to first option
vertical_video_url = next(
    (v["link"] for v in video_files if v["width"] <= 1080 and v["height"] >= 1280),
    video_files[0]["link"]
)

VIDEO_FILE = "background.mp4"
print("Downloading nature video...")
video_data = requests.get(vertical_video_url)
with open(VIDEO_FILE, "wb") as f:
    f.write(video_data.content)
print(f"Saved nature video: {VIDEO_FILE}")

# --- 4. DOWNLOAD AMBIENT NATURE SOUNDS ---
# Royalty-free ambient nature audio tracks
NATURE_SOUND_URLS = [
    "https://upload.wikimedia.org/wikipedia/commons/2/21/Forest_birds_and_stream.ogg",
    "https://upload.wikimedia.org/wikipedia/commons/0/05/Ocean_waves_sound.ogg",
    "https://upload.wikimedia.org/wikipedia/commons/b/b5/Gentle_rain_loop.ogg"
]

selected_sound_url = random.choice(NATURE_SOUND_URLS)
AUDIO_FILE = "nature_sound.ogg"

print("Downloading nature sound track...")
# Apply a custom browser User-Agent so Wikimedia does not block our download
audio_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
audio_data = requests.get(selected_sound_url, headers=audio_headers)

with open(AUDIO_FILE, "wb") as f:
    f.write(audio_data.content)
print("Nature sound downloaded successfully!")

# --- 5. RENDER FINAL VIDEO (MOVIEPY) ---
print("--- RENDERING FINAL RELAXATION SHORT ---")
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
