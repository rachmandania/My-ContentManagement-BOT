import os
import time
import random
import requests
import sys
import numpy as np
from PIL import Image
from moviepy import VideoClip, AudioFileClip, concatenate_audioclips

# --- 1. SETTINGS & DURATIONS ---
HORIZONTAL_DURATION = 30  # 30 seconds for testing
VERTICAL_DURATION = 15    # 15 seconds for testing

# --- 2. GENERATE SIMPLIFIED COZY CAFE IMAGE (NEW EACH RUN) ---
print("--- 1. GENERATING UNIQUE COZY CAFE IMAGE ---")
IMAGE_FILE = "background.jpg"

# Randomized prompts to guarantee a different cafe scene every run
CAFE_PROMPTS = [
    "digital painting of a cozy cafe interior with warm ambient lighting, steaming coffee on a wooden table, sharp focus, 4k resolution",
    "warm digital painting of a peaceful coffee shop with large windows and cozy wooden seating, sharp focus, 4k resolution",
    "lofi aesthetic painting of a warm inviting cafe at dusk, soft golden light, sharp focus, 4k resolution",
    "digital art of a quiet cozy cafe room with indoor plants and warm table lamps, highly detailed, sharp focus"
]

chosen_prompt = random.choice(CAFE_PROMPTS)
encoded_prompt = requests.utils.quote(chosen_prompt)

# Generate a random seed so Pollinations AI NEVER serves a cached duplicate
random_seed = random.randint(1, 999999)
image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=3840&height=2160&nologo=true&seed={random_seed}"

print(f"Prompt: '{chosen_prompt}' (Seed: {random_seed})")

try:
    img_data = requests.get(image_url, timeout=30)
    if img_data.status_code == 200 and len(img_data.content) > 10000:
        with open(IMAGE_FILE, "wb") as f:
            f.write(img_data.content)
        print("SUCCESS: New 4K Cafe image generated and saved!")
    else:
        raise Exception("Failed to fetch image or received empty response.")
except Exception as e:
    print(f"CRITICAL ERROR generating image: {e}")
    sys.exit(1)

# --- 3. DOWNLOAD CALM AUDIO (TRUE RANDOM ALTERNATION) ---
print("--- 2. FETCHING RANDOM RELAXING MUSIC ---")
AUDIO_FILE = "cafe_music.mp3"
audio_headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
audio_downloaded = False

# 6 fast, reliable direct MP3 links across different styles
CALM_MUSIC_URLS = [
    "https://cdn.pixabay.com/audio/2022/05/27/audio_1808fbf07a.mp3", # Lofi Chillhop 1
    "https://cdn.pixabay.com/audio/2022/05/16/audio_b2879685ed.mp3", # Lofi Chillhop 2
    "https://cdn.pixabay.com/audio/2022/01/18/audio_d0a13f69d2.mp3", # Gentle Acoustic
    "https://cdn.pixabay.com/audio/2022/03/15/audio_c8c8a7321f.mp3", # Smooth Lofi Jazz
    "https://archive.org/download/GymnopedieNo.1/Gymnopedie_No_1.mp3", # Classical Piano
    "https://archive.org/download/DebussyClairDeLune/Debussy%20-%20Clair%20de%20Lune.mp3" # Classical Piano
]

# Shuffle playlist so attempt sequence is unpredictable
random.shuffle(CALM_MUSIC_URLS)

for track_url in CALM_MUSIC_URLS[:3]:
    try:
        print("Attempting audio download...")
        audio_data = requests.get(track_url, headers=audio_headers, timeout=12, allow_redirects=True)
        if audio_data.status_code == 200 and len(audio_data.content) > 50000:
            with open(AUDIO_FILE, "wb") as f:
                f.write(audio_data.content)
            print("SUCCESS: Random calm audio downloaded!")
            audio_downloaded = True
            break
    except Exception as e:
        print(f"Track download failed ({e}), trying next track...")
        time.sleep(1)

# Randomized failsafe fallback if all primary attempts time out
if not audio_downloaded:
    print("Primary downloads timed out. Choosing randomized backup audio...")
    fallback_url = random.choice(CALM_MUSIC_URLS)
    audio_data = requests.get(fallback_url, headers=audio_headers, allow_redirects=True)
    with open(AUDIO_FILE, "wb") as f:
        f.write(audio_data.content)

# --- 4. RENDER MOVING VIDEOS (PAN & ZOOM) ---
print("--- 3. RENDERING SHARP MOVING VIDEOS ---")
audio_clip = AudioFileClip(AUDIO_FILE)
base_pil = Image.open(IMAGE_FILE)
orig_w, orig_h = base_pil.size

def prepare_audio(a_clip, target_dur):
    if a_clip.duration < target_dur:
        loops = int(target_dur // a_clip.duration) + 1
        a_out = concatenate_audioclips([a_clip] * loops)
    else:
        a_out = a_clip
    return a_out.subclipped(0, target_dur)

# Horizontal Rendering
print(f"Rendering horizontal_short.mp4 ({HORIZONTAL_DURATION}s)...")
def make_horiz_frame(t):
    p = t / HORIZONTAL_DURATION  
    zoom = 1.0 + 0.12 * p        
    crop_w = orig_w / zoom
    crop_h = orig_h / zoom
    x1 = (orig_w - crop_w) * p * 0.5
    y1 = (orig_h - crop_h) * p * 0.5
    cropped = base_pil.crop((x1, y1, x1 + crop_w, y1 + crop_h))
    resized = cropped.resize((1920, 1080), Image.Resampling.LANCZOS)
    return np.array(resized)

horiz_video = VideoClip(make_horiz_frame, duration=HORIZONTAL_DURATION)
horiz_audio = prepare_audio(audio_clip, HORIZONTAL_DURATION)
horiz_final = horiz_video.with_audio(horiz_audio)
horiz_final.write_videofile("horizontal_short.mp4", fps=24, codec="libx264", audio_codec="aac")

# Vertical Rendering
print(f"Rendering vertical_short.mp4 ({VERTICAL_DURATION}s)...")
target_v_w = int(orig_h * 9 / 16)
target_v_h = orig_h

if target_v_w % 2 != 0: target_v_w -= 1
if target_v_h % 2 != 0: target_v_h -= 1

def make_vert_frame(t):
    p = t / VERTICAL_DURATION
    zoom = 1.0 + 0.10 * p
    base_x1 = (orig_w - target_v_w) / 2
    crop_w = target_v_w / zoom
    crop_h = target_v_h / zoom
    x1 = base_x1 + (target_v_w - crop_w) * p * 0.5
    y1 = (target_v_h - crop_h) * p * 0.5
    cropped = base_pil.crop((x1, y1, x1 + crop_w, y1 + crop_h))
    resized = cropped.resize((1080, 1920), Image.Resampling.LANCZOS)
    return np.array(resized)

vert_video = VideoClip(make_vert_frame, duration=VERTICAL_DURATION)
vert_audio = prepare_audio(audio_clip, VERTICAL_DURATION)
vert_final = vert_video.with_audio(vert_audio)
vert_final.write_videofile("vertical_short.mp4", fps=24, codec="libx264", audio_codec="aac")

print("SUCCESS! Clean Cozy Cafe videos generated successfully!")
