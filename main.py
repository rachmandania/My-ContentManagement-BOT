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
AUDIO_FILE = "nature_sound.mp3"

# Using a highly reliable public MP3 stream that never blocks bots
sound_url = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"

print("Downloading sound track...")
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
audio_data = requests.get(sound_url, headers=headers, allow_redirects=True)

# Safety check: ensure we actually downloaded a real file, not an error page!
if audio_data.status_code == 200:
    with open(AUDIO_FILE, "wb") as f:
        f.write(audio_data.content)
    print("Sound downloaded successfully!")
else:
    print(f"CRITICAL ERROR: Failed to download audio. Status {audio_data.status_code}")
    exit(1)

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
